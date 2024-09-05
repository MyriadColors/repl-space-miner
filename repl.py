import data
from data import OreCargo
from game import Game
from helpers import format_seconds, take_input, euclidean_distance, rnd_float, rnd_int
from ore import Ore
from ship import Ship
from station import Station
from pygame import Vector2

def display_welcome_message():
    """Displays the welcome message to the player."""
    print("Welcome to the Space Trader CLI game!")


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

def handle_sell_command(game):
    """Handles the sell command."""
    if not game.player_ship.is_docked:
        print("Cannot sell while not docked.")
        return

    station: Station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
    if station.ore_cargo_volume >= station.ore_capacity:
        print("Cannot sell because the station's ore cargo is full, look for another one.")
        return

    ores_sold: list[OreCargo] = []

    # Get the ores to sell
    # remember that player_ship.cargohold is a set
    for ore_cargo in game.player_ship.cargohold:
        if ore_cargo.quantity > 0:
            if ore_cargo.ore.id not in [ore.id for ore in station.ores_available]:
                print(f"Cannot sell {ore_cargo.ore.name} because it is not available.")
                continue

            if ore_cargo.ore.volume > station.ore_capacity - station.ore_cargo_volume:
                print(f"Cannot sell {ore_cargo.ore.name} because the station's ore cargo is full.")
                continue

            ores_sold.append(ore_cargo)
    if len(ores_sold) == 0:
        print("No ores to sell.")
        return

    # Debug print the orecargo
    for ore_cargo in ores_sold:
        print(ore_cargo.ore.to_string())

    ore_names: set[str] = {ore.ore.name for ore in ores_sold}
    total_value = sum([ore_sold.quantity * ore_sold.price for ore_sold in ores_sold])
    total_volume = sum([ore_sold.quantity * ore_sold.ore.volume for ore_sold in ores_sold])
    total_units = sum([ore_sold.quantity for ore_sold in ores_sold])
    print(f"Ores to be sold: {', '.join(ore_names)}")
    print(f"Total value: {total_value} credits")
    print(f"Total volume: {total_volume} m³")
    print(f"Total units: {total_units}")
    print("Are you sure you want to sell these ores? y/n")
    confirm = take_input(">> ")
    if confirm != "y":
        print("Sell cancelled.")
        return
    game.player_credits += total_value
    station.ore_cargo_volume += total_volume
    for player_ore_cargo in game.player_ship.cargohold:
        if player_ore_cargo.ore.id in [ore.ore.id for ore in ores_sold]:
            player_ore_cargo.quantity -= total_units
    game.player_ship.cargohold = [cargo for cargo in game.player_ship.cargohold if cargo.quantity > 0]
    game.player_ship.calculate_volume_occupied(True)

    print(f"Sold {total_units} units of {', '.join(ore_names)} for {total_value} credits.")

def handle_buy_command(game: Game, args: list[str]):
    if not game.player_ship.is_docked:
        print("Cannot buy while not docked.")
        return
    if len(args) != 2:
        print("Invalid arguments. Please enter an ore name and amount to buy.")
        return

    ore_name = args[0].capitalize()
    try:
        amount = int(args[1])
    except ValueError:
        print("Invalid amount. Please enter a valid number.")
        return
    bartering_flag = False
    try:
        station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
        ore_exists, ore_cargo = station.get_ore_by_name(ore_name)
        if not ore_exists:
            print(f"Cannot buy {ore_name} because it is not available.")
            return

        total_volume = ore_cargo.ore.volume * amount
        volume_of_ore_available = ore_cargo.quantity * ore_cargo.ore.volume
        price = ore_cargo.price * amount
        print(f"Price for {amount} {ore_name}: {price} credits")
        print("Want to barter for a discount? y/n")
        confirm = take_input(">> ")
        if confirm == "y":
            bartering_flag = True
            rng_number: float = rnd_float(0, 1)
            if rng_number < 0.5:
                discount = rnd_int(10, 25)
                price = price * (100 - discount) / 100
                print(f"Bartered for {discount}% of the price.")
                print(f"New price: {price} credits")
                if price > game.player_credits:
                    print("You still don't have enough credits.")
                    return
            else:
                print("Bartering was unsuccessful.")
        if price > game.player_credits:
            print(f"Cannot buy {amount} {ore_name} because you don't have enough credits.")
            if not bartering_flag:
                print(f"Want to barter? y/n")
                confirm = take_input(">> ")
                if confirm == "y":
                    rng_number: float = rnd_float(0, 1)
                    if rng_number < 0.5:
                        discount = rnd_int(10, 25)
                        price = price * (100 - discount) / 100
                        print(f"Bartered for {discount}% of the price.")
                        print(f"New price: {price} credits")
                        if price > game.player_credits:
                            print("You still don't have enough credits.")
                            return
                    else:
                        print("Bartering was unsucessful.")
                else:
                    print("Buy cancelled.")
                    return
            else:
                rng_number: float = rnd_float(0, 1)
                if rng_number < 0.5:
                    discount = rnd_int(10, 25)
                    price = price * (100 - discount) / 100
                    print(f"Bartered for {discount}% of the price.")
                    print(f"New price: {price} credits")
                    if price > game.player_credits:
                        print("You still don't have enough credits.")
                        return
        if total_volume > volume_of_ore_available:
            print(f"Cannot buy {amount} {ore_name} because the station's doesn't have enough ore in its cargo.")
            print("Do you want to buy all available ore? y/n")
            confirm = take_input(">> ")
            if confirm == "y":
                amount = int(volume_of_ore_available / ore_cargo.ore.volume)
            else:
                print("Buy cancelled.")
                return

        ore_cargo.quantity -= amount
        ore_exists, ore_cargo_found = game.player_ship.get_ore_cargo_by_id(ore_cargo.ore.id)
        if ore_exists:
            print("Found roe, adding")
            ore_cargo_found.quantity += amount
        else:
            print("Did not found ore, appending")
            game.player_ship.cargohold.append(OreCargo(ore_cargo.ore, amount, ore_cargo.price))
        game.player_ship.cargohold = [cargo for cargo in game.player_ship.cargohold if cargo.quantity > 0]
        game.player_ship.calculate_volume_occupied(True)
        game.player_credits -= price
        print(f"Report: {amount} {ore_name} bought for {price} credits.")
    except ValueError:
        print("Invalid amount. Please enter a valid number.")

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
            if solar_system.is_object_within_an_asteroid_field_radius(player_ship.position):
                closest_field = get_closest_field(solar_system, player_ship.position, True)
            else:
                closest_field = get_closest_field(solar_system, player_ship.position)
            time = player_ship.travel(closest_field.position, time)
        elif object_type in ['station', 's']:
            if solar_system.get_object_within_interaction_radius(player_ship) is None:
                closest_station: Station = get_closest_station(solar_system, player_ship)
            else:
                closest_station: Station = get_closest_station(solar_system, player_ship, True)
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
            time = player_ship.travel(Vector2(x, y), time)

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
        time_to_mine = int(args[0])
        asteroid_field = solar_system.get_field_by_position(player_ship.position)
        time_spent = player_ship.mine_belt(asteroid_field, time_to_mine)
        global_time += time_spent
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
    print("  add (a) <quantity> <ore_type>: Adds an arbitrary amount of some ore to your cargohold.")
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

