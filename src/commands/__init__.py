from .registry import CommandRegistry, Command, Argument, command_registry
from .base import register_command
from .refuel import refuel_command
from .travel import travel_command, direct_travel_command
from .scan import scan_command, scan_field_command
from .docking import command_dock, command_undock
from .trading import buy_command, sell_command
from .mining import mine_command
from .upgrade import upgrade_command
from .debug import add_creds_debug_command, add_ore_debug_command, debug_mode_command
from .system import (
    display_help,
    display_time_and_status,
    command_exit,
    clear,
    save_game_command,
    load_game_command
)
from .appearance import color_command, reset_command
from .sound import toggle_sound_command
from .banking import banking_menu_command

# Export the global command registry
commands = command_registry

__all__ = [
    'commands',
    'Command',
    'Argument',
    'register_command',
    'refuel_command',
    'travel_command',
    'direct_travel_command',
    'scan_command',
    'scan_field_command',
    'command_dock',
    'command_undock',
    'buy_command',
    'sell_command',
    'mine_command',
    'upgrade_command',
    'add_creds_debug_command',
    'add_ore_debug_command',
    'debug_mode_command',
    'display_help',
    'display_time_and_status',
    'command_exit',
    'clear',
    'save_game_command',
    'load_game_command',
    'color_command',
    'reset_command',
    'toggle_sound_command',
    'banking_menu_command',
]