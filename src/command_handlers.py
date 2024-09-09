from typing import Tuple

from pygame import Vector2

from src import data
from src.classes.asteroid import AsteroidField
from src.classes.game import Game
from src.classes.ore import Ore
from src.classes.station import Station
from src.data import OreCargo
from src.helpers import take_input, rnd_float, rnd_int, get_closest_field, get_closest_station, euclidean_distance, \
    prompt_for_closest_travel_choice, format_seconds
from src.pygameterm import color_data
from src.pygameterm.terminal import PygameTerminal


def refuel_command(term: PygameTerminal, amount: float):
    """Handles the refuel command."""

    game: Game = term.app_state
    if not game.player_ship.is_docked:
        term.write("Cannot refuel while not docked.")
        return

    station = game.solar_system.get_object_within_interaction_radius(game)
    if amount <= 0:
        term.write("Invalid amount. Please enter a positive number.")
        return

    if game.player_ship.fuel + amount > game.player_ship.max_fuel:
        term.write(
            "Cannot refuel more than your ship's maximum fuel capacity, consider upgrading your ship."
        )
        return

    price = amount * station.fuel_price
    term.write(f"Total price for {round(amount, 2)}m³ of fuel: {round(price, 2)} credits.")
    term.write("Are you sure you want to refuel? y/n")
    confirm = take_input(">> ")
    if confirm.lower() != "y":
        term.write("Refuel cancelled.")
        return

    game.player_ship.refuel(amount)
    game.player_credits -= price
    term.write(f"Refueled with {round(amount, 2)} m3 for {round(price, 2)} credits.")


def barter(original_price: float) -> Tuple[bool, float, float]:
    """Returns the price of an item after being bartered."""
    rng_number: float = rnd_float(0, 1)
    if rng_number < 0.5:
        discount = rnd_int(10, 25)
        new_price = original_price * (100 - discount) / 100

        return True, discount, new_price
    else:
        return False, 0.0, original_price


def sell_command(term: PygameTerminal):
    """Handles the sell command."""
    game: Game = term.app_state
    if not game.player_ship.is_docked:
        term.write("Cannot sell while not docked.")
        print("Debug: Cannot sell while not docked.")
        return

    station: Station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
    if station.ore_cargo_volume >= station.ore_capacity:
        term.write("Cannot sell because the station's ore cargo is full, look for another one.")
        print("Debug: Cannot sell because the station's ore cargo is full, look for another one.")
        return

    ores_sold: list[OreCargo] = []

    # Get the ores to sell
    # remember that player_ship.cargohold is a set
    for ore_cargo in game.player_ship.cargohold:
        if ore_cargo.quantity > 0:
            if ore_cargo.ore.id not in [ore.id for ore in station.ores_available]:
                term.write(f"Cannot sell {ore_cargo.ore.name} because it is not available.", debug_flag=True)
                continue

            if ore_cargo.ore.volume > station.ore_capacity - station.ore_cargo_volume:
                term.write(f"Cannot sell {ore_cargo.ore.name} because the station's ore cargo is full.",
                           debug_flag=True)
                continue

            ores_sold.append(ore_cargo)
    if len(ores_sold) == 0:
        term.write("No ores to sell.", debug_flag=True)
        return
    for ore_cargo in ores_sold:
        term.write(ore_cargo.ore.to_string())

    ore_names: set[str] = {ore.ore.name for ore in ores_sold}
    total_value: float = 0.0
    for ore_sold in ores_sold:
        total_value += (ore_sold.quantity * ore_sold.price)
    total_volume = sum([ore_sold.quantity * ore_sold.ore.volume for ore_sold in ores_sold])
    total_units = sum([ore_sold.quantity for ore_sold in ores_sold])
    term.write(f"Ores to be sold: {', '.join(ore_names)}", debug_flag=True)
    term.write(f"Total value: {total_value} credits", debug_flag=True)
    term.write(f"Total volume: {total_volume} m³", debug_flag=True)
    term.write(f"Total units: {total_units}", debug_flag=True)
    confirm = term.prompt_user("Are you sure you want to sell these ores? y/n, debug_flag=True")
    if confirm != "y":
        term.write("Sell cancelled.", debug_flag=True)
        return
    game.player_credits = round(game.player_credits + total_value, 2)
    station.ore_cargo_volume += total_volume
    for player_ore_cargo in game.player_ship.cargohold:
        if player_ore_cargo.ore.id in [ore.ore.id for ore in ores_sold]:
            player_ore_cargo.quantity -= total_units
    game.player_ship.cargohold = [cargo for cargo in game.player_ship.cargohold if cargo.quantity > 0]
    game.player_ship.calculate_cargo_occupancy()

    term.write(f"Sold {total_units} units of {', '.join(ore_names)} for {total_value} credits.", debug_flag=True)


