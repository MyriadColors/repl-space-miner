import math
import random
from pygame import Vector2
import src.data as data
from src.classes.ore import Ore

def euclidean_distance(v1, v2):
    return round(math.sqrt((v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2), 2)


def rnd_float(min_val, max_val):
    return min_val + random.random() * (max_val - min_val)

def rnd_int(min_val, max_val):
    return random.randint(min_val, max_val)

def rnd_vector(min_val, max_val):
    return Vector2(rnd_float(min_val, max_val), rnd_float(min_val, max_val))


def vector_to_string(v):
    return f"({v.x:.3f}, {v.y:.3f})"


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
    seconds = (seconds % 86400) % 60

    formatted_days = f"{days} days, " if days > 0 else ""
    formatted_hours = f"{hours} hours, " if hours > 0 else ""
    formatted_minutes = f"{minutes} minutes" if minutes > 0 else ""

    return f"{formatted_days}{formatted_hours}{formatted_minutes} and {seconds} seconds"


def select_random_ore() -> Ore:
    rnd_index = random.randint(0, len(data.ORES) - 1)

    return data.ORES[rnd_index]


def get_closest_field(solar_system, position, is_at_field=False):
    if is_at_field:
        return solar_system.sort_fields('asc', 'distance', position)[1]
    closest_field = solar_system.sort_fields('asc', 'distance', position)[0]
    return closest_field


def get_closest_station(solar_system, player_ship, is_at_station=False):
    if is_at_station:
        return solar_system.sort_stations('asc', 'distance', player_ship.position)[1]
    return solar_system.sort_stations('asc', 'distance', player_ship.position)[0]


def prompt_for_closest_travel_choice(player_ship, closest_field, closest_station, time):
    """Prompts the player to choose between the closest field or station."""

    print("Do you wish to go to the closest 1. (f)ield or the closest 2. (s)tation?")
    tries = 3
    while tries > 0:
        response = take_input(">> ")
        if response in ["1", "f", "field"]:
            return player_ship.travel(closest_field.position, time)
        elif response in ["2", "s", "station"]:
            return player_ship.travel(closest_station.position, time)
        else:
            print("Invalid response.")
            tries -= 1

    print("Too many invalid attempts. Aborting.")
    return time
