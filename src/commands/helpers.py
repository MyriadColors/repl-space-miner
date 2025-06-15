from typing import Optional
from src.classes.game import Game
from src.classes.station import Station
from src.data import OreCargo


def update_ore_quantities(
    game_state: Game,
    ore_cargo: OreCargo,
    ore_name: str,
    amount: int,
    price: float,
    station: Optional[Station] = None,
) -> None:
    """Update ore quantities in both player ship and station inventories."""
    player_ship = game_state.get_player_ship()
    player_character = game_state.player_character

    if player_character is None:
        game_state.ui.error_message("Error: Player character not found.")
        return

    if station:
        amount = min(amount, ore_cargo.quantity)
        ore_cargo.quantity -= amount
        station.ore_cargo_volume -= round(amount * ore_cargo.ore.volume, 2)

    ore_cargo_found = player_ship.get_ore_cargo_by_id(ore_cargo.ore.id)

    if ore_cargo_found:
        ore_cargo_found.quantity += amount
    else:
        player_ship.cargohold.append(
            OreCargo(ore_cargo.ore, amount,
                     ore_cargo.buy_price, ore_cargo.sell_price)
        )

    player_ship.cargohold = [
        cargo for cargo in player_ship.cargohold if cargo.quantity > 0
    ]
    player_ship.calculate_cargo_occupancy()

    if station:
        player_character.credits -= price
        game_state.ui.success_message(
            f"Report: {amount} {ore_name} bought for {price} credits."
        )
        game_state.ui.info_message(
            f"Station Ore Report:\n{station.ore_cargo_volume} tons of ore remaining"
        )
        game_state.ui.info_message(
            f"Your new credit balance: {player_character.credits} credits"
        )
    else:
        game_state.ui.info_message(
            f"Updated player ship cargo with {amount} {ore_name}."
        )
