from helpers import format_seconds, take_input, euclidean_distance
from ore import Ore
from ship import Ship
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
    if not player_ship.is_docked:
        print("Cannot refuel while not docked.")
        return
    if len(args) != 1:
        print("Invalid arguments. Please enter the amount of fuel to add.")
        return
    try:
        amount = float(args[0])
        station = game.solar_system.get_object_within_interaction_radius(player_ship)
        if amount <= 0:
            print("Invalid amount. Please enter a positive number.")
            return

        if player_ship.fuel + amount > player_ship.max_fuel:
            print(
                "Cannot refuel more than your ship's maximum fuel capacity, consider upgrading your ship."
            )
            return
        price = amount * station.fuel_price
        print(f"Total price for {round(amount, 2)}m³ of fuel: {round(price, 2)} credits.")
        print("Are you sure you want to refuel? y/n")
        confirm = take_input(">> ")
        if confirm != "y":
            print("Refuel cancelled.")
            return
        player_ship.refuel(amount)
        game.player_credits -= price
        print(f"Refueled with {round(amount, 2)} m3 for {round(price, 2)} credits.")
    except ValueError:
        print("Invalid amount. Please enter a valid number.")

def handle_sell_command(player_ship: Ship, game):
    """Handles the sell command."""
    if not player_ship.is_docked:
        print("Cannot sell while not docked.")
        return

    station: Station = game.solar_system.get_object_within_interaction_radius(player_ship)
    if station.ore_cargo_volume == station.ore_capacity:
        print("Cannot sell because the station's ore cargo is full, look for another one.")
        return
    ores_to_sell: list[Ore] = []
    ores_which_cannot_sell: set[Ore] = set()
    for i, ore in enumerate(player_ship.cargohold):
        if station.is_ore_available(ore):
            print(f"Ore {i + 1}: {ore.name} ({ore.volume}m³) for {ore.base_value} credits.")
            ores_to_sell.append(ore)
        else:
            ores_which_cannot_sell.add(ore)

    if len(ores_to_sell) > 0:
        total_ore_volume = 0.0
        total_ore_price = 0.0
        ore_names = []

        for i, ore in enumerate(ores_to_sell):
            total_ore_volume += ore.volume
            # ore_price = station.get_ore_price(ore.name)
            # I have no idea how this can happen, but it's there for sanity checking in case im hallucinating
            # if ore_price is None:
            #     print("Something went wrong, please contact the developer's psychiatrist.")
            #     ores_which_cannot_sell.add(ore)
            total_ore_price += ore.base_value
            ore_names.append(ore.name)

        print(f"You can sell {round(total_ore_volume, 2)}m³ of ores for {round(total_ore_price, 2)} credits.")
        print("Confirm? y/n")
        confirm = take_input(">> ")

        if confirm != "y":
            print("Sell cancelled.")
            return

        for ore in ores_to_sell:
            player_ship.cargohold.remove(ore)
            station.ore_cargo[ore] = ore.volume
            player_ship.calculate_volume_occupied()
            station.calculate_cargo()

        game.player_credits += total_ore_price

        print(f"Sold {round(total_ore_volume, 2)}m³ of ores for {round(total_ore_price, 2)} credits.")
        return
    print(f"You cannot sell: ")
    for ore in set(ores_which_cannot_sell):
        print(ore.name)
    print("Because the station doesnt buy them.")
    return


