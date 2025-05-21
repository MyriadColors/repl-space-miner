"""
This module implements commands for comparing prices across different stations in the system.
"""

from pygame import Vector2
from typing import Dict, List, Tuple, Optional
from colorama import Fore, Style

from src.classes.game import Game
from src.classes.station import Station
from src.data import OreCargo
from src.helpers import format_seconds
from .base import register_command
from .registry import Argument


def get_travel_details(
    game_state: Game, station: Station
) -> Tuple[float, float, float, bool]:
    """
    Calculate travel details from player's current position to a station.

    Args:
        game_state: The current game state
        station: The destination station

    Returns:
        Tuple containing (distance, travel_time, fuel_consumed, is_reachable)
    """
    player_ship = game_state.get_player_ship()

    # Calculate raw travel data
    distance, travel_time, fuel_consumed = player_ship.calculate_travel_data(
        station.space_object.position
    )

    # Apply character modifiers if applicable
    character = game_state.get_player_character()
    if character:
        fuel_consumed = player_ship.calculate_adjusted_fuel_consumption(
            character, fuel_consumed
        )

    # Check if the station is reachable with current fuel
    is_reachable = player_ship.fuel >= fuel_consumed

    return distance, travel_time, fuel_consumed, is_reachable


def get_best_buy_prices(
    game_state: Game, include_unreachable: bool = False
) -> Dict[str, List[Tuple[Station, float, float, float, bool]]]:
    """
    Get the best buying prices for each ore across all stations.

    Args:
        game_state: The current game state
        include_unreachable: Whether to include stations that can't be reached with current fuel

    Returns:
        Dictionary mapping ore names to lists of (station, price, travel_cost, total_cost, reachable) tuples,
        sorted by total cost (price + travel cost)
    """
    current_system = game_state.get_current_solar_system()
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()
    # Dictionary to track best prices by ore
    ore_prices: Dict[str, List[Tuple[Station, float, float, float, bool]]] = {}

    # Character's buy price modifier (if applicable)
    price_modifier = 1.0
    if player_character and hasattr(player_character, "buy_price_mod"):
        price_modifier = player_character.buy_price_mod

        # Apply charisma bonus (0.5% discount per point above 5)
        if player_character.charisma > 5:
            charisma_bonus = 1 - ((player_character.charisma - 5) * 0.005)
            price_modifier *= charisma_bonus

        # Apply trader reputation bonus (0.25% per positive reputation point)
        if player_character.reputation_traders > 0:
            trader_bonus = 1 - (player_character.reputation_traders * 0.0025)
            price_modifier *= trader_bonus

    # Process each station
    for station in current_system.stations:
        # Skip current station if docked
        if player_ship.is_docked and player_ship.docked_at == station:
            distance, travel_time, fuel_consumed = 0.0, 0.0, 0.0
            is_reachable = True
        else:
            distance, travel_time, fuel_consumed, is_reachable = get_travel_details(
                game_state, station
            )

        if not is_reachable and not include_unreachable:
            continue

        # Calculate travel cost (fuel cost)
        fuel_cost = station.fuel_price * fuel_consumed

        # Process each ore type at this station
        for ore_cargo in station.ore_cargo:
            if ore_cargo.quantity <= 0:
                continue  # Skip ores not available for purchase

            ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"
            buy_price = ore_cargo.buy_price * price_modifier
            total_cost = buy_price + (
                fuel_cost / 100
            )  # Amortize fuel cost over 100 units

            if ore_name not in ore_prices:
                ore_prices[ore_name] = []

            ore_prices[ore_name].append(
                (station, buy_price, fuel_cost, total_cost, is_reachable)
            )

    # Sort each ore's entries by total cost
    for ore_name in ore_prices:
        ore_prices[ore_name].sort(key=lambda x: x[3])  # Sort by total_cost

    return ore_prices


