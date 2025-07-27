from src.classes.game import Game
from src.helpers import rnd_float, rnd_int, take_input
from src.events.skill_events import (
    process_skill_xp_from_activity,
    notify_skill_progress,
)
from .registry import Argument
from .base import register_command
import random
from typing import Optional, Tuple
from src.data import OreCargo


def barter(price: float) -> tuple[float, bool]:
    """Handles the bartering process and returns the potentially discounted price and success flag."""
    confirm = input("Want to barter for a discount? (y/n): ")
    bartering_flag: bool = False

    if confirm.lower() == "y":
        bartering_flag = True
        rng_number: float = rnd_float(0, 1)
        if rng_number < 0.5:
            discount: int = rnd_int(10, 25)
            new_price: float = round(price * (100 - discount) / 100, 2)
            print(f"Bartered for {discount}% discount off the original price.")
            print(f"New price: {new_price} credits")
            return new_price, bartering_flag
        else:
            print("Bartering failed.")
    return price, bartering_flag


def _validate_docking_status(game_state: Game) -> Optional[tuple]:
    """Validate that player is docked and return ship and station."""
    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message("Must be docked to trade items.")
        return None

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("Not docked at any station.")
        return None

    return player_ship, station


def _calculate_price_modifiers(player_character, is_buying: bool = True) -> float:
    """Calculate all price modifiers based on character traits and stats."""
    price_modifier = 1.0
    
    # Apply base trait modifier
    if is_buying and hasattr(player_character, "buy_price_mod"):
        price_modifier = player_character.buy_price_mod
    elif not is_buying and hasattr(player_character, "sell_price_mod"):
        price_modifier = player_character.sell_price_mod

    # Apply charisma bonus (0.5% per point above 5)
    if player_character.charisma > 5:
        charisma_multiplier = (player_character.charisma - 5) * 0.005
        if is_buying:
            charisma_bonus = 1 - charisma_multiplier  # Discount for buying
        else:
            charisma_bonus = 1 + charisma_multiplier  # Bonus for selling
        price_modifier *= charisma_bonus

    # Apply trader reputation bonus (0.25% per positive reputation point)
    if player_character.reputation_traders > 0:
        trader_multiplier = player_character.reputation_traders * 0.0025
        if is_buying:
            trader_bonus = 1 - trader_multiplier  # Discount for buying
        else:
            trader_bonus = 1 + trader_multiplier  # Bonus for selling
        price_modifier *= trader_bonus

    return price_modifier


def _apply_superstitious_trait(game_state: Game, player_character, price_modifier: float, is_buying: bool) -> float:
    """Apply superstitious trait effects randomly."""
    if (hasattr(player_character, "negative_trait") and 
        player_character.negative_trait == "Superstitious" and 
        random.random() < 0.1):  # 10% chance
        
        if is_buying:
            game_state.ui.warn_message(
                "You notice the transaction number ends in 13. A bad omen! You negotiate nervously."
            )
            return price_modifier * 1.05  # 5% price increase
        else:
            game_state.ui.warn_message(
                "You notice it's the 13th deal of the day. A bad omen! You negotiate nervously."
            )
            return price_modifier * 0.95  # 5% price decrease
    
    return price_modifier


def _show_price_adjustment_message(game_state: Game, price_modifier: float, is_buying: bool):
    """Show appropriate message based on price adjustment."""
    if is_buying:
        if price_modifier < 0.95:  # More than 5% discount
            game_state.ui.success_message("Your negotiation skills helped secure a better price!")
        elif price_modifier > 1.05:  # More than 5% increase
            game_state.ui.warn_message("The merchant seems to be charging you a premium...")
    else:
        if price_modifier > 1.05:  # More than 5% bonus
            game_state.ui.success_message("Your negotiation skills helped secure a better price!")
        elif price_modifier < 0.95:  # More than 5% decrease
            game_state.ui.warn_message("The merchant seems to be lowballing your offer...")


def _apply_charismatic_trait_message(game_state: Game, player_character, bartered: bool, price_modifier: float, is_buying: bool):
    """Apply charismatic trait message if applicable."""
    if (not bartered and 
        hasattr(player_character, "positive_trait") and 
        player_character.positive_trait == "Charismatic"):
        
        if (is_buying and price_modifier < 1.0) or (not is_buying and price_modifier > 1.0):
            message = "Your natural charisma helped secure a better deal." if is_buying else "Your natural charisma helped secure a better sale price."
            game_state.ui.success_message(message)


