"""
This module implements the market command to display the current station's market information.
"""

from src.classes.game import Game
from .base import register_command


def market_command(game_state: Game) -> None:
    """
    Display the market information of the current station the player is docked at.

    This command shows what items are available to buy and sell at the station,
    including their prices and available quantities.
    """
    player_ship = game_state.get_player_ship()

    if not player_ship:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    if not player_ship.is_docked:
        game_state.ui.error_message(
            "You must be docked at a station to access the market."
        )
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message(
            "Error: Cannot find the station you are docked at.")
        return

    # Display station market header
    game_state.ui.info_message(f"\n=== MARKET: {station.name} ===")
    game_state.ui.info_message(
        f"Cargo Capacity: {station.ore_cargo_volume:.2f}/{station.ore_capacity:.2f} m³\n"
    )

    # Display fuel prices
    game_state.ui.info_message("=== FUEL ===")
    game_state.ui.info_message(
        f"Fuel Price: {station.fuel_price:.2f} credits per m³")
    game_state.ui.info_message(
        f"Available Fuel: {station.fuel_tank:.2f}/{station.fuel_tank_capacity:.2f} m³\n"
    )

    # Display available ores for trading
    game_state.ui.info_message("=== AVAILABLE ORES ===")
    game_state.ui.info_message(
        f"{'Ore':<20} {'Quantity':<10} {'Buy Price':<12} {'Sell Price':<12} {'Value Diff':<12}"
    )
    game_state.ui.info_message("-" * 70)

    if station.ore_cargo:
        for ore_cargo in station.ore_cargo:
            ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"
            price_diff = ore_cargo.buy_price - ore_cargo.sell_price
            price_diff_str = f"{price_diff:.2f}"

            game_state.ui.info_message(
                f"{ore_name:<20} {ore_cargo.quantity:<10} {ore_cargo.buy_price:<12.2f} {ore_cargo.sell_price:<12.2f} {price_diff_str:<12}"
            )
    else:
        game_state.ui.info_message("No ores available at this station.")

    # Display trading instructions
    game_state.ui.info_message("\n=== TRADING COMMANDS ===")
    game_state.ui.info_message("To buy: 'buy <ore_name> <amount>'")
    game_state.ui.info_message("To sell: 'sell <ore_name> <amount>'")
    game_state.ui.info_message("To refuel: 'refuel <amount>'")
    game_state.ui.info_message(
        "\nNote: You can use 'all' instead of a specific amount."
    )
    game_state.ui.info_message(
        "Example: 'sell Pyrogen all' or 'buy Ferrite 50'")


# Register the market command
register_command(["market", "prices", "shop"], market_command, [])
