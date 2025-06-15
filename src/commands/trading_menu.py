"""
Enhanced trading menu system for the space station trading interface.
Provides a comprehensive, menu-driven CLI for all trading operations.
"""

from colorama import Fore, Style

from src.classes.game import Game
from src.classes.station import Station
from src.helpers import take_input
from .base import register_command
from .trading import buy_command, sell_command
from .cargo import cargo_command
from .market import market_command
from .price_compare import compare_prices_command, find_best_trade_routes


def trading_menu_command(game_state: Game) -> None:
    """
    Main trading menu interface providing access to all trading functions.

    This comprehensive menu allows users to:
    - View market prices and inventory
    - Buy and sell commodities with menu-driven interface
    - Compare prices across stations
    - Find profitable trade routes
    - Manage cargo and credits
    """
    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message(
            "You must be docked at a station to access trading services."
        )
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("Error: Cannot find the station you are docked at.")
        return

    player_character = game_state.get_player_character()
    if not player_character:
        game_state.ui.error_message("Error: Player character not found.")
        return

    while True:
        # Clear screen and show header
        game_state.ui.clear_screen()
        _display_trading_header(game_state, station, player_character)

        # Show main menu options
        game_state.ui.info_message(
            f"\n{Fore.CYAN}=== TRADING OPERATIONS ==={Style.RESET_ALL}"
        )
        game_state.ui.info_message("1. View Market Prices & Available Goods")
        game_state.ui.info_message("2. Buy Commodities (Menu Interface)")
        game_state.ui.info_message("3. Sell Commodities (Menu Interface)")
        game_state.ui.info_message("4. View Your Cargo & Inventory")
        game_state.ui.info_message("5. Compare Prices Across System")
        game_state.ui.info_message("6. Find Best Trade Routes")
        game_state.ui.info_message("7. Quick Trade Options")
        game_state.ui.info_message("8. Trading Statistics")
        game_state.ui.info_message("9. Batch Trading Operations")
        game_state.ui.info_message("10. Return to Station")

        choice = take_input(
            f"\n{Fore.YELLOW}Select an option (1-10): {Style.RESET_ALL}"
        )

        if choice == "1":
            _view_market_interface(game_state)
        elif choice == "2":
            _enhanced_buy_interface(game_state)
        elif choice == "3":
            _enhanced_sell_interface(game_state)
        elif choice == "4":
            _view_cargo_interface(game_state)
        elif choice == "5":
            _price_comparison_interface(game_state)
        elif choice == "6":
            _trade_routes_interface(game_state)
        elif choice == "7":
            _quick_trade_interface(game_state)
        elif choice == "8":
            _trading_statistics_interface(game_state)
        elif choice == "9":
            _batch_operations_interface(game_state)
        elif choice == "10":
            game_state.ui.info_message("Returning to station. Safe travels!")
            break
        else:
            game_state.ui.error_message("Invalid option. Please try again.")
            take_input("Press Enter to continue...")


def _display_trading_header(
    game_state: Game, station: Station, player_character
) -> None:
    """Display the trading menu header with current status."""
    game_state.ui.info_message(f"\n{'=' * 60}")
    game_state.ui.info_message(
        f"{Fore.GREEN}GALACTIC TRADING NETWORK - {station.name}{Style.RESET_ALL}"
    )
    game_state.ui.info_message(f"{'=' * 60}")

    # Show current financial status
    game_state.ui.info_message(
        f"Credits Available: {Fore.GREEN}{player_character.credits:.2f}{Style.RESET_ALL}"
    )

    # Show cargo space status
    player_ship = game_state.get_player_ship()
    cargo_used = player_ship.cargohold_occupied
    cargo_capacity = player_ship.cargohold_capacity
    cargo_percentage = (cargo_used / cargo_capacity * 100) if cargo_capacity > 0 else 0

    cargo_color = (
        Fore.GREEN
        if cargo_percentage < 80
        else Fore.YELLOW
        if cargo_percentage < 95
        else Fore.RED
    )
    game_state.ui.info_message(
        f"Cargo Space: {cargo_color}{cargo_used:.2f}/{cargo_capacity:.2f} m³ ({cargo_percentage:.1f}% full){Style.RESET_ALL}"
    )


def _view_market_interface(game_state: Game) -> None:
    """Enhanced market viewing interface."""
    game_state.ui.clear_screen()
    market_command(game_state)
    take_input(
        f"\n{Fore.YELLOW}Press Enter to return to trading menu...{Style.RESET_ALL}"
    )


