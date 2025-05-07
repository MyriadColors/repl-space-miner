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