def handle_travel_command(player_ship: Ship, solar_system, args, time):
    """Handles the travel command."""
    if player_ship.is_docked:
        print("Cannot travel while docked.")
        return time
    if len(args) < 1 or len(args) > 2:
        print("Invalid arguments. Please enter coordinates or use 'closest'.")
        return time
    if player_ship.fuel == 0:
        print("Cannot travel while out of fuel.")
        return time

    if len(args) == 1 and args[0] in ['closest', 'c']:
        if solar_system.is_object_within_an_asteroid_field_radius(player_ship.position):
            closest_field = get_closest_field(solar_system, player_ship.position, True)
        else:
            closest_field = get_closest_field(solar_system, player_ship.position, False)
        if solar_system.get_object_within_interaction_radius(player_ship) is None:
            closest_station: Station = get_closest_station(solar_system, player_ship)
        else:
            closest_station: Station = get_closest_station(solar_system, player_ship, True)
        print(f"Closest field is Field {closest_field.id} at {euclidean_distance(player_ship.position, closest_field.position)} AUs from here.")
        print(f"Closest station is Station {closest_station.id} at {euclidean_distance(player_ship.position, closest_station.position)} AUs from here.")
        print("Do you wish to go to the closest 1. (f)ield or the closest 2. (s)tation?")
        tries = 3
        while tries > 0:
            response = take_input(">> ")
            if response in ["1", "f", "field"]:
                time = player_ship.travel(closest_field.position, time)
                break
            elif response in ["2", "s", "station"]:
                time = player_ship.travel(closest_station.position, time)
                break
            elif tries > 0:
                print("Invalid response.")
                tries -= 1
            else:
                print("Too many tries. Aborting.")

    elif len(args) == 2 and args[0] in ['closest', 'c']:
        object_type = args[1]
        if object_type in ['field', 'f']:
            closest_field = get_closest_field(solar_system, player_ship.position)
            time = player_ship.travel(closest_field.position, time)
        elif object_type in ['station', 's']:
            closest_station = get_closest_station(solar_system, player_ship)
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

def get_closest_field(solar_system, position, is_at_field=False):
    if is_at_field:
        return solar_system.sort_fields('asc', 'distance', position)[1]
    closest_field = solar_system.sort_fields('asc', 'distance', position)[0]
    return closest_field

def get_closest_station(solar_system, player_ship, is_at_station=False):
    if is_at_station:
        return solar_system.sort_stations('asc', 'distance', player_ship.position)[1]
    return solar_system.sort_stations('asc', 'distance', player_ship.position)[0]


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
    print("  move or travel (m, t) <x> <y> or <closest> <object>:" +
          " Move the ship to the given coordinates or" +
          " 'closest' to travel to the closest asteroid field (f) or station (s).")
    print(
        "  mine (mi) <time>: Mine for the specified time at the nearest asteroid field."
    )
    print("  status (st): Display the current status of the ship.")
    print("  scan <amount>: Scan for the specified amount of objects and travel to one of them if you wish to.")
    print("  dock (do): Dock with the nearest station.")
    print("  undock (ud): Undock from the nearest station.")
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
        try:
            input_response = int(input_response)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return
        selected_object = objects[input_response]
        game.global_time = handle_travel_command(player_ship, game.solar_system, [selected_object.position.x, selected_object.position.y], game.global_time)

def handle_docking_command(player_ship, game):
    """Handles the docking command."""
    station_to_dock: Station = game.solar_system.get_object_within_interaction_radius(player_ship)
    if station_to_dock is None:
        print("No station found within range.")
    else:
        player_ship.dock_into_station(station_to_dock)
        print(f"Docked at {station_to_dock.name}.")
        print(f"This station has: ")
        print(station_to_dock.ores_available_to_string())

def handle_undocking_command(player_ship):
    """Handles the undocking command."""
    player_ship.undock_from_station()
    print("Undocked.")

def start_repl(game):
    display_help()
    while True:

        input_cmd = take_input(">> ").strip().lower().split()
        if len(input_cmd) == 0:
            print("Invalid command. Please enter a valid command.")
            continue
        cmd = input_cmd[0]
        args = input_cmd[1:]

        if cmd in ('q', 'quit'):
            break
        elif cmd in ['refuel', 'r']:
            handle_refuel_command(game.player_ship, game, args)
        elif cmd in ['sell', 's']:
            print("sell command")
            handle_sell_command(game.player_ship, game)
        elif cmd in ('move', 'travel', 'mo', 't'):
            game.global_time = handle_travel_command(game.player_ship,
                                                     game.solar_system, args,
                                                     game.global_time)
        elif cmd in ['mine', 'mi']:
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
            handle_undocking_command(game.player_ship)
        elif cmd in ["reset_name", 'rn']:
            new_name = take_input("Enter new name").strip()
            if len(new_name) == 0:
                print("Invalid name. Please enter a valid name.")
                continue
            game.player_ship.set_ship_name(new_name)
        elif cmd == 'help':
            display_help()
        else:
            print(
                "Unknown command. Type 'help' to see the list of available commands."
            )
