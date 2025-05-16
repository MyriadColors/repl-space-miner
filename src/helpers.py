import math
import random

from pygame import Vector2
from src.classes.ore import Ore


def euclidean_distance(v1: Vector2, v2: Vector2):
    return round(math.sqrt((v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2), 2)


def rnd_float(min_val, max_val):
    return round(min_val + random.random() * (max_val - min_val), 2)


def rnd_int(min_val, max_val):
    return random.randint(min_val, max_val)


def rnd_vector(min_val, max_val):
    return Vector2(rnd_float(min_val, max_val), rnd_float(min_val, max_val))


def vector_to_string(vector: Vector2):
    return f"({vector.x:.3f}, {vector.y:.3f})"


def take_input(prompt):
    return input(prompt)


def meters_cubed_to_km_cubed(meters_cubed):
    return round(meters_cubed / 1000000.0, 3)


def meters_cubed_to_million_km_cubed(meters_cubed):
    return round(meters_cubed / 1000000000.0, 3)


def meters_to_au_cubed(meters):
    return round(meters / 149_597_870_700.0, 3)


def format_seconds(seconds: float):
    if seconds == 0:
        return "0 seconds"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = ((seconds % 86400) % 3600) // 60
    seconds = int((seconds % 86400) % 60)

    formatted_days = f"{days} days " if days > 0 else ""
    formatted_hours = f"{hours} hours " if hours > 0 else ""
    formatted_minutes = f"{minutes} minutes " if minutes > 0 else ""

    return (
        f"{formatted_days}{formatted_hours}{formatted_minutes}{seconds} seconds".strip()
    )


def select_random_ore() -> Ore:
    rnd_index = random.randint(0, len(ORES) - 1)

    return ORES[rnd_index]


def get_closest_field(solar_system, position, is_at_field=False):
    """
    Find the closest asteroid field relative to a given position.

    Args:
        solar_system: Either a SolarSystem object or a list of AsteroidField objects
        position: The position to find the closest field from
        is_at_field: If True, returns the second closest field (skipping the current one)

    Returns:
        The closest AsteroidField object
    """
    # Handle when we receive a list of asteroid fields directly
    if isinstance(solar_system, list):
        # Sort the fields by distance
        sorted_fields = sorted(
            solar_system,
            key=lambda field: euclidean_distance(position, field.space_object.position),
        )
        # Return the second closest if at a field, otherwise the closest
        return (
            sorted_fields[1]
            if is_at_field and len(sorted_fields) > 1
            else sorted_fields[0]
        )
    else:
        # Handle when we receive a SolarSystem object
        if is_at_field:
            return solar_system.sort_fields("asc", "distance", position)[1]
        return solar_system.sort_fields("asc", "distance", position)[0]


def get_closest_station(solar_system, player_ship, is_at_station=False):
    """
    Find the closest station relative to a player ship's position.

    Args:
        solar_system: Either a SolarSystem object or a list of Station objects
        player_ship: The player's ship object
        is_at_station: If True, returns the second closest station (skipping the current one)

    Returns:
        The closest Station object
    """
    position = player_ship.space_object.get_position()

    # Handle when we receive a list of stations directly
    if isinstance(solar_system, list):
        # Sort the stations by distance
        sorted_stations = sorted(
            solar_system,
            key=lambda station: euclidean_distance(
                position, station.space_object.position
            ),
        )
        # Return the second closest if at a station, otherwise the closest
        return (
            sorted_stations[1]
            if is_at_station and len(sorted_stations) > 1
            else sorted_stations[0]
        )
    else:
        # Handle when we receive a SolarSystem object
        if is_at_station:
            return solar_system.sort_stations("asc", "distance", position)[1]
        return solar_system.sort_stations("asc", "distance", position)[0]


def prompt_for_closest_travel_choice(player_ship, closest_field, closest_station, time):
    """Prompts the player to choose between the closest field or station."""
    tries = 3
    while tries > 0:
        response = take_input(
            "Do you wish to go to the closest 1. (f)ield or the closest 2. (s)tation?"
        )
        if response in ["1", "f", "field"]:
            return player_ship.travel(closest_field.position, time)
        elif response in ["2", "s", "station"]:
            return player_ship.travel(closest_station.position, time)
        else:
            print("Invalid choice. Please enter 'f' or 's'.")
            tries -= 1

    print("Too many invalid attempts. Aborting.")


from src.classes.ore import ORES


def get_ore_by_id_or_name(identifier: str | int) -> Ore | None:
    """Returns an Ore from the ORES dictionary based on its ID or name.

    Args:
        identifier: The ID (int) or name (str) of the ore.

    Returns:
        The corresponding Ore object if found, otherwise None.
    """

    if isinstance(identifier, int):
        return ORES.get(identifier)
    elif isinstance(identifier, str):
        for ore_id, ore in ORES.items():
            if ore.name.lower() == identifier.lower():
                return ore
    return None


def is_valid_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_valid_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_valid_bool(value: str) -> bool:
    return value.lower() in ("true", "false", "1", "0")
