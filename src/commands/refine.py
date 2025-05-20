from typing import Optional
from src.classes.game import Game
from src.classes.ore import PurityLevel
from src.classes.mineral import MINERALS, MineralQuality
from src.helpers import take_input
from src.data import OreCargo, MineralCargo
from .base import register_command
from .registry import Argument
from src.events.skill_events import (
    process_skill_xp_from_activity,
    notify_skill_progress,
)


def refine_command(game_state: Game, amount: Optional[int] = None) -> None:
    """
    Handle refining ore to a higher purity level.

    This command allows the player to refine their raw ore into more valuable
    processed versions at a station. Refining increases the ore's value but costs
    credits based on the ore's refining difficulty.
    """
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()

    # Convert string amount to int if needed
    if amount is not None and isinstance(amount, str):
        try:
            amount = int(amount)
        except ValueError:
            game_state.ui.error_message(
                "Invalid amount. Please provide a valid number."
            )
            return

    if not player_ship:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    if not player_character:
        game_state.ui.error_message("Error: Player character not found.")
        return

    # Must be docked at a station to refine
    if not player_ship.is_docked:
        game_state.ui.error_message("You must be docked at a station to refine ore.")
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("You are not docked at a station.")
        return

    # Check if player has any ore to refine
    if not player_ship.cargohold:
        game_state.ui.error_message("You have no ore in your cargo hold to refine.")
        return

    # Display available items to refine
    refinable_cargo = [
        cargo for cargo in player_ship.cargohold if cargo.ore.can_refine()
    ]

    if not refinable_cargo:
        game_state.ui.error_message("You have no ore that can be refined further.")
        return

    game_state.ui.info_message("Available ores to refine:")
    for i, cargo in enumerate(refinable_cargo, 1):
        next_purity = cargo.ore.get_next_purity_level().name
        current_value = cargo.ore.get_value()
        refined_ore = cargo.ore.create_refined_version()
        refined_value = refined_ore.get_value()

        game_state.ui.info_message(
            f"{i}. {cargo.ore.purity.name} {cargo.ore.name} "
            f"-> {next_purity} {cargo.ore.name}"
        )
        game_state.ui.info_message(
            f"   Quantity: {cargo.quantity}, Value: {current_value} -> {refined_value} credits"
        )
        game_state.ui.info_message(
            f"   Volume: {cargo.ore.volume} -> {refined_ore.volume} m³ per unit"
        )

    # Get user selection
    try:
        selection = int(take_input("Select ore number to refine (0 to cancel): "))
        if selection == 0:
            game_state.ui.info_message("Refining cancelled.")
            return

        if selection < 1 or selection > len(refinable_cargo):
            game_state.ui.error_message(
                f"Invalid selection. Please choose 1-{len(refinable_cargo)}."
            )
            return

        selected_cargo = refinable_cargo[selection - 1]

        # Ask for amount if not provided
        max_amount = selected_cargo.quantity
        if amount is None or amount <= 0:
            try:
                amount_str = take_input(
                    f"How many units to refine (1-{max_amount}, 'all' for all): "
                )
                if amount_str.lower() == "all":
                    amount = max_amount
                else:
                    amount = int(amount_str)
            except ValueError:
                game_state.ui.error_message("Invalid amount. Refining cancelled.")
                return

        # Validate amount
        assert amount is not None
        if amount <= 0:
            game_state.ui.error_message("Amount must be greater than 0.")
            return

        amount = min(amount, max_amount)

        # Calculate refining cost based on refining difficulty and amount
        base_refining_cost = 50  # Base cost per unit
        refining_cost_per_unit = (
            base_refining_cost * selected_cargo.ore.refining_difficulty
        )
        total_refining_cost = round(refining_cost_per_unit * amount, 2)

        # Check if player has enough credits
        if player_character.credits < total_refining_cost:
            game_state.ui.error_message(
                f"Not enough credits. Refining {amount} units costs {total_refining_cost} credits."
            )
            return

        # Show refining summary and confirm
        current_value_total = round(selected_cargo.ore.get_value() * amount, 2)
        refined_ore = selected_cargo.ore.create_refined_version()
        refined_value_total = round(refined_ore.get_value() * amount, 2)
        value_increase = refined_value_total - current_value_total

        game_state.ui.info_message("\n=== Refining Summary ===")
        game_state.ui.info_message(
            f"Ore: {selected_cargo.ore.purity.name} {selected_cargo.ore.name} -> {refined_ore.purity.name} {refined_ore.name}"
        )
        game_state.ui.info_message(f"Amount: {amount} units")
        game_state.ui.info_message(f"Current value: {current_value_total} credits")
        game_state.ui.info_message(f"Refined value: {refined_value_total} credits")
        game_state.ui.info_message(f"Value increase: {value_increase} credits")
        game_state.ui.info_message(f"Refining cost: {total_refining_cost} credits")
        game_state.ui.info_message(
            f"Net profit: {value_increase - total_refining_cost} credits"
        )

        confirm = take_input("Proceed with refining? (y/n): ").lower()
        if confirm != "y":
            game_state.ui.info_message("Refining cancelled.")
            return

        # Process the refining
        # 1. Reduce player credits
        player_character.remove_credits(total_refining_cost)

        # 2. Remove the refined ore from inventory
        selected_cargo.quantity -= amount
        # 3. Add the refined version to inventory
        # We need to check if we already have this refined ore type in inventory
        refined_ore_cargo = None
        for cargo in player_ship.cargohold:
            if (
                cargo.ore.id == selected_cargo.ore.id
                and cargo.ore.purity == refined_ore.purity
            ):
                refined_ore_cargo = cargo
                break

        if refined_ore_cargo:
            # If we already have this refined ore, just increase quantity
            refined_ore_cargo.quantity += amount
        else:
            # Otherwise add a new entry for the refined ore
            assert amount is not None
            new_refined_cargo = OreCargo(
                ore=refined_ore,
                quantity=amount,
                buy_price=selected_cargo.buy_price
                * 1.5,  # Higher buy price for refined ore
                sell_price=selected_cargo.sell_price
                * 1.5,  # Higher sell price for refined ore
            )
            player_ship.cargohold.append(new_refined_cargo)

        # Clean up empty entries in cargohold
        player_ship.cargohold = [
            cargo for cargo in player_ship.cargohold if cargo.quantity > 0
        ]

        # Grant experience for Refining & Processing skill
        assert amount is not None
        process_skill_xp_from_activity(game_state, "Refining & Processing", amount * 2)

        game_state.ui.success_message(
            f"Successfully refined {amount} units of {selected_cargo.ore.name} "
            f"to {refined_ore.purity.name} purity."
        )
        game_state.ui.info_message(f"Remaining credits: {player_character.credits}")

    except ValueError:
        game_state.ui.error_message("Invalid selection. Please enter a number.")
        return


