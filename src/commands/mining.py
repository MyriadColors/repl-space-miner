from typing import Optional

from src.classes.game import Game

from .registry import Argument
from .base import register_command


def mine_command(
    game_state: Game,
    time_to_mine: int,
    mine_until_full: bool,
    ore_selected: str | None,
) -> None:
    """Handle mining command execution."""
    player_ship = game_state.get_player_ship()
    
    # Check if ship is in an asteroid field
    is_in_field, field = player_ship.check_field_presence(game_state)
    if not is_in_field or field is None:
        game_state.ui.error_message("You must be in an asteroid field to mine.")
        return

    # Check if cargo is full
    if player_ship.is_cargo_full():
        game_state.ui.error_message("Your cargo hold is full.")
        return

    # Convert ore_selected to list if provided
    ores_selected_list = [ore_selected] if ore_selected else None

    # Execute mining
    player_ship.mine_belt(
        game_state,
        field,
        time_to_mine,
        mine_until_full,
        ores_selected_list,
    )


def scan_field_command(game_state: Game) -> None:
    """Handle scanning asteroid field command."""
    player_ship = game_state.get_player_ship()
    player_ship.scan_field(game_state)


# Register mining commands
register_command(
    ["mine", "m"],
    mine_command,
    [
        Argument("time_to_mine", int, False),
        Argument("mine_until_full", bool, True),
        Argument("ore_selected", str, True),
    ],
)

register_command(
    ["scan", "s"],
    scan_field_command,
    [],
) 