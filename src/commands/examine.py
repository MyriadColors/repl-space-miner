"""
Examine Command Module

This module provides commands for examining celestial bodies and getting detailed information.
"""

from typing import Optional
from src.classes.game import Game
from src.helpers import take_input
from src.classes.celestial_body import Star, Planet, Moon, AsteroidBelt
from src.classes.asteroid import AsteroidField
from src.classes.station import Station
from .registry import Argument
from .base import register_command
from .travel import direct_travel_command
from src.events.skill_events import (
    process_skill_xp_from_activity,
    notify_skill_progress,
)


def examine_command(game_state: Game, object_id_str: Optional[str] = None) -> None:
    """
    Examine an object in the current solar system to get detailed information.

    Args:
        game_state: Current game state
        object_id_str: ID of the object to examine (if None, examines closest object)
    """
    if object_id_str is None:
        # Examine the closest celestial body or station
        _examine_closest_object(game_state)
        return

    try:
        object_id = int(object_id_str)
    except ValueError:
        game_state.ui.error_message("Invalid ID. Please provide a valid numeric ID.")
        return

    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    # Find the object by ID
    solar_system = game_state.get_current_solar_system()
    all_objects = solar_system.get_all_space_objects()

    found_object = None
    for obj in all_objects:
        if obj.space_object.id == object_id:
            found_object = obj
            break

    if not found_object:
        game_state.ui.error_message(f"No object found with ID {object_id}")
        return

    # Display detailed information based on object type
    if isinstance(found_object, Star):
        _display_star_info(game_state, found_object)
    elif isinstance(found_object, Planet):
        _display_planet_info(game_state, found_object)
    elif isinstance(found_object, Moon):
        _display_moon_info(game_state, found_object)
    elif isinstance(found_object, AsteroidBelt):
        _display_belt_info(game_state, found_object)
    elif isinstance(found_object, AsteroidField):
        _display_field_info(game_state, found_object)
    elif isinstance(found_object, Station):
        _display_station_info(game_state, found_object)
    else:
        game_state.ui.info_message(
            found_object.to_string_short(player_ship.space_object.position)
        )  # Process skill experience from examining
    if game_state.player_character:
        # Examining objects gives education XP
        skill_results = process_skill_xp_from_activity(
            game_state,
            "examine",
            difficulty=1.0,  # Base difficulty
        )
        notify_skill_progress(game_state, skill_results)


def _examine_closest_object(game_state: Game) -> None:
    """Examine the closest celestial body or station."""
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    solar_system = game_state.get_current_solar_system()
    all_objects = solar_system.get_all_space_objects()

    if not all_objects:
        game_state.ui.error_message("No objects found in the current system.")
        return

    # Find the closest object
    closest_object = min(
        all_objects,
        key=lambda obj: obj.space_object.position.distance_to(
            player_ship.space_object.position
        ),
    )

    distance = closest_object.space_object.position.distance_to(
        player_ship.space_object.position
    )

    # Handle name attribute properly for different object types
    if isinstance(closest_object, AsteroidField):
        object_name = f"Asteroid Field {closest_object.space_object.id}"
    else:
        object_name = getattr(
            closest_object, "name", f"Object {closest_object.space_object.id}"
        )
    game_state.ui.info_message(
        f"Examining closest object: {object_name} (Distance: {distance:.2f} AU)"
    )

    # Display detailed information based on object type
    if isinstance(closest_object, Star):
        _display_star_info(game_state, closest_object)
    elif isinstance(closest_object, Planet):
        _display_planet_info(game_state, closest_object)
    elif isinstance(closest_object, Moon):
        _display_moon_info(game_state, closest_object)
    elif isinstance(closest_object, AsteroidBelt):
        _display_belt_info(game_state, closest_object)
    elif isinstance(closest_object, AsteroidField):
        _display_field_info(game_state, closest_object)
    elif isinstance(closest_object, Station):
        _display_station_info(game_state, closest_object)
    else:
        game_state.ui.info_message(
            closest_object.to_string_short(player_ship.space_object.position)
        )

    # Process skill experience from examining
    if game_state.player_character:
        skill_results = process_skill_xp_from_activity(
            game_state,
            "examine",
            difficulty=1.0,
        )
        notify_skill_progress(game_state, skill_results)