def get_best_sell_prices(
    game_state: Game, include_unreachable: bool = False
) -> Dict[str, List[Tuple[Station, float, float, float, bool]]]:
    """
    Get the best selling prices for each ore across all stations.

    Args:
        game_state: The current game state
        include_unreachable: Whether to include stations that can't be reached with current fuel

    Returns:
        Dictionary mapping ore names to lists of (station, price, travel_cost, net_profit, reachable) tuples,
        sorted by net profit (price - travel cost)
    """
    current_system = game_state.get_current_solar_system()
    player_ship = game_state.get_player_ship()
    player_character = game_state.get_player_character()

    # Dictionary to track best prices by ore
    ore_prices: Dict[str, List[Tuple[Station, float, float, float, bool]]] = {}
    # Character's sell price modifier (if applicable)
    price_modifier = 1.0
    if player_character and hasattr(player_character, "sell_price_mod"):
        price_modifier = player_character.sell_price_mod

        # Apply charisma bonus (0.5% bonus per point above 5)
        if player_character.charisma > 5:
            charisma_bonus = 1 + ((player_character.charisma - 5) * 0.005)
            price_modifier *= charisma_bonus

        # Apply trader reputation bonus (0.25% per positive reputation point)
        if player_character.reputation_traders > 0:
            trader_bonus = 1 + (player_character.reputation_traders * 0.0025)
            price_modifier *= trader_bonus

    # Process each station
    for station in current_system.stations:
        # Skip current station if docked
        if player_ship.is_docked and player_ship.docked_at == station:
            distance, travel_time, fuel_consumed = 0.0, 0.0, 0.0
            is_reachable = True
        else:
            distance, travel_time, fuel_consumed, is_reachable = get_travel_details(
                game_state, station
            )

        if not is_reachable and not include_unreachable:
            continue

        # Calculate travel cost (fuel cost)
        fuel_cost = station.fuel_price * fuel_consumed

        # Process each ore type at this station
        for ore_cargo in station.ore_cargo:
            ore_name = f"{ore_cargo.ore.purity.name} {ore_cargo.ore.name}"
            sell_price = ore_cargo.sell_price * price_modifier
            net_profit = sell_price - (
                fuel_cost / 100
            )  # Amortize fuel cost over 100 units

            if ore_name not in ore_prices:
                ore_prices[ore_name] = []

            ore_prices[ore_name].append(
                (station, sell_price, fuel_cost, net_profit, is_reachable)
            )

    # Sort each ore's entries by net profit (descending)
    for ore_name in ore_prices:
        ore_prices[ore_name].sort(key=lambda x: x[3], reverse=True)

    return ore_prices


def get_trade_opportunities(
    game_state: Game, include_unreachable: bool = False
) -> List[Tuple[str, Station, Station, float, float, float, bool]]:
    """
    Calculate trade opportunities between stations.

    Args:
        game_state: The current game state
        include_unreachable: Whether to include stations that can't be reached with current fuel

    Returns:
        List of tuples, each containing:
        (ore_name, buy_station, sell_station, buy_price, sell_price, potential_profit, is_viable)
        sorted by potential profit in descending order
    """
    buy_prices = get_best_buy_prices(game_state, include_unreachable)
    sell_prices = get_best_sell_prices(game_state, include_unreachable)
    player_ship = game_state.get_player_ship()

    opportunities = []

    for ore_name in buy_prices:
        if ore_name not in sell_prices:
            continue

        for buy_station, buy_price, buy_fuel_cost, _, buy_reachable in buy_prices[
            ore_name
        ]:
            for (
                sell_station,
                sell_price,
                sell_fuel_cost,
                _,
                sell_reachable,
            ) in sell_prices[ore_name]:
                # Skip if buying and selling at the same station
                if buy_station == sell_station:
                    continue

                # Can we reach both stations?
                is_viable = buy_reachable and sell_reachable

                # Calculate round trip costs
                if player_ship.is_docked and player_ship.docked_at == buy_station:
                    trip_fuel_cost = sell_fuel_cost  # Already at buy station
                elif player_ship.is_docked and player_ship.docked_at == sell_station:
                    trip_fuel_cost = buy_fuel_cost  # Already at sell station
                else:
                    trip_fuel_cost = buy_fuel_cost + sell_fuel_cost

                # Calculate profit
                price_diff = sell_price - buy_price
                profit_per_unit = price_diff - (
                    trip_fuel_cost / 100
                )  # Amortize fuel cost over 100 units

                opportunities.append(
                    (
                        ore_name,
                        buy_station,
                        sell_station,
                        buy_price,
                        sell_price,
                        profit_per_unit,
                        is_viable,
                    )
                )

    # Sort by profit (descending)
    opportunities.sort(key=lambda x: x[5], reverse=True)
    return opportunities


