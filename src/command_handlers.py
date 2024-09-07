from pygame import Vector2

from src import data
from src.data import OreCargo
from src.classes.game import Game
from src.helpers import take_input, rnd_float, rnd_int, get_closest_field, get_closest_station, euclidean_distance, \
    prompt_for_closest_travel_choice, format_seconds
from src.classes.ore import Ore
from src.classes.ship import Ship
from src.classes.station import Station


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


def barter(original_price: float) -> (bool, float, float):
    """Returns the price of an item after being bartered."""
    rng_number: float = rnd_float(0, 1)
    if rng_number < 0.5:
        discount = rnd_int(10, 25)
        new_price = original_price * (100 - discount) / 100

        return True, discount, new_price
    else:
        return False, 0.0, original_price


def handle_bartering(price: float) -> tuple[float, bool]:
    """Handle the bartering process, returns new price and bartering flag."""
    bartering_flag = False
    print("Want to barter for a discount? y/n")
    confirm = take_input(">> ")
    if confirm == "y":
        bartering_flag = True
        result, discount, new_price = barter(price)
        if result:
            price = new_price
            print(f"Bartered for {discount}% of the price.")
            print(f"New price: {price} credits")
        else:
            print("Bartering failed.")
    return price, bartering_flag


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

    try:
        station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
        ore_exists, ore_cargo = station.get_ore_by_name(ore_name)
        if not ore_exists:
            print(f"Cannot buy {ore_name} because it is not available.")
            return

        total_volume = round(ore_cargo.ore.volume * amount, 2)
        volume_of_ore_available = round(ore_cargo.quantity * ore_cargo.ore.volume, 2)
        price = round(ore_cargo.price * amount, 2)

        print(f"Price for {amount} {ore_name}: {price} credits")

        # Handle bartering logic
        price, bartering_flag = handle_bartering(price)

        if price > game.player_credits:
            print(f"Cannot buy {amount} {ore_name} because you don't have enough credits.")
            return

        if total_volume > volume_of_ore_available:
            print(f"Cannot buy {amount} {ore_name} because the station doesn't have enough ore in its cargo.")
            confirm = take_input("Do you want to buy all available ore? y/n >> ")
            if confirm == "y":
                amount = int(volume_of_ore_available / ore_cargo.ore.volume)
            else:
                print("Buy cancelled.")
                return

        # Update ore quantities in the station and player's ship
        update_ore_quantities(game, ore_cargo, ore_name, amount, price, station)

    except ValueError:
        print("Invalid amount. Please enter a valid number.")
        return


def update_ore_quantities(game: Game, ore_cargo: OreCargo, ore_name: str, amount: int, price: float, station: Station):
    """Updates the quantities of ore in both the station and the player's ship."""
    ore_cargo.quantity -= amount
    ore_exists, ore_cargo_found = game.player_ship.get_ore_cargo_by_id(ore_cargo.ore.id)

    if ore_exists:
        ore_cargo_found.quantity += amount
    else:
        game.player_ship.cargohold.append(OreCargo(ore_cargo.ore, amount, ore_cargo.price))

    # Remove empty cargo entries and recalculate volume
    game.player_ship.cargohold = [cargo for cargo in game.player_ship.cargohold if cargo.quantity > 0]
    game.player_ship.calculate_volume_occupied(True)
    game.player_credits -= price

    # Update station
    station.ore_cargo_volume -= round(amount * ore_cargo.ore.volume, 2)


    # Reporting
    print(f"Report: {amount} {ore_name} bought for {price} credits.")
    print(f"Station Ore Report:\n{station.ore_cargo_volume} tons of {ore_name} ore")


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

    # Handle 'closest' command
    if args[0] in ['closest', 'c']:
        time = handle_closest_travel(player_ship, solar_system, args, time)

    # Handle direct coordinates
    elif len(args) == 2:
        time = handle_direct_travel(player_ship, solar_system, args, time)

    else:
        print("You need to enter the coordinate (x y) or use 'closest' to go to the closest object available.")

    return time


def handle_closest_travel(player_ship: Ship, solar_system, args, time):
    """Handles travel to the closest field or station."""

    object_type = args[1] if len(args) == 2 else None

    # Get closest field and station
    closest_field = get_closest_field(solar_system, player_ship.space_object.get_position(),
                                      solar_system.is_object_within_an_asteroid_field_radius(player_ship.space_object.get_position()) is not None)
    closest_station = get_closest_station(solar_system, player_ship,
                                          solar_system.get_object_within_interaction_radius(player_ship) is not None)

    if not object_type:
        # Ask user for input to choose between field or station
        print(
            f"Closest field is Field {closest_field.id} at {euclidean_distance(player_ship.space_object.get_position(), closest_field.position)} AUs from here.")
        print(
            f"Closest station is Station {closest_station.id} at {euclidean_distance(player_ship.space_object.get_position(), closest_station.position)} AUs from here.")
        time = prompt_for_closest_travel_choice(player_ship, closest_field, closest_station, time)

    elif object_type in ['field', 'f']:
        time = player_ship.travel(closest_field.position, time)

    elif object_type in ['station', 's']:
        time = player_ship.travel(closest_station.position, time)

    else:
        print("Invalid object type. Use 'field' or 'station'.")

    return time