def buy_command(item_name: str, amount: str, term: PygameTerminal):
    game: Game = term.app_state
    station: Station | None = game.player_ship.get_docked_station()
    if not station:
        term.write("Must be docked to buy ore.")
        return

    try:
        ore_cargo: OreCargo | None = station.get_ore_by_name(item_name)
        if not ore_cargo:
            term.write(f"Cannot buy {item_name} because it is not available.")
            return

        amount_number = int(amount)
        total_volume: float = round(ore_cargo.ore.volume * amount_number, 2)
        volume_of_ore_available: float = round(ore_cargo.quantity * ore_cargo.ore.volume, 2)
        price: float = round(ore_cargo.price * amount_number, 2)

        term.write(f"Price for {amount} {item_name}: {price} credits")

        # Handle bartering logic
        price, bartering_flag = bartering(term, price)

        if price > game.player_credits:
            term.write(f"Cannot buy {amount} {item_name} because you don't have enough credits.")
            return

        if total_volume > volume_of_ore_available:
            term.write(f"Cannot buy {amount} {item_name} because the station doesn't have enough ore in its cargo.")
            confirm = term.prompt_user("Do you want to buy all available ore? y/n >> ")
            if confirm.lower() == "y":
                amount_number = int(volume_of_ore_available / ore_cargo.ore.volume)
                price = round(ore_cargo.price * amount_number, 2)
                term.write(f"Adjusting purchase to {amount_number} {item_name} for {price} credits.")
            else:
                term.write("Buy cancelled.")
                return

        # Update ore quantities in the station and player's ship
        update_ore_quantities(term, ore_cargo, item_name, amount_number, price, station)

    except ValueError:
        term.write("Invalid amount. Please enter a valid number.")
        return


def update_ore_quantities(term: PygameTerminal, ore_cargo: OreCargo, ore_name: str, amount: int, price: float,
                          station: Station):
    """Updates the quantities of ore in both the station and the player's ship."""
    game: Game = term.app_state

    # Ensure we don't buy more than available
    amount = min(amount, ore_cargo.quantity)

    ore_cargo.quantity -= amount
    ore_cargo_found = game.player_ship.get_ore_cargo_by_id(ore_cargo.ore.id)

    if ore_cargo_found:
        ore_cargo_found.quantity += amount
    else:
        game.player_ship.cargohold.append(OreCargo(ore_cargo.ore, amount, ore_cargo.price))

    # Remove empty cargo entries and recalculate volume
    game.player_ship.cargohold = [cargo for cargo in game.player_ship.cargohold if cargo.quantity > 0]
    game.player_ship.calculate_cargo_occupancy()
    game.player_credits -= price

    # Update station
    station.ore_cargo_volume -= round(amount * ore_cargo.ore.volume, 2)

    # Reporting
    term.write(f"Report: {amount} {ore_name} bought for {price} credits.")
    term.write(f"Station Ore Report:\n{station.ore_cargo_volume} tons of ore remaining")
    term.write(f"Your new credit balance: {game.player_credits} credits")


def bartering(term: PygameTerminal, price: float) -> tuple[float, bool]:
    """Handle the bartering process, returns new price and bartering flag."""
    bartering_flag = False
    confirm = term.prompt_user("Want to barter for a discount? y/n")
    if confirm.lower() == "y":
        bartering_flag = True
        result, discount, new_price = barter(price)
        if result:
            price = new_price
            term.write(f"Bartered for {discount}% discount off the original price.")
            term.write(f"New price: {price} credits")
        else:
            term.write("Bartering failed.")
    return price, bartering_flag


def travel_command(*args, term: PygameTerminal):
    """Handles the travel command."""
    game: Game = term.app_state
    global_time = game.global_time
    if game.player_ship.is_docked:
        term.write("Cannot travel while docked.")
        return global_time

    if game.player_ship.fuel == 0:
        term.write("Cannot travel while out of fuel.")
        return global_time

    # Handle 'closest' command
    if args[0] == "closest":
        global_time = closest_travel(term, args[1], global_time)
        return global_time
    else:
        term.write("Invalid argument. Please enter 'closest' to travel to the closest field or station.")