def compare_fuel_prices(
    game_state: Game, stations: List[Station], include_unreachable: bool
) -> None:
    """
    Compare fuel prices across stations, including travel costs.

    Args:
        game_state: The current game state
        stations: List of stations to compare
        include_unreachable: Whether to include unreachable stations
    """
    player_ship = game_state.get_player_ship()

    # Sort stations by fuel price for easier comparison
    stations_with_data = []

    for station in stations:
        # Skip current station if docked
        if player_ship.is_docked and player_ship.docked_at == station:
            distance, travel_time, fuel_consumed, fuel_cost = 0.0, 0.0, 0.0, 0.0
            effective_price = station.fuel_price
            is_reachable = True
        else:
            distance, travel_time, fuel_consumed, is_reachable = get_travel_details(
                game_state, station
            )

            # Calculate the effective price including travel costs
            # Travel cost divided by a typical refuel amount (e.g., 500 units)
            fuel_to_travel = fuel_consumed
            typical_refuel = 500.0  # Typical amount a player might refuel

            # Calculate fuel cost to get there
            if player_ship.is_docked and player_ship.docked_at:
                # Use current station's fuel price if we're docked
                fuel_cost = fuel_to_travel * player_ship.docked_at.fuel_price
            else:
                # Use average system fuel price if we're not docked
                fuel_cost = fuel_to_travel * station.fuel_price

            # Calculate effective price including travel cost amortized over typical refuel
            travel_cost_per_unit = (
                fuel_cost / typical_refuel if typical_refuel > 0.0 else 0.0
            )
            effective_price = station.fuel_price + travel_cost_per_unit

        if is_reachable or include_unreachable:
            stations_with_data.append(
                (
                    station,
                    distance,
                    fuel_consumed,
                    fuel_cost,
                    station.fuel_price,
                    effective_price,
                    is_reachable,
                )
            )

    # Sort by effective price (ascending)
    stations_with_data.sort(key=lambda x: x[5])

    # Display results
    game_state.ui.info_message("\n=== FUEL PRICE COMPARISON ===")
    game_state.ui.info_message(
        f"{'Station':<20} {'Fuel Price':<12} {'Distance':<10} {'Travel Cost':<12} {'Effective Price':<15} {'Reachable':<10}"
    )
    game_state.ui.info_message("-" * 85)

    for (
        station,
        distance,
        fuel_consumed,
        fuel_cost,
        price,
        effective_price,
        is_reachable,
    ) in stations_with_data:
        reachable_str = "Yes" if is_reachable else "No (Low fuel)"

        # Color coding based on price competitiveness
        price_str = f"{price:.2f}"

        game_state.ui.info_message(
            f"{station.name:<20} {price_str:<12} {distance:<10.2f} {fuel_cost:<12.2f} {effective_price:<15.2f} {reachable_str:<10}"
        )
    game_state.ui.info_message("")


