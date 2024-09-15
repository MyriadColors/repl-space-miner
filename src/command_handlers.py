from pygame import Vector2

from src import helpers
from src.classes.asteroid import AsteroidField
from src.classes.game import Game
from src.classes.ore import Ore
from src.classes.station import Station
from src.data import OreCargo
from src.helpers import take_input, rnd_float, rnd_int, get_closest_field, get_closest_station, euclidean_distance, \
    format_seconds, prompt_for_closest_travel_choice
from src.pygameterm import color_data
from src.pygameterm.terminal import PygameTerminal


def refuel_command(term: PygameTerminal, amount: float):
    """Handles the refuel command."""

    game: Game = term.app_state
    if not game.player_ship.is_docked:
        term.write("Cannot refuel while not docked.")
        return

    station = game.solar_system.get_object_within_interaction_radius(game)

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


def barter(term: PygameTerminal, price: float) -> tuple[float, bool]:
    """Handles the bartering process and returns the potentially discounted price and a bartering success flag."""
    confirm = term.prompt_user("Want to barter for a discount? y/n")
    bartering_flag = False  # Initialize the flag
    if confirm.lower() == "y":
        bartering_flag = True  # Set the flag to True if bartering is attempted
        rng_number = rnd_float(0, 1)
        if rng_number < 0.5:
            discount = rnd_int(10, 25)
            new_price = price * (100 - discount) / 100
            term.write(f"Bartered for {discount}% discount off the original price.")
            term.write(f"New price: {new_price} credits")
            return new_price, bartering_flag  # Return both values
        else:
            term.write("Bartering failed.")
    return price, bartering_flag  # Return original price and flag


def sell_command(term: PygameTerminal):
    """Handles the sell command."""
    game: Game = term.app_state

    if not game.player_ship.is_docked:
        term.write("Cannot sell while not docked.")
        return

    station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
    if station.ore_cargo_volume >= station.ore_capacity:
        term.write("Cannot sell because the station's ore cargo is full. Look for another one.")
        return

    sellable_ores: list[OreCargo] = []
    for ore_cargo in game.player_ship.cargohold:
        # Check if the player has this ore, if the station accepts this ore and if the station has enough capacity
        if ore_cargo.quantity > 0 and ore_cargo.ore.id in [ore.id for ore in station.ores_available] and \
                ore_cargo.ore.volume <= station.ore_capacity - station.ore_cargo_volume:
            sellable_ores.append(ore_cargo)

    if not sellable_ores:
        term.write("No ores to sell.")
        return

    # Display the ores to be sold
    term.write("Ores to be sold:")
    for ore_cargo in sellable_ores:
        term.write(ore_cargo.ore.to_string())

    total_value = sum(ore_cargo.quantity * ore_cargo.sell_price for ore_cargo in sellable_ores)
    total_volume = sum(ore_cargo.quantity * ore_cargo.ore.volume for ore_cargo in sellable_ores)
    total_units = sum(ore_cargo.quantity for ore_cargo in sellable_ores)

    term.write(f"Total value: {total_value:.2f} credits")
    term.write(f"Total volume: {total_volume:.2f} m³")
    term.write(f"Total units: {total_units}")

    confirm = term.prompt_user("Are you sure you want to sell these ores? (y/n)")
    if confirm.lower() != "y":
        term.write("Sell cancelled.")
        return

    # Update game state
    game.player_credits += total_value
    station.ore_cargo_volume += total_volume

    # Remove sold ores from the player's cargo hold
    for ore_cargo in sellable_ores:
        player_ore_cargo = game.player_ship.get_ore_cargo_by_id(ore_cargo.ore.id)
        if player_ore_cargo:
            player_ore_cargo.quantity -= ore_cargo.quantity

    game.player_ship.cargohold = [cargo for cargo in game.player_ship.cargohold if cargo.quantity > 0]
    game.player_ship.calculate_cargo_occupancy()

    term.write(f"Sold {total_units} units for {total_value:.2f} credits.")


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
        price: float = round(ore_cargo.buy_price * amount_number, 2)

        term.write(f"Price for {amount} {item_name}: {price} credits")

        # Handle bartering logic
        price, bartering_flag = barter(term, price)

        if price > game.player_credits:
            term.write(f"Cannot buy {amount} {item_name} because you don't have enough credits.")
            return

        if total_volume > volume_of_ore_available:
            term.write(f"Cannot buy {amount} {item_name} because the station doesn't have enough ore in its cargo.")
            confirm = term.prompt_user("Do you want to buy all available ore? y/n >> ")
            if confirm.lower() == "y":
                amount_number = int(volume_of_ore_available / ore_cargo.ore.volume)
                price = round(ore_cargo.buy_price * amount_number, 2)
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
                          station: Station = None):
    """Updates the quantities of ore.

    If a station is provided, it updates both the station and the player's ship.
    If no station is provided, it only updates the player's ship.
    """
    game: Game = term.app_state

    # Ensure we don't buy more than available (only if buying from a station)
    if station:
        amount = min(amount, ore_cargo.quantity)
        ore_cargo.quantity -= amount
        station.ore_cargo_volume -= round(amount * ore_cargo.ore.volume, 2)

    ore_cargo_found = game.player_ship.get_ore_cargo_by_id(ore_cargo.ore.id)

    if ore_cargo_found:
        ore_cargo_found.quantity += amount
    else:
        game.player_ship.cargohold.append(OreCargo(ore_cargo.ore, amount, ore_cargo.buy_price, ore_cargo.sell_price))

    # Remove empty cargo entries and recalculate volume
    game.player_ship.cargohold = [cargo for cargo in game.player_ship.cargohold if cargo.quantity > 0]
    game.player_ship.calculate_cargo_occupancy()

    # Only deduct credits if buying from a station
    if station:
        game.player_credits -= price

        # Reporting for station purchases
        term.write(f"Report: {amount} {ore_name} bought for {price} credits.")
        term.write(f"Station Ore Report:\n{station.ore_cargo_volume} tons of ore remaining")
        term.write(f"Your new credit balance: {game.player_credits} credits")
    else:
        # Reporting for other ore updates (e.g., debug commands)
        term.write(f"Updated player ship cargo with {amount} {ore_name}.")


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
        closest_travel(term, args[1])
    else:
        term.write("Invalid argument. Please enter 'closest' to travel to the closest field or station.")