def closest_travel(term: PygameTerminal, object_type, time):
    """Handles travel to the closest field or station."""
    game: Game = term.app_state
    # Get the closest field and station
    closest_field: AsteroidField = get_closest_field(game.solar_system, game.player_ship.space_object.get_position(),
                                                     game.solar_system.is_object_within_an_asteroid_field_radius(
                                                         game.player_ship.space_object.get_position()) is not None)
    closest_station: Station = get_closest_station(game.solar_system, game.player_ship,
                                                   game.solar_system.get_object_within_interaction_radius(
                                                       game.player_ship) is not None)

    if not object_type:
        # Ask user for input to choose between field or station
        term.write(
            f"Closest field is Field {closest_field.id} at {euclidean_distance(game.player_ship.space_object.get_position(), closest_field.position)} AUs from here.")
        term.write(
            f"Closest station is Station {closest_station.id} at {euclidean_distance(game.player_ship.space_object.get_position(), closest_station.position)} AUs from here.")
        time = prompt_for_closest_travel_choice(game.player_ship, closest_field, closest_station, time)

    elif object_type in ['field', 'f']:
        field_position: Vector2 = closest_field.position
        time = term.app_state.player_ship.travel(term, field_position)

    elif object_type in ['station', 's']:
        station_position: Vector2 = closest_station.position
        time = term.app_state.player_ship.travel(term, station_position)
    else:
        term.write("Invalid object type. Use 'field' or 'station'.")

    return time


def direct_travel(args, term: PygameTerminal):
    """Handles direct coordinate travel."""
    game: Game = term.app_state
    x, y = args[0], args[1]
    try:
        x, y = float(args[0]), float(args[1])
    except ValueError:
        term.write("Invalid coordinates. Please enter valid numbers.")
        term.write(f"Found {args[0]} and {args[1]}.")

    if x >= game.solar_system.size or y >= game.solar_system.size:
        term.write("Invalid coordinates. Please enter coordinates within the solar system.")
    else:
        game.player_ship.travel(term, Vector2(x, y))


def mine_command(time_to_mine, term: PygameTerminal):
    """Handles the mine command."""
    game: Game = term.app_state

    if not game.solar_system.is_object_within_an_asteroid_field_radius(
            game.player_ship.space_object.get_position()):
        term.write("You must be within an asteroid field to mine.")
        return

    try:
        time_to_mine = int(time_to_mine)
        asteroid_field = game.solar_system.get_field_by_position(game.player_ship.space_object.get_position())
        game.player_ship.mine_belt(term, asteroid_field, time_to_mine)

    except ValueError:
        term.write("Invalid time. Please enter a valid number.")


def display_help(term: PygameTerminal):
    """Displays the help message."""
    term.write("Available commands:")
    term.write("  q, quit: Quit the game.")
    term.write("  refuel <amount>: Refuel the ship with the given amount.")
    term.write("  move or travel (m, t) <x> <y> or <closest> <object>:")
    term.write("  Move the ship to the given coordinates or")
    term.write("  'closest' to travel to the closest asteroid field (f) or station (s).")
    term.write(
        "  mine (mi) <time>: Mine for the specified time at the nearest asteroid field."
    )
    term.write("  status (st): Display the current status of the ship.")
    term.write("  scan <amount>: Scan for the specified amount of objects and travel to one of them if you wish to.")
    term.write("  dock (do): Dock with the nearest station.")
    term.write("  undock (ud): Undock from the nearest station.")
    term.write("  add_ore (ao) <quantity> <ore_type>: Adds an arbitrary amount of some ore to your cargohold.")
    term.write("  add_credits (ac) <quantity>: Adds an arbitrary amount of credits to your account.")
    term.write("  buy <ore_type> <quantity>: Purchase some ore from the station you are docked in.")
    term.write("  sell <ore_type>: Sell some ore to the station you are docked in.")
    term.write("  help: Display this help message.")


def command_dock(term: PygameTerminal):
    """Handles the dock and undock commands."""

    def on_dock_complete():
        term.write("Dock complete.")
        game.player_ship.dock_into_station(station)
        station_to_dock: Station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
        term.write(f"Docked at {station_to_dock.name}.")
        term.write(f"This station has: ")
        term.write(station_to_dock.ores_available_to_string())

    game: Game = term.app_state
    if game.player_ship.is_docked:
        term.write("You are already docked.")
    else:
        station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
        if station is None:
            term.write("You must be close to a station to dock.")
            return

        term.countdown_with_message(
            start_value=5.0,
            end_value=1.0,
            step=0.5,
            message_template="Docking in... {}",
            wait_time=0.05,
            on_complete=on_dock_complete
        )


def command_undock(term: PygameTerminal):
    """Handles the undocking command."""
    game: Game = term.app_state
    if not game.player_ship.is_docked:
        term.write("You are not docked.")
        return

    def on_undock_complete():
        game.player_ship.undock_from_station()
        term.write("Undocked.")

    term.countdown_with_message(
        start_value=5.0,
        end_value=1.0,
        step=0.5,
        message_template="Undocking in... {}",
        wait_time=0.5,
        on_complete=on_undock_complete
    )


