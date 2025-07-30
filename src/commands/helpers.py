from typing import Optional
from src.classes.game import Game
from src.classes.station import Station
from src.classes.result import Result, CargoError, CargoErrorDetails


def update_ore_quantities(
    game_state: Game,
    ore_item,  # Changed from OreCargo to generic ore item
    ore_name: str,
    amount: int,
    price: float,
    station: Optional[Station] = None,
) -> None:
    """Update ore quantities in both player ship and station inventories using unified cargo system."""
    player_ship = game_state.get_player_ship()
    player_character = game_state.player_character

    if player_character is None:
        game_state.ui.error_message("Error: Player character not found.")
        return

    if station:
        # Handle station inventory updates if needed
        # This would need to be updated based on how station inventory is managed
        pass

    # Use the unified cargo system to add ore
    add_result = player_ship.add_cargo(
        ore_item, amount, price, price
    )
    if add_result.is_err():
        error = add_result.unwrap_err()
        if error.error_type == CargoError.INSUFFICIENT_SPACE:
            game_state.ui.error_message(f"Not enough cargo space: {error.message}")
            if error.context:
                game_state.ui.error_message(f"Required: {error.context.get('required_space', 'unknown')} m³, Available: {error.context.get('available_space', 'unknown')} m³")
        elif error.error_type == CargoError.INVALID_QUANTITY:
            game_state.ui.error_message(f"Invalid quantity: {error.message}")
        else:
            game_state.ui.error_message(f"Failed to add cargo: {error.message}")
        return  # Exit early on error

    # Note: calculate_cargo_occupancy is no longer needed with unified system

    if station:
        player_character.credits -= price
        game_state.ui.success_message(
            f"Report: {amount} {ore_name} bought for {price} credits."
        )
        game_state.ui.info_message(
            f"Your new credit balance: {player_character.credits} credits"
        )
    else:
        game_state.ui.info_message(
            f"Updated player ship cargo with {amount} {ore_name}."
        )
