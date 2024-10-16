from pygame import Vector2

from src import helpers
from src.classes.asteroid import AsteroidField
from src.classes.game import Character, Game
from src.classes.ore import Ore
from src.classes.ship import Ship
from src.classes.station import Station
from src.data import OreCargo
from src.helpers import take_input, rnd_float, rnd_int, get_closest_field, get_closest_station, euclidean_distance, \
    format_seconds, prompt_for_closest_travel_choice
from src.pygameterm import color_data
from src.pygameterm.terminal import PygameTerminal


def refuel_command(term: PygameTerminal, amount: float) -> None:
    """Handles the refuel command.

    Args:
        term (PygameTerminal): The Pygame terminal object.
        amount (float): The amount of fuel to refuel.
    Returns:
        None
    """

    game: Game = term.app_state
    if not game.player_ship.is_docked:
        term.writeLn("Cannot refuel while not docked.")
        return

    station: Station = game.solar_system.get_object_within_interaction_radius(game)

    if game.player_ship.fuel + amount > game.player_ship.max_fuel:
        term.writeLn(
            "Cannot refuel more than your ship's maximum fuel capacity, consider upgrading your ship."
        )
        return

    price: float = amount * station.fuel_price
    term.writeLn(f"Total price for {round(amount, 2)}m³ of fuel: {round(price, 2)} credits.")
    term.writeLn("Are you sure you want to refuel? y/n")
    confirm: str = take_input(">> ")
    if confirm.lower() != "y":
        term.writeLn("Refuel cancelled.")
        return

    game.player_ship.refuel(amount)
    game.player_character.credits -= price
    term.writeLn(f"Refueled with {round(amount, 2)} m3 for {round(price, 2)} credits.")


def barter(term: PygameTerminal, price: float) -> tuple[float, bool]:
    """Handles the bartering process and returns the potentially discounted price as a float and a bartering success flag as a bool."""
    confirm = term.prompt_user("Want to barter for a discount? y/n")
    bartering_flag: bool = False  # Initialize the flag
    if confirm.lower() == "y":
        bartering_flag = True  # Set the flag to True if bartering is attempted
        rng_number: float = rnd_float(0, 1)
        if rng_number < 0.5:
            discount: int = rnd_int(10, 25)
            new_price: float = price * (100 - discount) / 100
            term.writeLn(f"Bartered for {discount}% discount off the original price.")
            term.writeLn(f"New price: {new_price} credits")
            return new_price, bartering_flag  # Return both values
        else:
            term.writeLn("Bartering failed.")
    return price, bartering_flag  # Return original price and flag


def sell_command(term: PygameTerminal) -> None:
    """Handles the sell command.

    Args:
        term (PygameTerminal): The Pygame terminal object.

    Returns:
        None
    """
    game = term.app_state

    if not game.player_ship.is_docked:
        term.writeLn("Cannot sell while not docked.")
        return

    station = game.solar_system.get_object_within_interaction_radius(game.player_ship)
    if station.ore_cargo_volume >= station.ore_capacity:
        term.writeLn("Cannot sell because the station's ore cargo is full. Look for another one.")
        return

    sellable_ores = [
        ore_cargo
        for ore_cargo in game.player_ship.cargohold
        if ore_cargo.quantity > 0
        and ore_cargo.ore.id in [ore.id for ore in station.ores_available]
        and ore_cargo.ore.volume <= station.ore_capacity - station.ore_cargo_volume
    ]

    if not sellable_ores:
        term.writeLn("No ores to sell.")
        return

    total_value = sum(ore_cargo.quantity * ore_cargo.sell_price for ore_cargo in sellable_ores)
    total_volume = sum(ore_cargo.quantity * ore_cargo.ore.volume for ore_cargo in sellable_ores)
    total_units = sum(ore_cargo.quantity for ore_cargo in sellable_ores)

    term.writeLn("Ores to be sold:")
    for ore_cargo in sellable_ores:
        term.writeLn(ore_cargo.ore.to_string())

    term.writeLn(f"Total value: {total_value:.2f} credits")
    term.writeLn(f"Total volume: {total_volume:.2f} m³")
    term.writeLn(f"Total units: {total_units}")

    confirm = term.prompt_user("Are you sure you want to sell these ores? (y/n)")
    if confirm.lower() != "y":
        term.writeLn("Sell cancelled.")
        return

    # Update game state
    game.player_character.credits += total_value
    station.ore_cargo_volume += total_volume

    # Remove sold ores from the player's cargo hold
    game.player_ship.cargohold = [cargo for cargo in game.player_ship.cargohold if cargo.quantity > 0]
    game.player_ship.calculate_cargo_occupancy()

    term.writeLn(f"Sold {total_units} units for {total_value:.2f} credits.")


