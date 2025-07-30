from typing import Optional, cast, Dict, Any
from src.classes.game import Game
from src.classes.ore import Ore
from src.classes.mineral import MINERALS, MineralQuality, Mineral
from src.helpers import take_input, get_ore_by_id_or_name
from .base import register_command
from .registry import Argument
from src.events.skill_events import process_skill_xp_from_activity, notify_skill_progress
from src.classes.result import Result, CargoError, CargoErrorDetails

def refine_command(game_state: Game, amount: Optional[str] = None) -> None:
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()

    if not player_ship:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    if not player_character:
        game_state.ui.error_message("Error: Player character not found.")
        return

    # Must be docked at a station to refine
    if not player_ship.is_docked:
        game_state.ui.error_message(
            "You must be docked at a station to refine ore.")
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("You are not docked at a station.")
        return

    # Check if player has any ore to refine
    ore_cargo = player_ship.get_cargo_by_type(Ore)
    if not ore_cargo:
        game_state.ui.error_message(
            "You have no ore in your cargo hold to refine.")
        return

    # Get refinable cargo items using unified system
    refinable_cargo = []
    for cargo_item in ore_cargo:
        # Type guard to ensure we have an Ore that can be refined
        if isinstance(cargo_item.item, Ore) and cargo_item.item.can_refine():
            refinable_cargo.append(cargo_item)

    if not refinable_cargo:
        game_state.ui.error_message(
            "You have no ore that can be refined further.")
        return

    # Parse the amount parameter
    target_ore = None
    refine_amount = None
    refine_all = False
    
    if amount:
        amount_parts = amount.strip().split()
        
        if len(amount_parts) == 1:
            if amount_parts[0].lower() == "all":
                refine_all = True
            else:
                # Try to parse as a number
                try:
                    refine_amount = int(amount_parts[0])
                except ValueError:
                    game_state.ui.error_message(
                        "Invalid amount. Please provide a valid number, 'all', or 'all <ore_name>'."
                    )
                    return
        elif len(amount_parts) == 2 and amount_parts[0].lower() == "all":
            # "all <ore_name>" format
            refine_all = True
            target_ore_name = amount_parts[1]
            target_ore = get_ore_by_id_or_name(target_ore_name)
            if not target_ore:
                game_state.ui.error_message(f"Unknown ore: {target_ore_name}")
                return
        else:
            game_state.ui.error_message(
                "Invalid format. Use: refine <amount>, refine all, or refine all <ore_name>"
            )
            return

    # If refining all of a specific ore type
    if refine_all and target_ore:
        # Find all cargo of the specified ore type that can be refined
        target_cargo = [
            cargo for cargo in refinable_cargo 
            if cargo.item.commodity.commodity_id == target_ore.commodity.commodity_id
        ]
        
        if not target_cargo:
            game_state.ui.error_message(
                f"You have no {target_ore.name} that can be refined further."
            )
            return
            
        # Refine each purity level of the target ore
        for cargo in target_cargo:
            _refine_specific_cargo(game_state, cargo, cargo.quantity)
        return

    # If refining all available ore
    if refine_all and not target_ore:
        game_state.ui.info_message("Refining all available ore...")
        
        # Calculate detailed information for each operation
        total_cost = 0.0
        total_current_value = 0.0
        total_refined_value = 0.0
        refining_operations: list[Dict[str, Any]] = []
        
        for cargo in refinable_cargo:
            # Type assertion since we know all items in refinable_cargo are Ore objects
            ore_item = cast(Ore, cargo.item)
            base_refining_cost = 50
            refining_cost_per_unit = base_refining_cost * ore_item.refining_difficulty
            operation_cost = round(refining_cost_per_unit * cargo.quantity, 2)
            
            # Calculate current and refined values
            current_value = round(ore_item.get_value() * cargo.quantity, 2)
            refined_ore = ore_item.create_refined_version()
            refined_value = round(refined_ore.get_value() * cargo.quantity, 2)
            value_increase = refined_value - current_value
            net_profit = value_increase - operation_cost
            
            total_cost += operation_cost
            total_current_value += current_value
            total_refined_value += refined_value
            
            refining_operations.append({
                'cargo': cargo,
                'amount': cargo.quantity,
                'cost': operation_cost,
                'current_value': current_value,
                'refined_value': refined_value,
                'value_increase': value_increase,
                'net_profit': net_profit,
                'refined_ore': refined_ore
            })
        
        # Check if player has enough credits for all operations
        if player_character.credits < total_cost:
            game_state.ui.error_message(
                f"Not enough credits. Refining all ore costs {total_cost} credits, "
                f"but you only have {player_character.credits} credits."
            )
            return
        
        # Show detailed summary
        game_state.ui.info_message("\n=== Refine All Summary ===")
        game_state.ui.info_message(f"Total operations: {len(refining_operations)}")
        game_state.ui.info_message("")
        
        # Show details for each operation
        for i, op in enumerate(refining_operations, 1):
            cargo = op['cargo']
            # Type assertion since we know all items in refining_operations are Ore objects
            ore_item = cast(Ore, cargo.item)
            refined_ore = cast(Ore, op['refined_ore'])
            game_state.ui.info_message(
                f"{i}. {ore_item.purity.name} {ore_item.name} -> {refined_ore.purity.name} {refined_ore.name}"
            )
            game_state.ui.info_message(f"   Amount: {op['amount']} units")
            game_state.ui.info_message(f"   Current value: {op['current_value']} credits")
            game_state.ui.info_message(f"   Refined value: {op['refined_value']} credits")
            game_state.ui.info_message(f"   Value increase: {op['value_increase']} credits")
            game_state.ui.info_message(f"   Refining cost: {op['cost']} credits")
            game_state.ui.info_message(f"   Net profit: {op['net_profit']} credits")
            game_state.ui.info_message("")
        
        # Show totals
        total_value_increase = total_refined_value - total_current_value
        total_net_profit = total_value_increase - total_cost
        
        game_state.ui.info_message("=== Totals ===")
        game_state.ui.info_message(f"Total current value: {total_current_value} credits")
        game_state.ui.info_message(f"Total refined value: {total_refined_value} credits")
        game_state.ui.info_message(f"Total value increase: {total_value_increase} credits")
        game_state.ui.info_message(f"Total refining cost: {total_cost} credits")
        game_state.ui.info_message(f"Total net profit: {total_net_profit} credits")
        
        confirm = take_input("Proceed with refining all ore? (y/n): ").lower()
        if confirm != "y":
            game_state.ui.info_message("Refining cancelled.")
            return
        
        # Process all refining operations
        for op in refining_operations:
            cargo = op['cargo']
            refine_amount = cast(int, op['amount'])
            _refine_specific_cargo(game_state, cargo, refine_amount, show_summary=False)
        
        game_state.ui.success_message(
            f"Successfully refined all available ore for {total_cost} credits."
        )
        game_state.ui.info_message(f"Total net profit: {total_net_profit} credits")
        return

    # Interactive selection mode (original behavior)
    game_state.ui.info_message("Available ores to refine:")
    for i, cargo in enumerate(refinable_cargo, 1):
        # Type assertion since we know all items in refinable_cargo are Ore objects
        ore_item = cast(Ore, cargo.item)
        next_purity_level = ore_item.get_next_purity_level()
        if next_purity_level is None:
            continue  # Skip if can't be refined further
        next_purity = next_purity_level.name
        current_value = ore_item.get_value()
        refined_ore = ore_item.create_refined_version()
        refined_value = refined_ore.get_value()

        game_state.ui.info_message(
            f"{i}. {ore_item.purity.name} {ore_item.name} "
            f"-> {next_purity} {ore_item.name}"
        )
        game_state.ui.info_message(
            f"   Quantity: {cargo.quantity}, Value: {current_value} -> {refined_value} credits"
        )
        game_state.ui.info_message(
            f"   Volume: {ore_item.volume} -> {refined_ore.volume} m³ per unit"
        )

    # Get user selection
    try:
        selection = int(take_input(
            "Select ore number to refine (0 to cancel): "))
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
        if refine_amount is None or refine_amount <= 0:
            try:
                amount_str = take_input(
                    f"How many units to refine (1-{max_amount}, 'all' for all): "
                )
                if amount_str.lower() == "all":
                    refine_amount = max_amount
                else:
                    refine_amount = int(amount_str)
            except ValueError:
                game_state.ui.error_message(
                    "Invalid amount. Refining cancelled.")
                return

        # Validate amount - ensure refine_amount is not None before proceeding
        if refine_amount is None or refine_amount <= 0:
            game_state.ui.error_message("Amount must be greater than 0.")
            return

        refine_amount = min(refine_amount, max_amount)
        
        # At this point, refine_amount is guaranteed to be a positive integer
        assert refine_amount is not None and refine_amount > 0
        
        # Process the refining
        _refine_specific_cargo(game_state, selected_cargo, refine_amount)

    except ValueError:
        game_state.ui.error_message(
            "Invalid selection. Please enter a number.")
        return