def _display_star_info(game_state: Game, star: Star) -> None:
    """Display detailed information about a star."""
    game_state.ui.info_message(f"===== STAR: {star.name} =====")
    game_state.ui.info_message(f"ID: {star.space_object.id}")
    game_state.ui.info_message(
        f"Position: ({star.space_object.position.x:.2f}, {star.space_object.position.y:.2f})"
    )
    game_state.ui.info_message(f"Stellar Class: {star.stellar_class}")
    game_state.ui.info_message(f"Temperature: {star.temperature} K")
    game_state.ui.info_message(f"Luminosity: {star.luminosity} (solar units)")
    game_state.ui.info_message(f"Radius: {star.radius:.3f} AU")

    # List orbiting objects
    if star.children or star.stations:
        game_state.ui.info_message("\nOrbiting Objects:")
        for child in star.children:
            game_state.ui.info_message(f"- {child.name} (ID: {child.space_object.id})")
        for station in star.stations:
            game_state.ui.info_message(
                f"- {station.name} Station (ID: {station.space_object.id})"
            )


def _display_planet_info(game_state: Game, planet: Planet) -> None:
    """Display detailed information about a planet."""
    game_state.ui.info_message(f"===== PLANET: {planet.name} =====")
    game_state.ui.info_message(f"ID: {planet.space_object.id}")
    game_state.ui.info_message(
        f"Position: ({planet.space_object.position.x:.2f}, {planet.space_object.position.y:.2f})"
    )
    game_state.ui.info_message(f"Type: {planet.planet_type}")
    game_state.ui.info_message(f"Atmosphere: {planet.atmosphere}")
    game_state.ui.info_message(f"Habitability Score: {planet.habitability_score}")
    game_state.ui.info_message(f"Orbital Distance: {planet.orbital_distance:.2f} AU")
    game_state.ui.info_message(f"Radius: {planet.radius:.3f} AU")

    # List moons and stations
    if planet.children:
        game_state.ui.info_message("\nMoons:")
        for child in planet.children:
            if isinstance(child, Moon):
                game_state.ui.info_message(
                    f"- {child.name} (ID: {child.space_object.id})"
                )

    if planet.stations:
        game_state.ui.info_message("\nOrbital Stations:")
        for station in planet.stations:
            game_state.ui.info_message(
                f"- {station.name} (ID: {station.space_object.id})"
            )


def _display_moon_info(game_state: Game, moon: Moon) -> None:
    """Display detailed information about a moon."""
    game_state.ui.info_message(f"===== MOON: {moon.name} =====")
    game_state.ui.info_message(f"ID: {moon.space_object.id}")
    game_state.ui.info_message(
        f"Position: ({moon.space_object.position.x:.2f}, {moon.space_object.position.y:.2f})"
    )
    game_state.ui.info_message(f"Parent Planet: {moon.parent_planet.name}")
    game_state.ui.info_message(f"Orbital Distance: {moon.orbital_distance:.2f} AU")
    game_state.ui.info_message(f"Radius: {moon.radius:.3f} AU")

    # List stations
    if moon.stations:
        game_state.ui.info_message("\nOrbital Stations:")
        for station in moon.stations:
            game_state.ui.info_message(
                f"- {station.name} (ID: {station.space_object.id})"
            )


