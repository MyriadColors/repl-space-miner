from helpers import format_seconds, take_input, euclidean_distance
from station import Station
from vector2d import Vector2d


def display_welcome_message():
    """Displays the welcome message to the player."""
    print("Welcome to the spaceship simulator!")


def display_time_and_status(time, player_ship):
    """Displays the current time and the player's ship status."""
    print(f"Time: {format_seconds(time)}s")
    print(player_ship.status_to_string())


def handle_refuel_command(player_ship, game, args):
    """Handles the refuel command."""
    if len(args) != 1:
        print("Invalid arguments. Please enter the amount of fuel to add.")
        return
    try:
        amount = float(args[0])
        if amount <= 0:
            print("Invalid amount. Please enter a positive number.")
            return

        if player_ship.fuel + amount > player_ship.max_fuel:
            print(
                "Cannot refuel more than your ship's maximum fuel capacity, consider upgrading your ship."
            )
            return

        price = amount * 15
        player_ship.refuel(amount)
        game.player_credits -= price
        print(f"Refueled with {amount} m3 for {price} credits.")
    except ValueError:
        print("Invalid amount. Please enter a valid number.")


def handle_travel_command(player_ship, solar_system, args, time):
    """Handles the travel command."""
    if player_ship.is_docked:
        print("Cannot travel while docked.")
        return time
    if len(args) < 1 or len(args) > 2:
        print("Invalid arguments. Please enter coordinates or use 'closest'.")
        return time

    if len(args) == 1 and args[0] == "closest":
        closest_field = get_closest_field(solar_system, player_ship.position)
        closest_station: Station = get_closest_station(solar_system, player_ship)
        print(f"Closest field is {closest_field.id} at {euclidean_distance(player_ship.position, closest_field.position)} AUs from here.")
        print("Do you wish to go to the closest field or the closest station?")
        response = take_input(">> ")
        if response == "field":
            time = player_ship.travel(closest_field.position, time)
        else:
            time = player_ship.travel(closest_station.position, time)
    elif len(args) == 1:
        print("You need to enter the coordinate (x y) or use 'closest' to go to the closest object available.")
    else:
        try:
            x = float(args[0])
            y = float(args[1])
        except ValueError:
            print("Invalid coordinates. Please enter valid numbers.")
            return time

        if x >= solar_system.size or y >= solar_system.size:
            print("Invalid coordinates. Please enter coordinates within the solar system.")
        else:
            time = player_ship.travel(Vector2d(x, y), time)

    return time

def get_closest_field(solar_system, position):
    closest_field = solar_system.sort_fields('asc', 'distance', position)[0]
    return closest_field

def get_closest_station(solar_system, player_ship ):
    closest_station: Station = solar_system.sort_stations('asc', 'distance', 'all', player_ship.position)[0]
    return closest_station


def handle_mine_command(player_ship, solar_system, args, global_time):
    """Handles the mine command."""
    if len(args) != 1:
        print(
            "Invalid arguments. Please enter the time to mine in seconds as an argument."
        )
        return global_time

    if not solar_system.is_object_within_an_asteroid_field_radius(
            player_ship.position):
        print("You must be within an asteroid field to mine.")
        return global_time

    try:
        time_to_mine = float(args[0])
        global_time += time_to_mine
        asteroid_field = solar_system.get_field_by_position(
            player_ship.position)
        print(player_ship.mine_belt(asteroid_field, time_to_mine))
        return global_time
    except ValueError:
        print("Invalid time. Please enter a valid number.")

def display_help():
    """Displays the help message."""
    print("Available commands:")
    print("  q, quit: Quit the game.")
    print("  refuel <amount>: Refuel the ship with the given amount.")
    print("  move or travel <x> <y> or 'closest':" +
          " Move the ship to the given coordinates or" +
          " 'closest' to travel to the closest asteroid.")
    print(
        "  mine <time>: Mine for the specified time at the nearest asteroid field."
    )
    print("  status: Display the current status of the ship.")
    print("  scan <amount>: Scan for the specified amount of objects and travel to one of them if you wish to.")
    print("  help: Display this help message.")





def handle_scan_command(player_ship, game, args):
    """Handles the scan command."""
    if len(args) != 1:
        print(
            "Invalid arguments. Please enter the number of objects you wish to scan for."
        )
        return

    amount_of_objects = int(args[0])
    print(f"Amount : {amount_of_objects}")
    objects = game.solar_system.scan_system_objects(player_ship.position, amount_of_objects)
    for i in range(amount_of_objects):
        print(f"{i}. {objects[i].to_string_short(player_ship.position)}")

    print(f"Enter object to navigate to or -1 to abort:")
    input_response = take_input(">> ").strip()

    if input_response == "-1":
        return
    else:
        selected_object = objects[int(input_response)]
        game.global_time = handle_travel_command(player_ship, game.solar_system, [selected_object.position.x, selected_object.position.y], game.global_time)

def handle_docking_command(player_ship, game):
    """Handles the docking command."""
    station_to_dock = game.solar_system.get_object_within_interaction_radius(player_ship)
    if station_to_dock is None:
        print("No station found within range.")
    else:
        player_ship.dock_into_station(station_to_dock)
        print(f"Docked at {station_to_dock.name}.")

def handle_undocking_command(player_ship, game):
    """Handles the undocking command."""
    player_ship.undock_from_station()
    print("Undocked.")

def start_repl(game):
    display_help()
    while True:

        input_cmd = take_input(">> ").strip().lower().split()
        cmd = input_cmd[0]
        args = input_cmd[1:]

        if cmd in ('q', 'quit'):
            break
        elif cmd in ['refuel', 'r']:
            handle_refuel_command(game.player_ship, game, args)
        elif cmd in ('move', 'travel', 'm', 't'):
            game.global_time = handle_travel_command(game.player_ship,
                                                     game.solar_system, args,
                                                     game.global_time)
        elif cmd in ['mine', 'm']:
            game.global_time = handle_mine_command(game.player_ship,
                                                   game.solar_system, args,
                                                   game.global_time)
        elif cmd in ['s', 'scan']:
            handle_scan_command(game.player_ship, game, args)
        elif cmd in ['st', 'status']:
            print(game.player_ship.status_to_string())
            print(f"Credits: {game.player_credits}")
            print(f"Time: {format_seconds(game.global_time)}s")
        elif cmd in ['do', 'dock']:
            handle_docking_command(game.player_ship, game)
        elif cmd in ['ud', 'undock']:
            handle_undocking_command(game.player_ship, game)
        elif cmd == 'help':
            display_help()
        else:
            print(
                "Unknown command. Type 'help' to see the list of available commands."
            )