def buy_command(item_name: str, amount: str, term: PygameTerminal):
    game: Game = term.app_state
    station: Station | None = game.player_ship.get_docked_station()
    
    if not station:
        term.writeLn("Must be docked to buy ore.")
        return

    try:
        amount_number = int(amount)
        if amount_number <= 0:
            term.writeLn("Quantity must be positive.")
            return
    except ValueError:
        term.writeLn("Invalid amount. Please enter a valid number.")
        return

    ore_cargo: OreCargo | None = station.get_ore_by_name(item_name)
    if not ore_cargo:
        term.writeLn(f"Cannot buy {item_name} because it is not available.")
        return

    total_volume = round(ore_cargo.ore.volume * amount_number, 2)
    available_volume = round(ore_cargo.quantity * ore_cargo.ore.volume, 2)
    price = round(ore_cargo.buy_price * amount_number, 2)

    term.writeLn(f"Price for {amount_number} {item_name}: {price} credits")

    # Handle bartering logic
    price, _ = barter(term, price)

    if price > game.player_character.credits:
        term.writeLn(f"Cannot buy {amount_number} {item_name} because you don't have enough credits.")
        return

    if total_volume > available_volume:
        term.writeLn(f"Cannot buy {amount_number} {item_name} because the station doesn't have enough ore in its cargo.")
        confirm = term.prompt_user("Do you want to buy all available ore? y/n >> ")
        if confirm.lower() == "y":
            amount_number = int(available_volume / ore_cargo.ore.volume)
            price = round(ore_cargo.buy_price * amount_number, 2)
            term.writeLn(f"Adjusting purchase to {amount_number} {item_name} for {price} credits.")
        else:
            term.writeLn("Buy cancelled.")
            return

    # Update ore quantities in the station and player's ship
    update_ore_quantities(term, ore_cargo, item_name, amount_number, price, station)

