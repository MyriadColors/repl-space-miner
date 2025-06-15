from typing import List
from src.classes.game import Game
from src.helpers import take_input
from src.events.skill_events import (
    process_skill_xp_from_activity,
    notify_skill_progress,
)
from .registry import Argument
from .base import register_command
from .travel import direct_travel_command
from src.classes.celestial_body import CelestialBody, Star, Planet, Moon, AsteroidBelt


def scan_command(game_state: Game, num_objects: str) -> None:
    """Scan for objects in the system."""
    player_ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    # Check if 'all' flag is used for complete system map
    if num_objects.lower() == "all":
        game_state.ui.info_message("Performing complete system scan...")
        game_state.ui.info_message("=" * 50)
        game_state.ui.info_message("COMPLETE SYSTEM MAP")
        game_state.ui.info_message("=" * 50)

        # Get all objects in the system without limitations
        solar_system = game_state.get_current_solar_system()
        all_objects = solar_system.get_all_space_objects()

        if not all_objects:
            game_state.ui.warn_message(
                "No objects found in the current system.")
            return

        # Sort objects by distance for organized display
        sorted_objects = sorted(
            all_objects,
            key=lambda obj: obj.space_object.position.distance_to(
                player_ship.space_object.position
            ),
        )

        game_state.ui.info_message(
            f"Total objects in system: {len(sorted_objects)}")
        game_state.ui.info_message("-" * 50)

        # Display all objects with detailed information
        for i, obj in enumerate(sorted_objects):
            game_state.ui.info_message(
                f"{i}. {obj.to_string_short(player_ship.space_object.get_position())}"
            )

        # Also show asteroid fields from belts separately for clarity

        asteroid_fields = solar_system.get_all_asteroid_fields()
        if asteroid_fields:
            game_state.ui.info_message("-" * 50)
            game_state.ui.info_message("ASTEROID FIELDS:")
            for i, field in enumerate(asteroid_fields):
                game_state.ui.info_message(
                    f"  Field {i}: {field.to_string_short(player_ship.space_object.get_position())}"
                )

        game_state.ui.info_message("=" * 50)
        objects = sorted_objects  # Use all objects for selection
    else:
        # Standard scan with limitations
        try:
            amount_of_objects: int = int(num_objects)
        except ValueError:
            game_state.ui.error_message(
                "Invalid input. Please enter a number or 'all'."
            )
            return

        game_state.ui.info_message(
            f"Scanning for {amount_of_objects} objects...")

        # Get limited objects from the scan based on sensor range and priority
        objects = game_state.get_current_solar_system().scan_system_objects(
            player_ship.space_object.get_position(), amount_of_objects
        )

        # Check if any objects were found
        if not objects:
            game_state.ui.warn_message(
                "No objects detected within sensor range.")
            return

        game_state.ui.info_message("Sensor detected the following objects:")
        for i in range(min(amount_of_objects, len(objects))):
            game_state.ui.info_message(
                f"{i}. {objects[i].to_string_short(player_ship.space_object.get_position())}"
            )  # Process skill experience from scanning
    if game_state.player_character:
        # Scanning gives education and engineering XP
        # For 'all' scans, use a higher difficulty based on total objects found
        if num_objects.lower() == "all":
            # All scan is more challenging
            difficulty = min(3.0, len(objects) / 10)
        else:
            # Standard scan difficulty
            difficulty = min(2.0, int(num_objects) / 5)

        skill_results = process_skill_xp_from_activity(
            game_state,
            "scan",
            difficulty=difficulty,
        )
        notify_skill_progress(game_state, skill_results)

    # Only proceed with selection if objects were found
    if objects:
        game_state.ui.warn_message(
            "Enter object to examine or navigate to, or -1 to abort:"
        )
        input_response = take_input(
            "Enter the number of the object or -1 to abort: ")

        if input_response == "-1":
            return
        else:
            try:
                input_response_index = int(input_response)

                # Validate the index is within bounds
                if input_response_index < 0 or input_response_index >= len(objects):
                    game_state.ui.error_message(
                        f"Invalid selection. Please choose a number between 0 and {len(objects) - 1}."
                    )
                    return

                selected_object = objects[input_response_index]

                # Check if selected object is a celestial body for detailed view
                if isinstance(selected_object, CelestialBody):
                    display_celestial_detail(game_state, selected_object)

                    # Ask if the player wants to travel to the object
                    travel_response = take_input(
                        "Travel to this object? (y/n): ")
                    if travel_response.lower() != "y":
                        return

                selected_object_position = selected_object.space_object.position
                # Ensure debt interest is calculated by properly handling the travel command
                direct_travel_command(
                    game_state,
                    str(selected_object_position.x),
                    str(selected_object_position.y),
                )
            except ValueError:
                game_state.ui.error_message(
                    "Invalid input. Please enter a valid number."
                )
                return