def _display_belt_info(game_state: Game, belt: AsteroidBelt) -> None:
    """Display detailed information about an asteroid belt."""
    game_state.ui.info_message(f"===== ASTEROID BELT: {belt.name} =====")
    game_state.ui.info_message(f"ID: {belt.space_object.id}")
    game_state.ui.info_message(
        f"Position: ({belt.space_object.position.x:.2f}, {belt.space_object.position.y:.2f})"
    )
    game_state.ui.info_message(f"Inner Radius: {belt.inner_radius:.2f} AU")
    game_state.ui.info_message(f"Outer Radius: {belt.outer_radius:.2f} AU")
    game_state.ui.info_message(f"Density: {belt.density:.3f} fields/AU²")

    # List fields with interactive options
    if belt.asteroid_fields:
        game_state.ui.info_message(
            f"\nContains {len(belt.asteroid_fields)} asteroid fields:"
        )
        for i, field in enumerate(belt.asteroid_fields):
            player_ship = game_state.get_player_ship()
            distance = field.space_object.position.distance_to(
                player_ship.space_object.position
            )
            ore_names = [
                ore.name for ore in field.ores_available[:3]
            ]  # Show first 3 ores
            ore_summary = ", ".join(ore_names)
            if len(field.ores_available) > 3:
                ore_summary += f" (+{len(field.ores_available) - 3} more)"

            game_state.ui.info_message(
                f"- Field {field.space_object.id}: {field.asteroid_quantity} asteroids, "
                f"Distance: {distance:.2f} AU"
            )
            game_state.ui.info_message(f"  Ores: {ore_summary}")

        # Offer to navigate to fields
        game_state.ui.info_message("\nBelt Navigation Options:")
        game_state.ui.info_message(
            f"- Use 'belt_fields {belt.space_object.id}' to see detailed field list with travel options"
        )
        game_state.ui.info_message(
            "- Use 'travel closest field' to go to the nearest asteroid field in any belt"
        )


def _display_field_info(game_state: Game, field: AsteroidField) -> None:
    """Display detailed information about an asteroid field."""
    game_state.ui.info_message("===== ASTEROID FIELD =====")
    game_state.ui.info_message(f"ID: {field.space_object.id}")
    game_state.ui.info_message(
        f"Position: ({field.space_object.position.x:.2f}, {field.space_object.position.y:.2f})"
    )
    game_state.ui.info_message(f"Radius: {field.radius:.2f} AU")
    game_state.ui.info_message(f"Asteroid Count: {field.asteroid_quantity}")
    game_state.ui.info_message(f"Rarity Score: {field.rarity_score}")

    # List available ores
    if field.ores_available:
        game_state.ui.info_message("\nOres Available:")
        for ore in field.ores_available:
            game_state.ui.info_message(f"- {ore.name}")


def _display_station_info(game_state: Game, station: Station) -> None:
    """Display detailed information about a station."""
    game_state.ui.info_message(f"===== STATION: {station.name} =====")
    game_state.ui.info_message(f"ID: {station.space_object.id}")
    game_state.ui.info_message(
        f"Position: ({station.space_object.position.x:.2f}, {station.space_object.position.y:.2f})"
    )

    # Orbital information
    if station.is_orbital_station():
        game_state.ui.info_message(f"Status: {station.get_orbital_info()}")
    else:
        game_state.ui.info_message("Status: Independent station")

    # Resources
    game_state.ui.info_message(
        f"Fuel: {station.fuel_tank:.1f}/{station.fuel_tank_capacity:.1f} m³"
    )
    game_state.ui.info_message(f"Fuel Price: {station.fuel_price} credits")
    game_state.ui.info_message(f"Cargo Capacity: {station.ore_capacity} m³")


# Register examine command
register_command(
    ["examine", "ex"],
    examine_command,
    [Argument("object_id_str", str, True)],
)