def compare_prices_command(
    game_state: Game, option: str = "all", show_all: str = "no"
) -> None:
    """
    Compare prices across the system for buying, selling, or trading.

    This command helps you find the best deals across all stations in the current solar system.
    It can show where to buy and sell different ores, calculate potential profits, and compare
    fuel prices while factoring in travel costs.
    """
    player_ship = game_state.get_player_ship()
    current_system = game_state.get_current_solar_system()

    include_unreachable = show_all.lower() in ["yes", "y", "true", "1"]
    # Validate option
    valid_options = ["buy", "sell", "trade", "fuel", "all"]
    option = option.lower()
    if option not in valid_options:
        game_state.ui.error_message(
            f"Invalid option: {option}. Use 'buy', 'sell', 'trade', 'fuel', or 'all'."
        )
        return

    # Show system information
    game_state.ui.info_message(
        f"\n=== PRICE COMPARISON: {current_system.name} SYSTEM ==="
    )
    game_state.ui.info_message(
        f"Current position: ({player_ship.space_object.position.x:.3f}, {player_ship.space_object.position.y:.3f})"
    )
    game_state.ui.info_message(
        f"Fuel available: {player_ship.fuel:.2f}/{player_ship.max_fuel} m³"
    )
    game_state.ui.info_message(
        f"Fuel consumption: {player_ship.fuel_consumption:.4f} m³/AU\n"
    )

    if option in ["buy", "all"]:
        buy_prices = get_best_buy_prices(game_state, include_unreachable)

        if buy_prices:
            game_state.ui.info_message("=== BEST BUYING PRICES ===")
            game_state.ui.info_message(
                f"{'Ore':<20} {'Station':<20} {'Price':<10} {'Fuel Cost':<10} {'Reachable':<10}"
            )
            game_state.ui.info_message("-" * 70)

            for ore_name in sorted(buy_prices.keys()):
                best_deal = buy_prices[ore_name][0]  # The best deal is already first
                station, price, fuel_cost, _, reachable = best_deal

                reachable_str = "Yes" if reachable else "No (Low fuel)"

                game_state.ui.info_message(
                    f"{ore_name:<20} {station.name:<20} {price:<10.2f} {fuel_cost:<10.2f} {reachable_str:<10}"
                )
            game_state.ui.info_message("")
        else:
            game_state.ui.info_message("No buying options available.\n")

    if option in ["sell", "all"]:
        sell_prices = get_best_sell_prices(game_state, include_unreachable)

        if sell_prices:
            game_state.ui.info_message("=== BEST SELLING PRICES ===")
            game_state.ui.info_message(
                f"{'Ore':<20} {'Station':<20} {'Price':<10} {'Fuel Cost':<10} {'Reachable':<10}"
            )
            game_state.ui.info_message("-" * 70)

            for ore_name in sorted(sell_prices.keys()):
                best_deal = sell_prices[ore_name][0]  # The best deal is already first
                station, price, fuel_cost, _, reachable = best_deal

                reachable_str = "Yes" if reachable else "No (Low fuel)"
                game_state.ui.info_message(
                    f"{ore_name:<20} {station.name:<20} {price:<10.2f} {fuel_cost:<10.2f} {reachable_str:<10}"
                )
            game_state.ui.info_message("")
        else:
            game_state.ui.info_message("No selling options available.\n")

    if option in ["trade", "all"]:
        opportunities = get_trade_opportunities(game_state, include_unreachable)

        if opportunities:
            game_state.ui.info_message("=== TRADE OPPORTUNITIES ===")
            game_state.ui.info_message(
                f"{'Ore':<20} {'Buy at':<20} {'Sell at':<20} {'Buy':<8} {'Sell':<8} {'Profit/Unit':<12} {'Viable':<8}"
            )
            game_state.ui.info_message("-" * 96)

            # Only show top 10 opportunities to avoid overwhelming the player
            for (
                ore_name,
                buy_station,
                sell_station,
                buy_price,
                sell_price,
                profit,
                viable,
            ) in opportunities[:10]:
                viable_str = "Yes" if viable else "No"
                profit_str = f"{profit:.2f}"

                # Highlight good profit opportunities
                if profit > 100:
                    profit_str = f"{Fore.GREEN}{profit:.2f}{Style.RESET_ALL}"
                elif profit > 50:
                    profit_str = f"{Fore.YELLOW}{profit:.2f}{Style.RESET_ALL}"
                elif profit <= 0:
                    profit_str = f"{Fore.RED}{profit:.2f}{Style.RESET_ALL}"

                game_state.ui.info_message(
                    f"{ore_name:<20} {buy_station.name:<20} {sell_station.name:<20} "
                    f"{buy_price:<8.2f} {sell_price:<8.2f} {profit_str:<12} {viable_str:<8}"
                )
            game_state.ui.info_message("")
            if len(opportunities) > 10:
                game_state.ui.info_message(
                    f"Showing top 10 of {len(opportunities)} opportunities."
                )
        else:
            game_state.ui.info_message("No trading opportunities found.\n")

    if option in ["fuel", "all"]:
        # Compare fuel prices across stations
        compare_fuel_prices(game_state, current_system.stations, include_unreachable)

    game_state.ui.info_message("\n=== COMMAND HELP ===")
    game_state.ui.info_message("Usage: compare [option] [show_all]")
    game_state.ui.info_message("  Options:  buy   - Best buying prices")
    game_state.ui.info_message("           sell   - Best selling prices")
    game_state.ui.info_message("           trade  - Find trade opportunities")
    game_state.ui.info_message("           fuel   - Compare fuel prices")
    game_state.ui.info_message("           all    - Show all (default)")
    game_state.ui.info_message(
        "  Show all: yes/no - Include unreachable stations (default: no)"
    )
    game_state.ui.info_message(
        "\nTip: Try 'routes' command to find the most profitable trade routes."
    )


