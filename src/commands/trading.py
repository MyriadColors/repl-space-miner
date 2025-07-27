from src.classes.game import Game
from src.helpers import rnd_float, rnd_int, take_input
from src.events.skill_events import (
    process_skill_xp_from_activity,
    notify_skill_progress,
)
from .registry import Argument
from .base import register_command


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


def buy_command(game_state: Game, item_name: str, amount: str) -> None:
    """Handle buying items from a station by name or index."""
    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message("Must be docked to buy items.")
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("Not docked at any station.")
        return

    ore_cargo = None
    
    # Check if item_name is a number (index)
    if item_name.isdigit():
        index = int(item_name) - 1  # Convert to 0-based index
        available_cargo = [cargo for cargo in station.ore_cargo if cargo.quantity > 0]
        
        if 0 <= index < len(available_cargo):
            ore_cargo = available_cargo[index]
        else:
            game_state.ui.error_message(f"Invalid index. Available items: 1-{len(available_cargo)}")
            return
    else:
        # Original name-based lookup
        ore_cargo = next(
            (
                cargo
                for cargo in station.ore_cargo
                if cargo.ore.name.lower() == item_name.lower() and cargo.quantity > 0
            ),
            None,
        )

    if not ore_cargo:
        game_state.ui.error_message(f"Item {item_name} not found or not available.")
        return

    item = ore_cargo.ore

    # Handle "all" amount - buy maximum affordable quantity
    if amount.lower() == "all":
        player_character = game_state.get_player_character()
        if player_character is None:
            game_state.ui.error_message("Player character not found.")
            return

        # Calculate how many we can afford
        base_price_per_unit = ore_cargo.buy_price
        
        # Apply price modifiers to get actual price per unit
        price_modifier = 1.0
        if hasattr(player_character, "buy_price_mod"):
            price_modifier = player_character.buy_price_mod

        # Apply charisma bonus (0.5% discount per point above 5)
        if player_character.charisma > 5:
            charisma_bonus = 1 - ((player_character.charisma - 5) * 0.005)
            price_modifier *= charisma_bonus

        # Apply trader reputation bonus (0.25% per positive reputation point)
        if player_character.reputation_traders > 0:
            trader_bonus = 1 - (player_character.reputation_traders * 0.0025)
            price_modifier *= trader_bonus

        actual_price_per_unit = base_price_per_unit * price_modifier
        
        # Calculate maximum affordable quantity
        max_affordable = int(player_character.credits // actual_price_per_unit)
        
        # Also check cargo space constraints
        remaining_space = player_ship.get_remaining_cargo_space()
        max_by_space = int(remaining_space // item.volume)
        
        # Take the minimum of what we can afford, what's available, and what fits
        amount_int = min(max_affordable, ore_cargo.quantity, max_by_space)
        
        if amount_int <= 0:
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

    # Check if station has enough of the item
    if ore_cargo.quantity < amount_int:
        game_state.ui.error_message(
            f"Station only has {ore_cargo.quantity} {item.purity.name} {item.name} available."
        )
        return

    # Check cargo space
    required_space = item.volume * amount_int
    if player_ship.get_remaining_cargo_space() < required_space:
        game_state.ui.error_message(
            f"Not enough cargo space. Need {required_space:.2f} m³, but only {player_ship.get_remaining_cargo_space():.2f} m³ available."
        )
        return

    # Calculate base price
    base_price = ore_cargo.buy_price * amount_int

    # Apply character trait modifiers to price
    player_character = game_state.get_player_character()
    if player_character is None:
        game_state.ui.error_message("Player character not found.")
        return

    # Apply buy price modifier from traits
    price_modifier = 1.0
    if hasattr(player_character, "buy_price_mod"):
        price_modifier = player_character.buy_price_mod

    # Apply charisma bonus (0.5% discount per point above 5)
    if player_character.charisma > 5:
        charisma_bonus = 1 - ((player_character.charisma - 5) * 0.005)
        price_modifier *= charisma_bonus

    # Apply trader reputation bonus (0.25% per positive reputation point)
    if player_character.reputation_traders > 0:
        trader_bonus = 1 - (player_character.reputation_traders * 0.0025)
        price_modifier *= trader_bonus

    # Apply superstitious trait randomly
    import random

    if (
        hasattr(player_character, "negative_trait")
        and player_character.negative_trait == "Superstitious"
    ):
        if random.random() < 0.1:  # 10% chance to miss a deal
            game_state.ui.warn_message(
                "You notice the transaction number ends in 13. A bad omen! You negotiate nervously."
            )
            price_modifier *= 1.05  # 5% price increase

    # Apply modified price
    total_price = round(base_price * price_modifier, 2)

    # Show price adjustment notification if significant
    if price_modifier < 0.95:  # More than 5% discount
        game_state.ui.success_message(
            "Your negotiation skills helped secure a better price!"
        )
    elif price_modifier > 1.05:  # More than 5% increase
        game_state.ui.warn_message(
            "The merchant seems to be charging you a premium...")

    if player_character.credits < total_price:
        game_state.ui.error_message(
            "Not enough credits to make this purchase.")
        return

    # Try to barter
    final_price, bartered = barter(total_price)
    # Ensure the bartered price is also rounded
    final_price = round(final_price, 2)

    # Apply Charismatic trait message if applicable and wasn't already bartered down
    if (
        not bartered
        and hasattr(player_character, "positive_trait")
        and player_character.positive_trait == "Charismatic"
        and price_modifier < 1.0
    ):
        game_state.ui.success_message(
            "Your natural charisma helped secure a better deal."
        )  # Update game state using our credit management method
    player_character.remove_credits(final_price)

    # Process skill experience from trading
    skill_results = process_skill_xp_from_activity(
        game_state,
        "trading",
        difficulty=min(
            2.0, max(1.0, final_price / 1000)
        ),  # Higher price = more complex trade
    )
    notify_skill_progress(game_state, skill_results)

    # Update station inventory by reducing ore quantity
    if ore_cargo:
        ore_cargo.quantity -= amount_int

    # Add item to ship's cargo
    existing_cargo = next(
        (cargo for cargo in player_ship.cargohold if cargo.ore.id == item.id), None
    )
    if existing_cargo:
        existing_cargo.quantity += amount_int
    else:
        from src.data import OreCargo

        if ore_cargo:  # Ensure ore_cargo is not None before accessing its attributes
            player_ship.cargohold.append(
                OreCargo(item, amount_int, ore_cargo.buy_price,
                         ore_cargo.sell_price)
            )

    game_state.ui.info_message(
        f"Successfully purchased {amount_int} {item.purity.name} {item.name} for {final_price} credits."
    )


def sell_command(game_state: Game) -> None:
    """Handle selling items to a station."""
    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message("Must be docked to sell items.")
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("Not docked at any station.")
        return

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
        selection = int(take_input(
            "Select item number to sell (0 to cancel): "))
        if selection == 0:
            return
        if selection < 1 or selection > len(player_ship.cargohold):
            game_state.ui.error_message("Invalid selection.")
            return
    except ValueError:
        game_state.ui.error_message("Invalid input.")
        return

    # Get quantity to sell
    try:
        quantity = int(take_input("Enter quantity to sell: "))
        if quantity <= 0:
            game_state.ui.error_message("Quantity must be positive.")
            return
    except ValueError:
        game_state.ui.error_message("Invalid quantity.")
        return

    # Get selected item
    selected_cargo = player_ship.cargohold[selection - 1]
    if quantity > selected_cargo.quantity:
        game_state.ui.error_message("Not enough items in cargo.")
        return

    # Get the player character
    player_character = game_state.get_player_character()
    if player_character is None:
        game_state.ui.error_message("Player character not found.")
        return

    # Calculate base price using get_value() method instead of price attribute
    base_price = selected_cargo.ore.get_value() * quantity

    # Apply sell price modifier from traits
    price_modifier = 1.0
    if hasattr(player_character, "sell_price_mod"):
        price_modifier = player_character.sell_price_mod

    # Apply charisma bonus (0.5% bonus per point above 5)
    if player_character.charisma > 5:
        charisma_bonus = 1 + ((player_character.charisma - 5) * 0.005)
        price_modifier *= charisma_bonus

    # Apply trader reputation bonus (0.25% per positive reputation point)
    if player_character.reputation_traders > 0:
        trader_bonus = 1 + (player_character.reputation_traders * 0.0025)
        price_modifier *= trader_bonus

    # Apply superstitious trait randomly
    import random

    if (
        hasattr(player_character, "negative_trait")
        and player_character.negative_trait == "Superstitious"
    ):
        if random.random() < 0.1:  # 10% chance to miss a deal
            game_state.ui.warn_message(
                "You notice it's the 13th deal of the day. A bad omen! You negotiate nervously."
            )
            price_modifier *= 0.95  # 5% price decrease

    # Apply modified price
    total_price = round(base_price * price_modifier, 2)

    # Show price adjustment notification if significant
    if price_modifier > 1.05:  # More than 5% bonus
        game_state.ui.success_message(
            "Your negotiation skills helped secure a better price!"
        )
    elif price_modifier < 0.95:  # More than 5% decrease
        game_state.ui.warn_message(
            "The merchant seems to be lowballing your offer...")

    # Try to barter
    final_price, bartered = barter(total_price)
    # Ensure the bartered price is also rounded
    final_price = round(final_price, 2)

    # Apply Charismatic trait message if applicable and wasn't already bartered up
    if (
        not bartered
        and hasattr(player_character, "positive_trait")
        and player_character.positive_trait == "Charismatic"
        and price_modifier > 1.0
    ):
        game_state.ui.success_message(
            "Your natural charisma helped secure a better sale price."
        )

    # Check for Forgetful negative trait - 5% chance to forget some of your payment
    if (
        hasattr(player_character, "negative_trait")
        and player_character.negative_trait == "Forgetful"
    ):
        if random.random() < 0.05:  # 5% chance to lose some credits
            lost_amount = round(final_price * 0.05, 2)  # Lose 5% of the sale
            final_price -= lost_amount
            game_state.ui.warn_message(
                f"You misplaced {lost_amount} credits during the transaction. How forgetful!"
            )  # Update game state
    player_character.add_credits(final_price)

    # Process skill experience from selling
    skill_results = process_skill_xp_from_activity(
        game_state,
        "trading",
        difficulty=min(
            2.0, max(1.0, final_price / 1000)
        ),  # Higher price = more complex trade
    )
    notify_skill_progress(game_state, skill_results)

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