def _refine_specific_cargo(game_state: Game, selected_cargo, amount: int, show_summary: bool = True) -> None:
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()
    
    if not player_ship or not player_character:
        return

    # Calculate refining cost
    # Type assertion since we know selected_cargo.item is an Ore object
    ore_item = cast(Ore, selected_cargo.item)
    base_refining_cost = 50
    refining_cost_per_unit = base_refining_cost * ore_item.refining_difficulty
    total_refining_cost = round(refining_cost_per_unit * amount, 2)

    # Check if player has enough credits
    if player_character.credits < total_refining_cost:
        game_state.ui.error_message(
            f"Not enough credits. Refining {amount} units costs {total_refining_cost} credits."
        )
        return

    # Create refined version of the ore
    refined_ore = ore_item.create_refined_version()
    if not refined_ore:
        game_state.ui.error_message("This ore cannot be refined further.")
        return

    # Calculate values for summary
    current_value = round(ore_item.get_value() * amount, 2)
    refined_value = round(refined_ore.get_value() * amount, 2)
    value_increase = refined_value - current_value
    net_profit = value_increase - total_refining_cost

    if show_summary:
        game_state.ui.info_message("\n=== Refining Summary ===")
        game_state.ui.info_message(
            f"Ore: {ore_item.purity.name} {ore_item.name} -> {refined_ore.purity.name} Refined {refined_ore.name}"
        )
        game_state.ui.info_message(f"Amount: {amount} units")
        game_state.ui.info_message(f"Current value: {current_value} credits")
        game_state.ui.info_message(f"Refined value: {refined_value} credits")
        game_state.ui.info_message(f"Value increase: {value_increase} credits")
        game_state.ui.info_message(f"Refining cost: {total_refining_cost} credits")
        game_state.ui.info_message(f"Net profit: {net_profit} credits")

        confirm = take_input("Proceed with refining? (y/n): ").lower()
        if confirm != "y":
            game_state.ui.info_message("Refining cancelled.")
            return

    # Process the refining
    # 1. Reduce player credits
    player_character.remove_credits(total_refining_cost)

    # 2. Remove the original ore from cargo using the unified cargo system
    remove_result = player_ship.remove_cargo(selected_cargo.item_id, amount)
    if remove_result.is_err():
        error = remove_result.unwrap_err()
        if error.error_type == CargoError.ITEM_NOT_FOUND:
            game_state.ui.error_message(f"Ore not found in cargo: {error.message}")
        elif error.error_type == CargoError.INVALID_QUANTITY:
            game_state.ui.error_message(f"Invalid quantity for refining: {error.message}")
            if error.context:
                game_state.ui.error_message(f"Requested: {error.context.get('requested', 'unknown')}, Available: {error.context.get('available', 'unknown')}")
        else:
            game_state.ui.error_message(f"Failed to remove ore from cargo: {error.message}")
        # Refund the credits since the operation failed
        player_character.add_credits(total_refining_cost)
        return

    # 3. Add the refined ore to cargo
    add_result = player_ship.add_cargo(
        refined_ore,
        amount,
        selected_cargo.buy_price,  # Keep original buy price
        refined_ore.get_value() * 1.1  # Set sell price slightly above market value
    )
    
    if add_result.is_err():
        error = add_result.unwrap_err()
        if error.error_type == CargoError.INSUFFICIENT_SPACE:
            game_state.ui.error_message(f"Not enough cargo space for refined ore: {error.message}")
            if error.context:
                game_state.ui.error_message(f"Required: {error.context.get('required_space', 'unknown')} m³, Available: {error.context.get('available_space', 'unknown')} m³")
        else:
            game_state.ui.error_message(f"Failed to add refined ore to cargo: {error.message}")
        
        # Try to restore the original ore since refining failed
        restore_result = player_ship.add_cargo(
            ore_item,
            amount,
            selected_cargo.buy_price,
            selected_cargo.sell_price
        )
        
        if restore_result.is_err():
            game_state.ui.error_message("Critical error: Failed to restore original ore after refining failure!")
        
        # Refund the credits
        player_character.add_credits(total_refining_cost)
        return

    # 5. Grant experience for Refining & Processing skill
    skill_results = process_skill_xp_from_activity(
        game_state, "Refining & Processing", amount
    )
    notify_skill_progress(game_state, skill_results)

    if show_summary:
        game_state.ui.success_message(
            f"Successfully refined {amount} units of {ore_item.name} to {refined_ore.purity.name} purity."
        )
        game_state.ui.info_message(f"Remaining credits: {player_character.credits}")


