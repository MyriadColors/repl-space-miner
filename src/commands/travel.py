from pygame import Vector2

from src.classes.game import Game  # Ensure this is the updated Game class
from src.classes.solar_system import (
    SolarSystem,
)  # Import SolarSystem for type hinting if needed
from src.helpers import (
    get_closest_field,
    get_closest_station,
    format_seconds,
)
from .registry import Argument
from .base import register_command


def travel_command(game_state: Game, **kwargs) -> float:
    """Handle travel command execution."""
    player_ship = game_state.get_player_ship()
    destination = Vector2(
        float(kwargs.get("destination_x", 0)), float(
            kwargs.get("destination_y", 0))
    )

    # Check if destination is within system boundaries
    current_system: SolarSystem = game_state.get_current_solar_system()
    system_size = current_system.size
    if destination.length() > system_size:
        game_state.ui.error_message(
            f"Destination is outside system boundaries. Maximum distance from center is {system_size} AU."
        )
        return 0.0

    distance, travel_time, fuel_consumed = player_ship.calculate_travel_data(
        destination
    )

    if player_ship.fuel - fuel_consumed < 0:
        game_state.ui.error_message(
            "Not enough fuel to travel. Please refuel.")
        return 0.0

    # Show travel details before confirmation
    game_state.ui.info_message("Travel details:")
    game_state.ui.info_message(f"  Distance: {distance:.2f} AU")
    game_state.ui.info_message(
        f"  Fuel required: {fuel_consumed:.2f} m³ (You have: {player_ship.fuel:.2f} m³)"
    )
    game_state.ui.info_message(
        f"  Estimated travel time: {format_seconds(travel_time)}"
    )

    confirm = input("Confirm travel? (y/n) ")
    # Accept various forms of "yes" as confirmation
    if confirm.lower() not in ["y", "yes", "yeah", "yep", "sure", "ok", "okay"]:
        game_state.ui.info_message("Travel cancelled.")
        return 0.0

    player_ship.consume_fuel(fuel_consumed)
    player_ship.space_object.position = destination
    game_state.global_time += round(travel_time)

    # Check for debt interest after time has passed
    if game_state.player_character:
        interest_result = game_state.player_character.calculate_debt_interest(
            int(game_state.global_time / 3600)
        )
        if interest_result:
            interest_amount, new_debt = interest_result
            game_state.ui.warn_message("\n⚠️ DEBT ALERT! ⚠️")
            game_state.ui.warn_message(
                f"While traveling, {interest_amount:.2f} credits of interest has accumulated on your debt!"
            )
            game_state.ui.warn_message(
                f"Your current debt is now {new_debt:.2f} credits."
            )

            # Advice based on debt levels
            if new_debt > 10000:
                game_state.ui.error_message(
                    "Your debt has reached dangerous levels. Creditors may soon take action!"
                )
                game_state.ui.info_message(
                    "Visit any station's banking terminal to make payments on your debt."
                )
            elif new_debt > 5000:
                game_state.ui.warn_message(
                    "Your debt is growing. Consider making payments at a station soon."
                )

    game_state.ui.info_message(f"The ship has arrived at {destination}")
    return float(travel_time)


def closest_travel(game_state: Game, object_type: str) -> None:
    """Handle travel to closest object command."""
    player_ship = game_state.get_player_ship()
    current_system: SolarSystem = game_state.get_current_solar_system()

    if object_type.lower() == "field":
        closest_field = get_closest_field(
            current_system.get_all_asteroid_fields(), player_ship.space_object.position
        )
        if closest_field:
            travel_command(
                game_state,
                destination_x=str(closest_field.space_object.position.x),
                destination_y=str(closest_field.space_object.position.y),
            )
        else:
            game_state.ui.error_message("No asteroid fields found.")

    elif object_type.lower() == "station":
        closest_station = get_closest_station(
            current_system.get_all_stations(), player_ship.space_object.position
        )
        if closest_station:
            travel_command(
                game_state,
                destination_x=str(closest_station.space_object.position.x),
                destination_y=str(closest_station.space_object.position.y),
            )
        else:
            game_state.ui.error_message("No stations found.")
    else:
        game_state.ui.error_message(f"Unknown object type: {object_type}")


def direct_travel_command(game_state: Game, destination_x: str, destination_y: str):
    """Handle direct travel to coordinates command."""
    try:
        if game_state.get_player_ship().is_docked:
            game_state.ui.error_message(
                "You must undock your ship before traveling.")
            return
        x = float(destination_x)
        y = float(destination_y)
        # Ensure we pass the return value properly so debt interest calculation happens
        return travel_command(game_state, destination_x=str(x), destination_y=str(y))
    except ValueError:
        game_state.ui.error_message(
            "Invalid coordinates. Please provide valid numbers."
        )


# Register travel commands
register_command(
    ["travel", "t"],
    travel_command,
    [
        Argument("destination_x", float, False),
        Argument("destination_y", float, False),
    ],
)

register_command(
    ["closest", "c"],
    closest_travel,
    [Argument("object_type", str, False)],
)

register_command(
    ["direct", "d"],
    direct_travel_command,
    [
        Argument("destination_x", str, False),
        Argument("destination_y", str, False),
    ],
)
