from src.classes.game import Game
from .registry import Argument
from .base import register_command


def refuel_command(game_state: Game, amount: float) -> None:
    """Handle refueling the ship at a station.

    Args:
        game_state (Game): The current game state.
        amount (float): The amount of fuel to refuel.
    """
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        game_state.ui.error_message("Invalid amount specified for refueling.")
        return

    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message("Must be docked at a station to refuel.")
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("Not docked at any station.")
        return

    # Calculate how much fuel can be added
    max_fuel = player_ship.max_fuel - player_ship.fuel
    if max_fuel <= 0:
        game_state.ui.error_message("Ship's fuel tank is already full.")
        return

    # Limit amount to what can be added
    amount = min(amount, max_fuel)

    # Calculate cost with proper rounding
    total_cost = round(amount * station.fuel_price, 2)
    player_character = game_state.get_player_character()
    if player_character is None:
        game_state.ui.error_message("Player character not found.")
        return

    if player_character.credits < total_cost:
        game_state.ui.error_message(
            f"Not enough credits. Cost: {total_cost} credits")
        return

    # Confirm purchase
    game_state.ui.info_message(
        f"Refueling {amount} m³ of fuel will cost {total_cost} credits."
    )
    confirm = input("Confirm purchase? (y/n): ").lower()
    if confirm != "y":
        game_state.ui.info_message("Refueling cancelled.")
        return

    # Process refueling with proper credit management
    player_character.remove_credits(total_cost)
    player_ship.fuel += amount
    station.fuel_tank -= amount

    game_state.ui.success_message(
        f"Successfully refueled {amount} m³ of fuel.")
    game_state.ui.info_message(
        f"New fuel level: {player_ship.fuel}/{player_ship.max_fuel} m³"
    )
    game_state.ui.info_message(
        f"Remaining credits: {player_character.credits}")


# Register refuel command
register_command(
    ["refuel", "ref"],
    refuel_command,
    [Argument("amount", float, False)],
)
