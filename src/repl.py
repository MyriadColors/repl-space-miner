from src.classes.game import Character, Game
from src.classes.ship import Ship
from src.commands import (
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
    upgrade_command,
    save_game_command,
    load_game_command,
    display_character_sheet,
    register_command,
    Argument,
)
from src.command_handlers import process_command
from src.events import intro_event
import pygame as pg
from colorama import init
from src.helpers import is_valid_int, is_valid_float, is_valid_bool

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
    """Register all game commands."""
    # System commands
    register_command(["status", "st"], display_time_and_status, [])
    register_command(
        ["help"], display_help, [Argument("command_name", str, True, 0, None)]
    )
    register_command(["exit"], command_exit, [])
    register_command(["clear", "cl"], clear, [])
    register_command(
        ["save"], save_game_command, [Argument("filename", str, True, 0, None)]
    )
    register_command(
        ["load"], load_game_command, [Argument("filename", str, True, 0, None)]
    )
    register_command(
        ["character", "char", "c", "character_sheet", "cs"], display_character_sheet, []
    )

    # Navigation commands
    register_command(
        ["travel", "tr"],
        travel_command,
        [
            Argument("sort_type", str, False, 0, None),
            Argument("object_type", str, True, 1, None),
        ],
    )
    register_command(
        ["direct_travel", "dtr"],
        direct_travel_command,
        [
            Argument("destination_x", str, False, 0, is_valid_float),
            Argument("destination_y", str, False, 1, is_valid_float),
        ],
    )
    register_command(
        ["scan", "sc"],
        scan_command,
        [Argument("num_objects", str, False, 0, is_valid_int)],
    )
    register_command(["scan_field", "scf"], scan_field_command, [])

    # Docking commands
    register_command(["dock", "do"], command_dock, [])
    register_command(["undock", "ud"], command_undock, [])

    # Trading commands
    register_command(
        ["buy", "by"],
        buy_command,
        [
            Argument("item_name", str, False, 0, None),
            Argument("amount", str, False, 1, is_valid_int),
        ],
    )
    register_command(["sell", "sl"], sell_command, [])
    register_command(
        ["refuel", "ref"],
        refuel_command,
        [Argument("amount", float, False, 0, None)],
    )

    # Mining commands
    register_command(
        ["mine", "mi"],
        mine_command,
        [
            Argument("time_to_mine", int, False, 0, is_valid_int),
            Argument("mine_until_full", bool, False, 1, is_valid_bool),
            Argument("ore_selected", str, True, 2, None),
        ],
    )

    # Upgrade commands
    register_command(
        ["upgrade", "up"],
        upgrade_command,
        [Argument("args", list, True)],
    )

    # Debug commands
    register_command(["debug", "dm"], debug_mode_command, [])
    register_command(
        ["add_credits", "ac"],
        add_creds_debug_command,
        [Argument("amount", str, False, 0, None)],
    )
    register_command(
        ["add_ores", "ao"],
        add_ore_debug_command,
        [
            Argument("amount", int, False, 0, None),
            Argument("ore_name", str, False, 1, None),
        ],
    )
    # Removed duplicate registration for display_character_sheet


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
        pg.time.wait(100)  # Add a small delay to reduce CPU usage
    # Perform necessary cleanup operations here
    print("Performing cleanup operations before exiting the game.")
    pg.quit()