def closest_travel(term: PygameTerminal, object_type):
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
        prompt_for_closest_travel_choice(game.player_ship, closest_field, closest_station,  game.global_time, term)

    elif object_type in ['field', 'f']:
        field_position: Vector2 = closest_field.position
        term.app_state.player_ship.travel(term, field_position)

    elif object_type in ['station', 's']:
        station_position: Vector2 = closest_station.position
        term.app_state.player_ship.travel(term, station_position)
    else:
        term.write("Invalid object type. Use 'field' or 'station'.")

    return


def direct_travel_command(destination_x: str, destination_y: str, term: PygameTerminal):
    """Handles direct coordinate travel."""
    game: Game = term.app_state

    try:
        x = float(destination_x)
        y = float(destination_y)
    except ValueError:
        term.write("Invalid coordinates. Please enter valid numbers.")
        return

    if x >= game.solar_system.size or y >= game.solar_system.size:
        term.write("Invalid coordinates. Please enter coordinates within the solar system.")
        return

    game.player_ship.travel(term, Vector2(x, y))


def mine_command(time_to_mine = None, mine_until_full = None, ore_selected = None, term: PygameTerminal = None):
    """Handles the mine command."""
    game: Game = term.app_state

    if not game.solar_system.is_object_within_an_asteroid_field_radius(
            game.player_ship.space_object.get_position()):
        term.write("You must be within an asteroid field to mine.")
        return

    try:
        time_to_mine = int(time_to_mine)
        asteroid_field = game.solar_system.get_field_by_position(game.player_ship.space_object.get_position())
        
        if ore_selected:
            # Convert comma-separated string to list of ore names
            ore_selected = [ore.strip() for ore in ore_selected.split(',')]
        else:
            # If no ores specified, mine all available ores, set to None
            ore_selected = None

        game.player_ship.mine_belt(term, asteroid_field, time_to_mine, mine_until_full, ore_selected)

    except ValueError:
        term.write("Invalid time. Please enter a valid number.")


def command_dock(term: PygameTerminal):
    """Handles the dock commands."""

    def on_dock_complete():
        term.write("Dock complete.")
        game.player_ship.dock_into_station(station)
        station_to_dock: Station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
        term.write(f"Docked at {station_to_dock.name}.")
        term.write(f"This station has: ")
        term.write(station_to_dock.ores_available_to_string(term))

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
        wait_time=0.1,
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
        direct_travel_command(selected_object_position.x, selected_object_position.y, term=term)


def add_ore_debug_command(amount: str, ore_name: str, term: PygameTerminal):
    """Handles the add ore command. It will add ores to the player ship cargohold"""
    term.write("This is a debug/cheat command: with great power comes great responsibility!")
    game: Game = term.app_state

    amount_num = int(amount)
    if amount_num < 0:
        term.write("You have entered a negative number.")

    ore: Ore = helpers.get_ore_by_id_or_name(ore_name)
    if ore is None:
        term.write(f"Invalid ore name: {ore_name}")
        return

    total_volume = ore.volume * amount_num
    if total_volume > game.player_ship.cargohold_occupied:
        term.write("You are trying to add more cargo than your ship's capacity.")
        term.write("Since this is a debug command, i will allow you to do that.")

    # Create the ore cargo
    ore_cargo: OreCargo = OreCargo(ore, amount_num, ore.base_value, ore.base_value)

    # Update ore quantities (this will add it to the cargohold)
    update_ore_quantities(term, ore_cargo, ore_name, amount_num, ore.base_value)

    display_status(term)