def refine_to_minerals_command(game_state: Game, amount: Optional[int] = None) -> None:
    """
    Handle refining ore into minerals.

    This command allows the player to refine their ore into minerals at a station.
    The process is affected by ore purity, with higher purity ores yielding more minerals.
    """
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()

    # Convert string amount to int if needed
    if amount is not None and isinstance(amount, str):
        try:
            amount = int(amount)
        except ValueError:
            game_state.ui.error_message(
                "Invalid amount. Please provide a valid number."
            )
            return

    if not player_ship:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    if not player_character:
        game_state.ui.error_message("Error: Player character not found.")
        return

    # Must be docked at a station to refine
    if not player_ship.is_docked:
        game_state.ui.error_message(
            "You must be docked at a station to refine ore into minerals."
        )
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("You are not docked at a station.")
        return

    # Check if player has any ore to refine
    if not player_ship.cargohold:
        game_state.ui.error_message("You have no ore in your cargo hold to refine.")
        return

    # Display available items to refine
    refinable_cargo = [
        cargo for cargo in player_ship.cargohold if cargo.ore.mineral_yield
    ]

    if not refinable_cargo:
        game_state.ui.error_message(
            "You have no ore that can be refined into minerals."
        )
        return

    game_state.ui.info_message("Available ores to refine into minerals:")

    for i, cargo in enumerate(refinable_cargo, 1):
        mineral_yields = cargo.ore.get_mineral_yield()

        minerals_list = []
        for mineral_id, yield_amount in mineral_yields.items():
            mineral = MINERALS.get(mineral_id)
            if mineral:
                minerals_list.append(f"{mineral.name} ({yield_amount * 100:.0f}%)")

        minerals_str = ", ".join(minerals_list)

        game_state.ui.info_message(
            f"{i}. {cargo.ore.purity.name} {cargo.ore.name} " f"-> {minerals_str}"
        )
        game_state.ui.info_message(
            f"   Quantity: {cargo.quantity}, Purity: {cargo.ore.purity.name}"
        )

    # Get user selection
    try:
        selection = int(
            take_input("Select ore number to refine into minerals (0 to cancel): ")
        )
        if selection == 0:
            game_state.ui.info_message("Refining cancelled.")
            return

        if selection < 1 or selection > len(refinable_cargo):
            game_state.ui.error_message(
                f"Invalid selection. Please choose 1-{len(refinable_cargo)}."
            )
            return

        selected_cargo = refinable_cargo[selection - 1]
        # Ask for amount if not provided
        max_amount = selected_cargo.quantity
        if amount is None or amount <= 0:
            try:
                amount_str = take_input(
                    f"How many units to refine (1-{max_amount}, 'all' for all): "
                )
                if amount_str.lower() == "all":
                    amount = max_amount
                else:
                    amount = int(amount_str)
            except ValueError:
                game_state.ui.error_message("Invalid amount. Refining cancelled.")
                return
        # Validate amount
        if amount is None or amount <= 0:
            game_state.ui.error_message("Amount must be greater than 0.")
            return

        # At this point, amount is guaranteed to be a positive integer
        assert amount is not None, "Amount should not be None here"

        # Ensure amount doesn't exceed available quantity
        amount = min(amount, max_amount)

        # Calculate refining cost based on refining difficulty and amount
        base_refining_cost = 75  # Base cost per unit (higher than regular refining)
        refining_cost_per_unit = (
            base_refining_cost * selected_cargo.ore.refining_difficulty
        )
        total_refining_cost = round(refining_cost_per_unit * amount, 2)

        # Check if player has enough credits
        if player_character.credits < total_refining_cost:
            game_state.ui.error_message(
                f"Not enough credits. Refining {amount} units costs {total_refining_cost} credits."
            )
            return

        # Calculate the minerals that will be produced
        mineral_yields = selected_cargo.ore.get_mineral_yield()
        minerals_produced = {}
        total_minerals_volume = 0
        total_minerals_value = 0

        # Apply engineering skill bonus (if above 5, 1% per point)
        skill_bonus = 1.0
        if (
            hasattr(player_character, "engineering")
            and player_character.engineering > 5
        ):
            skill_bonus = 1.0 + ((player_character.engineering - 5) * 0.01)

        # Show refining summary
        game_state.ui.info_message("\n=== Mineral Refining Summary ===")
        game_state.ui.info_message(
            f"Ore: {selected_cargo.ore.purity.name} {selected_cargo.ore.name}"
        )
        game_state.ui.info_message(f"Amount: {amount} units")
        game_state.ui.info_message(
            f"Engineering Skill Bonus: +{(skill_bonus - 1.0) * 100:.0f}%"
        )
        game_state.ui.info_message("Minerals to be produced:")

        for mineral_id, yield_ratio in mineral_yields.items():
            mineral = MINERALS.get(mineral_id)
            if mineral:
                # Calculate mineral amount produced, applying skill bonus
                mineral_amount = round(amount * yield_ratio * skill_bonus)
                mineral_value = round(mineral.get_value() * mineral_amount, 2)
                mineral_volume = round(mineral.volume * mineral_amount, 2)

                total_minerals_value += mineral_value
                total_minerals_volume += mineral_volume

                minerals_produced[mineral_id] = mineral_amount

                game_state.ui.info_message(
                    f"  - {mineral.name}: {mineral_amount} units "
                    f"(Value: {mineral_value} credits, Volume: {mineral_volume} m³)"
                )

        # Check if we have enough cargo space
        ore_volume_to_be_removed = selected_cargo.ore.volume * amount
        net_volume_change = total_minerals_volume - ore_volume_to_be_removed

        if player_ship.get_remaining_cargo_space() < net_volume_change:
            game_state.ui.error_message(
                f"Not enough cargo space. This refining operation requires {net_volume_change} m³ additional space."
            )
            return

        game_state.ui.info_message(
            f"Total minerals value: {total_minerals_value} credits"
        )
        game_state.ui.info_message(f"Total minerals volume: {total_minerals_volume} m³")
        game_state.ui.info_message(f"Net cargo volume change: {net_volume_change} m³")
        game_state.ui.info_message(f"Refining cost: {total_refining_cost} credits")
        game_state.ui.info_message(
            f"Net profit: {total_minerals_value - total_refining_cost} credits"
        )
        confirm = take_input("Proceed with refining into minerals? (y/n): ").lower()
        if confirm != "y":
            game_state.ui.info_message("Refining cancelled.")
            return
        # Process the refining
        # 1. Reduce player credits
        player_character.remove_credits(total_refining_cost)

        # 2. Remove the ore from inventory
        selected_cargo.quantity -= amount

        # 3. Add the minerals to inventory
        for mineral_id, mineral_amount in minerals_produced.items():
            mineral = MINERALS.get(mineral_id)
            if (
                mineral and mineral_amount > 0
            ):  # Check if we already have this mineral in inventory
                existing_mineral_cargo = None

                # Player ship may not have mineralhold yet, create it if needed
                if not hasattr(player_ship, "mineralhold"):
                    player_ship.mineralhold = []

                for cargo in player_ship.mineralhold:
                    if (
                        cargo.mineral.id == mineral_id
                        and cargo.mineral.quality == MineralQuality.STANDARD
                    ):
                        existing_mineral_cargo = cargo
                        break

                if existing_mineral_cargo:
                    # If we already have this mineral, just increase quantity
                    existing_mineral_cargo.quantity += mineral_amount
                else:
                    # Otherwise add a new entry for the mineral
                    buy_price = (
                        mineral.get_value() * 0.8
                    )  # Some markdown from base value
                    sell_price = (
                        mineral.get_value() * 1.2
                    )  # Some markup from base value

                    new_mineral_cargo = MineralCargo(
                        mineral=mineral,
                        quantity=mineral_amount,
                        buy_price=buy_price,
                        sell_price=sell_price,
                    )
                    player_ship.mineralhold.append(new_mineral_cargo)
        # Clean up empty entries in cargohold
        player_ship.cargohold = [
            cargo for cargo in player_ship.cargohold if cargo.quantity > 0
        ]

        # Grant experience for Refining & Processing skill - more XP than regular refining
        assert amount is not None, "Amount should not be None here"
        skill_results = process_skill_xp_from_activity(
            game_state, "Refining & Processing", amount * 3
        )
        notify_skill_progress(game_state, skill_results)

        mineral_names = [
            MINERALS[mineral_id].name for mineral_id in minerals_produced.keys()
        ]
        mineral_names_str = ", ".join(mineral_names)

        game_state.ui.success_message(
            f"Successfully refined {amount} units of {selected_cargo.ore.name} "
            f"into minerals: {mineral_names_str}."
        )
        game_state.ui.info_message(f"Remaining credits: {player_character.credits}")

    except ValueError:
        game_state.ui.error_message("Invalid selection. Please enter a number.")
        return


# Register refine command
register_command(
    ["refine", "ref-ore"],
    refine_command,
    [Argument("amount", str, True)],
)

# Register mineral refining command
register_command(
    ["purify", "pur"],
    refine_to_minerals_command,
    [Argument("amount", str, True)],
)
