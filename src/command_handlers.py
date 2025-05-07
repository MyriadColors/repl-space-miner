import os
from typing import Callable, Any, Optional

from src.classes.game import Game
from src.helpers import (
    take_input,
    rnd_float,
    rnd_int,
    get_closest_field,
    get_closest_station,
    euclidean_distance,
    prompt_for_closest_travel_choice,
    is_valid_int,
    is_valid_float,
    is_valid_bool,
)

# Colorama is still needed for direct colors in specific cases
import colorama
from colorama import Fore, Style
colorama.init()

from src.commands import commands, Command, Argument, register_command
from src.commands.travel import *
from src.commands.trading import *
from src.commands.mining import *
from src.commands.system import *
from src.commands.docking import *
from src.commands.debug import *
from src.commands.upgrade import *
from src.commands.refuel import refuel_command

# Make refuel_command available in this module's namespace
__all__ = [
    'refuel_command',
    'process_command',
    'execute_valid_command',
    'register_command',
    'Argument',
]


def process_command(game_state: Game, command_line: str):
    """
    Process a user command and execute the corresponding function.
    
    Parameters:
        game_state (Game): The current state of the game.
        command_line (str): The raw command string entered by the user.
    """
    # Handle empty command
    command_line = command_line.strip()
    if not command_line:
        game_state.ui.warn_message("No command entered.")
        raise ValueError("No command entered.")

    # Parse command input
    parts = command_line.split()
    command_name = parts[0]
    args = parts[1:]

    # Find and execute command if it exists
    command = commands.get_command(command_name)
    if command:
        try:
            execute_valid_command(game_state, command_name, args)
        except ValueError as e:
            game_state.ui.error_message(str(e))
    else:
        game_state.ui.error_message(f"Unknown command: {command_name}")


def execute_valid_command(game_state: Game, command_name: str, args: list[str]):
    """
    Execute a command after validating its arguments.
    
    Parameters:
        game_state (Game): The current state of the game.
        command_name (str): The name of the command to execute.
        args (list[str]): The arguments provided for the command.
    
    Raises:
        ValueError: If required arguments are missing or insufficient arguments are provided.
    """
    command = commands.get_command(command_name)
    if not command:
        raise ValueError(f"Command not found: {command_name}")
    
    # Check if we have enough arguments
    required_args_count = len([arg for arg in command.arguments if not arg.is_optional])
    if len(args) < required_args_count:
        game_state.ui.error_message(f"Missing required arguments for command '{command_name}'.")
        return
    
    # Map provided arguments to command parameters
    arg_dict = {}
    for i, arg in enumerate(command.arguments):
        if i < len(args):
            arg_dict[arg.name] = args[i]
        elif arg.is_optional:
            arg_dict[arg.name] = ""
        else:
            raise ValueError(f"Missing required argument: {arg.name}")
    
    # Execute the command
    command.function(game_state, **arg_dict)
