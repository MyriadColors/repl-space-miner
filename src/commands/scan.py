from src.classes.game import Game
from src.classes.solar_system import SolarSystem
from src.helpers import take_input
from src.events.skill_events import process_skill_xp_from_activity, notify_skill_progress
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

    # Get all objects from the scan - now get them directly without sensor range filtering
    objects = game_state.get_current_solar_system().scan_system_objects(
        player_ship.space_object.get_position(), amount_of_objects
    )
    
    # Check if any objects were found
    if not objects:
        game_state.ui.warn_message("No objects detected within sensor range.")
        return
        
    # Only iterate through the actual number of objects found
    for i in range(min(amount_of_objects, len(objects))):
        game_state.ui.info_message(
            f"{i}. {objects[i].to_string_short(player_ship.space_object.get_position())}"
        )
        
    # Process skill experience from scanning
    if game_state.player_character:
        # Scanning gives education and engineering XP
        skill_results = process_skill_xp_from_activity(
            game_state, 
            "scan", 
            difficulty=min(2.0, amount_of_objects/5)  # More objects = more difficult scan
        )
        notify_skill_progress(game_state, skill_results)
    
    # Only proceed with selection if objects were found
    if objects:
        game_state.ui.warn_message("Enter object to navigate to or -1 to abort:")
        input_response = take_input(
            "Enter the number of the object to navigate to or -1 to abort: "
        )

        if input_response == "-1":
            return
        else:
            try:
                input_response_index = int(input_response)
                
                # Validate the index is within bounds
                if input_response_index < 0 or input_response_index >= len(objects):
                    game_state.ui.error_message(f"Invalid selection. Please choose a number between 0 and {len(objects) - 1}.")
                    return
                    
                selected_object = objects[input_response_index]
                selected_object_position = selected_object.space_object.position
                direct_travel_command(
                    game_state, str(selected_object_position.x), str(selected_object_position.y)
                )
            except ValueError:
                game_state.ui.error_message("Invalid input. Please enter a valid number.")
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
    if game_state.player_character:        # Calculate difficulty based on variety of ores and field properties
        ore_variety = len(field.ores_available) / 5  # Higher variety = higher difficulty
        asteroid_quantity = field.asteroid_quantity / 50  # More asteroids = higher difficulty
        base_difficulty = min(2.0, max(1.0, (ore_variety + asteroid_quantity) / 2))
        
        # Apply rarity modifier - rarer fields are more complex to analyze
        final_difficulty = base_difficulty * field.rarity_score * 0.7

        # Check if the player has enough energy to scan
        energy_cost = 10  # Example energy cost
        if player_ship.power < energy_cost: # MODIFIED: Check ship's power
            game_state.ui.warn_message("Not enough ship power to perform scan.") # MODIFIED: Message reflects ship power
            return

        # Deduct energy cost
        player_ship.power -= energy_cost # MODIFIED: Deduct from ship's power

        skill_results = process_skill_xp_from_activity(
            game_state, 
            "scan", 
            difficulty=final_difficulty
        )
        notify_skill_progress(game_state, skill_results)


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