def add_creds_debug_command(amount: str, term: PygameTerminal):
    """Handles the add credits command."""
    game: Game = term.app_state
    if game.debug_flag:
        amount = int(amount)
        if amount < 0:
            term.write("You have entered a negative number, this means you are in debt.")
            term.write("Are you sure? (y/n)")
            confirm = take_input(">> ").strip()
            if confirm != "y":
                return
        game.player_credits += amount
        term.write(f"{amount} credits added to your credits.")
    else:
        term.write("Debug commands can only be used through the use of the 'debug' ('dm') command.")
        return


def display_status(term: PygameTerminal):
    game: Game = term.app_state
    term.write(f"Credits: {game.player_credits}")
    for status in game.player_ship.status_to_string():
        term.write(status)


def display_time_and_status(term: PygameTerminal):
    """Displays the current time and the player's ship status."""
    game: Game = term.app_state
    time_string = f"Time: {format_seconds(term.app_state.global_time)}s"
    term.write(time_string)
    term.write(f"Credits: {game.player_credits}")
    for status in game.player_ship.status_to_string():
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


def command_reset(type_of_reset: str, term: PygameTerminal):
    if type_of_reset == "color":
        term.fg_color = term.default_fg_color
        term.bg_color = term.default_bg_color
    elif type_of_reset == "bg":
        term.bg_color = term.default_bg_color
    elif type_of_reset == "fg":
        term.fg_color = term.default_fg_color
    elif type_of_reset == "text":
        clear(term)
    elif type_of_reset == "history":
        term.command_history.clear()
        clear(term)
    elif type_of_reset == "all":
        term.fg_color = term.default_fg_color
        term.bg_color = term.default_bg_color
        clear(term)
    else:
        term.fg_color = term.default_fg_color
        term.bg_color = term.default_bg_color
        clear(term)


def clear(term):
    """Clear the terminal screen."""
    term.terminal_lines.clear()

def scan_field_command(term: PygameTerminal):
    """Handles the scan field command."""
    game: Game = term.app_state
    game.player_ship.scan_field(term)

def debug_mode_command(term):
    """Handles the debug mode command."""
    game: Game = term.app_state
    if game.debug_flag:
        game.debug_flag = False
        term.write("Debug mode disabled.")
    else:
        game.debug_flag = True
        term.write("Debug mode enabled.")

def init_music(term: PygameTerminal):
    from pygame import mixer

    game: Game = term.app_state

    mixer.init()
    mixer.music.load("Decoherence.mp3")
    mixer.music.play(-1)
    game.mute_flag = False
    game.sound_init = True
    term.write("Sound init.")

def pause_sound(term: PygameTerminal):
    from pygame import mixer
    mixer.music.pause()
    term.write(f"Sound disabled.")

def unpause_sound(term: PygameTerminal):
    from pygame import mixer
    mixer.music.unpause()
    term.write("Sound enabled.")

def toggle_sound_command(term: PygameTerminal):
    game: Game = term.app_state

    if game.mute_flag:
        if not game.sound_init:
            init_music(term)
        else:
            unpause_sound(term)
        game.mute_flag = False
    else:
        game.mute_flag = True
        pause_sound(term)