def update_ore_quantities(term: PygameTerminal, ore_cargo: OreCargo, ore_name: str, amount: int, price: float,
                          station: Station | None = None) -> None:
    """Updates the quantities of ore.

    If a station is provided, it updates both the station and the player's ship.
    If no station is provided, it only updates the player's ship.

    Args:
        term (PygameTerminal): The PygameTerminal instance.
        ore_cargo (OreCargo): The OreCargo instance to update.
        ore_name (str): The name of the ore.
        amount (int): The amount of ore to add or remove.
        price (float): The price of the ore.
        station (Station | None): The station to update, if any.
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
        game.player_character.credits -= price

        # Reporting for station purchases
        term.writeLn(f"Report: {amount} {ore_name} bought for {price} credits.")
        term.writeLn(f"Station Ore Report:\n{station.ore_cargo_volume} tons of ore remaining")
        term.writeLn(f"Your new credit balance: {game.player_character.credits} credits")
    else:
        # Reporting for other ore updates (e.g., debug commands)
        term.writeLn(f"Updated player ship cargo with {amount} {ore_name}.")


def travel_command(*args: str, term: PygameTerminal) -> float:
    """Handles the travel command.

    Args:
        args (str): The arguments for the travel command.
        term (PygameTerminal): The PygameTerminal instance.

    Returns:
        float: The updated global time after the travel command.
    """
    game: Game = term.app_state
    global_time: float = game.global_time
    if game.player_ship.is_docked:
        term.writeLn("Cannot travel while docked.")
        return global_time

    if game.player_ship.fuel == 0:
        term.writeLn("Cannot travel while out of fuel.")
        return global_time

    # Handle 'closest' command
    if args[0] == "closest":
        try:
            closest_travel(term, args[1])
        except IndexError:
            term.writeLn("Invalid argument. Please enter 'closest' followed by 'field' or 'station'.")
    else:
        term.writeLn("Invalid argument. Please enter 'closest' to travel to the closest field or station.")


def closest_travel(term: PygameTerminal, object_type: str) -> None:
    """Handles travel to the closest field or station.

    Args:
        term (PygameTerminal): The PygameTerminal instance.
        object_type (str): The type of object to travel to. Can be 'field', 'f', 'station', or 's'.

    Returns:
        None
    """
    game: Game = term.app_state

    try:
        # Get the closest field and station
        closest_field: AsteroidField = get_closest_field(game.solar_system, game.player_ship.space_object.get_position(),
                                                         game.solar_system.is_object_within_an_asteroid_field_radius(
                                                             game.player_ship.space_object.get_position()) is not None)
        closest_station: Station = get_closest_station(game.solar_system, game.player_ship,
                                                       game.solar_system.get_object_within_interaction_radius(
                                                           game.player_ship) is not None)

        if not object_type:
            # Ask user for input to choose between field or station
            term.writeLn(
                f"Closest field is Field {closest_field.id} at {euclidean_distance(game.player_ship.space_object.get_position(), closest_field.position)} AUs from here.")
            term.writeLn(
                f"Closest station is Station {closest_station.id} at {euclidean_distance(game.player_ship.space_object.get_position(), closest_station.position)} AUs from here.")
            prompt_for_closest_travel_choice(game.player_ship, closest_field, closest_station, game.global_time, term)

        elif object_type in ['field', 'f']:
            field_position: Vector2 = closest_field.position
            term.app_state.player_ship.travel(term, field_position)

        elif object_type in ['station', 's']:
            station_position: Vector2 = closest_station.position
            term.app_state.player_ship.travel(term, station_position)
        else:
            raise ValueError("Invalid object type. Use 'field' or 'station'.")
    except (AttributeError, ValueError) as e:
        term.writeLn(f"Error: {e}")


def direct_travel_command(destination_x: str, destination_y: str, term: PygameTerminal):
    """Handles direct coordinate travel."""
    game: Game = term.app_state

    try:
        x = float(destination_x)
        y = float(destination_y)
    except ValueError:
        term.writeLn("Invalid coordinates. Please enter valid numbers.")
        return

    # Check if the coordinates are valid
    if x < 0 or y < 0 or x >= game.solar_system.size or y >= game.solar_system.size:
        term.writeLn(
            "Invalid coordinates. Please enter coordinates within the solar system's bounds (0 <= x < {}, 0 <= y < {}).".format(
                game.solar_system.size, game.solar_system.size))
        return

    # Check if the coordinates are occupied by an asteroid field or station
    if game.solar_system.is_object_at_position(Vector2(x, y)):
        term.writeLn("Cannot travel to occupied coordinates.")
        return

    game.player_ship.travel(term, Vector2(x, y))


def mine_command(time_to_mine: int, mine_until_full: bool, ore_selected: list[str] | None, term: PygameTerminal) -> None:
    """Handles the mine command.

    Args:
        time_to_mine (int): The amount of time to mine for in seconds.
        mine_until_full (bool): If True, mine until the cargo hold is full.
        ore_selected (List[str] | None): List of ore names to mine, or None to mine all available ores.
        term (PygameTerminal): The PygameTerminal instance.
    """
    game: Game = term.app_state

    if not game.solar_system.is_object_within_an_asteroid_field_radius(
            game.player_ship.space_object.get_position()):
        term.writeLn("You must be within an asteroid field to mine.")
        return

    try:
        asteroid_field = game.solar_system.get_field_by_position(game.player_ship.space_object.get_position())

        if ore_selected is None:
            ore_selected = None

        game.player_ship.mine_belt(term, asteroid_field, time_to_mine, mine_until_full, ore_selected)

    except ValueError:
        term.writeLn("Invalid time. Please enter a valid number.")


def command_dock(term: PygameTerminal) -> None:
    """Handles the dock command.

    Args:
        term (PygameTerminal): The terminal instance for output.

    Returns:
        None
    """
    game: Game = term.app_state
    player_ship: Ship = game.player_ship
    if player_ship.is_docked:
        term.writeLn("You are already docked.")
        return
    target_station: Station | None = helpers.get_closest_station(game.solar_system, player_ship)
    if target_station is None:
        term.writeLn("There are no stations within range.")
        return
    on_dock_complete(term, station_to_dock=target_station)
    

def on_dock_complete(term: PygameTerminal, station_to_dock: Station) -> None:
    """Callback function for when the docking countdown is complete.

    Args:
        term (PygameTerminal): The terminal instance for output.
        station_to_dock (Station): The station to dock with.
    """
    game: Game = term.app_state
    player_ship: Ship = game.player_ship
    player_ship.dock_into_station(station_to_dock)
    term.writeLn(f"Docked with {station_to_dock.name}.")
    term.writeLn(station_to_dock.ores_available_to_string(term))


def command_undock(term: PygameTerminal) -> None:
    """Handles the undocking command.

    Args:
        term (PygameTerminal): The terminal instance for output.
    """
    game: Game = term.app_state
    if not game.player_ship.is_docked:
        term.writeLn("You are not docked.")
        return

    def on_undock_complete() -> None:
        game.player_ship.undock_from_station()
        term.writeLn("Undocked.")

    term.countdown_with_message(
        start_value=5.0,
        end_value=1.0,
        step=0.5,
        message_template="Undocking in... {}",
        wait_time=0.1,
        on_complete=on_undock_complete
    )


def scan_command(number: str, term: PygameTerminal) -> None:
    """Handles the scan command.

    Args:
        number (str): The number of objects to scan.
        term (PygameTerminal): The terminal instance for output.

    Returns:
        None
    """
    game: Game = term.app_state
    amount_of_objects: int = int(number)
    term.writeLn(f"Scanning for {amount_of_objects} objects...")
    objects: list[Station | AsteroidField] = game.solar_system.scan_system_objects(
        game.player_ship.space_object.get_position(), amount_of_objects
    )
    for i in range(amount_of_objects):
        term.writeLn(f"{i}. {objects[i].to_string_short(game.player_ship.space_object.get_position())}")

    term.writeLn(f"Enter object to navigate to or -1 to abort:")
    input_response: str = term.prompt_user("Enter the number of the object to navigate to or -1 to abort:")

    if input_response == "-1":
        return
    else:
        try:
            input_response_index: int = int(input_response)
        except ValueError:
            term.writeLn("Invalid input. Please enter a valid number.")
            return
        selected_object: Station | AsteroidField = objects[input_response_index]
        selected_object_position: Vector2 = selected_object.position
        direct_travel_command(selected_object_position.x, selected_object_position.y, term=term)


def add_ore_debug_command(amount: int, ore_name: str, term: PygameTerminal) -> None:
    """Handles the add ore command. It will add ores to the player ship cargohold

    Args:
        amount (int): The amount of ore to add.
        ore_name (str): The name of the ore to add.
        term (PygameTerminal): The terminal instance for output.
    """
    term.writeLn("This is a debug/cheat command: with great power comes great responsibility!")
    game: Game = term.app_state

    if amount < 0:
        term.writeLn("You have entered a negative number.")
        return

    ore: Ore = helpers.get_ore_by_id_or_name(ore_name)
    if ore is None:
        term.writeLn(f"Invalid ore name: {ore_name}")
        return

    total_volume = ore.volume * amount
    if total_volume > game.player_ship.cargohold_occupied:
        term.writeLn("You are trying to add more cargo than your ship's capacity.")
        term.writeLn("Since this is a debug command, i will allow you to do that.")

    # Create the ore cargo
    ore_cargo: OreCargo = OreCargo(ore, amount, ore.base_value, ore.base_value)

    # Update ore quantities (this will add it to the cargohold)
    update_ore_quantities(term, ore_cargo, ore_name, amount, ore.base_value)

    display_status(term)

def add_creds_debug_command(amount: int, term: PygameTerminal) -> None:
    """Handles the add credits command.

    Args:
        amount (int): The amount of credits to add.
        term (PygameTerminal): The terminal instance for output.
    """
    game: Game = term.app_state
    if game.debug_flag:
        if amount < 0:
            term.writeLn("You have entered a negative number, this means you are in debt.")
            term.writeLn("Are you sure? (y/n)")
            confirm = take_input(">> ").strip()
            if confirm != "y":
                return
        game.player_character.credits += amount
        term.writeLn(f"{amount} credits added to your credits.")
    else:
        term.writeLn("Debug commands can only be used through the use of the 'debug' ('dm') command.")
        return

def display_status(term: PygameTerminal) -> None:
    """Displays the current status of the player character and ship.

    Args:
        term (PygameTerminal): The terminal instance for output.
    """
    game: Game = term.app_state
    term.writeLn("Player Status:")
    for status in game.player_character.to_string():
        term.writeLn(status)
    term.writeLn("")
    term.writeLn("Ship Status:")
    for status in game.player_ship.status_to_string():
        term.writeLn(status)    

def display_time_and_status(
    term: PygameTerminal, selection_flag: ["player", "ship", "both"] = "both"
) -> None:
    """Displays the current time and the player's ship status.

    Args:
        selection_flag (["player", "ship", "both"]): The type of status to display. Defaults to "both".
        term (PygameTerminal): The terminal instance for output.
    """
    game: Game = term.app_state
    time_string = f"Time: {format_seconds(game.global_time)}s"
    term.writeLn(time_string)
    player_character: Character = game.player_character
    player_ship: Ship = game.player_ship
    if selection_flag is None:
        selection_flag = "both"

    if selection_flag in ["player", "both"]:
        term.writeLn("========= Player Status =========")
        for status in player_character.to_string():
            term.writeLn(status)

    if selection_flag in ["ship", "both"]:
        term.writeLn("========= Ship Status =========")
        for status in player_ship.status_to_string():
            term.writeLn(status)

    term.writeLn("=================================")

def command_exit(term: PygameTerminal) -> None:
    """Exit the term.

    Args:
        term (PygameTerminal): The terminal instance for output.
    """
    term.countdown_with_message(
        start_value=3.0,
        end_value=1.0,
        step=0.5,
        message_template="Exiting in... {}",
        wait_time=0.5,
        on_complete=term.quit
    )
    term.running = False

def command_color(color_type: ["bg", "fg"], color: str, term: PygameTerminal) -> None:
    """Change the terminal's text color.

    Args:
        color_type (["bg", "fg"]): Type of color to change. "bg" for background,
            "fg" for foreground.
        color (str): The color to use. Must be a valid color name.
        term (PygameTerminal): The terminal instance for output.
    """
    if color_type not in ["bg", "fg"]:
        term.write(f"Invalid type: {color_type}")
        return

    if not color_data.does_color_exist(color):
        term.write(f"Invalid color: {color}")
        return

    if color_type == "bg":
        term.bg_color = color_data.get_color(color)
        return

    if color_type == "fg":
        term.fg_color = color_data.get_color(color)
        return

def command_reset(type_of_reset: ["color", "bg", "fg", "text", "history", "all"], term: PygameTerminal) -> None:
    """Reset the terminal colors or text.
    
    Args:
        type_of_reset (["color", "bg", "fg", "text", "history", "all"]): Type of reset to perform.
        term (PygameTerminal): The terminal instance for output.
    """
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


def pause_sound(term: PygameTerminal):
    from pygame import mixer
    mixer.music.pause()
    term.writeLn(f"Sound disabled.")


def unpause_sound(term: PygameTerminal):
    from pygame import mixer
    mixer.music.unpause()
    term.writeLn("Sound enabled.")


def toggle_sound_command(term: PygameTerminal) -> None:
    """Toggle sound on or off.

    Args:
        term (PygameTerminal): The terminal instance for output.
    """
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

def show_image_command(image_source, term):
        term.show_illustration(image_source, x=100, y=50, width=200)  # or provide a URL
        term.writeLn("Image displayed.")

def display_help(command_name: str = None, term: PygameTerminal = None):
    """Displays help information for available commands.

    If a specific command name is provided, detailed help for that
    command is displayed. Otherwise, a list of all available commands
    is shown, with their descriptions and whether they are allowed
    based on the current game state.

    Args:
        command_name (str, optional): The name of the command for which
            detailed help is requested. Defaults to None.
        term (PygameTerminal, optional): The terminal instance for output.
            Defaults to None.
    """
    term.writeLn("Available commands (type 'help <command>' for more details):")

    game: Game = term.app_state
    player_ship: Ship = game.player_ship
    
    station = game.solar_system.get_object_within_interaction_radius(player_ship)
    if station is not None:
        is_docked = player_ship.is_docked
    else:
        is_docked = False
    field = game.solar_system.get_field_by_position(player_ship.space_object.get_position())
    
    location = "field" if field is not None else "station" if station is not None else "none"

    def write_command(command, description, allowed: bool):
        if allowed:
            term.writeLn(f"{f"<blue>{command}</blue>"}: {description}")
        else:
            term.writeLn(f"{f"<red>{command}</red>"}: {description}")
            
    write_command("status (st) <selection_flag>", "Displays your current credits, ship status (fuel, cargo, location), and time elapsed.", True)
    write_command("scan (sc) <quantity>", "Scan for nearby asteroid fields and stations.", True)
    write_command("scan_field (scf)", "Scan for nearby asteroid fields and stations.", True)
    write_command("travel (tr) closest <field|station>", "Travel to the closest asteroid field or station.", True)
    write_command("direct_travel (dtr) <x> <y>", "Travel to specific coordinates in the solar system.", True)
    write_command("mine (mi) <time> <until_full> <ore_name: optional>", "Mine for ores at the current asteroid field.", True if location == "field" else False)
    write_command("dock (do)", "Dock with the nearest station.", True if not is_docked else False)
    write_command("undock (ud)", "Undock from the current station.", True if is_docked else False)
    write_command("buy (by) <ore_name> <amount>", "Buy ores from the docked station.", True if is_docked else False)
    write_command("sell (sl)", "Sell ores at the docked station.", True if is_docked else False)
    write_command("refuel (ref) <amount>", "Refuel your ship at the docked station.", True if is_docked else False)
    write_command("upgrade", "View and purchase ship upgrades.", True if is_docked else False)
    write_command("color (co) <bg|fg> <color_name>", "Change the terminal colors.", True)
    write_command("reset (rs) <color|bg|fg|text|history|all>", "Reset terminal settings.", True)
    write_command("clear (cl)", "Clear the terminal screen.", True)
    write_command("debug (dm)", "Enable the Debug Mode", True)
    write_command("toggle_sound (ts)", "Enable or disable the game's sound.", True)
    write_command("add_credits (ac)", "Add credits to your account (debug mode command)", game.debug_flag)
    write_command("add_ores (ao)", "Add ores to your ship (debug mode command)", game.debug_flag)
    write_command("exit", "Exit the game.", True)

    if command_name:
        command_name = command_name.lower()
        if command_name == "status" or command_name == "st":
            term.writeLn("status (st):")
            term.writeLn("  Displays your current credits, ship status (fuel, cargo, location), and time elapsed.")
            term.writeLn("  Options:")
            term.writeLn("    selection_flag: (optional) 'player', 'ship', or 'both' (default is 'both').")
            term.writeLn("    Example: status both")
        elif command_name == "scan" or command_name == "sc":
            term.writeLn("scan (sc) <quantity>:")
            term.writeLn("  Scans for the specified number of nearby asteroid fields and stations.")
            term.writeLn("  Example: scan 5")
        elif command_name == "travel" or command_name == "tr":
            term.writeLn("travel (tr) closest <field|station>:")
            term.writeLn("  Travels to the closest asteroid field or station.")
            term.writeLn("  Example: travel closest field")
        elif command_name == "direct_travel" or command_name == "dtr":
            term.writeLn("travel_direct (dtr) <x> <y>:")
            term.writeLn("  Travels to the specified coordinates in the solar system.")
            term.writeLn("  Example: travel 10.5 20.3")
        elif command_name == "mine" or command_name == "mi":
            term.writeLn("mine (mi) <time>:")
            term.writeLn("  Mines for ores at the current asteroid field for the specified amount of time, if you want to mine until full, you can do so by adding 'until_full'.")
            term.writeLn("  If you want to mine for a specific ore, you can add the ore name to the command.")
            term.writeLn("  You must be within an asteroid field to mine.")
            term.writeLn("  Options:")
            term.writeLn("    time: The amount of time to mine for in seconds.")
            term.writeLn("    until_full: If you want to mine until the cargo hold is full, you can do so by adding 'until_full'.")
            term.writeLn("    ore_name: If you want to mine for a specific ore, you can add the ore name to the command.")
            term.writeLn("  Example: mine 60 until_full")
            term.writeLn("  Example: mine 60 Pyrogen")
        elif command_name == "dock" or command_name == "do":
            term.writeLn("dock (do):")
            term.writeLn("  Docks with the nearest station if you are within range.")
        elif command_name == "undock" or command_name == "ud":
            term.writeLn("undock (ud):")
            term.writeLn("  Undocks from the current station.")
        elif command_name == "buy" or command_name == "by":
            term.writeLn("buy (by) <ore_name> <amount>:")
            term.writeLn("  Buys the specified amount of ore from the docked station.")
            term.writeLn("  Example: buy Pyrogen 10")
        elif command_name == "sell" or command_name == "sl":
            term.writeLn("sell (sl):")
            term.writeLn("  Sells all ores in your cargo hold to the docked station.")
        elif command_name == "refuel" or command_name == "ref":
            term.writeLn("refuel (ref) <amount>:")
            term.writeLn("  Refuels your ship with the specified amount of fuel at the docked station.")
            term.writeLn("  Example: refuel 50")
        elif command_name == "upgrade":
            term.writeLn("upgrade:")
            term.writeLn("  Displays available ship upgrades and allows you to purchase them.")
        elif command_name == "color" or command_name == "co":
            term.writeLn("color (co) <bg|fg> <color_name>:")
            term.writeLn("  Changes the terminal's background or foreground color.")
            term.writeLn("  Available colors: black, white, red, green, blue, yellow, magenta, cyan")
            term.writeLn("  Example: color bg blue")
        elif command_name == "reset" or command_name == "rs":
            term.writeLn("reset (rs) <color|bg|fg|text|history|all>:")
            term.writeLn("  Resets various aspects of the terminal.")
            term.writeLn("  Options:")
            term.writeLn("    color: Resets both foreground and background colors.")
            term.writeLn("    bg: Resets the background color.")
            term.writeLn("    fg: Resets the foreground color.")
            term.writeLn("    text: Clears the terminal screen.")
            term.writeLn("    history: Clears the command history.")
            term.writeLn("    all: Resets all terminal settings.")
        elif command_name == "clear" or command_name == "cl":
            term.writeLn("clear (cl):")
            term.writeLn("  Clears the terminal screen.")
        elif command_name == "debug" or command_name == "dm":
            term.writeLn("debug (dm):")
            term.writeLn("  Enables or Disables the Debug Mode.")
        elif command_name == "toggle_sound" or command_name == "ts":
            term.writeLn("toggle_sound (ts):")
            term.writeLn("  Toggles the game's sound effects and music on or off.")
        elif command_name == "add_credits" or command_name == "ac":
            term.writeLn("add_credits (ac):")
            term.writeLn("  Adds the specified amount of credits to your account.")
            term.writeLn("  Example: add_credits 100")
            term.writeLn("  Needs Debug Mode to be Enabled")
        elif command_name == "add_ores" or command_name == "ao":
            term.writeLn("  Adds the specified amount of ores to your account.")
            term.writeLn("  Example: add_ores 100 Pyrogen")
            term.writeLn("  Needs Debug Mode to be Enabled")
        elif command_name == "exit":
            term.writeLn("exit:")
            term.writeLn("  Exits the game.")
        else:
            term.writeLn(f"Unknown command: {command_name}")


