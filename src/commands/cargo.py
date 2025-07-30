"""
This module implements the cargo command to display the player's ship cargo contents.
"""

from src.classes.game import Game
from src.classes.ore import Ore
from src.classes.mineral import Mineral
from src.classes.component import Component
from src.classes.finished_good import FinishedGood
from .base import register_command


def cargo_command(game_state: Game) -> None:
    """
    Display the current cargo contents of the player's ship.

    This command shows a detailed inventory of all items in the ship's unified cargo hold,
    including quantities, values, and the total cargo space used/remaining.
    """
    player_ship = game_state.get_player_ship()

    if not player_ship:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    try:
        # Get all cargo items using the new unified system
        all_cargo = player_ship.get_all_cargo()
        
        # Calculate total cargo space used
        total_occupied = player_ship.get_cargo_space_used()
        remaining_space = player_ship.get_remaining_cargo_space()

        game_state.ui.info_message(f"\n=== CARGO MANIFEST: {player_ship.name} ===")
        game_state.ui.info_message(
            f"Cargo Capacity: {total_occupied:.2f}/{player_ship.cargo_hold.capacity:.2f} m³ "
            f"({(total_occupied / player_ship.cargo_hold.capacity * 100):.1f}% full)"
        )
        game_state.ui.info_message(f"Available Space: {remaining_space:.2f} m³\n")

        if not all_cargo:
            game_state.ui.info_message("No items in cargo hold.\n")
            return
    except Exception as e:
        game_state.ui.error_message(f"Error accessing cargo information: {str(e)}")
        return

    # Group cargo by type for organized display
    ores = player_ship.get_cargo_by_type(Ore)
    minerals = player_ship.get_cargo_by_type(Mineral)
    components = player_ship.get_cargo_by_type(Component)
    finished_goods = player_ship.get_cargo_by_type(FinishedGood)

    total_cargo_value = 0.0

    # Display ores
    if ores:
        game_state.ui.info_message("=== ORES ===")
        game_state.ui.info_message(
            f"{'Ore':<20} {'Quantity':<10} {'Volume':<10} {'Value/Unit':<12} {'Total Value':<12}"
        )
        game_state.ui.info_message("-" * 70)

        ore_total_value = 0.0
        for cargo_item in ores:
            ore = cargo_item.item
            if isinstance(ore, Ore):
                ore_name = f"{ore.purity.name} {ore.commodity.name}"
                ore_volume = cargo_item.total_volume
                ore_value = ore.get_value()
                ore_item_total_value = ore_value * cargo_item.quantity
                ore_total_value += ore_item_total_value

                game_state.ui.info_message(
                    f"{ore_name:<20} {cargo_item.quantity:<10} {ore_volume:<10.2f} {ore_value:<12.2f} {ore_item_total_value:<12.2f}"
                )

        game_state.ui.info_message(f"\nTotal Ore Value: {ore_total_value:.2f} credits")
        game_state.ui.info_message(f"Total Ore Volume: {sum(item.total_volume for item in ores):.2f} m³\n")
        total_cargo_value += ore_total_value

    # Display minerals
    if minerals:
        game_state.ui.info_message("=== MINERALS ===")
        game_state.ui.info_message(
            f"{'Mineral':<20} {'Quality':<10} {'Quantity':<10} {'Volume':<10} {'Value/Unit':<12} {'Total Value':<12}"
        )
        game_state.ui.info_message("-" * 80)

        mineral_total_value = 0.0
        for cargo_item in minerals:
            mineral = cargo_item.item
            if isinstance(mineral, Mineral):
                mineral_name = mineral.commodity.name
                quality = mineral.quality.name.replace("_", " ").title()
                mineral_volume = cargo_item.total_volume
                mineral_value = mineral.get_value()
                mineral_item_total_value = mineral_value * cargo_item.quantity
                mineral_total_value += mineral_item_total_value

                game_state.ui.info_message(
                    f"{mineral_name:<20} {quality:<10} {cargo_item.quantity:<10} {mineral_volume:<10.2f} {mineral_value:<12.2f} {mineral_item_total_value:<12.2f}"
                )

        game_state.ui.info_message(f"\nTotal Mineral Value: {mineral_total_value:.2f} credits")
        game_state.ui.info_message(f"Total Mineral Volume: {sum(item.total_volume for item in minerals):.2f} m³\n")
        total_cargo_value += mineral_total_value

    # Display components
    if components:
        game_state.ui.info_message("=== COMPONENTS ===")
        game_state.ui.info_message(
            f"{'Component':<20} {'Quality':<10} {'Quantity':<10} {'Volume':<10} {'Value/Unit':<12} {'Total Value':<12}"
        )
        game_state.ui.info_message("-" * 80)

        component_total_value = 0.0
        for cargo_item in components:
            component = cargo_item.item
            if isinstance(component, Component):
                component_name = component.commodity.name
                quality = component.quality.name.replace("_", " ").title()
                component_volume = cargo_item.total_volume
                component_value = component.get_value()
                component_item_total_value = component_value * cargo_item.quantity
                component_total_value += component_item_total_value

                game_state.ui.info_message(
                    f"{component_name:<20} {quality:<10} {cargo_item.quantity:<10} {component_volume:<10.2f} {component_value:<12.2f} {component_item_total_value:<12.2f}"
                )

        game_state.ui.info_message(f"\nTotal Component Value: {component_total_value:.2f} credits")
        game_state.ui.info_message(f"Total Component Volume: {sum(item.total_volume for item in components):.2f} m³\n")
        total_cargo_value += component_total_value

    # Display finished goods
    if finished_goods:
        game_state.ui.info_message("=== FINISHED GOODS ===")
        game_state.ui.info_message(
            f"{'Finished Good':<20} {'Quality':<10} {'Quantity':<10} {'Volume':<10} {'Value/Unit':<12} {'Total Value':<12}"
        )
        game_state.ui.info_message("-" * 80)

        finished_good_total_value = 0.0
        for cargo_item in finished_goods:
            finished_good = cargo_item.item
            if isinstance(finished_good, FinishedGood):
                finished_good_name = finished_good.commodity.name
                quality = finished_good.quality.name.replace("_", " ").title()
                finished_good_volume = cargo_item.total_volume
                finished_good_value = finished_good.get_value()
                finished_good_item_total_value = finished_good_value * cargo_item.quantity
                finished_good_total_value += finished_good_item_total_value

                game_state.ui.info_message(
                    f"{finished_good_name:<20} {quality:<10} {cargo_item.quantity:<10} {finished_good_volume:<10.2f} {finished_good_value:<12.2f} {finished_good_item_total_value:<12.2f}"
                )

        game_state.ui.info_message(f"\nTotal Finished Good Value: {finished_good_total_value:.2f} credits")
        game_state.ui.info_message(f"Total Finished Good Volume: {sum(item.total_volume for item in finished_goods):.2f} m³\n")
        total_cargo_value += finished_good_total_value

    # Display total cargo value
    game_state.ui.info_message("=== SUMMARY ===")
    game_state.ui.info_message(f"Total Cargo Value: {total_cargo_value:.2f} credits")
    game_state.ui.info_message(
        f"Total Cargo Space Used: {total_occupied:.2f}/{player_ship.cargo_hold.capacity:.2f} m³"
    )


# Register the cargo command
register_command(["cargo", "inv", "inventory"], cargo_command, [])