def _apply_forgetful_trait(game_state: Game, player_character, final_price: float) -> float:
    """Apply forgetful trait effects for selling."""
    if (hasattr(player_character, "negative_trait") and 
        player_character.negative_trait == "Forgetful" and 
        random.random() < 0.05):  # 5% chance
        
        lost_amount = round(final_price * 0.05, 2)  # Lose 5% of the sale
        final_price -= lost_amount
        game_state.ui.warn_message(
            f"You misplaced {lost_amount} credits during the transaction. How forgetful!"
        )
    
    return final_price


def _process_trading_skill_xp(game_state: Game, final_price: float):
    """Process skill experience from trading."""
    skill_results = process_skill_xp_from_activity(
        game_state,
        "trading",
        difficulty=min(2.0, max(1.0, final_price / 1000)),  # Higher price = more complex trade
    )
    notify_skill_progress(game_state, skill_results)


def _find_ore_cargo_by_identifier(station, identifier: str):
    """Find ore cargo by name or index."""
    available_cargo = [cargo for cargo in station.ore_cargo if cargo.quantity > 0]
    
    if identifier.isdigit():
        index = int(identifier) - 1  # Convert to 0-based index
        if 0 <= index < len(available_cargo):
            return available_cargo[index]
        return None
    else:
        return next(
            (cargo for cargo in available_cargo 
             if cargo.ore.name.lower() == identifier.lower()),
            None
        )