def scan_command(number, term: PygameTerminal):
    """Handles the scan command."""
    game: Game = term.app_state
    amount_of_objects = int(number)
    term.write(f"Scanning for {amount_of_objects} objects...")
    objects = game.solar_system.scan_system_objects(game.player_ship.space_object.get_position(), amount_of_objects)
    for i in range(amount_of_objects):
        term.write(f"{i}. {objects[i].to_string_short(game.player_ship.space_object.get_position())}")

    term.write(f"Enter object to navigate to or -1 to abort:")
    input_response: str = term.prompt_user("Enter the number of the object to navigate to or -1 to abort:")

    if input_response == "-1":
        return
    else:
        try:
            input_response_index: int = int(input_response)
        except ValueError:
            term.write("Invalid input. Please enter a valid number.")
            return
        selected_object: Station | AsteroidField = objects[input_response_index]
        selected_object_position: Vector2 = selected_object.position
        direct_travel([selected_object_position.x, selected_object_position.y], term=term)


def add_ore_command(term: PygameTerminal, args):
    """Handles the add ore command."""
    game: Game = term.app_state
    if len(args) != 2:
        term.write(
            "Invalid arguments. Please enter the amount of ore you wish to add and the name of the ore."
        )
        return
    ore_amount = int(args[0])
    if ore_amount < 0:
        term.write("Invalid amount. Please enter a positive number.")
        return
    ore_name = args[1]
    ore_selected: Ore
    for ore in data.ORES:
        if ore_name == ore.get_name().lower():
            ore_selected = ore
            break
    else:
        term.write("Invalid ore name. Please enter a valid ore name.")
        return

    if ore.volume * ore_amount > game.player_ship.cargohold_capacity:
        term.write(
            "You are trying to add more ore than your ship can hold, since this is a cheat/debug command I will allow it.")
    for _ in range(ore_amount):
        existing_ore_cargo = next((cargo for cargo in game.player_ship.cargohold if cargo.ore == ore_selected), None)
        if existing_ore_cargo:
            existing_ore_cargo.quantity += ore_amount
        else:
            ore_cargo = OreCargo(ore_selected, ore_amount, ore.base_value)
            game.player_ship.cargohold.append(ore_cargo)

    term.write(f"{ore_amount} of {ore_name} added to cargohold.")


def add_creds_command(args, term: PygameTerminal):
    """Handles the add credits command."""
    game: Game = term.app_state
    amount = int(args)
    if amount < 0:
        term.write("You have entered a negative number, this means you are in debt.")
        term.write("Are you sure? (y/n)")
        confirm = take_input(">> ").strip()
        if confirm != "y":
            return
    game.player_credits += amount
    term.write(f"{amount} credits added to your credits.")


def display_time_and_status(term: PygameTerminal):
    """Displays the current time and the player's ship status."""
    game: Game = term.app_state
    time_string = f"Time: {format_seconds(term.app_state.global_time)}s"
    ship_status = game.player_ship.status_to_string()
    term.write(time_string)
    term.write(f"Credits: {game.player_credits}")
    for status in ship_status:
        term.write(status)


def command_exit(term: PygameTerminal):
    """Exit the term."""
    term.countdown_with_message(
        start_value=3.0,
        end_value=1.0,
        step=0.5,
        message_template="Exiting in... {}",
        wait_time=0.5,
        on_complete=term.quit
    )
    term.running = False


def command_color(color_type: str, color: str, term):

    color_type = color_type
    if color_type not in ["bg", "fg"]:
        term.write(f"Invalid type: {color_type}")
        return

    color = color
    if not color_data.does_color_exist(color):
        term.write(f"Invalid color: {color}")
        return

    if color_type == "bg":
        term.bg_color = color_data.get_color(color)
        return

    if color_type == "fg":
        term.fg_color = color_data.get_color(color)
        return


def command_reset(self, type_of_reset: str):
    if type_of_reset == "color":
        self.fg_color = self.default_fg_color
        self.bg_color = self.default_bg_color
    elif type_of_reset == "bg":
        self.bg_color = self.default_bg_color
    elif type_of_reset == "fg":
        self.fg_color = self.default_fg_color
    elif type_of_reset == "text":
        self.clear(self)
    elif type_of_reset == "history":
        self.command_history.clear()
    elif type_of_reset == "all":
        self.fg_color = self.default_fg_color
        self.bg_color = self.default_bg_color
        self.clear(self)
    else:
        self.fg_color = self.default_fg_color
        self.bg_color = self.default_bg_color
        self.clear(self)

def clear(term):
    """Clear the terminal screen."""
    term.terminal_lines.clear()