def scan_asteroids_command(game_state: Game) -> None:
    """Scan the current asteroid field for available ores."""
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    is_inside_field, field = player_ship.check_field_presence(game_state)
    if not is_inside_field or field is None:
        game_state.ui.error_message("You are not inside a field.")
        return

    game_state.ui.info_message("Available ores in this field:")
    for ore in field.ores_available:
        game_state.ui.info_message(f"- {ore.name}")

    # Process skill experience from field scanning
    if game_state.player_character:
        # Calculate difficulty based on variety of ores and field properties
        ore_variety = (
            len(field.ores_available) / 5
        )  # Higher variety = higher difficulty
        asteroid_quantity = (
            field.asteroid_quantity / 50
        )  # More asteroids = higher difficulty
        base_difficulty = min(
            2.0, max(1.0, (ore_variety + asteroid_quantity) / 2))

        # Apply rarity modifier - rarer fields are more complex to analyze
        final_difficulty = base_difficulty * field.rarity_score * 0.7

        # Check if the player has enough energy to scan
        energy_cost = 10  # Example energy cost
        if player_ship.power < energy_cost:
            game_state.ui.warn_message(
                "Not enough ship power to perform scan.")
            return

        # Deduct energy cost
        player_ship.power -= energy_cost

        skill_results = process_skill_xp_from_activity(
            game_state, "scan", difficulty=final_difficulty
        )
        notify_skill_progress(game_state, skill_results)


def scan_celestial_command(game_state: Game) -> None:
    """Perform a detailed scan of nearby celestial bodies."""
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return  # Get all celestial bodies in the system
    solar_system = game_state.get_current_solar_system()
    celestial_bodies: List[CelestialBody] = []

    # Collect all celestial objects
    if solar_system.star:
        celestial_bodies.append(solar_system.star)

    celestial_bodies.extend(solar_system.planets)

    for planet in solar_system.planets:
        celestial_bodies.extend(planet.children)

    celestial_bodies.extend(solar_system.asteroid_belts)

    # Sort by distance
    celestial_bodies.sort(
        key=lambda body: body.space_object.position.distance_to(
            player_ship.space_object.position
        )
    )

    # Display the bodies
    if not celestial_bodies:
        game_state.ui.warn_message(
            "No celestial bodies detected in this system.")
        return

    game_state.ui.info_message("Celestial bodies in this system:")
    for i, body in enumerate(celestial_bodies):
        game_state.ui.info_message(
            f"{i}. {body.to_string_short(player_ship.space_object.position)}"
        )

    # Let player select a body for detailed info
    game_state.ui.warn_message("Enter body number to examine or -1 to abort:")
    response = take_input(
        "Enter the number of the celestial body or -1 to abort: ")

    if response == "-1":
        return

    try:
        index = int(response)
        if 0 <= index < len(celestial_bodies):
            selected_body = celestial_bodies[index]
            display_celestial_detail(game_state, selected_body)

            # Ask if the player wants to travel to the body
            travel_response = take_input(
                "Travel to this celestial body? (y/n): ")
            if travel_response.lower() == "y":
                direct_travel_command(
                    game_state,
                    str(selected_body.space_object.position.x),
                    str(selected_body.space_object.position.y),
                )
        else:
            game_state.ui.error_message(
                f"Invalid selection. Please choose a number between 0 and {len(celestial_bodies) - 1}."
            )
    except ValueError:
        game_state.ui.error_message(
            "Invalid input. Please enter a valid number.")

    # Process skill experience
    if game_state.player_character:
        skill_results = process_skill_xp_from_activity(
            game_state, "scan", difficulty=1.5
        )
        notify_skill_progress(game_state, skill_results)