def handle_direct_travel(player_ship: Ship, solar_system, args, time):
    """Handles direct coordinate travel."""

    try:
        x, y = float(args[0]), float(args[1])
    except ValueError:
        print("Invalid coordinates. Please enter valid numbers.")
        return time

    if x >= solar_system.size or y >= solar_system.size:
        print("Invalid coordinates. Please enter coordinates within the solar system.")
    else:
        time = player_ship.travel(Vector2(x, y), time)

    return time


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
    print("  add_ore (ao) <quantity> <ore_type>: Adds an arbitrary amount of some ore to your cargohold.")
    print("  add_credits (ac) <quantity>: Adds an arbitrary amount of credits to your account.")
    print("  buy <ore_type> <quantity>: Purchase some ore from the station you are docked in.")
    print("  sell <ore_type>: Sell some ore to the station you are docked in.")
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

# TODO: Fix upgrades
def handle_upgrade_command(game: Game, args):
    """Handles the upgrade command."""

    prices = {
        "speed": data.upgrade_data["speed"]["price"],
        "mining_speed": data.upgrade_data["mining_speed"]["price"],
        "cargo_capacity": data.upgrade_data["cargo_capacity"]["price"],
        "fuel_consumption": data.upgrade_data["fuel_consumption"]["price"],
        "fuel_capacity": data.upgrade_data["fuel_capacity"]["price"],
    }

    upgrade_string = "\n".join([f"{key}: {value}" for key, value in prices.items()])

    if len(args) != 1:
        print("Invalid arguments. Please enter the ship stat you wish to upgrade or 'help' to see available upgrades.")
        print(upgrade_string)
        return

    if not game.player_ship.is_docked:
        print("You must be docked to upgrade your ship.")
        return

    if args[0] == "speed":
        price = data.upgrade_data["speed"]["price"]
        if game.player_credits < price:
            print(f"You do not have enough credits to upgrade this stat: need {price}")
            return
        multiplier = data.upgrade_data["speed"]["multiplier"]
        old_stat = game.player_ship.moves.get_speed()
        game.player_ship.moves.set_speed(round(old_stat * multiplier, 4))
        game.player_credits -= price
        print(f"Upgraded from {old_stat} to {game.player_ship.moves.get_speed()}AU³/s for 5000 credits.")
    elif args[0] == "mining_speed":
        price = data.upgrade_data["mining_speed"]["price"]
        if game.player_credits < price:
            print(f"You do not have enough credits to upgrade this stat: need {price}")
            return
        multiplier = data.upgrade_data["mining_speed"]["multiplier"]
        old_stat = game.player_ship.mining_speed
        game.player_ship.mining_speed = round(old_stat * multiplier, 5)
        game.player_credits -= price
        print(f"Upgraded from {old_stat} to {game.player_ship.mining_speed}AU³/s for 10000 credits.")
    elif args[0] == "cargo_capacity":
        price = data.upgrade_data["cargo_capacity"]["price"]
        if game.player_credits < price:
            print(f"You do not have enough credits to upgrade this stat: need {price}")
            return
        multiplier = data.upgrade_data["cargo_capacity"]["multiplier"]
        old_stat = game.player_ship.cargohold_capacity
        game.player_ship.cargohold_capacity = round(old_stat * multiplier, 2)
        game.player_credits -= price
        print(f"Upgraded from {old_stat} to {game.player_ship.cargohold_capacity}m3 for {price} credits.")
    elif args[0] == "fuel_consumption":
        price = data.upgrade_data["fuel_consumption"]["price"]
        if game.player_credits < price:
            print(f"You do not have enough credits to upgrade this stat: need {price}")
            return
        multiplier = data.upgrade_data["fuel_consumption"]["multiplier"]
        old_stat = game.player_ship.fuel_consumption
        game.player_ship.fuel_consumption = round(old_stat * multiplier, 2)
        game.player_credits -= price
        print(f"Upgraded from {old_stat} to {game.player_ship.fuel_consumption}m3/AU for {price} credits.")
    elif args[0] == "fuel_capacity":
        price = data.upgrade_data["fuel_capacity"]["price"]
        if game.player_credits < price:
            print(f"You do not have enough credits to upgrade this stat: need {price}")
            return
        multiplier = data.upgrade_data["fuel_capacity"]["multiplier"]
        old_stat = game.player_ship.max_fuel
        game.player_ship.max_fuel = round(old_stat * multiplier, 2)
        game.player_credits -= price
        print(f"Upgraded from {old_stat} to {game.player_ship.max_fuel}m3 for {price} credits.")
    elif args[0] == "help":
        print(upgrade_string)
    else:
        print("Invalid argument. Please enter the ship stat you wish to upgrade or 'help' to see available upgrades.")


def display_welcome_message():
    """Displays the welcome message to the player."""
    print("Welcome to the Space Trader CLI game!")


def display_time_and_status(time, player_ship):
    """Displays the current time and the player's ship status."""
    print(f"Time: {format_seconds(time)}s")
    print(player_ship.status_to_string())
