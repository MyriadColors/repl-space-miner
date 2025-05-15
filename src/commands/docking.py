from src.classes.game import Game
from src.classes.solar_system import SolarSystem
from src.classes.station import Station
from src.helpers import get_closest_station, euclidean_distance, vector_to_string
from .base import register_command


def command_dock(game_state: Game) -> None:
    """Handle docking with the nearest station."""
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    if player_ship.is_docked:
        game_state.ui.info_message("You are already docked.")
        return

    current_system: SolarSystem = game_state.get_current_solar_system()

    # Check if player is already at a station (i.e., position matches very closely)
    current_station_at_loc = None
    for station_obj in current_system.stations:
        if station_obj.space_object.position.distance_to(player_ship.space_object.position) < 0.001: 
            current_station_at_loc = station_obj
            break
    
    target_station = current_station_at_loc
    
    if target_station is None: # If not exactly at a station, find the closest one
        if not current_system.stations: # Check if there are any stations in the current system
             game_state.ui.error_message("There are no stations in the current system.")
             return
        target_station = get_closest_station(
            current_system.stations, 
            player_ship
        )

    if target_station is None:
        game_state.ui.error_message("There are no stations within range or in the system.")
        return

    if (
        target_station.space_object.position.distance_to(
            player_ship.space_object.position
        )
        > player_ship.interaction_radius
    ):
        game_state.ui.error_message(
            f"Station {target_station.name} is not within docking range (must be within {player_ship.interaction_radius} AUs)."
        )
        return

    on_dock_complete(game_state, station_to_dock=target_station)


def on_dock_complete(game_state: Game, station_to_dock: Station) -> None:
    """Handle post-docking actions."""
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    player_ship.dock_into_station(station_to_dock)
    game_state.ui.success_message(f"Docked with {station_to_dock.name}.")

    ores_available = station_to_dock.ores_available_to_string()
    if ores_available is not None:
        game_state.ui.info_message(ores_available)
    else:
        game_state.ui.warn_message("No ores available.")


def command_undock(game_state: Game) -> None:
    """Handle undocking from the current station."""
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    if not player_ship.is_docked:
        game_state.ui.error_message("You are not docked.")
        return

    player_ship.undock_from_station()
    game_state.ui.success_message("Undocked.")


# Register docking commands
register_command(
    ["dock", "do"],
    command_dock,
    [],
)

register_command(
    ["undock", "ud"],
    command_undock,
    [],
)
