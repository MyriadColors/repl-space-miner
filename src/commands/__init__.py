from .registry import Command, Argument, command_registry
from .base import register_command
from .refuel import refuel_command
from .travel import travel_command, direct_travel_command
from .scan import scan_command, scan_asteroids_command
from .examine import examine_command, belt_fields_command
from .docking import command_dock, command_undock
from .trading import buy_command, sell_command
from .trading_menu import trading_menu_command
from .mining import mine_command
from .upgrade import upgrade_command
from .debug import add_creds_debug_command, add_ore_debug_command, debug_mode_command
from .refine import refine_command, refine_to_minerals_command
from .cargo import cargo_command
from .market import market_command
from .price_compare import compare_prices_command, find_best_trade_routes
from .habitability import habitability_command, habitability_survey_command
from .ftl_commands import (
    refuel_antimatter_command,
    repair_containment_command,
    emergency_ejection_command,
    ftl_jump_command,
    list_systems_command,
)
from .game_reset import game_reset_command

# Antimatter Commands:
# - refuel_antimatter_command: Refuels the antimatter containment system.
# - repair_containment_command: Repairs the containment system to prevent leaks.
# - emergency_ejection_command: Ejects antimatter in emergencies to avoid catastrophic failure.
# - ftl_jump_command: Executes a faster-than-light jump using antimatter propulsion.
# - list_systems_command: Lists all available solar systems.
# - system_jump_command: Jumps to a solar system by index.
from .system import (
    display_help,
    display_time_and_status,
    command_exit,
    clear,
    save_game_command,
    load_game_command,
)
from .character import display_character_sheet
from .appearance import color_command, reset_command
from .sound import toggle_sound_command
from .banking import banking_menu_command

# Export the global command registry
commands = command_registry

__all__ = [
    "commands",
    "Command",
    "Argument",
    "register_command",
    "refuel_command",
    "travel_command",
    "direct_travel_command",
    "scan_command",
    "scan_asteroids_command",
    "examine_command",
    "belt_fields_command",
    "command_dock",
    "command_undock",
    "buy_command",
    "sell_command",
    "trading_menu_command",
    "mine_command",
    "upgrade_command",
    "display_help",
    "display_time_and_status",
    "command_exit",
    "clear",
    "save_game_command",
    "load_game_command",
    "display_character_sheet",
    "color_command",
    "reset_command",
    "toggle_sound_command",
    "banking_menu_command",
    "add_creds_debug_command",
    "add_ore_debug_command",
    "debug_mode_command",
    "market_command",
    "cargo_command",
    "habitability_command",
    "habitability_survey_command",
    "refuel_antimatter_command",
    "repair_containment_command",
    "emergency_ejection_command",
    "ftl_jump_command",
    "list_systems_command",
    "refine_command",
    "refine_to_minerals_command",
    "compare_prices_command",
    "find_best_trade_routes",
    "game_reset_command",
]