def refine_to_minerals_command(game_state: Game, amount: Optional[str] = None) -> None:
    """
    Handle refining ore into minerals.

    This command allows the player to refine their ore into minerals at a station.
    The process is affected by ore purity, with higher purity ores yielding more minerals.
    """
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()

    # Convert string amount to int if needed
    refine_amount: Optional[int] = None
    if amount is not None:
        try:
            refine_amount = int(amount)
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
    ore_cargo = player_ship.get_cargo_by_type(Ore)
    if not ore_cargo:
        game_state.ui.error_message(
            "You have no ore in your cargo hold to refine.")
        return

    # Get refinable cargo items using unified system
    refinable_cargo = []
    for cargo_item in ore_cargo:
        # Type guard to ensure we have an Ore that can yield minerals
        if isinstance(cargo_item.item, Ore) and cargo_item.item.mineral_yield:
            refinable_cargo.append(cargo_item)

    if not refinable_cargo:
        game_state.ui.error_message(
            "You have no ore that can be refined into minerals."
        )
        return

    game_state.ui.info_message("Available ores to refine into minerals:")
    for i, cargo in enumerate(refinable_cargo, 1):
        # Type assertion since we know all items in refinable_cargo are Ore objects
        ore_item = cast(Ore, cargo.item)
        mineral_yields = ore_item.get_mineral_yield()
        minerals_list = []
        for mineral_id, yield_amount in mineral_yields.items():
            mineral = MINERALS.get(mineral_id)
            if mineral:
                minerals_list.append(
                    f"{mineral.commodity.name} ({yield_amount * 100:.0f}%)")

        minerals_str = ", ".join(minerals_list)

        game_state.ui.info_message(
            f"{i}. {ore_item.purity.name} {ore_item.name} -> {minerals_str}"
        )
        game_state.ui.info_message(
            f"   Quantity: {cargo.quantity}, Purity: {ore_item.purity.name}"
        )

    # Get user selection
    try:
        selection = int(
            take_input(
                "Select ore number to refine into minerals (0 to cancel): ")
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
        if refine_amount is None or refine_amount <= 0:
            try:
                amount_str = take_input(
                    f"How many units to refine (1-{max_amount}, 'all' for all): "
                )
                if amount_str.lower() == "all":
                    refine_amount = max_amount
                else:
                    refine_amount = int(amount_str)
            except ValueError:
                game_state.ui.error_message(
                    "Invalid amount. Refining cancelled.")
                return
        # Validate amount
        if refine_amount is None or refine_amount <= 0:
            game_state.ui.error_message("Amount must be greater than 0.")
            return

        # At this point, refine_amount is guaranteed to be a positive integer
        assert refine_amount is not None, "Amount should not be None here"

        # Ensure amount doesn't exceed available quantity
        refine_amount = min(refine_amount, max_amount)

        # Calculate refining cost based on refining difficulty and amount
        # Base cost per unit (higher than regular refining)
        # Type assertion since we know selected_cargo.item is an Ore object
        ore_item = cast(Ore, selected_cargo.item)
        base_refining_cost = 75
        refining_cost_per_unit = (
            base_refining_cost * ore_item.refining_difficulty
        )
        total_refining_cost = round(refining_cost_per_unit * refine_amount, 2)

        # Check if player has enough credits
        if player_character.credits < total_refining_cost:
            game_state.ui.error_message(
                f"Not enough credits. Refining {refine_amount} units costs {total_refining_cost} credits."
            )
            return

        # Calculate the minerals that will be produced
        mineral_yields = ore_item.get_mineral_yield()
        minerals_produced = {}
        total_minerals_volume = 0.0
        total_minerals_value = 0.0

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
            f"Ore: {ore_item.purity.name} {ore_item.name}"
        )
        game_state.ui.info_message(f"Amount: {refine_amount} units")
        game_state.ui.info_message(
            f"Engineering Skill Bonus: +{(skill_bonus - 1.0) * 100:.0f}%"
        )
        game_state.ui.info_message("Minerals to be produced:")

        for mineral_id, yield_ratio in mineral_yields.items():
            mineral = MINERALS.get(mineral_id)
            if mineral:
                # Calculate mineral amount produced, applying skill bonus
                mineral_amount = round(refine_amount * yield_ratio * skill_bonus)
                mineral_value = round(mineral.get_value() * mineral_amount, 2)
                mineral_volume = round(
                    mineral.commodity.volume_per_unit * mineral_amount, 2)

                total_minerals_value += mineral_value
                total_minerals_volume += mineral_volume

                minerals_produced[mineral_id] = mineral_amount

                game_state.ui.info_message(
                    f"  - {mineral.commodity.name}: {mineral_amount} units "
                    f"(Value: {mineral_value} credits, Volume: {mineral_volume} m³)"
                )

        # Check if we have enough cargo space
        ore_volume_to_be_removed = ore_item.volume * refine_amount
        net_volume_change = total_minerals_volume - ore_volume_to_be_removed

        if player_ship.get_remaining_cargo_space() < net_volume_change:
            game_state.ui.error_message(
                f"Not enough cargo space. This refining operation requires {net_volume_change} m³ additional space."
            )
            return

        game_state.ui.info_message(
            f"Total minerals value: {total_minerals_value} credits"
        )
        game_state.ui.info_message(
            f"Total minerals volume: {total_minerals_volume} m³")
        game_state.ui.info_message(
            f"Net cargo volume change: {net_volume_change} m³")
        game_state.ui.info_message(
            f"Refining cost: {total_refining_cost} credits")
        game_state.ui.info_message(
            f"Net profit: {total_minerals_value - total_refining_cost} credits"
        )
        confirm = take_input(
            "Proceed with refining into minerals? (y/n): ").lower()
        if confirm != "y":
            game_state.ui.info_message("Refining cancelled.")
            return
        # Process the refining
        # 1. Reduce player credits
        player_character.remove_credits(total_refining_cost)

        # 2. Remove the ore from inventory using unified cargo system
        remove_result = player_ship.remove_cargo(selected_cargo.item_id, refine_amount)
        if remove_result.is_err():
            error = remove_result.unwrap_err()
            if error.error_type == CargoError.ITEM_NOT_FOUND:
                game_state.ui.error_message(f"Ore not found in cargo: {error.message}")
            elif error.error_type == CargoError.INVALID_QUANTITY:
                game_state.ui.error_message(f"Invalid quantity for mineral refining: {error.message}")
                if error.context:
                    game_state.ui.error_message(f"Requested: {error.context.get('requested', 'unknown')}, Available: {error.context.get('available', 'unknown')}")
            else:
                game_state.ui.error_message(f"Failed to remove ore from cargo: {error.message}")
            # Refund the credits since the operation failed
            player_character.add_credits(total_refining_cost)
            return

        # 3. Add the minerals to inventory
        for mineral_id, mineral_amount in minerals_produced.items():
            mineral = MINERALS.get(mineral_id)
            if (
                mineral and mineral_amount > 0
            ):  # Check if we already have this mineral in inventory
                # Check if we already have this mineral using the unified cargo system
                existing_mineral_cargo = None
                mineral_items = player_ship.get_cargo_by_type(Mineral)
                
                for cargo_item in mineral_items:
                    # Type guard to ensure we have a Mineral
                    if isinstance(cargo_item.item, Mineral) and (
                        cargo_item.item.id == mineral_id
                        and cargo_item.item.quality == MineralQuality.STANDARD
                    ):
                        existing_mineral_cargo = cargo_item
                        break

                if existing_mineral_cargo:
                    # If we already have this mineral, add more using the unified system
                    # Remove the existing amount and add the new total
                    remove_result = player_ship.remove_cargo(existing_mineral_cargo.item_id, existing_mineral_cargo.quantity)
                    if remove_result.is_err():
                        error = remove_result.unwrap_err()
                        game_state.ui.error_message(f"Failed to remove existing mineral: {error.message}")
                        continue
                    
                    add_result = player_ship.add_cargo(
                        existing_mineral_cargo.item,
                        existing_mineral_cargo.quantity + mineral_amount,
                        existing_mineral_cargo.buy_price,
                        existing_mineral_cargo.sell_price
                    )
                    if add_result.is_err():
                        error = add_result.unwrap_err()
                        if error.error_type == CargoError.INSUFFICIENT_SPACE:
                            game_state.ui.error_message(f"Not enough cargo space for mineral {mineral.name}: {error.message}")
                        else:
                            game_state.ui.error_message(f"Failed to add mineral to cargo: {error.message}")
                        continue
                else:
                    # Otherwise add a new entry for the mineral
                    buy_price = (
                        mineral.get_value() * 0.8
                    )  # Some markdown from base value
                    sell_price = (
                        mineral.get_value() * 1.2
                    )  # Some markup from base value

                    add_result = player_ship.add_cargo(
                        mineral,
                        mineral_amount,
                        buy_price,
                        sell_price
                    )
                    if add_result.is_err():
                        error = add_result.unwrap_err()
                        if error.error_type == CargoError.INSUFFICIENT_SPACE:
                            game_state.ui.error_message(f"Not enough cargo space for mineral {mineral.name}: {error.message}")
                            if error.context:
                                game_state.ui.error_message(f"Required: {error.context.get('required_space', 'unknown')} m³, Available: {error.context.get('available_space', 'unknown')} m³")
                        else:
                            game_state.ui.error_message(f"Failed to add mineral to cargo: {error.message}")
                        continue
        # Note: Cleanup is now handled automatically by the unified cargo system

        # Grant experience for Refining & Processing skill - more XP than regular refining
        assert refine_amount is not None, "Amount should not be None here"
        skill_results = process_skill_xp_from_activity(
            game_state, "Refining & Processing", refine_amount * 3
        )
        notify_skill_progress(game_state, skill_results)

        mineral_names = [
            MINERALS[mineral_id].commodity.name for mineral_id in minerals_produced.keys()
        ]
        mineral_names_str = ", ".join(mineral_names)

        game_state.ui.success_message(
            f"Successfully refined {refine_amount} units of {ore_item.name} "
            f"into minerals: {mineral_names_str}."
        )
        game_state.ui.info_message(
            f"Remaining credits: {player_character.credits}")

    except ValueError:
        game_state.ui.error_message(
            "Invalid selection. Please enter a number.")
        return


# Register refine command - change argument type to str to handle "all" and "all <ore_name>"
register_command(
    ["refine", "ref-ore"],
    refine_command,
    [Argument("amount", str, True)],  # Change False to True to make it optional
)

# Register mineral refining command
register_command(
    ["refine-minerals", "ref-min"],
    refine_to_minerals_command,
    [Argument("amount", str, False)],  # Also update this one for consistency
)