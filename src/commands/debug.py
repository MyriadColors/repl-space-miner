from src.classes.game import Game
from src.helpers import get_ore_by_id_or_name
from src.data import OreCargo
from .registry import Argument
from .base import register_command
from .helpers import update_ore_quantities
from .system import display_status


def add_ore_debug_command(game_state: Game, amount: int, ore_name: str) -> None:
    """Debug command to add ores to the player's ship."""
    game_state.ui.warn_message(
        "This is a debug/cheat command: with great power comes great responsibility!"
    )
    player_ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    if amount < 0:
        game_state.ui.error_message("You have entered a negative number.")
        return

    ore = get_ore_by_id_or_name(ore_name)
    if ore is None:
        game_state.ui.error_message(f"Invalid ore name: {ore_name}")
        return

    total_volume = ore.volume * amount
    if total_volume > player_ship.cargohold_occupied:
        game_state.ui.warn_message(
            "You are trying to add more cargo than your ship's capacity."
        )
        game_state.ui.warn_message(
            "Since this is a debug command, i will allow you to do that."
        )

    ore_cargo = OreCargo(ore, amount, ore.base_value, ore.base_value)
    update_ore_quantities(game_state, ore_cargo, ore_name, amount, ore.base_value)
    display_status(game_state)


def add_creds_debug_command(game_state: Game, amount: str) -> None:
    """Debug command to add credits to the player's account."""
    player_character = game_state.get_player_character()

    try:
        amount_value = float(amount)
    except ValueError:
        game_state.ui.error_message("Invalid amount. Please enter a valid number.")
        return

    if player_character is None:
        game_state.ui.error_message("Error: Player character not found.")
        return

    game_state.ui.info_message(
        f"You are adding {amount_value} credits to your account."
    )

    if game_state.debug_flag:
        if amount_value < 0:
            game_state.ui.warn_message(
                "You have entered a negative number, this means you lose money."
            )
            game_state.ui.warn_message("Are you sure? (y/n)")
            confirm = input(">> ").strip()
            if confirm != "y":
                return
        player_character.credits += amount_value
        game_state.ui.success_message(f"{amount_value} credits added to your credits.")
    else:
        game_state.ui.error_message(
            "Debug commands can only be used through the use of the 'debug' ('dm') command."
        )
        return

def add_cargo_space_debug_command(game_state: Game, amount: str) -> None:
    """Debug command to add cargo space to the player's ship."""
    try:
        amount_value = int(amount)
    except ValueError:
        game_state.ui.error_message("Invalid amount. Please enter a valid integer.")
        return

    player_ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    if amount_value < 0:
        game_state.ui.error_message("You have entered a negative number.")
        return

    player_ship.cargohold_capacity += amount_value
    game_state.ui.success_message(f"{amount_value} cargo space added to your ship.")

def debug_mode_command(game_state: Game) -> None:
    """Toggle debug mode on/off."""
    game_state.debug_flag = not game_state.debug_flag
    status = "enabled" if game_state.debug_flag else "disabled"
    game_state.ui.info_message(f"Debug mode {status}")


# Register debug commands
register_command(
    ["add_ore", "ao"],
    add_ore_debug_command,
    [
        Argument("amount", int, False),
        Argument("ore_name", str, False),
    ],
)

register_command(
    ["add_credits", "ac"],
    add_creds_debug_command,
    [Argument("amount", str, False)],
)

register_command(
    ["add_cargo", "acs"],
    add_cargo_space_debug_command,
    [Argument("amount", int, False)],
)

register_command(
    ["debug", "dm"],
    debug_mode_command,
    [],
)
