"""
This module implements the cargo command to display the player's ship cargo contents.
"""

from src.classes.game import Game
from .base import register_command


def cargo_command(game_state: Game) -> None:
    """
    Display the current cargo contents of the player's ship.

    This command shows a detailed inventory of all ores and minerals in the ship's cargo hold,
    including quantities, values, and the total cargo space used/remaining.
    """
    player_ship = game_state.get_player_ship()

    if not player_ship:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    # Calculate total cargo values and volumes
    total_ore_value = 0.0
    total_mineral_value = 0.0

    # Display header with cargo capacity information
    total_occupied = player_ship.cargohold_occupied + player_ship.mineralhold_occupied
    remaining_space = player_ship.get_remaining_cargo_space()

    game_state.ui.info_message(f"\n=== CARGO MANIFEST: {player_ship.name} ===")
    game_state.ui.info_message(
        f"Cargo Capacity: {total_occupied:.2f}/{player_ship.cargohold_capacity:.2f} m³ "
        f"({(total_occupied / player_ship.cargohold_capacity * 100):.1f}% full)"
    )
    game_state.ui.info_message(f"Available Space: {remaining_space:.2f} m³\n")

    # Display ores
    if player_ship.cargohold:
        game_state.ui.info_message("=== ORES ===")
        game_state.ui.info_message(
            f"{'Ore':<20} {'Quantity':<10} {'Volume':<10} {'Value/Unit':<12} {'Total Value':<12}"
        )
        game_state.ui.info_message("-" * 70)

        for cargo in player_ship.cargohold:
            ore_name = f"{cargo.ore.purity.name} {cargo.ore.name}"
            ore_volume = cargo.ore.volume * cargo.quantity
            ore_value = cargo.ore.get_value()
            ore_total_value = ore_value * cargo.quantity
            total_ore_value += ore_total_value

            game_state.ui.info_message(
                f"{ore_name:<20} {cargo.quantity:<10} {ore_volume:<10.2f} {ore_value:<12.2f} {ore_total_value:<12.2f}"
            )

        game_state.ui.info_message(
            f"\nTotal Ore Value: {total_ore_value:.2f} credits")
        game_state.ui.info_message(
            f"Total Ore Volume: {player_ship.cargohold_occupied:.2f} m³\n"
        )
    else:
        game_state.ui.info_message("No ores in cargo hold.\n")

    # Display minerals
    if player_ship.mineralhold:
        game_state.ui.info_message("=== MINERALS ===")
        game_state.ui.info_message(
            f"{'Mineral':<20} {'Quality':<10} {'Quantity':<10} {'Volume':<10} {'Value/Unit':<12} {'Total Value':<12}"
        )
        game_state.ui.info_message("-" * 80)

        for cargo in player_ship.mineralhold:
            mineral_name = cargo.mineral.name
            quality = cargo.mineral.quality.name.replace("_", " ").title()
            mineral_volume = cargo.mineral.volume * cargo.quantity
            mineral_value = cargo.mineral.get_value()
            mineral_total_value = mineral_value * cargo.quantity
            total_mineral_value += mineral_total_value

            game_state.ui.info_message(
                f"{mineral_name:<20} {quality:<10} {cargo.quantity:<10} {mineral_volume:<10.2f} {mineral_value:<12.2f} {mineral_total_value:<12.2f}"
            )

        game_state.ui.info_message(
            f"\nTotal Mineral Value: {total_mineral_value:.2f} credits"
        )
        game_state.ui.info_message(
            f"Total Mineral Volume: {player_ship.mineralhold_occupied:.2f} m³\n"
        )
    else:
        game_state.ui.info_message("No minerals in cargo hold.\n")

    # Display total cargo value
    total_cargo_value = total_ore_value + total_mineral_value
    game_state.ui.info_message("=== SUMMARY ===")
    game_state.ui.info_message(
        f"Total Cargo Value: {total_cargo_value:.2f} credits")
    game_state.ui.info_message(
        f"Total Cargo Space Used: {total_occupied:.2f}/{player_ship.cargohold_capacity:.2f} m³"
    )


# Register the cargo command
register_command(["cargo", "inv", "inventory"], cargo_command, [])
