from typing import Optional
from src.classes.game import Game
from src.helpers import take_input
from .registry import Argument
from .base import register_command
from .travel import direct_travel_command

def scan_command(game_state: Game, num_objects: str) -> None:
    """Scan for objects in the system."""
    amount_of_objects: int = int(num_objects)
    game_state.ui.info_message(f"Scanning for {amount_of_objects} objects...")
    player_ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    
    # Get player character to apply trait effects
    player_character = game_state.get_player_character()
    effective_sensor_range = player_ship.sensor_range
    
    # Apply character's sensor range modifier if applicable
    if player_character and hasattr(player_character, "sensor_range_mod"):
        # Apply the trait modifier to the sensor range
        effective_sensor_range *= player_character.sensor_range_mod
        
        # Apply education skill bonus (0.5% per point above 5)
        if player_character.education > 5:
            education_bonus = 1 + ((player_character.education - 5) * 0.005)
            effective_sensor_range *= education_bonus
            
        # If Perceptive trait provides significant improvement, mention it
        if (player_character.positive_trait == "Perceptive" and 
            player_character.sensor_range_mod > 1.1):
            game_state.ui.success_message("Your perceptive nature enhances the scan results.")
    
    from contextlib import contextmanager

    @contextmanager
    def temporary_sensor_range(ship, new_range):
        original_range = ship.sensor_range
        ship.sensor_range = new_range
        try:
            yield
        finally:
            ship.sensor_range = original_range

    # Use the context manager to temporarily modify the ship's sensor range
    with temporary_sensor_range(player_ship, effective_sensor_range):
        objects = game_state.solar_system.scan_system_objects(
            player_ship.space_object.get_position(), amount_of_objects
        )
    
    for i in range(amount_of_objects):
        game_state.ui.info_message(
            f"{i}. {objects[i].to_string_short(player_ship.space_object.get_position())}"
        )

    game_state.ui.warn_message("Enter object to navigate to or -1 to abort:")
    input_response = take_input("Enter the number of the object to navigate to or -1 to abort: ")

    if input_response == "-1":
        return
    else:
        try:
            input_response_index = int(input_response)
        except ValueError:
            game_state.ui.error_message("Invalid input. Please enter a valid number.")
            return
        selected_object = objects[input_response_index]
        selected_object_position = selected_object.space_object.position
        direct_travel_command(
            game_state, str(selected_object_position.x), str(selected_object_position.y)
        )

def scan_field_command(game_state: Game) -> None:
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

# Register scan commands
register_command(
    ["scan", "sc"],
    scan_command,
    [Argument("num_objects", str, False)],
)

register_command(
    ["scan_field", "scf"],
    scan_field_command,
    [],
)