# Register the commands
def find_best_trade_routes(
    game_state: Game, max_routes=None, include_unreachable=None
) -> None:
    """
    Find the most profitable trade routes within the current solar system.

    Usage: routes [max_routes] [include_unreachable]

    Parameters:
        max_routes - Maximum number of routes to display (default: 5)
        include_unreachable - Whether to include stations that can't be reached with current fuel
                             (true/false, default: false)

    Examples:
        routes         - Show top 5 profitable trade routes for reachable stations
        routes 10      - Show top 10 profitable trade routes
        routes 5 true  - Show top 5 routes including unreachable stations

    The command calculates potential profit based on your ship's cargo capacity,
    available quantities, and fuel costs for the trip.
    """
    player_ship = game_state.get_player_ship()
    current_system = game_state.get_current_solar_system()

    # Set defaults and convert types
    try:
        max_routes_int = int(max_routes) if max_routes is not None else 5
    except (ValueError, TypeError):
        max_routes_int = 5

    # Convert include_unreachable to boolean
    if include_unreachable is None:
        include_unreachable_bool = False
    elif isinstance(include_unreachable, str):
        include_unreachable_bool = include_unreachable.lower() in [
            "true",
            "yes",
            "y",
            "1",
        ]
    else:
        include_unreachable_bool = bool(include_unreachable)

    if not current_system or not current_system.stations:
        game_state.ui.error_message("No stations found in the current system.")
        return

    # Get all buying and selling opportunities
    buy_prices = get_best_buy_prices(game_state, include_unreachable_bool)
    sell_prices = get_best_sell_prices(game_state, include_unreachable_bool)

    # Calculate max cargo capacity in units for each ore type
    ore_capacity = {}
    for ore_name in buy_prices:
        # Get the ore from the first buy opportunity
        if buy_prices[ore_name]:
            station, _, _, _, _ = buy_prices[ore_name][0]
            ore_cargo = next(
                (
                    oc
                    for oc in station.ore_cargo
                    if f"{oc.ore.purity.name} {oc.ore.name}" == ore_name
                ),
                None,
            )

            if ore_cargo:
                # Calculate how many units of this ore the ship can hold
                max_units = int(player_ship.cargohold_capacity // ore_cargo.ore.volume)
                ore_capacity[ore_name] = max_units

    # Calculate potential routes
    routes = []

    for ore_name in buy_prices:
        if (
            ore_name not in sell_prices
            or not buy_prices[ore_name]
            or not sell_prices[ore_name]
        ):
            continue

        for buy_index, buy_data in enumerate(buy_prices[ore_name]):
            buy_station, buy_price, buy_fuel_cost, _, buy_reachable = buy_data

            # Skip unreachable stations if not including them
            if not buy_reachable and not include_unreachable_bool:
                continue

            for sell_index, sell_data in enumerate(sell_prices[ore_name]):
                sell_station, sell_price, sell_fuel_cost, _, sell_reachable = sell_data

                # Skip same station or unreachable stations
                if buy_station == sell_station or (
                    not sell_reachable and not include_unreachable_bool
                ):
                    continue

                # Calculate round-trip distance and fuel costs
                if player_ship.is_docked and player_ship.docked_at:
                    start_pos = player_ship.docked_at.position
                else:
                    start_pos = player_ship.space_object.position

                trip_distance = start_pos.distance_to(
                    buy_station.position
                ) + buy_station.position.distance_to(sell_station.position)

                trip_fuel = trip_distance * player_ship.fuel_consumption
                trip_fuel_cost = (
                    trip_fuel * buy_station.fuel_price
                )  # Use buy station's fuel price as proxy

                # Calculate potential profit
                price_diff = sell_price - buy_price
                # Get available quantity at the buy station
                ore_obj = buy_station.get_ore_by_name(ore_name.split()[-1])
                available_qty = ore_obj.quantity if ore_obj else 0

                max_units = min(
                    ore_capacity.get(ore_name, 100),  # Ship capacity
                    available_qty,  # Available quantity
                )

                if max_units <= 0:
                    continue  # Skip if no units available

                total_profit = (price_diff * max_units) - trip_fuel_cost
                profit_per_au = total_profit / trip_distance if trip_distance > 0 else 0

                # Only include profitable routes
                if total_profit > 0:
                    routes.append(
                        {
                            "ore_name": ore_name,
                            "buy_station": buy_station,
                            "sell_station": sell_station,
                            "buy_price": buy_price,
                            "sell_price": sell_price,
                            "profit_per_unit": price_diff,
                            "max_units": max_units,
                            "distance": trip_distance,
                            "fuel_cost": trip_fuel_cost,
                            "total_profit": total_profit,
                            "profit_per_au": profit_per_au,
                            "viable": buy_reachable and sell_reachable,
                        }
                    )

    # Sort by total profit (highest first)
    routes.sort(key=lambda x: x["total_profit"], reverse=True)

    # Display results
    game_state.ui.info_message("\n=== BEST TRADE ROUTES ===")

    if routes:
        game_state.ui.info_message(
            f"{'Ore':<20} {'Buy at':<20} {'Sell at':<20} {'Profit/Unit':<12} "
            f"{'Units':<8} {'Dist':<8} {'Fuel Cost':<10} {'Total Profit':<12} {'Viable':<12}"
        )
        game_state.ui.info_message("-" * 120)

        # Show limited number of best routes
        for i, route in enumerate(routes[:max_routes_int]):
            viable_str = "Yes" if route["viable"] else "No"

            # Highlight good profits
            profit_str = f"{route['profit_per_unit']:.2f}"
            total_profit_str = f"{route['total_profit']:.2f}"

            if route["total_profit"] > 10000:
                total_profit_str = (
                    f"{Fore.GREEN}{route['total_profit']:.2f}{Style.RESET_ALL}"
                )
            elif route["total_profit"] > 5000:
                total_profit_str = (
                    f"{Fore.YELLOW}{route['total_profit']:.2f}{Style.RESET_ALL}"
                )

            game_state.ui.info_message(
                f"{route['ore_name']:<20} {route['buy_station'].name:<20} {route['sell_station'].name:<20} "
                f"{profit_str:<12} {route['max_units']:<8} {route['distance']:<8.2f} {route['fuel_cost']:<10.2f} "
                f"{total_profit_str:<12} {viable_str:<8}"
            )

        game_state.ui.info_message("")
        if len(routes) > max_routes_int:
            game_state.ui.info_message(
                f"Showing top {max_routes_int} of {len(routes)} routes."
            )
    else:
        game_state.ui.info_message("No profitable trade routes found.")
    game_state.ui.info_message("")


# Register the commands
register_command(
    ["compare", "comp", "market_compare", "prices"],
    compare_prices_command,
    [Argument("option", str, True), Argument("show_all", str, True)],
)

register_command(
    ["routes", "traderoutes", "bestroutes", "tr"],
    find_best_trade_routes,
    [Argument("max_routes", int, True), Argument("include_unreachable", bool, True)],
)