def _enhanced_buy_interface(game_state: Game) -> None:
    """Enhanced menu-driven interface for buying commodities."""
    station = game_state.get_player_ship().get_station_docked_at()
    player_character = game_state.get_player_character()

    if not station:
        game_state.ui.error_message("Error: Not docked at a station.")
        take_input("Press Enter to continue...")
        return

    while True:
        game_state.ui.clear_screen()
        game_state.ui.info_message(
            f"\n{Fore.GREEN}=== BUY COMMODITIES ==={Style.RESET_ALL}"
        )
        game_state.ui.info_message(f"Station: {station.name}")
        game_state.ui.info_message(
            f"Available Credits: {Fore.GREEN}{player_character.credits:.2f}{Style.RESET_ALL}\n"
        )

        # Display available items with indices
        if not station.ore_cargo or all(
            cargo.quantity <= 0 for cargo in station.ore_cargo
        ):
            game_state.ui.error_message(
                "No commodities available for purchase at this station."
            )
            take_input("Press Enter to return...")
            return

        available_items = [cargo for cargo in station.ore_cargo if cargo.quantity > 0]

        game_state.ui.info_message("Available Commodities:")
        game_state.ui.info_message(
            f"{'#':<3} {'Commodity':<20} {'Quantity':<10} {'Price/Unit':<12} {'Total Value':<12}"
        )
        game_state.ui.info_message("-" * 65)

        for i, ore_cargo in enumerate(available_items, 1):
            ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"
            total_value = ore_cargo.buy_price * ore_cargo.quantity

            # Apply character modifiers for display
            display_price = _calculate_modified_buy_price(
                game_state, ore_cargo.buy_price
            )

            game_state.ui.info_message(
                f"{i:<3} {ore_name:<20} {ore_cargo.quantity:<10} {display_price:<12.2f} {total_value:<12.2f}"
            )

        game_state.ui.info_message(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
        game_state.ui.info_message("• Enter item number to buy")
        game_state.ui.info_message("• Type 'all' to buy maximum affordable quantity")
        game_state.ui.info_message("• Type '0' to return to trading menu")

        choice = take_input(f"\n{Fore.YELLOW}Select item to buy: {Style.RESET_ALL}")

        if choice == "0":
            break
        elif choice.lower() == "all":
            _buy_all_affordable(game_state, available_items)
        elif choice.isdigit():
            item_index = int(choice) - 1
            if 0 <= item_index < len(available_items):
                _process_item_purchase(game_state, available_items[item_index])
            else:
                game_state.ui.error_message("Invalid item number.")
                take_input("Press Enter to continue...")
        else:
            game_state.ui.error_message(
                "Invalid input. Please enter a number or 'all'."
            )
            take_input("Press Enter to continue...")


def _enhanced_sell_interface(game_state: Game) -> None:
    """Enhanced menu-driven interface for selling commodities."""
    player_ship = game_state.get_player_ship()

    while True:
        game_state.ui.clear_screen()
        game_state.ui.info_message(
            f"\n{Fore.GREEN}=== SELL COMMODITIES ==={Style.RESET_ALL}"
        )

        if not player_ship.cargohold:
            game_state.ui.error_message("No commodities to sell in your cargo hold.")
            take_input("Press Enter to return...")
            return

        # Display cargo with enhanced information
        game_state.ui.info_message("Your Cargo:")
        game_state.ui.info_message(
            f"{'#':<3} {'Commodity':<20} {'Quantity':<10} {'Est. Price/Unit':<15} {'Est. Total':<12}"
        )
        game_state.ui.info_message("-" * 70)

        for i, cargo in enumerate(player_ship.cargohold, 1):
            ore_name = f"{cargo.ore.purity.name} {cargo.ore.name}"

            # Calculate estimated sell price with modifiers
            estimated_price = _calculate_modified_sell_price(
                game_state, cargo.ore.price
            )
            estimated_total = estimated_price * cargo.quantity

            game_state.ui.info_message(
                f"{i:<3} {ore_name:<20} {cargo.quantity:<10} {estimated_price:<15.2f} {estimated_total:<12.2f}"
            )

        game_state.ui.info_message(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
        game_state.ui.info_message("• Enter item number to sell")
        game_state.ui.info_message("• Type 'all' to sell entire cargo hold")
        game_state.ui.info_message("• Type '0' to return to trading menu")

        choice = take_input(f"\n{Fore.YELLOW}Select item to sell: {Style.RESET_ALL}")

        if choice == "0":
            break
        elif choice.lower() == "all":
            _sell_all_cargo(game_state)
        elif choice.isdigit():
            item_index = int(choice) - 1
            if 0 <= item_index < len(player_ship.cargohold):
                _process_item_sale(game_state, player_ship.cargohold[item_index])
            else:
                game_state.ui.error_message("Invalid item number.")
                take_input("Press Enter to continue...")
        else:
            game_state.ui.error_message(
                "Invalid input. Please enter a number or 'all'."
            )
            take_input("Press Enter to continue...")


def _view_cargo_interface(game_state: Game) -> None:
    """Enhanced cargo viewing interface."""
    game_state.ui.clear_screen()
    cargo_command(game_state)
    take_input(
        f"\n{Fore.YELLOW}Press Enter to return to trading menu...{Style.RESET_ALL}"
    )


def _price_comparison_interface(game_state: Game) -> None:
    """Interface for price comparison across stations."""
    game_state.ui.clear_screen()
    game_state.ui.info_message(
        f"\n{Fore.GREEN}=== PRICE COMPARISON ==={Style.RESET_ALL}"
    )

    game_state.ui.info_message("Select comparison type:")
    game_state.ui.info_message("1. Best buying prices")
    game_state.ui.info_message("2. Best selling prices")
    game_state.ui.info_message("3. Trade opportunities")
    game_state.ui.info_message("4. All (comprehensive)")

    choice = take_input(f"\n{Fore.YELLOW}Select option (1-4): {Style.RESET_ALL}")

    option_map = {"1": "buy", "2": "sell", "3": "trade", "4": "all"}
    if choice in option_map:
        compare_prices_command(game_state, option_map[choice], "no")
    else:
        game_state.ui.error_message("Invalid option.")

    take_input(
        f"\n{Fore.YELLOW}Press Enter to return to trading menu...{Style.RESET_ALL}"
    )


def _trade_routes_interface(game_state: Game) -> None:
    """Interface for finding best trade routes."""
    game_state.ui.clear_screen()
    game_state.ui.info_message(
        f"\n{Fore.GREEN}=== TRADE ROUTE FINDER ==={Style.RESET_ALL}"
    )

    max_routes = take_input("Maximum routes to display (default 5): ") or "5"
    include_unreachable = (
        take_input("Include unreachable stations? (y/n, default n): ").lower() == "y"
    )

    find_best_trade_routes(game_state, max_routes, include_unreachable)
    take_input(
        f"\n{Fore.YELLOW}Press Enter to return to trading menu...{Style.RESET_ALL}"
    )


def _quick_trade_interface(game_state: Game) -> None:
    """Interface for quick trading operations."""
    game_state.ui.clear_screen()
    game_state.ui.info_message(
        f"\n{Fore.GREEN}=== QUICK TRADE OPTIONS ==={Style.RESET_ALL}"
    )

    game_state.ui.info_message("1. Sell all cargo")
    game_state.ui.info_message("2. Buy maximum affordable of most profitable item")
    game_state.ui.info_message("3. Fill cargo with cheapest available items")
    game_state.ui.info_message("4. Return to trading menu")

    choice = take_input(f"\n{Fore.YELLOW}Select option (1-4): {Style.RESET_ALL}")

    if choice == "1":
        _sell_all_cargo(game_state)
    elif choice == "2":
        _buy_most_profitable(game_state)
    elif choice == "3":
        _fill_cargo_cheap(game_state)
    elif choice == "4":
        return
    else:
        game_state.ui.error_message("Invalid option.")
        take_input("Press Enter to continue...")


def _trading_statistics_interface(game_state: Game) -> None:
    """Display comprehensive trading statistics and analytics."""
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()
    station = player_ship.get_station_docked_at()

    if not station:
        game_state.ui.error_message("Error: Not docked at a station.")
        take_input("Press Enter to continue...")
        return

    game_state.ui.clear_screen()
    game_state.ui.info_message(
        f"\n{Fore.GREEN}=== TRADING ANALYTICS ==={Style.RESET_ALL}"
    )

    # Calculate current portfolio value
    portfolio_value = 0.0
    cargo_items = len(player_ship.cargohold)
    total_cargo_volume = sum(
        cargo.ore.volume * cargo.quantity for cargo in player_ship.cargohold
    )

    for cargo in player_ship.cargohold:
        # Use station's sell price as estimated value
        station_ore = station.get_ore_by_name(cargo.ore.name)
        if station_ore:
            estimated_value = (
                _calculate_modified_sell_price(game_state, station_ore.sell_price)
                * cargo.quantity
            )
        else:
            estimated_value = cargo.ore.price * cargo.quantity
        portfolio_value += estimated_value

    # Display financial overview
    game_state.ui.info_message(
        f"{Fore.CYAN}=== FINANCIAL OVERVIEW ==={Style.RESET_ALL}"
    )
    game_state.ui.info_message(
        f"Available Credits: {Fore.GREEN}{player_character.credits:.2f}{Style.RESET_ALL}"
    )
    game_state.ui.info_message(
        f"Cargo Portfolio Value: {Fore.YELLOW}{portfolio_value:.2f}{Style.RESET_ALL}"
    )
    total_net_worth: float = player_character.credits + portfolio_value
    game_state.ui.info_message(
        f"Total Net Worth: {Fore.GREEN}{total_net_worth:.2f}{Style.RESET_ALL}"
    )

    # Display cargo statistics
    game_state.ui.info_message(
        f"\n{Fore.CYAN}=== CARGO STATISTICS ==={Style.RESET_ALL}"
    )
    game_state.ui.info_message(f"Cargo Items: {cargo_items}")
    game_state.ui.info_message(
        f"Cargo Volume Used: {total_cargo_volume:.2f}/{player_ship.cargohold_capacity:.2f} m³"
    )
    cargo_efficiency = (
        (total_cargo_volume / player_ship.cargohold_capacity * 100)
        if player_ship.cargohold_capacity > 0
        else 0
    )
    game_state.ui.info_message(f"Cargo Efficiency: {cargo_efficiency:.1f}%")

    # Display most valuable items in cargo
    if player_ship.cargohold:
        game_state.ui.info_message(
            f"\n{Fore.CYAN}=== TOP CARGO VALUES ==={Style.RESET_ALL}"
        )
        cargo_values = []
        for cargo in player_ship.cargohold:
            station_ore = station.get_ore_by_name(cargo.ore.name)
            if station_ore:
                unit_value = _calculate_modified_sell_price(
                    game_state, station_ore.sell_price
                )
            else:
                unit_value = cargo.ore.price
            total_value = unit_value * cargo.quantity
            ore_name = f"{cargo.ore.purity.name} {cargo.ore.name}"
            cargo_values.append((ore_name, cargo.quantity, unit_value, total_value))

        # Sort by total value (descending)
        cargo_values.sort(key=lambda x: x[3], reverse=True)

        game_state.ui.info_message(
            f"{'Commodity':<20} {'Qty':<8} {'Unit Value':<12} {'Total Value':<12}"
        )
        game_state.ui.info_message("-" * 60)

        # Top 5
        for ore_name, quantity, unit_value, total_value in cargo_values[:5]:
            game_state.ui.info_message(
                f"{ore_name:<20} {quantity:<8} {unit_value:<12.2f} {total_value:<12.2f}"
            )

    # Display trading efficiency metrics
    game_state.ui.info_message(
        f"\n{Fore.CYAN}=== TRADING EFFICIENCY ==={Style.RESET_ALL}"
    )

    # Calculate character bonuses
    charisma_bonus: float = 0.0
    if player_character.charisma > 5:
        charisma_bonus = (player_character.charisma - 5) * 0.5

    trader_rep_bonus = (
        player_character.reputation_traders * 0.25
        if hasattr(player_character, "reputation_traders")
        else 0
    )

    game_state.ui.info_message(f"Charisma Bonus: {charisma_bonus:.1f}% better prices")
    game_state.ui.info_message(
        f"Trader Reputation Bonus: {trader_rep_bonus:.1f}% better prices"
    )

    # Calculate best opportunities at this station
    game_state.ui.info_message(
        f"\n{Fore.CYAN}=== CURRENT STATION OPPORTUNITIES ==={Style.RESET_ALL}"
    )
    best_buys = []
    best_sells = []

    for ore_cargo in station.ore_cargo:
        if ore_cargo.quantity > 0:
            buy_price = _calculate_modified_buy_price(game_state, ore_cargo.buy_price)
            value_ratio = ore_cargo.ore.base_value / buy_price if buy_price > 0 else 0
            ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"
            best_buys.append((ore_name, buy_price, value_ratio))

    for cargo in player_ship.cargohold:
        station_ore = station.get_ore_by_name(cargo.ore.name)
        if station_ore:
            sell_price = _calculate_modified_sell_price(
                game_state, station_ore.sell_price
            )
            # Compare to what we might have paid (use ore base value as proxy)
            profit_margin = (
                (sell_price - cargo.ore.base_value) / cargo.ore.base_value
                if cargo.ore.base_value > 0
                else 0
            )
            ore_name = f"{cargo.ore.purity.name} {cargo.ore.name}"
            best_sells.append((ore_name, cargo.quantity, sell_price, profit_margin))

    if best_buys:
        best_buys.sort(key=lambda x: x[2], reverse=True)  # Sort by value ratio
        game_state.ui.info_message("Best Buy Opportunities (by value ratio):")
        for ore_name, price, ratio in best_buys[:3]:
            game_state.ui.info_message(
                f"  {ore_name}: {price:.2f} credits (value ratio: {ratio:.2f})"
            )

    if best_sells:
        # Sort by profit margin
        best_sells.sort(key=lambda x: x[3], reverse=True)
        game_state.ui.info_message("Best Sell Opportunities (by profit margin):")
        for ore_name, quantity, price, margin in best_sells[:3]:
            game_state.ui.info_message(
                f"  {ore_name}: {price:.2f} credits ({margin:.1%} margin)"
            )

    take_input(
        f"\n{Fore.YELLOW}Press Enter to return to trading menu...{Style.RESET_ALL}"
    )


def _batch_operations_interface(game_state: Game) -> None:
    """Interface for batch trading operations."""
    game_state.ui.clear_screen()
    game_state.ui.info_message(
        f"\n{Fore.GREEN}=== BATCH TRADING OPERATIONS ==={Style.RESET_ALL}"
    )

    game_state.ui.info_message("1. Buy most profitable item (max affordable)")
    game_state.ui.info_message("2. Fill cargo with cheapest items")
    game_state.ui.info_message("3. Sell all cargo at once")
    game_state.ui.info_message(
        "4. Smart cargo management (sell low-value, buy high-value)"
    )
    game_state.ui.info_message("5. Return to trading menu")

    choice = take_input(
        f"\n{Fore.YELLOW}Select batch operation (1-5): {Style.RESET_ALL}"
    )

    if choice == "1":
        _buy_most_profitable(game_state)
    elif choice == "2":
        _fill_cargo_cheap(game_state)
    elif choice == "3":
        _sell_all_cargo(game_state)
    elif choice == "4":
        _smart_cargo_management(game_state)
    elif choice == "5":
        return
    else:
        game_state.ui.error_message("Invalid option.")
        take_input("Press Enter to continue...")


def _smart_cargo_management(game_state: Game) -> None:
    """Intelligently manage cargo by selling low-value items and buying high-value ones."""
    player_ship = game_state.get_player_ship()
    station = player_ship.get_station_docked_at()

    if not station:
        game_state.ui.error_message("Error: Not docked at a station.")
        take_input("Press Enter to continue...")
        return

    game_state.ui.info_message("Analyzing cargo for smart management...")

    # Calculate value per volume for all cargo items
    cargo_efficiency = []
    for cargo in player_ship.cargohold:
        station_ore = station.get_ore_by_name(cargo.ore.name)
        if station_ore:
            sell_price = _calculate_modified_sell_price(
                game_state, station_ore.sell_price
            )
            value_per_volume = (
                sell_price / cargo.ore.volume if cargo.ore.volume > 0 else 0
            )
            ore_name = f"{cargo.ore.purity.name} {cargo.ore.name}"
            cargo_efficiency.append((cargo, ore_name, sell_price, value_per_volume))

    if not cargo_efficiency:
        game_state.ui.warn_message("No cargo to manage.")
        take_input("Press Enter to continue...")
        return

    # Sort by value per volume (ascending = least efficient first)
    cargo_efficiency.sort(key=lambda x: x[3])

    # Calculate value per volume for station items
    station_efficiency = []
    for ore_cargo in station.ore_cargo:
        if ore_cargo.quantity > 0:
            buy_price = _calculate_modified_buy_price(game_state, ore_cargo.buy_price)
            value_per_volume = (
                ore_cargo.ore.base_value / ore_cargo.ore.volume
                if ore_cargo.ore.volume > 0
                else 0
            )
            ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"
            station_efficiency.append(
                (ore_cargo, ore_name, buy_price, value_per_volume)
            )

    # Sort by value per volume (descending = most efficient first)
    station_efficiency.sort(key=lambda x: x[3], reverse=True)

    game_state.ui.info_message(
        f"\n{Fore.GREEN}=== SMART CARGO MANAGEMENT ==={Style.RESET_ALL}"
    )
    game_state.ui.info_message("Least efficient cargo items (candidates for selling):")

    for i, (cargo, ore_name, sell_price, efficiency) in enumerate(cargo_efficiency[:3]):
        game_state.ui.info_message(
            f"  {i + 1}. {ore_name}: {efficiency:.2f} value/m³ (sell for {sell_price:.2f})"
        )

    game_state.ui.info_message(
        "\nMost efficient station items (candidates for buying):"
    )

    for i, (ore_cargo, ore_name, buy_price, efficiency) in enumerate(
        station_efficiency[:3]
    ):
        game_state.ui.info_message(
            f"  {i + 1}. {ore_name}: {efficiency:.2f} value/m³ (buy for {buy_price:.2f})"
        )

    # Suggest optimization
    if cargo_efficiency and station_efficiency:
        worst_cargo = cargo_efficiency[0]
        best_station = station_efficiency[0]

        if best_station[3] > worst_cargo[3] * 1.2:  # 20% better efficiency
            game_state.ui.info_message(
                f"\n{Fore.YELLOW}RECOMMENDATION:{Style.RESET_ALL}"
            )
            game_state.ui.info_message(
                f"Sell {worst_cargo[1]} and buy {best_station[1]} for better cargo efficiency!"
            )

            confirm = take_input(
                f"\n{Fore.YELLOW}Execute this recommendation? (y/n): {Style.RESET_ALL}"
            )
            if confirm.lower() == "y":
                # Sell the inefficient item
                game_state.ui.info_message(f"Selling {worst_cargo[1]}...")
                # Note: This would need to integrate with the existing sell system
                game_state.ui.info_message(
                    "Manual selling recommended - use the sell interface."
                )
        else:
            game_state.ui.info_message(
                f"\n{Fore.GREEN}Your cargo is already well-optimized!{Style.RESET_ALL}"
            )

    take_input("Press Enter to continue...")


def _process_item_purchase(game_state: Game, ore_cargo) -> None:
    """Process the purchase of a specific item."""
    player_character = game_state.get_player_character()
    ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"

    # Calculate modified price
    unit_price = _calculate_modified_buy_price(game_state, ore_cargo.buy_price)

    game_state.ui.info_message(f"\n{Fore.GREEN}Purchasing: {ore_name}{Style.RESET_ALL}")
    game_state.ui.info_message(f"Available Quantity: {ore_cargo.quantity}")
    game_state.ui.info_message(f"Price per Unit: {unit_price:.2f} credits")
    game_state.ui.info_message(f"Your Credits: {player_character.credits:.2f}")

    # Calculate maximum affordable
    max_affordable = int(player_character.credits // unit_price)
    max_available = min(max_affordable, ore_cargo.quantity)

    if max_available <= 0:
        game_state.ui.error_message("You cannot afford any of this item.")
        take_input("Press Enter to continue...")
        return

    game_state.ui.info_message(f"Maximum you can afford: {max_available}")

    # Get quantity
    while True:
        quantity_input = take_input(
            f"\n{Fore.YELLOW}Enter quantity to buy (max {max_available}): {Style.RESET_ALL}"
        )

        if quantity_input.lower() == "max":
            quantity = max_available
            break
        elif quantity_input.isdigit():
            quantity = int(quantity_input)
            if 1 <= quantity <= max_available:
                break
            else:
                game_state.ui.error_message(
                    f"Please enter a quantity between 1 and {max_available}."
                )
        else:
            game_state.ui.error_message("Please enter a valid number or 'max'.")

    # Calculate total cost
    total_cost = unit_price * quantity

    # Confirm purchase
    game_state.ui.info_message("\nPurchase Summary:")
    game_state.ui.info_message(f"Item: {ore_name}")
    game_state.ui.info_message(f"Quantity: {quantity}")
    game_state.ui.info_message(f"Unit Price: {unit_price:.2f} credits")
    game_state.ui.info_message(f"Total Cost: {total_cost:.2f} credits")
    game_state.ui.info_message(
        f"Credits After Purchase: {player_character.credits - total_cost:.2f}"
    )

    confirm = take_input(f"\n{Fore.YELLOW}Confirm purchase? (y/n): {Style.RESET_ALL}")

    if confirm.lower() == "y":
        # Use existing buy command
        buy_command(game_state, ore_cargo.ore.name, str(quantity))
        take_input("Press Enter to continue...")
    else:
        game_state.ui.info_message("Purchase cancelled.")
        take_input("Press Enter to continue...")


def _process_item_sale(game_state: Game, ore_cargo) -> None:
    """Process the sale of a specific item."""
    ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"

    # Calculate estimated sell price
    estimated_price = _calculate_modified_sell_price(game_state, ore_cargo.ore.price)

    game_state.ui.info_message(f"\n{Fore.GREEN}Selling: {ore_name}{Style.RESET_ALL}")
    game_state.ui.info_message(f"Available Quantity: {ore_cargo.quantity}")
    game_state.ui.info_message(
        f"Estimated Price per Unit: {estimated_price:.2f} credits"
    )

    # Get quantity to sell
    while True:
        quantity_input = take_input(
            f"\n{Fore.YELLOW}Enter quantity to sell (max {ore_cargo.quantity}, 'all' for all): {Style.RESET_ALL}"
        )

        if quantity_input.lower() == "all":
            quantity = ore_cargo.quantity
            break
        elif quantity_input.isdigit():
            quantity = int(quantity_input)
            if 1 <= quantity <= ore_cargo.quantity:
                break
            else:
                game_state.ui.error_message(
                    f"Please enter a quantity between 1 and {ore_cargo.quantity}."
                )
        else:
            game_state.ui.error_message("Please enter a valid number or 'all'.")

    # Calculate estimated total
    estimated_total = estimated_price * quantity

    # Confirm sale
    game_state.ui.info_message("\nSale Summary:")
    game_state.ui.info_message(f"Item: {ore_name}")
    game_state.ui.info_message(f"Quantity: {quantity}")
    game_state.ui.info_message(f"Estimated Unit Price: {estimated_price:.2f} credits")
    game_state.ui.info_message(f"Estimated Total: {estimated_total:.2f} credits")

    confirm = take_input(f"\n{Fore.YELLOW}Confirm sale? (y/n): {Style.RESET_ALL}")

    if confirm.lower() == "y":
        # Simulate item selection for sell command
        player_ship = game_state.get_player_ship()
        item_index = player_ship.cargohold.index(ore_cargo) + 1

        # Mock user input for the sell command
        original_take_input = take_input
        responses = [str(item_index), str(quantity)]
        response_iter = iter(responses)

        def mock_input(prompt):
            try:
                return next(response_iter)
            except StopIteration:
                return original_take_input(prompt)

        # Temporarily replace take_input
        import src.helpers

        src.helpers.take_input = mock_input

        try:
            sell_command(game_state)
        finally:
            # Restore original take_input
            src.helpers.take_input = original_take_input

        take_input("Press Enter to continue...")
    else:
        game_state.ui.info_message("Sale cancelled.")
        take_input("Press Enter to continue...")


def _sell_all_cargo(game_state: Game) -> None:
    """Sell all items in cargo hold."""
    player_ship = game_state.get_player_ship()

    if not player_ship.cargohold:
        game_state.ui.error_message("No cargo to sell.")
        return

    total_estimated_value = 0
    for cargo in player_ship.cargohold:
        estimated_price = _calculate_modified_sell_price(game_state, cargo.ore.price)
        total_estimated_value += estimated_price * cargo.quantity

    game_state.ui.info_message(
        f"\nEstimated total value of all cargo: {total_estimated_value:.2f} credits"
    )
    confirm = take_input(f"{Fore.YELLOW}Sell all cargo? (y/n): {Style.RESET_ALL}")

    if confirm.lower() == "y":
        # Sell each item
        items_sold = 0
        while player_ship.cargohold and items_sold < 50:  # Safety limit
            # Mock inputs for sell command
            original_take_input = take_input
            # Always select first item, sell all quantity
            responses = ["1", "all"]
            response_iter = iter(responses)

            def mock_input(prompt):
                try:
                    return next(response_iter)
                except StopIteration:
                    return original_take_input(prompt)

            import src.helpers

            src.helpers.take_input = mock_input

            try:
                sell_command(game_state)
                items_sold += 1
            finally:
                src.helpers.take_input = original_take_input

        game_state.ui.success_message("All cargo sold successfully!")
    else:
        game_state.ui.info_message("Sale cancelled.")


def _buy_all_affordable(game_state: Game, available_items) -> None:
    """Buy maximum affordable quantity of selected items."""
    game_state.ui.info_message("\nSelect items to buy maximum affordable quantity:")

    for i, ore_cargo in enumerate(available_items, 1):
        ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"
        unit_price = _calculate_modified_buy_price(game_state, ore_cargo.buy_price)
        player_character = game_state.get_player_character()
        max_affordable = int(player_character.credits // unit_price)
        max_available = min(max_affordable, ore_cargo.quantity)

        game_state.ui.info_message(f"{i}. {ore_name} - Max affordable: {max_available}")

    selection = take_input(f"\n{Fore.YELLOW}Enter item number: {Style.RESET_ALL}")

    if selection.isdigit():
        item_index = int(selection) - 1
        if 0 <= item_index < len(available_items):
            ore_cargo = available_items[item_index]
            unit_price = _calculate_modified_buy_price(game_state, ore_cargo.buy_price)
            player_character = game_state.get_player_character()
            max_affordable = int(player_character.credits // unit_price)
            quantity = min(max_affordable, ore_cargo.quantity)

            if quantity > 0:
                buy_command(game_state, ore_cargo.ore.name, str(quantity))
            else:
                game_state.ui.error_message("Cannot afford any of this item.")
        else:
            game_state.ui.error_message("Invalid item number.")
    else:
        game_state.ui.error_message("Invalid input.")

    take_input("Press Enter to continue...")


def _buy_most_profitable(game_state: Game) -> None:
    """Buy maximum affordable quantity of the most profitable item."""
    from .price_compare import get_trade_opportunities

    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()
    station = player_ship.get_station_docked_at()

    if not station:
        game_state.ui.error_message("Error: Not docked at a station.")
        take_input("Press Enter to continue...")
        return

    game_state.ui.info_message("Analyzing profitable trade opportunities...")

    # Get trade opportunities
    opportunities = get_trade_opportunities(game_state, include_unreachable=False)

    if not opportunities:
        game_state.ui.warn_message("No profitable trade opportunities found.")
        take_input("Press Enter to continue...")
        return

    # Filter opportunities for items available at this station
    available_opportunities = []
    for (
        ore_name,
        buy_station,
        sell_station,
        buy_price,
        sell_price,
        profit_per_unit,
        is_viable,
    ) in opportunities:
        if buy_station == station and is_viable and profit_per_unit > 0:
            # Check if item is actually available
            ore_cargo = station.get_ore_by_name(ore_name.split()[-1])
            if ore_cargo and ore_cargo.quantity > 0:
                available_opportunities.append(
                    (ore_name, ore_cargo, sell_station, profit_per_unit)
                )

    if not available_opportunities:
        game_state.ui.warn_message("No profitable items available at this station.")
        take_input("Press Enter to continue...")
        return

    # Sort by profit per unit (descending)
    available_opportunities.sort(key=lambda x: x[3], reverse=True)

    best_opportunity = available_opportunities[0]
    ore_name, ore_cargo, sell_station, profit_per_unit = best_opportunity

    # Calculate how much we can afford
    modified_price = _calculate_modified_buy_price(game_state, ore_cargo.buy_price)
    max_affordable = int(player_character.credits // modified_price)
    max_available = ore_cargo.quantity

    # Calculate cargo space limit
    cargo_space_used = sum(
        cargo.ore.volume * cargo.quantity for cargo in player_ship.cargohold
    )
    cargo_space_available = player_ship.cargohold_capacity - cargo_space_used
    max_by_space = int(cargo_space_available // ore_cargo.ore.volume)

    max_quantity = min(max_affordable, max_available, max_by_space)

    if max_quantity <= 0:
        game_state.ui.warn_message(
            "Cannot afford any units or no cargo space available."
        )
        take_input("Press Enter to continue...")
        return

    total_cost = modified_price * max_quantity
    potential_profit = profit_per_unit * max_quantity

    game_state.ui.info_message(
        f"\n{Fore.GREEN}=== MOST PROFITABLE OPPORTUNITY ==={Style.RESET_ALL}"
    )
    game_state.ui.info_message(f"Item: {ore_name}")
    game_state.ui.info_message(f"Quantity Available: {max_quantity}")
    game_state.ui.info_message(f"Price per Unit: {modified_price:.2f} credits")
    game_state.ui.info_message(f"Total Cost: {total_cost:.2f} credits")
    game_state.ui.info_message(f"Sell Location: {sell_station.name}")
    game_state.ui.info_message(
        f"Potential Profit: {Fore.GREEN}{potential_profit:.2f} credits{Style.RESET_ALL}"
    )

    confirm = take_input(
        f"\n{Fore.YELLOW}Buy {max_quantity} units? (y/n): {Style.RESET_ALL}"
    )
    if confirm.lower() == "y":
        # Use existing buy command
        from .trading import buy_command

        buy_command(game_state, ore_name.split()[-1], str(max_quantity))
    else:
        game_state.ui.info_message("Purchase cancelled.")

    take_input("Press Enter to continue...")


def _fill_cargo_cheap(game_state: Game) -> None:
    """Fill cargo hold with cheapest available items."""
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()
    station = player_ship.get_station_docked_at()

    if not station:
        game_state.ui.error_message("Error: Not docked at a station.")
        take_input("Press Enter to continue...")
        return

    game_state.ui.info_message("Finding cheapest items to fill cargo hold...")

    # Calculate available cargo space
    cargo_space_used = sum(
        cargo.ore.volume * cargo.quantity for cargo in player_ship.cargohold
    )
    cargo_space_available = player_ship.cargohold_capacity - cargo_space_used

    if cargo_space_available <= 0:
        game_state.ui.warn_message("No cargo space available.")
        take_input("Press Enter to continue...")
        return

    # Get available items and sort by price per unit (cheapest first)
    available_items = [
        (ore_cargo, _calculate_modified_buy_price(game_state, ore_cargo.buy_price))
        for ore_cargo in station.ore_cargo
        if ore_cargo.quantity > 0
    ]

    if not available_items:
        game_state.ui.warn_message("No items available for purchase.")
        take_input("Press Enter to continue...")
        return

    # Sort by price per unit (ascending)
    available_items.sort(key=lambda x: x[1])

    total_cost = 0.0
    purchases = []
    remaining_space = cargo_space_available
    remaining_credits = player_character.credits

    game_state.ui.info_message(
        f"\n{Fore.GREEN}=== FILLING CARGO WITH CHEAPEST ITEMS ==={Style.RESET_ALL}"
    )
    game_state.ui.info_message(f"Available cargo space: {cargo_space_available:.2f} m³")
    game_state.ui.info_message(f"Available credits: {remaining_credits:.2f}")

    # Fill cargo with cheapest items
    for ore_cargo, unit_price in available_items:
        if remaining_space <= 0 or remaining_credits <= 0:
            break

        # Calculate how many we can fit by space
        max_by_space = int(remaining_space // ore_cargo.ore.volume)
        # Calculate how many we can afford
        max_affordable = int(remaining_credits // unit_price)
        # Calculate how many are available
        max_available = ore_cargo.quantity

        quantity = min(max_by_space, max_affordable, max_available)

        if quantity > 0:
            cost = quantity * unit_price
            volume = quantity * ore_cargo.ore.volume

            purchases.append((ore_cargo, quantity, cost))
            total_cost += cost
            remaining_space -= volume
            remaining_credits -= cost

            ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"
            game_state.ui.info_message(
                f"+ {quantity} {ore_name} @ {unit_price:.2f} = {cost:.2f} credits"
            )

    if not purchases:
        game_state.ui.warn_message(
            "Cannot afford any items or insufficient cargo space."
        )
        take_input("Press Enter to continue...")
        return

    game_state.ui.info_message(
        f"\n{Fore.YELLOW}Total Cost: {total_cost:.2f} credits{Style.RESET_ALL}"
    )
    game_state.ui.info_message(f"Remaining Credits: {remaining_credits:.2f}")
    game_state.ui.info_message(f"Remaining Cargo Space: {remaining_space:.2f} m³")

    confirm = take_input(
        f"\n{Fore.YELLOW}Proceed with bulk purchase? (y/n): {Style.RESET_ALL}"
    )

    if confirm.lower() == "y":
        for ore_cargo, quantity, cost in purchases:
            # Execute each purchase
            from .trading import buy_command

            buy_command(game_state, ore_cargo.ore.name, str(quantity))

        game_state.ui.success_message(
            f"\nBulk purchase completed! Total spent: {total_cost:.2f} credits"
        )
    else:
        game_state.ui.info_message("Bulk purchase cancelled.")

    take_input("Press Enter to continue...")


def _calculate_modified_buy_price(game_state: Game, base_price: float) -> float:
    """Calculate buy price with character modifiers applied."""
    player_character = game_state.get_player_character()
    if not player_character:
        return base_price

    price_modifier = 1.0

    # Apply buy price modifier from traits
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

    return base_price * price_modifier


def _calculate_modified_sell_price(game_state: Game, base_price: float) -> float:
    """Calculate sell price with character modifiers applied."""
    player_character = game_state.get_player_character()
    if not player_character:
        return base_price

    price_modifier = 1.0

    # Apply sell price modifier from traits
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

    return base_price * price_modifier


# Register the enhanced trading menu command
register_command(["trade_menu", "trading", "tm"], trading_menu_command, [])