# TODO: This is broken, dunno why, investigate later.
def handle_add_ore_command(player_ship: Ship, args):
    """Handles the add ore command."""
    if len(args) != 2:
        print(
            "Invalid arguments. Please enter the amount of ore you wish to add and the name of the ore."
        )
        return
    ore_amount = int(args[0])
    if ore_amount < 0:
        print("Invalid amount. Please enter a positive number.")
        return
    ore_name = args[1]
    ore_selected: Ore
    for ore in data.ORES:
        if ore_name == ore.get_name().lower():
            ore_selected = ore
            break
    else:
        print("Invalid ore name. Please enter a valid ore name.")
        return

    if ore.volume * ore_amount > player_ship.cargohold_capacity:
        print("You are trying to add more ore than your ship can hold, since this is a cheat/debug command I will allow it.")
    for _ in range(ore_amount):
        existing_ore_cargo = next((cargo for cargo in player_ship.cargohold if cargo.ore == ore_selected), None)
        if existing_ore_cargo:
            existing_ore_cargo.quantity += ore_amount
        else:
            ore_cargo = OreCargo(ore_selected, ore_amount, ore.base_value)
            player_ship.cargohold.append(ore_cargo)


    print(f"{ore_amount} of {ore_name} added to cargohold.")

def handle_add_creds_command(game, args):
    """Handles the add credits command."""
    if len(args) != 1:
        print("Invalid arguments. Please enter the amount of credits you wish to add.")
        return
    amount = int(args[0])
    if amount < 0:
        print("You have entered a negative number, this means you are in debt.")
        print("Are you sure? (y/n)")
        confirm = take_input(">> ").strip()
        if confirm != "y":
            return
    game.player_credits += amount
    print(f"{amount} credits added to your credits.")

def handle_upgrade_command(game: Game, args):
    """Handles the upgrade command."""
    if len(args) != 1:
        print("Invalid arguments. Please enter the ship stat you wish to upgrade or 'help' to see available upgrades.")
        print("Available stats: speed, mining_speed, cargo_capacity")
        print("Costs: 5000, 10000, 7500")
        return

    if not game.player_ship.is_docked:
        print("You must be docked to upgrade your ship.")
        return
    if args[0] == "list":
        print("Available stats: speed (price 5000), mining_speed (price: 10000), cargo_capacity (price: 7500)")
        return

    if args[0] == "speed":
        if game.player_credits < 5000:
            print("You do not have enough credits to upgrade this stat.")
            return
        old_stat = game.player_ship.speed
        game.player_ship.speed = round(old_stat * 1.1, 2)
        game.player_credits -= 5000
        print(f"Upgraded from {old_stat} to {game.player_ship.speed}AU³/s for 5000 credits.")
    elif args[0] == "mining_speed":
        if game.player_credits < 10000:
            print("You do not have enough credits to upgrade this stat.")
            return
        old_stat = game.player_ship.mining_speed
        game.player_ship.mining_speed = round(old_stat * 1.1, 2)
        game.player_credits -= 10000
        print(f"Upgraded from {old_stat} to {game.player_ship.mining_speed}m³/s for 10000 credits.")
    elif args[0] == "cargo_capacity":
        if game.player_credits < 7500:
            print("You do not have enough credits to upgrade this stat.")
            return
        old_stat = game.player_ship.cargohold_capacity
        game.player_ship.cargohold_capacity = round(old_stat * 1.1, 2)
        game.player_credits -= 7500
        print(f"Upgraded from {old_stat} to {game.player_ship.cargohold_capacity}m³ for 7500 credits.")
    else:
        print("Invalid argument. Please enter the ship stat you wish to upgrade or 'help' to see available upgrades.")

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
            handle_sell_command(game)
        elif cmd in ['buy', 'b']:
            handle_buy_command(game, args)
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
        elif cmd in ['up', 'upgrade']:
            handle_upgrade_command(game, args)
        elif cmd in ['ao', 'add_ore']:
            print("Sorry, this command is broken, try again next update.")
            # handle_add_ore_command(game.player_ship, args)
        elif cmd in['ac', 'add_creds']:
            handle_add_creds_command(game, args)
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
