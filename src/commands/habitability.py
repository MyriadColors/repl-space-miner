"""
Habitability Command Module

This module provides commands for detailed habitability analysis using the Universal Habitability Score (UHS) system.
"""

from typing import Optional
from src.classes.game import Game
from src.classes.celestial_body import Planet, Moon
from .registry import Argument
from .base import register_command
from src.events.skill_events import (
    process_skill_xp_from_activity,
    notify_skill_progress,
)


def _perform_habitability_analysis(game_state: Game, celestial_body) -> None:
    """Perform the actual habitability analysis"""
    try:
        # Get habitability details
        details = celestial_body.get_habitability_details()

        # Display results
        game_state.ui.info_message(
            f"=== Habitability Analysis: {celestial_body.name} ==="
        )
        game_state.ui.info_message(details)

        # Award experience for scanning
        skill_results = process_skill_xp_from_activity(
            game_state, "scan", 25.0)
        notify_skill_progress(game_state, skill_results)

    except Exception as e:
        game_state.ui.error_message(
            f"Error performing habitability analysis: {str(e)}")


def _analyze_closest_habitable_body(game_state: Game) -> None:
    """Find and analyze the closest potentially habitable body"""
    player_ship = game_state.get_player_ship()
    solar_system = game_state.get_current_solar_system()
    # Find all planets and moons
    habitable_bodies = []
    all_objects = solar_system.get_all_space_objects()

    for obj in all_objects:
        if isinstance(obj, (Planet, Moon)):
            distance = obj.space_object.position.distance_to(
                player_ship.space_object.position
            )
            habitable_bodies.append((obj, distance))

    if not habitable_bodies:
        game_state.ui.error_message(
            "No planets or moons found in the current system")
        return

    # Sort by distance and pick the closest
    habitable_bodies.sort(key=lambda x: x[1])
    closest_body = habitable_bodies[0][0]

    game_state.ui.info_message(
        f"Analyzing closest habitable body: {closest_body.name}")
    _perform_habitability_analysis(game_state, closest_body)


def habitability_command(game_state: Game, object_id_str: Optional[str] = None) -> None:
    """
    Perform a detailed habitability analysis of a celestial body using the Universal Habitability Score (UHS) system.

    Args:
        game_state: Current game state
        object_id_str: ID of the object to analyze (if None, analyzes closest habitable body)
    """
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    solar_system = game_state.get_current_solar_system()

    if object_id_str is None:
        # Find the closest potentially habitable body
        _analyze_closest_habitable_body(game_state)
        return

    try:
        object_id = int(object_id_str)
    except ValueError:
        game_state.ui.error_message(
            "Invalid ID. Please provide a valid numeric ID.")
        return

    # Find the object by ID
    all_objects = solar_system.get_all_space_objects()
    found_object = None

    for obj in all_objects:
        if obj.space_object.id == object_id:
            found_object = obj
            break

    if found_object is None:
        game_state.ui.error_message(
            f"No celestial body found with ID {object_id}")
        return
    # Check if it's a habitable body type
    if not isinstance(found_object, (Planet, Moon)):
        object_name = getattr(found_object, "name", f"Object {object_id}")
        game_state.ui.error_message(f"{object_name} is not a planet or moon")
        return

    # Perform habitability analysis
    _perform_habitability_analysis(game_state, found_object)


def habitability_survey_command(game_state: Game) -> None:
    """
    Perform a comprehensive habitability survey of all celestial bodies in the current system.
    """
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    solar_system = game_state.get_current_solar_system()

    # Find all planets and moons
    all_objects = solar_system.get_all_space_objects()
    habitable_bodies = []

    for obj in all_objects:
        if isinstance(obj, (Planet, Moon)):
            habitable_bodies.append(obj)

    if not habitable_bodies:
        game_state.ui.error_message(
            "No planets or moons found in the current system")
        return

    # Sort by habitability score (highest first)
    try:
        habitable_bodies.sort(key=lambda x: x.habitability_score, reverse=True)
    except AttributeError:
        # Fallback sorting by name if habitability_score not available
        habitable_bodies.sort(key=lambda x: x.name)

    # Display survey results
    game_state.ui.info_message(
        f"=== Habitability Survey: {solar_system.name} System ==="
    )

    for i, body in enumerate(habitable_bodies, 1):
        try:
            score = getattr(body, "habitability_score", 0)
            body_type = "Moon" if isinstance(body, Moon) else "Planet"
            distance = body.space_object.position.distance_to(
                player_ship.space_object.position
            )

            game_state.ui.info_message(
                f"{i}. {body.name} ({body_type}) - UHS: {score:.1f}, Distance: {distance:.3f} AU, ID: {body.space_object.id}"
            )
        except Exception as e:
            game_state.ui.error_message(
                f"Error analyzing {body.name}: {str(e)}")

    # Award experience for comprehensive survey
    xp_amount = len(habitable_bodies) * 15
    skill_results = process_skill_xp_from_activity(
        game_state, "scan", float(xp_amount) / 10.0
    )
    notify_skill_progress(game_state, skill_results)


# Register the commands
register_command(
    ["habitability", "hab"],
    habitability_command,
    [Argument("object_id_str", str, True)],
)

register_command(
    ["habitability_survey", "habsurvey"],
    habitability_survey_command,
    [],
)