def display_help(command_name: str = None, term: PygameTerminal = None):
    """Displays the help message."""

    if command_name is None:
        # Display general help
        term.write("Welcome to Space Miner! Explore, mine, trade, and upgrade your ship.")
        term.write("Available commands (type 'help <command>' for more details):")
        term.write("  status (st): Display your ship's status, credits, and time.")
        term.write("  scan (sc) <quantity>: Scan for nearby asteroid fields and stations.")
        term.write("  travel (tr) closest <field|station>: Travel to the closest asteroid field or station.")
        term.write("  direct_travel (dtr) <x> <y>: Travel to specific coordinates in the solar system.")
        term.write("  mine (mi) <time>: Mine for ores at the current asteroid field.")
        term.write("  dock (do): Dock with the nearest station.")
        term.write("  undock (ud): Undock from the current station.")
        term.write("  buy (by) <ore_name> <amount>: Buy ores from the docked station.")
        term.write("  sell (sl): Sell ores at the docked station.")
        term.write("  refuel (ref) <amount>: Refuel your ship at the docked station.")
        term.write("  upgrade: View and purchase ship upgrades.")
        term.write("  color (co) <bg|fg> <color_name>: Change the terminal colors.")
        term.write("  reset (rs) <color|bg|fg|text|history|all>: Reset terminal settings.")
        term.write("  clear (cl): Clear the terminal screen.")
        term.write("  debug (dm): Enable the Debug Mode")
        term.write("  toggle_sound (ts): Enable or disable the game's sound.")
        term.write("  add_credits (ac): Add credits to your account (debug mode command)")
        term.write("  add_ores (ao): Add ores to your ship (debug mode command)")
        term.write("  exit: Exit the game.")
    else:
        command_name = command_name.lower()
        if command_name == "status" or command_name == "st":
            term.write("status (st):")
            term.write("  Displays your current credits, ship status (fuel, cargo, location), and time elapsed.")
        elif command_name == "scan" or command_name == "sc":
            term.write("scan (sc) <quantity>:")
            term.write("  Scans for the specified number of nearby asteroid fields and stations.")
            term.write("  Example: scan 5")
        elif command_name == "travel" or command_name == "tr":
            term.write("travel (tr) closest <field|station>:")
            term.write("  Travels to the closest asteroid field or station.")
            term.write("  Example: travel closest field")
        elif command_name == "direct_travel" or command_name == "dtr":
            term.write("travel_direct (dtr) <x> <y>:")
            term.write("  Travels to the specified coordinates in the solar system.")
            term.write("  Example: travel 10.5 20.3")
        elif command_name == "mine" or command_name == "mi":
            term.write("mine (mi) <time>:")
            term.write("  Mines for ores at the current asteroid field for the specified amount of time.")
            term.write("  You must be within an asteroid field to mine.")
            term.write("  Example: mine 60 (mines for 60 seconds)")
        elif command_name == "dock" or command_name == "do":
            term.write("dock (do):")
            term.write("  Docks with the nearest station if you are within range.")
        elif command_name == "undock" or command_name == "ud":
            term.write("undock (ud):")
            term.write("  Undocks from the current station.")
        elif command_name == "buy" or command_name == "by":
            term.write("buy (by) <ore_name> <amount>:")
            term.write("  Buys the specified amount of ore from the docked station.")
            term.write("  Example: buy Pyrogen 10")
        elif command_name == "sell" or command_name == "sl":
            term.write("sell (sl):")
            term.write("  Sells all ores in your cargo hold to the docked station.")
        elif command_name == "refuel" or command_name == "ref":
            term.write("refuel (ref) <amount>:")
            term.write("  Refuels your ship with the specified amount of fuel at the docked station.")
            term.write("  Example: refuel 50")
        elif command_name == "upgrade":
            term.write("upgrade:")
            term.write("  Displays available ship upgrades and allows you to purchase them.")
        elif command_name == "color" or command_name == "co":
            term.write("color (co) <bg|fg> <color_name>:")
            term.write("  Changes the terminal's background or foreground color.")
            term.write("  Available colors: black, white, red, green, blue, yellow, magenta, cyan")
            term.write("  Example: color bg blue")
        elif command_name == "reset" or command_name == "rs":
            term.write("reset (rs) <color|bg|fg|text|history|all>:")
            term.write("  Resets various aspects of the terminal.")
            term.write("  Options:")
            term.write("    color: Resets both foreground and background colors.")
            term.write("    bg: Resets the background color.")
            term.write("    fg: Resets the foreground color.")
            term.write("    text: Clears the terminal screen.")
            term.write("    history: Clears the command history.")
            term.write("    all: Resets all terminal settings.")
        elif command_name == "clear" or command_name == "cl":
            term.write("clear (cl):")
            term.write("  Clears the terminal screen.")
        elif command_name == "debug" or command_name == "dm":
            term.write("debug (dm):")
            term.write("  Enables or Disables the Debug Mode.")
        elif command_name == "toggle_sound" or command_name == "ts":
            term.write("toggle_sound (ts):")
            term.write("  Toggles the game's sound effects and music on or off.")
        elif command_name == "add_credits" or command_name == "ac":
            term.write("add_credits (ac):")
            term.write("  Adds the specified amount of credits to your account.")
            term.write("  Example: add_credits 100")
            term.write("  Needs Debug Mode to be Enabled")
        elif command_name == "add_ores" or command_name == "ao":
            term.write("  Adds the specified amount of ores to your account.")
            term.write("  Example: add_ores 100 Pyrogen")
            term.write("  Needs Debug Mode to be Enabled")
        elif command_name == "exit":
            term.write("exit:")
            term.write("  Exits the game.")
        else:
            term.write(f"Unknown command: {command_name}")