def belt_fields_command(game_state: Game, belt_id_str: str) -> None:
    """
    Show asteroid fields within a specific belt and allow navigation.

    This command displays detailed information about all asteroid fields within
    a specified asteroid belt, including their positions, ore availability,
    and rarity scores. It also provides an interactive menu for navigating
    directly to any field within the belt.

    Usage:
        belt_fields <belt_id>
        bf <belt_id>

    Examples:
        belt_fields 15    # Show fields in belt with ID 15
        bf 15             # Short form of the same command

    Args:
        game_state: Current game state
        belt_id_str: ID of the belt to examine
    """
    try:
        belt_id = int(belt_id_str)
    except ValueError:
        game_state.ui.error_message(
            "Invalid ID. Please provide a valid numeric belt ID."
        )
        return

    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    # Find the belt by ID
    solar_system = game_state.get_current_solar_system()
    found_belt = None

    for belt in solar_system.asteroid_belts:
        if belt.space_object.id == belt_id:
            found_belt = belt
            break

    if not found_belt:
        game_state.ui.error_message(f"No asteroid belt found with ID {belt_id}")
        return

    if not found_belt.asteroid_fields:
        game_state.ui.info_message(
            f"Belt {found_belt.name} contains no asteroid fields."
        )
        return

    # Display detailed field information
    game_state.ui.info_message(
        f"\n===== {found_belt.name.upper()} - ASTEROID FIELDS ====="
    )
    game_state.ui.info_message(
        f"Belt contains {len(found_belt.asteroid_fields)} asteroid fields:\n"
    )

    # Show field details with navigation options
    for i, field in enumerate(found_belt.asteroid_fields):
        distance = field.space_object.position.distance_to(
            player_ship.space_object.position
        )
        ore_names = [ore.name for ore in field.ores_available]
        ore_list = ", ".join(ore_names) if ore_names else "Unknown"

        game_state.ui.info_message(f"Field {i + 1}: ID {field.space_object.id}")
        game_state.ui.info_message(
            f"  Position: ({field.space_object.position.x:.2f}, {field.space_object.position.y:.2f})"
        )
        game_state.ui.info_message(f"  Distance: {distance:.2f} AU")
        game_state.ui.info_message(f"  Asteroids: {field.asteroid_quantity}")
        game_state.ui.info_message(f"  Radius: {field.radius:.2f} AU")
        game_state.ui.info_message(f"  Available Ores: {ore_list}")
        game_state.ui.info_message(f"  Rarity Score: {field.rarity_score}")
        game_state.ui.info_message("")

    # Interactive navigation menu
    while True:
        game_state.ui.info_message("Navigation Options:")
        game_state.ui.info_message(
            "- Enter field number (1-{}) to travel there".format(
                len(found_belt.asteroid_fields)
            )
        )
        game_state.ui.info_message("- Enter 'closest' to travel to the nearest field")
        game_state.ui.info_message("- Enter 'quit' or 'q' to exit")

        choice = take_input("Choose an option: ").strip().lower()

        if choice in ["quit", "q", "exit"]:
            break
        elif choice == "closest":
            # Find closest field in this belt
            closest_field = min(
                found_belt.asteroid_fields,
                key=lambda f: f.space_object.position.distance_to(
                    player_ship.space_object.position
                ),
            )
            game_state.ui.info_message(
                f"Traveling to closest field (ID: {closest_field.space_object.id})..."
            )
            direct_travel_command(
                game_state,
                str(closest_field.space_object.position.x),
                str(closest_field.space_object.position.y),
            )
            break
        else:
            try:
                field_num = int(choice)
                if 1 <= field_num <= len(found_belt.asteroid_fields):
                    selected_field = found_belt.asteroid_fields[field_num - 1]
                    game_state.ui.info_message(
                        f"Traveling to field {field_num} (ID: {selected_field.space_object.id})..."
                    )
                    direct_travel_command(
                        game_state,
                        str(selected_field.space_object.position.x),
                        str(selected_field.space_object.position.y),
                    )
                    break
                else:
                    game_state.ui.error_message(
                        f"Invalid field number. Please choose 1-{len(found_belt.asteroid_fields)}"
                    )
            except ValueError:
                game_state.ui.error_message(
                    "Invalid input. Please enter a field number, 'closest', or 'quit'"
                )


# Register belt fields command
register_command(
    ["belt_fields", "bf"],
    belt_fields_command,
    [Argument("belt_id_str", str, True)],
)
