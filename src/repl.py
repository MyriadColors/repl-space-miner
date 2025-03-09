from src.classes.game import Character, Game
from src.classes.ship import Ship
from src.command_handlers import (
    refuel_command,
    scan_field_command,
    sell_command,
    travel_command,
    scan_command,
    display_help,
    command_dock,
    command_undock,
    display_time_and_status,
    mine_command,
    buy_command,
    add_creds_debug_command,
    command_exit,
    clear,
    add_ore_debug_command,
    direct_travel_command,
    debug_mode_command,
    process_command,
)
from src.command_handlers import register_command, Argument
from src.events import intro_event
import time
import pygame as pg
from colorama import Fore, Back, Style, init

init(autoreset=True)

# Constants for Character and Ship initialization
CHARACTER_NAME = "Player"
CHARACTER_AGE = 25
CHARACTER_SEX = "male"
CHARACTER_BACKGROUND = "Belter"
CHARACTER_STARTING_CREDS = 1000.0
CHARACTER_STARTING_DEBT = 0.0

SHIP_POSITION = pg.math.Vector2(0, 0)  # Placeholder for actual position
SHIP_SPEED = 0.0001
SHIP_FUEL_CAPACITY = 100
SHIP_FUEL_CONSUMPTION = 0.05
SHIP_HULL_CAPACITY = 100
SHIP_HULL_INTEGRITY = 100
SHIP_SHIELD_CAPACITY = 0.01
SHIP_NAME = "Player's Ship"

def register_commands(game_state: "Game"):
    register_command(
        ["refuel", "ref"],
        refuel_command,
        argument_list=[
            Argument(
                name="amount",
                type=float,
                is_optional=False,
                custom_validator=lambda x: isinstance(x, float) and x > 0,
            )
        ],
    )

    register_command(
        ["sell", "sl"],
        sell_command,
    )

    register_command(
        ["buy", "by"],
        buy_command,
        argument_list=[
            Argument(name="item_name", type=str, is_optional=False),
            Argument(
                name="amount",
                type=int,
                is_optional=False,
                custom_validator=lambda x: int(x) > 0,
            ),
        ],
    )

    register_command(
        ["travel", "tr"],  # Include "tr" as an abbreviation
        travel_command,
        argument_list=[
            Argument(
                name="sort_type",
                type=str,
                is_optional=False,
                custom_validator=lambda x: x in ["closest", "c"],
            ),
            Argument(
                name="object_type",
                type=str,
                is_optional=False,
                custom_validator=lambda x: x in ["field", "station", "f", "s"],
            ),
        ],
    )

    register_command(
        ["scan", "sc"],
        scan_command,
        argument_list=[
            Argument(
                name="num_objects",
                type=int,
                is_optional=False,
            ),
        ],
    )

    register_command(
        ["help", "h"],
        display_help,
        argument_list=[Argument(name="command_name", type=str, is_optional=True)],
    )

    register_command(
        ["direct_travel", "dtr"],
        direct_travel_command,
        argument_list=[
            Argument(name="destination_x", type=float, is_optional=False),
            Argument(name="destination_y", type=float, is_optional=False),
        ],
    )

    register_command(
        ["dock", "do"],
        command_dock,
    )

    register_command(
        ["undock", "ud"],
        command_undock,
    )

    register_command(
        ["status", "st"],
        display_time_and_status,
    )

    register_command(
        ["mine", "mi"],
        mine_command,
        argument_list=[
            Argument(name="time_to_mine", type=int, is_optional=True),  # Time to mine
            Argument(
                name="mine_until_full", type=str, is_optional=True
            ),  # Mine until full
            Argument(name="ore_selected", type=str, is_optional=True),  # Ores to mine
        ],
    )

    # COmmand to scan the asteroid field,r eturning the ores available
    register_command(
        ["scan_field", "scf"],
        scan_field_command,
    )

    register_command(["clear", "cl"], clear)

    register_command(["debug", "dm"], debug_mode_command)

    register_command(
        ["add_ore", "ao"],
        add_ore_debug_command,
        argument_list=[
            Argument(name="amount", type=int, is_optional=False),
            Argument(name="ore_name", type=str, is_optional=False),
        ],
    )

    register_command(
        ["add_creds", "ac"],
        add_creds_debug_command,
        argument_list=[Argument(name="amount", type=int, is_optional=False)],
    )


def start_repl():
    game_state = Game()
    register_commands(game_state)
    run_intro_and_setup(game_state)
    run_game_loop(game_state)


def run_intro_and_setup(game_state):
    intro_event(game_state)
    if not game_state.player_character:
        game_state.player_character = Character(
            name="Player", age=25, sex="male", background="Belter"
        )
    if not game_state.player_ship:
        game_state.player_ship = Ship(
            game_state.rnd_station.position,
            0.0001,
            100,
            0.05,
            100,
            100,
            0.01,
            "Player's Ship",
        )


def run_game_loop(game_state):
    while True:
        command_input = input("> ").lower()
        if command_input in ["exit", "quit"]:
            command_exit(game_state)
            break
        try:
            process_command(game_state, command_input)
        except ValueError as e:
            print(f"Invalid command: {e}")
        pg.time.wait(100) # Add a small delay to reduce CPU usage
    # Perform necessary cleanup operations here
    print("Performing cleanup operations before exiting the game.")
    pg.quit()