def _calculate_max_buyable_quantity(player_character, ore_cargo, player_ship, actual_price_per_unit: float) -> int:
    """Calculate maximum quantity that can be bought considering credits, space, and availability."""
    max_affordable = int(player_character.credits // actual_price_per_unit)
    remaining_space = player_ship.get_remaining_cargo_space()
    max_by_space = int(remaining_space // ore_cargo.ore.volume)
    
    return min(max_affordable, ore_cargo.quantity, max_by_space)


def buy_command(game_state: Game, item_name: str, amount: str) -> None:
    """Handle buying items from a station by name or index."""
    # Validate docking status
    docking_result = _validate_docking_status(game_state)
    if not docking_result:
        return
    player_ship, station = docking_result

    # Find the item to buy
    ore_cargo = _find_ore_cargo_by_identifier(station, item_name)
    if not ore_cargo:
        game_state.ui.error_message(f"Item {item_name} not found or not available.")
        return

    item = ore_cargo.ore
    player_character = game_state.get_player_character()
    if player_character is None:
        game_state.ui.error_message("Player character not found.")
        return

    # Calculate price modifiers
    price_modifier = _calculate_price_modifiers(player_character, is_buying=True)
    price_modifier = _apply_superstitious_trait(game_state, player_character, price_modifier, is_buying=True)
    actual_price_per_unit = ore_cargo.buy_price * price_modifier

    # Handle "all" amount or parse quantity
    if amount.lower() == "all":
        amount_int = _calculate_max_buyable_quantity(player_character, ore_cargo, player_ship, actual_price_per_unit)
        
        if amount_int <= 0:
            max_affordable = int(player_character.credits // actual_price_per_unit)
            remaining_space = player_ship.get_remaining_cargo_space()
            max_by_space = int(remaining_space // item.volume)
            
            if max_affordable <= 0:
                game_state.ui.error_message("Not enough credits to buy any units.")
            elif max_by_space <= 0:
                game_state.ui.error_message("Not enough cargo space.")
            else:
                game_state.ui.error_message("No units available to buy.")
            return
            
        game_state.ui.info_message(f"Buying maximum affordable quantity: {amount_int} units")
    else:
        try:
            amount_int = int(amount)
        except ValueError:
            game_state.ui.error_message("Invalid amount specified.")
            return

    # Validate quantity and space
    if ore_cargo.quantity < amount_int:
        game_state.ui.error_message(
            f"Station only has {ore_cargo.quantity} {item.purity.name} {item.name} available."
        )
        return

    required_space = item.volume * amount_int
    if player_ship.get_remaining_cargo_space() < required_space:
        game_state.ui.error_message(
            f"Not enough cargo space. Need {required_space:.2f} m³, but only {player_ship.get_remaining_cargo_space():.2f} m³ available."
        )
        return

    # Calculate total price
    total_price = round(ore_cargo.buy_price * amount_int * price_modifier, 2)
    
    # Show price adjustment message
    _show_price_adjustment_message(game_state, price_modifier, is_buying=True)

    if player_character.credits < total_price:
        game_state.ui.error_message("Not enough credits to make this purchase.")
        return

    # Handle bartering and confirmation
    final_price, bartered = barter(total_price)
    final_price = round(final_price, 2)
    
    game_state.ui.info_message(f"Total cost: {final_price} credits")
    
    confirm = take_input(f"Confirm purchase of {amount_int} {item.purity.name} {item.name} for {final_price} credits? (y/n): ")
    if confirm.lower() != "y":
        game_state.ui.info_message("Purchase cancelled.")
        return
    
    if player_character.credits < final_price:
        game_state.ui.error_message("Not enough credits to make this purchase.")
        return

    # Apply charismatic trait message
    _apply_charismatic_trait_message(game_state, player_character, bartered, price_modifier, is_buying=True)

    # Process transaction
    player_character.remove_credits(final_price)
    _process_trading_skill_xp(game_state, final_price)

    # Update inventories
    ore_cargo.quantity -= amount_int
    
    existing_cargo = next(
        (cargo for cargo in player_ship.cargohold if cargo.ore.id == item.id), None
    )
    if existing_cargo:
        existing_cargo.quantity += amount_int
    else:
        player_ship.cargohold.append(
            OreCargo(item, amount_int, ore_cargo.buy_price, ore_cargo.sell_price)
        )

    game_state.ui.info_message(
        f"Successfully purchased {amount_int} {item.purity.name} {item.name} for {final_price} credits."
    )


def sell_command(game_state: Game) -> None:
    """Handle selling items to a station."""
    # Validate docking status
    docking_result = _validate_docking_status(game_state)
    if not docking_result:
        return
    player_ship, station = docking_result

    if not player_ship.cargohold:
        game_state.ui.error_message("No items to sell.")
        return

    # Display available items
    game_state.ui.info_message("Available items to sell:")
    for i, cargo in enumerate(player_ship.cargohold, 1):
        game_state.ui.info_message(
            f"{i}. {cargo.ore.name} - Quantity: {cargo.quantity}"
        )

    # Get user selection
    try:
        selection = int(take_input("Select item number to sell (0 to cancel): "))
        if selection == 0:
            return
        if selection < 1 or selection > len(player_ship.cargohold):
            game_state.ui.error_message("Invalid selection.")
            return
    except ValueError:
        game_state.ui.error_message("Invalid input.")
        return

    # Get quantity to sell
    quantity_input = take_input("Enter quantity to sell (or 'all' for entire stack): ")
    
    # Validate selection first to get the cargo
    selected_cargo = player_ship.cargohold[selection - 1]
    
    # Handle "all" or parse quantity
    if quantity_input.lower() == "all":
        quantity = selected_cargo.quantity
        game_state.ui.info_message(f"Selling all {quantity} units")
    else:
        try:
            quantity = int(quantity_input)
            if quantity <= 0:
                game_state.ui.error_message("Quantity must be positive.")
                return
        except ValueError:
            game_state.ui.error_message("Invalid quantity. Enter a number or 'all'.")
            return

    # Validate quantity
    if quantity > selected_cargo.quantity:
        game_state.ui.error_message("Not enough items in cargo.")
        return

    player_character = game_state.get_player_character()
    if player_character is None:
        game_state.ui.error_message("Player character not found.")
        return

    # Calculate price with modifiers
    base_price = selected_cargo.ore.get_value() * quantity
    price_modifier = _calculate_price_modifiers(player_character, is_buying=False)
    price_modifier = _apply_superstitious_trait(game_state, player_character, price_modifier, is_buying=False)
    total_price = round(base_price * price_modifier, 2)

    # Show price adjustment message
    _show_price_adjustment_message(game_state, price_modifier, is_buying=False)

    # Try to barter
    final_price, bartered = barter(total_price)
    final_price = round(final_price, 2)
    
    # Confirm the sale before proceeding
    confirm = take_input(f"Confirm sale of {quantity} {selected_cargo.ore.name} for {final_price} credits? (y/n): ")
    if confirm.lower() != "y":
        game_state.ui.info_message("Sale cancelled.")
        return

    # Apply Charismatic trait message if applicable and wasn't already bartered up
    _apply_charismatic_trait_message(game_state, player_character, bartered, price_modifier, is_buying=False)

    # Check for Forgetful negative trait - 5% chance to forget some of your payment
    final_price = _apply_forgetful_trait(game_state, player_character, final_price)

    # Process transaction
    player_character.add_credits(final_price)
    _process_trading_skill_xp(game_state, final_price)

    # Update cargo quantities
    selected_cargo.quantity -= quantity
    if selected_cargo.quantity <= 0:
        player_ship.cargohold.remove(selected_cargo)

    # Add to station inventory
    station.add_item(selected_cargo.ore, quantity)

    game_state.ui.info_message(
        f"Successfully sold {quantity} {selected_cargo.ore.name} for {final_price} credits."
    )


# Register trading commands
register_command(
    ["buy", "b"],
    buy_command,
    [
        Argument("item_name", str, False),
        Argument("amount", str, False),
    ],
)

register_command(
    ["sell", "s"],
    sell_command,
    [],
)