def display_celestial_detail(game_state: Game, celestial_body: CelestialBody) -> None:
    """Display detailed information about a celestial body."""
    game_state.ui.info_message(f"\n===== {celestial_body.name} =====")

    if isinstance(celestial_body, Star):
        game_state.ui.info_message("Type: Star")
        game_state.ui.info_message(
            f"Stellar Class: {celestial_body.stellar_class}")
        game_state.ui.info_message(
            f"Temperature: {celestial_body.temperature} K")
        game_state.ui.info_message(
            f"Luminosity: {celestial_body.luminosity} solar units"
        )

        # List orbital stations
        if celestial_body.stations:
            game_state.ui.info_message(
                f"\nOrbital Stations ({len(celestial_body.stations)}):"
            )
            for station in celestial_body.stations:
                game_state.ui.info_message(f"- {station.name}")

        # List planets
        solar_system = game_state.get_current_solar_system()
        if solar_system.planets:
            game_state.ui.info_message(
                f"\nPlanets in system ({len(solar_system.planets)}):"
            )
        for planet in solar_system.planets:
            game_state.ui.info_message(
                f"- {planet.name} (distance: {planet.orbital_distance:.2f} AU)"
            )

    elif isinstance(celestial_body, Planet):
        game_state.ui.info_message("Type: Planet")
        game_state.ui.info_message(
            f"Planet Type: {celestial_body.planet_type.name.replace('_', ' ').title()}"
        )
        game_state.ui.info_message(
            f"Atmosphere: {celestial_body.atmosphere.title()}")

        # Display UHS information
        if (
            hasattr(celestial_body, "habitability_result")
            and celestial_body.habitability_result
        ):
            result = celestial_body.habitability_result
            game_state.ui.info_message(
                f"Habitability: {result.uhs_score:.2f}/100 ({result.rating_text})"
            )
            if result.is_viable:
                game_state.ui.info_message("Viable for life: Yes")
            else:
                game_state.ui.info_message("Viable for life: No")
        else:
            game_state.ui.info_message(
                f"Habitability: {celestial_body.habitability_score:.2f}/100"
            )
        game_state.ui.info_message(
            f"Orbital Distance: {celestial_body.orbital_distance:.2f} AU"
        )
        game_state.ui.info_message(f"Radius: {celestial_body.radius:.2f} AU")

        # List moons
        moons = [
            child for child in celestial_body.children if isinstance(child, Moon)]
        if moons:
            game_state.ui.info_message(f"\nMoons ({len(moons)}):")
            for moon in moons:
                game_state.ui.info_message(f"- {moon.name}")

        # List orbital stations
        if celestial_body.stations:
            game_state.ui.info_message(
                f"\nOrbital Stations ({len(celestial_body.stations)}):"
            )
            for station in celestial_body.stations:
                game_state.ui.info_message(f"- {station.name}")

    elif isinstance(celestial_body, Moon):
        game_state.ui.info_message("Type: Moon")
        game_state.ui.info_message(
            f"Parent Planet: {celestial_body.parent_planet.name}"
        )  # Display UHS information for moons
        if (
            hasattr(celestial_body, "habitability_result")
            and celestial_body.habitability_result
        ):
            result = celestial_body.habitability_result
            game_state.ui.info_message(
                f"Habitability: {result.uhs_score:.2f}/100 ({result.rating_text})"
            )
            if result.is_viable:
                game_state.ui.info_message("Viable for life: Yes")
            else:
                game_state.ui.info_message("Viable for life: No")
        else:
            game_state.ui.info_message(
                f"Habitability: {getattr(celestial_body, 'habitability_score', 0):.2f}/100"
            )

        game_state.ui.info_message(
            f"Orbital Distance: {celestial_body.orbital_distance:.2f} AU"
        )
        game_state.ui.info_message(f"Radius: {celestial_body.radius:.2f} AU")

        # List orbital stations
        if celestial_body.stations:
            game_state.ui.info_message(
                f"\nOrbital Stations ({len(celestial_body.stations)}):"
            )
            for station in celestial_body.stations:
                game_state.ui.info_message(f"- {station.name}")

    elif isinstance(celestial_body, AsteroidBelt):
        game_state.ui.info_message("Type: Asteroid Belt")
        game_state.ui.info_message(
            f"Inner Radius: {celestial_body.inner_radius:.2f} AU"
        )
        game_state.ui.info_message(
            f"Outer Radius: {celestial_body.outer_radius:.2f} AU"
        )
        game_state.ui.info_message(
            f"Belt Density: {celestial_body.density:.4f} fields/AU²"
        )
        game_state.ui.info_message(
            f"Asteroid Fields: {len(celestial_body.asteroid_fields)} fields"
        )

        # List some asteroid fields
        if celestial_body.asteroid_fields:
            fields_to_show = min(5, len(celestial_body.asteroid_fields))
            game_state.ui.info_message(
                f"\nSample Asteroid Fields ({fields_to_show} of {len(celestial_body.asteroid_fields)}):"
            )
            for i in range(fields_to_show):
                field = celestial_body.asteroid_fields[i]
                game_state.ui.info_message(
                    f"- Field {field.space_object.id}: {field.asteroid_quantity} asteroids"
                )


# Register scan commands
register_command(
    ["scan", "sc"],
    scan_command,
    [Argument("num_objects", str, False)],
)

register_command(
    ["scan_asteroids", "scna"],
    scan_asteroids_command,
    [],
)

register_command(
    ["scan_celestial", "scc"],
    scan_celestial_command,
    [],
)
