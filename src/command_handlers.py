import os
from dataclasses import field, dataclass
from typing import Callable, Any, Optional

from pygame import Vector2

from src import helpers
from src.classes.asteroid import AsteroidField
from src.classes.game import Character, Game
from src.classes.ore import Ore
from src.classes.ship import Ship
from src.classes.station import Station
from src.data import OreCargo
from src.helpers import (
    take_input,
    rnd_float,
    rnd_int,
    get_closest_field,
    get_closest_station,
    euclidean_distance,
    prompt_for_closest_travel_choice,
    is_valid_int,
    is_valid_float,
    is_valid_bool,
)

# Colorama is still needed for direct colors in specific cases
import colorama
from colorama import Fore, Style
colorama.init()


def process_command(game_state: "Game", command_line: str):
    """
    Process a user command and execute the corresponding function.
    
    Parameters:
        game_state (Game): The current state of the game.
        command_line (str): The raw command string entered by the user.
    """
    # Handle empty command
    command_line = command_line.strip()
    if not command_line:
        game_state.ui.warn_message("No command entered.")
        return

    # Parse command input
    parts = command_line.split()
    command_name = parts[0]
    args = parts[1:]

    # Find and execute command if it exists
    if command_name in commands.commands:
        try:
            execute_valid_command(game_state, command_name, args)
        except ValueError as e:
            game_state.ui.error_message(str(e))
    else:
        game_state.ui.error_message(f"Unknown command: {command_name} not implemented yet.")


def execute_valid_command(game_state: "Game", command_name: str, args: list[str]):
    """
    Execute a command after validating its arguments.
    
    Parameters:
        game_state (Game): The current state of the game.
        command_name (str): The name of the command to execute.
        args (list[str]): The arguments provided for the command.
    
    Raises:
        ValueError: If required arguments are missing.
    """
    command = commands.commands[command_name]
    
    # Check if we have enough arguments
    required_args_count = len([arg for arg in command.arguments if not arg.is_optional])
    if len(args) < required_args_count:
        game_state.ui.error_message(f"Missing required arguments for command '{command_name}'.")
        return
    
    # Map provided arguments to command parameters
    arg_dict = {}
    for i, arg in enumerate(command.arguments):
        if i < len(args):
            arg_dict[arg.name] = args[i]
        elif arg.is_optional:
            arg_dict[arg.name] = ""
        else:
            raise ValueError(f"Missing required argument: {arg.name}")
    
    # Execute the command
    command.function(game_state, **arg_dict)


@dataclass
class Argument:
    name: str
    type: type
    is_optional: bool
    positional_index: int | None = None
    custom_validator: Callable[[Any], bool] | None = None

@dataclass
class Command:
    """
    Represents a command that can be executed in the game.
    arguments: list[Argument] = field(default_factory=list)
        function (Callable): The function to execute for this command.
        arguments (list[Argument]): The list of arguments required by the command.
        number_of_arguments (int): The number of arguments required by the command.
        command_name (str): The name of the command.
    """
    function: Callable
    arguments: list[Argument] = field(default_factory=list)
    number_of_arguments: int = field(init=False)
    command_name: str = ""

    def __post_init__(self):
        self.number_of_arguments = len(self.arguments)

    def get_optional_arguments(self):
        return [arg for arg in self.arguments if arg.is_optional]

    def validate_arguments(self, args):
        required_args = [arg for arg in self.arguments if not arg.is_optional]
        if len(args) < len(required_args):
            return False, "Not enough arguments provided."
        if len(args) > len(self.arguments):
            return False, "Too many arguments provided."

        for i, (arg, value) in enumerate(zip(self.arguments, args), start=1):
            if arg.type == int:
                if not self._is_valid_int(value):
                    return False, f"Argument {i} ({arg.name}) must be an integer."
            elif arg.type == float:
                if not self._is_valid_float(value):
                    return False, f"Argument {i} ({arg.name}) must be a float."
            elif arg.type == bool:
                if not self._is_valid_bool(value):
                    return (
                        False,
                        f"Argument {i} ({arg.name}) must be a boolean value (true/false or 1/0).",
                    )
            elif arg.type == str:
                pass
            else:
                if not value:
                    return False, f"Argument {i} ({arg.name}) cannot be empty."

        return True, ""

    @staticmethod
    def _is_valid_int(value):
        return is_valid_int(value)

    @staticmethod
    def _is_valid_float(value):
        return is_valid_float(value)

    @staticmethod
    def _is_valid_bool(value):
        return is_valid_bool(value)

    def __call__(self, *args: Any, game_state: "Game") -> Any:
        valid, message = self.validate_arguments(args)
        if not valid:
            raise ValueError(message)
        return self.function(*args, game_state=game_state)


@dataclass
class CommandRegistry:
    commands: dict[str, Command] = field(default_factory=dict)

    def register(self, name: str, command: Command):
        self.commands[name] = command
        command.command_name = name

    def unregister(self, command_name: str):
        self.commands.pop(command_name, None)

    def get_command(self, command_name: str) -> Optional[Command]:
        return self.commands.get(command_name)

    @staticmethod
    def execute(self, command: Command, *args, **kwargs):
        command.function(*args, **kwargs)


commands: "CommandRegistry" = CommandRegistry()


def typeof(value):
    return type(value)


def register_command(
    command_names: list[str],
    command_function: Callable,
    argument_list: list[Argument] | None = None,
):
    for name in command_names:
        argument_struct_list_with_index = []
        for i, arg in enumerate(argument_list or []):
            if arg.positional_index is None:
                # If positional_index is not set, create a new Argument with the index
                new_arg = Argument(
                    name=arg.name,
                    type=arg.type,
                    is_optional=arg.is_optional,
                    positional_index=i,
                    custom_validator=arg.custom_validator,
                )
                argument_struct_list_with_index.append(new_arg)
            else:
                # If positional_index is already set, use the original Argument
                argument_struct_list_with_index.append(arg)

        command = Command(
            function=command_function, arguments=argument_struct_list_with_index
        )
        commands.register(name, command)


def barter(price: float) -> tuple[float, bool]:
    """Handles the bartering process and returns the potentially discounted price as a float and a bartering success flag as a bool."""
    confirm = input("Want to barter for a discount? y/n")
    bartering_flag: bool = False  # Initialize the flag
    if confirm.lower() == "y":
        bartering_flag = True  # Set the flag to True if bartering is attempted
        rng_number: float = rnd_float(0, 1)
        if rng_number < 0.5:
            discount: int = rnd_int(10, 25)
            new_price: float = price * (100 - discount) / 100
            print(f"Bartered for {discount}% discount off the original price.")
            print(f"New price: {new_price} credits")
            return new_price, bartering_flag  # Return both values
        else:
            print("Bartering failed.")
    return price, bartering_flag  # Return original price and flag


def buy_command(game_state: "Game", item_name: str, amount: str):
    player_ship: Ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message("Must be docked to buy ore.")
        return

    station: Station | None = (
        game_state.solar_system.get_object_within_interaction_radius(player_ship)
    )

    if not station:
        game_state.ui.error_message("No station within interaction radius.")
        return
    try:
        amount_number = int(amount)
        if amount_number <= 0:
            game_state.ui.error_message("Quantity must be positive.")
            return
    except ValueError:
        game_state.ui.error_message("Invalid amount. Please enter a valid number.")
        return

    ore_cargo: OreCargo | None = station.get_ore_by_name(item_name)
    if not ore_cargo:
        game_state.ui.error_message(f"Cannot buy {item_name} because it is not available.")
        return

    total_volume = round(ore_cargo.ore.volume * amount_number, 2)
    available_volume = round(ore_cargo.quantity * ore_cargo.ore.volume, 2)
    price = round(ore_cargo.buy_price * amount_number, 2)

    game_state.ui.success_message(f"Price for {amount_number} {item_name}: {price} credits")

    price, _ = barter(price)

    if game_state.player_character is None or price > (
        game_state.player_character.credits if game_state.player_character else 0
    ):
        game_state.ui.error_message(f"Cannot buy {amount_number} {item_name} because you don't have enough credits.")
        return

    if total_volume > available_volume:
        game_state.ui.error_message(f"Cannot buy {amount_number} {item_name} because the station doesn't have enough ore in its cargo.")
        confirm = input(game_state.ui.format_text("Do you want to buy all available ore? y/n >> ", fg=Fore.YELLOW))
        if confirm.lower() == "y":
            amount_number = int(available_volume / ore_cargo.ore.volume)
            price = round(ore_cargo.buy_price * amount_number, 2)
            game_state.ui.success_message(f"Adjusting purchase to {amount_number} {item_name} for {price} credits.")
        else:
            game_state.ui.error_message("Buy cancelled.")
            return

    update_ore_quantities(
        game_state, ore_cargo, item_name, amount_number, price, station
    )


def update_ore_quantities(
    game_state,
    ore_cargo: OreCargo,
    ore_name: str,
    amount: int,
    price: float,
    station: Station | None = None,
) -> None:
    player_ship: Ship = game_state.get_player_ship()
    player_character = game_state.player_character

    if player_character is None:
        print("Error: Player character not found.")
        return
    if station:
        amount = min(amount, ore_cargo.quantity)
        ore_cargo.quantity -= amount
        station.ore_cargo_volume -= round(amount * ore_cargo.ore.volume, 2)

    ore_cargo_found = player_ship.get_ore_cargo_by_id(ore_cargo.ore.id)

    if ore_cargo_found:
        ore_cargo_found.quantity += amount
    else:
        player_ship.cargohold.append(
            OreCargo(ore_cargo.ore, amount, ore_cargo.buy_price, ore_cargo.sell_price)
        )

    player_ship.cargohold = [
        cargo for cargo in player_ship.cargohold if cargo.quantity > 0
    ]
    player_ship.calculate_cargo_occupancy()

    if station:
        player_character.credits -= price
        print(f"Report: {amount} {ore_name} bought for {price} credits.")
        print(f"Station Ore Report:\n{station.ore_cargo_volume} tons of ore remaining")
        print(f"Your new credit balance: {player_character.credits} credits")
    else:
        print(f"Updated player ship cargo with {amount} {ore_name}.")


def travel_command(game_state: "Game", **kwargs) -> float:
    global_time: float = game_state.global_time
    player_ship: Ship = game_state.get_player_ship()

    if player_ship.is_docked:
        game_state.ui.error_message("Cannot travel while docked.")
        return global_time

    if player_ship.fuel == 0:
        game_state.ui.error_message("Cannot travel while out of fuel.")
        return global_time

    if kwargs.get("sort_type") == "closest":
        try:
            closest_travel(game_state, kwargs.get("object_type", ""))
        except IndexError:
            game_state.ui.error_message(
                "Invalid argument. Please enter 'closest' followed by 'field' or 'station'."
            )
    else:
        game_state.ui.error_message(
            "Invalid argument. Please enter 'closest' to travel to the closest field or station."
        )

    return global_time


def refuel_command(game_state: "Game", amount: float) -> None:
    player_ship: Ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    if not player_ship.is_docked:
        game_state.ui.error_message("Cannot refuel while not docked.")
        return

    station: Station | None = (
        game_state.solar_system.get_object_within_interaction_radius(game_state)
    )
    if station is None:
        game_state.ui.error_message("No station within interaction radius.")
        return

    if player_ship.fuel + amount > player_ship.max_fuel:
        game_state.ui.error_message(
            "Cannot refuel more than your ship's maximum fuel capacity, consider upgrading your ship."
        )
        return

    price: float = amount * station.fuel_price
    game_state.ui.info_message(f"Total price for {round(amount, 2)}m³ of fuel: {round(price, 2)} credits.")
    game_state.ui.warn_message("Are you sure you want to refuel? y/n")
    confirm: str = take_input(">> ")
    if confirm.lower() != "y":
        game_state.ui.info_message("Refuel cancelled.")
        return

    player_ship.refuel(amount)
    if game_state.player_character:
        game_state.player_character.credits -= price
    game_state.ui.success_message(f"Refueled with {round(amount, 2)} m3 for {round(price, 2)} credits.")


def sell_command(game_state: "Game") -> None:
    if (
        game_state.get_player_ship() is None
        or not game_state.get_player_ship().is_docked
    ):
        game_state.ui.error_message("Cannot sell while not docked.")
        return

    station = game_state.solar_system.get_object_within_interaction_radius(
        game_state.get_player_ship()
    )
    if station.ore_cargo_volume >= station.ore_capacity:
        game_state.ui.error_message(
            "Cannot sell because the station's ore cargo is full. Look for another one."
        )
        return

    sellable_ores = [
        ore_cargo
        for ore_cargo in game_state.get_player_ship().cargohold
        if ore_cargo.quantity > 0
        and ore_cargo.ore.id in [ore.id for ore in station.ores_available]
        and ore_cargo.ore.volume <= station.ore_capacity - station.ore_cargo_volume
    ]

    if not sellable_ores:
        game_state.ui.warn_message("No ores to sell.")
        return

    total_value = sum(
        ore_cargo.quantity * ore_cargo.sell_price for ore_cargo in sellable_ores
    )
    total_volume = sum(
        ore_cargo.quantity * ore_cargo.ore.volume for ore_cargo in sellable_ores
    )
    total_units = sum(ore_cargo.quantity for ore_cargo in sellable_ores)

    game_state.ui.info_message("Ores to be sold:")
    for ore_cargo in sellable_ores:
        print(game_state.ui.format_text(ore_cargo.ore.to_string(), fg=Fore.CYAN))

    print(game_state.ui.format_text(f"Total value: {total_value:.2f} credits", fg=Fore.GREEN))
    print(game_state.ui.format_text(f"Total volume: {total_volume:.2f} m³", fg=Fore.CYAN))
    print(game_state.ui.format_text(f"Total units: {total_units}", fg=Fore.CYAN))

    confirm = input(game_state.ui.format_text("Are you sure you want to sell these ores? (y/n) ", fg=Fore.YELLOW))
    if confirm.lower() != "y":
        game_state.ui.info_message("Sell cancelled.")
        return

    if not game_state.player_character:
        game_state.ui.error_message("Error: Player character not found.")
        return

    game_state.player_character.credits += total_value
    station.ore_cargo_volume += total_volume

    game_state.get_player_ship().cargohold = [
        cargo for cargo in game_state.get_player_ship().cargohold if cargo.quantity > 0
    ]
    game_state.get_player_ship().calculate_cargo_occupancy()

    game_state.ui.success_message(f"Sold {total_units} units for {total_value:.2f} credits.")


def closest_travel(game_state: "Game", object_type: str) -> None:
    player_ship: Ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    try:
        closest_field: AsteroidField = get_closest_field(
            game_state.solar_system,
            player_ship.space_object.get_position(),
            game_state.solar_system.is_object_within_an_asteroid_field_radius(
                player_ship.space_object.get_position()
            )
            is not None,
        )
        closest_station: Station = get_closest_station(
            game_state.solar_system,
            player_ship,
            game_state.solar_system.get_object_within_interaction_radius(player_ship)
            is not None,
        )

        if not object_type:
            game_state.ui.info_message(
                f"Closest field is Field {closest_field.space_object.id} at {euclidean_distance(player_ship.space_object.get_position(), closest_field.space_object.position)} AUs from here."
            )
            game_state.ui.info_message(
                f"Closest station is Station {closest_station.space_object.id} at {euclidean_distance(player_ship.space_object.get_position(), closest_station.space_object.position)} AUs from here."
            )
            prompt_for_closest_travel_choice(
                player_ship, closest_field, closest_station, game_state.global_time
            )

        elif object_type in ["field", "f"]:
            field_position: Vector2 = closest_field.space_object.position
            assert player_ship is not None
            player_ship.travel(game_state, field_position)

        elif object_type in ["station", "s"]:
            station_position: Vector2 = closest_station.space_object.position
            assert player_ship is not None
            player_ship.travel(game_state, station_position)
        else:
            raise ValueError("Invalid object type. Use 'field' or 'station'.")
    except (AttributeError, ValueError) as e:
        game_state.ui.error_message(f"Error: {e}")


def direct_travel_command(game_state: "Game", destination_x: str, destination_y: str):
    player_ship: Ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    try:
        x = float(destination_x)
        y = float(destination_y)
    except ValueError:
        game_state.ui.error_message("Invalid coordinates. Please enter valid numbers.")
        return

    if (
        x < -game_state.solar_system.size
        or y < -game_state.solar_system.size
        or x >= game_state.solar_system.size
        or y >= game_state.solar_system.size
    ):
        game_state.ui.error_message(
            f"Invalid coordinates. Please enter coordinates within the solar system's bounds (-{game_state.solar_system.size} <= x < {game_state.solar_system.size}, -{game_state.solar_system.size} <= y < {game_state.solar_system.size})."
        )
        return

    # if game_state.solar_system.is_object_at_position(Vector2(x, y)):
    #     print("Cannot travel to occupied coordinates.")
    #     return

    player_ship.travel(game_state, Vector2(x, y))


def mine_command(
    game_state: "Game",
    time_to_mine: int,
    mine_until_full: bool,
    ore_selected: str | None,
) -> None:
    player_ship: Ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    if not game_state.solar_system.is_object_within_an_asteroid_field_radius(
        player_ship.space_object.get_position()
    ):
        game_state.ui.error_message("You must be within an asteroid field to mine.")
        return

    try:
        asteroid_field = game_state.solar_system.get_field_by_position(
            player_ship.space_object.get_position()
        )

        selected_ores = [ore_selected] if ore_selected else None

        player_ship.mine_belt(
            game_state, asteroid_field, time_to_mine, mine_until_full, selected_ores
        )

    except ValueError:
        game_state.ui.error_message("Invalid time. Please enter a valid number.")


def command_dock(game_state) -> None:
    game: Game = game_state
    player_ship: Ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    if player_ship.is_docked:
        game_state.ui.info_message("You are already docked.")
        return
    target_station: Station | None = helpers.get_closest_station(
        game_state.solar_system, player_ship
    )
    if target_station is None:
        game_state.ui.error_message("There are no stations within range.")
        return
    if target_station.space_object.position.distance_to(player_ship.space_object.position) > player_ship.interaction_radius:
        game_state.ui.error_message(f"Station is not within docking range (must be within {player_ship.interaction_radius} AUs).")
        return
    on_dock_complete(game_state, station_to_dock=target_station)


def on_dock_complete(game_state, station_to_dock: Station) -> None:
    game: Game = game_state
    player_ship: Ship = game_state.get_player_ship()
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


def command_undock(game_state) -> None:
    game: Game = game_state
    player_ship: Ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    if not player_ship.is_docked:
        game_state.ui.error_message("You are not docked.")
        return

    def on_undock_complete() -> None:
        player_ship.undock_from_station()
        game_state.ui.success_message("Undocked.")

    on_undock_complete()

def scan_command(game_state, num_objects: str):
    amount_of_objects: int = int(num_objects)
    game_state.ui.info_message(f"Scanning for {amount_of_objects} objects...")
    player_ship: Ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    objects: list[Station | AsteroidField] = (
        game_state.solar_system.scan_system_objects(
            player_ship.space_object.get_position(), amount_of_objects
        )
    )
    for i in range(amount_of_objects):
        print(game_state.ui.format_text(
            f"{i}. {objects[i].to_string_short(player_ship.space_object.get_position())}",
            fg=Fore.CYAN
        ))

    game_state.ui.warn_message("Enter object to navigate to or -1 to abort:")
    input_response: str = input(
        game_state.ui.format_text("Enter the number of the object to navigate to or -1 to abort: ", fg=Fore.YELLOW)
    )

    if input_response == "-1":
        return
    else:
        try:
            input_response_index: int = int(input_response)
        except ValueError:
            game_state.ui.error_message("Invalid input. Please enter a valid number.")
            return
        selected_object: Station | AsteroidField = objects[input_response_index]
        selected_object_position: Vector2 = selected_object.space_object.position
        direct_travel_command(
            game_state, str(selected_object_position.x), str(selected_object_position.y)
        )


def add_ore_debug_command(game_state, amount: int, ore_name: str) -> None:
    game_state.ui.warn_message("This is a debug/cheat command: with great power comes great responsibility!")
    game: Game = game_state
    player_ship: Ship = game_state.get_player_ship()

    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return
    if amount < 0:
        game_state.ui.error_message("You have entered a negative number.")
        return

    ore: Ore | None = helpers.get_ore_by_id_or_name(ore_name)
    if ore is None:
        game_state.ui.error_message(f"Invalid ore name: {ore_name}")
        return

    total_volume = ore.volume * amount
    if total_volume > player_ship.cargohold_occupied:
        game_state.ui.warn_message("You are trying to add more cargo than your ship's capacity.")
        game_state.ui.warn_message("Since this is a debug command, i will allow you to do that.")

    ore_cargo: OreCargo = OreCargo(ore, amount, ore.base_value, ore.base_value)
    update_ore_quantities(game_state, ore_cargo, ore_name, amount, ore.base_value)
    display_status(game_state)


def add_creds_debug_command(game_state, amount: str) -> None:
    """Handles the add credits command.

    Args:
        game_state (Game): The game state instance for output.
        amount (str): The amount of credits to add as a string.
    """
    game: Game = game_state
    player_character: Character = game_state.get_player_character()
    
    try:
        amount_value = float(amount)
    except ValueError:
        game_state.ui.error_message("Invalid amount. Please enter a valid number.")
        return
        
    if player_character is None:
        game_state.ui.error_message("Error: Player character not found.")
        return
        
    game_state.ui.info_message(f"You are adding {amount_value} credits to your account.")
    
    if game_state.debug_flag:
        if amount_value < 0:
            game_state.ui.warn_message("You have entered a negative number, this means you lose money.")
            game_state.ui.warn_message("Are you sure? (y/n)")
            confirm = take_input(">> ").strip()
            if confirm != "y":
                return
        player_character.credits += amount_value
        game_state.ui.success_message(f"{amount_value} credits added to your credits.")
    else:
        game_state.ui.error_message(
            "Debug commands can only be used through the use of the 'debug' ('dm') command."
        )
        return


def display_status(game_state) -> None:
    game: Game = game_state
    player_character: Character = game_state.get_player_character()
    player_ship: Ship = game_state.get_player_ship()

    # Display Player Status with header
    print(game_state.ui.format_text("===== PLAYER STATUS =====", fg=Fore.CYAN, style=Style.BRIGHT))
    for status in player_character.to_string():
        print(game_state.ui.format_text(status, fg=Fore.GREEN))
    print()

    # Display Ship Status with header
    print(game_state.ui.format_text("===== SHIP STATUS =====", fg=Fore.CYAN, style=Style.BRIGHT))
    for status in player_ship.status_to_string():
        print(game_state.ui.format_text(status, fg=Fore.YELLOW))


def display_time_and_status(game_state) -> None:
    game: Game = game_state

    # Display time with styling
    print(game_state.ui.format_text(f"Time: {game_state.global_time} Seconds", fg=Fore.CYAN, style=Style.BRIGHT))
    print(game_state.ui.format_text("=================", fg=Fore.CYAN))

    # Display player character status
    player_character = game_state.get_player_character()
    if player_character:
        print(game_state.ui.format_text("Player Status:", fg=Fore.CYAN, style=Style.BRIGHT))
        for status in player_character.to_string():
            print(game_state.ui.format_text(status, fg=Fore.GREEN))
    else:
        game_state.ui.error_message("Error: Player character not found.")
    print("")

    # Display player ship status
    player_ship = game_state.get_player_ship()
    if player_ship:
        print(game_state.ui.format_text("Ship Status:", fg=Fore.CYAN, style=Style.BRIGHT))
        for status in player_ship.status_to_string():
            print(game_state.ui.format_text(status, fg=Fore.YELLOW))
    else:
        game_state.ui.error_message("Error: Player ship not found.")


def command_exit(game_state) -> None:
    """Exit the game_state.

    Args:
        game_state (Pygamegame_stateinal): The game_stateinal instance for output.
    """
    game_state.running = False


def clear(game_state):
    """Clear the game_stateinal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def scan_field_command(game_state) -> None:
    """Handles the scan field command."""
    game: Game = game_state
    player_ship: Ship = game_state.get_player_ship()
    player_ship.scan_field(game_state)


def debug_mode_command(game_state) -> None:
    """Handles the debug mode command."""
    game: Game = game_state
    if game_state.debug_flag:
        game_state.debug_flag = False
        game_state.ui.info_message("Debug mode disabled.")
    else:
        game_state.debug_flag = True
        game_state.ui.info_message("Debug mode enabled.")


def display_help(game_state: "Game", command_name: str):
    if not command_name:
        command_name = ""
    game_state.ui.info_message("Available commands (type 'help <command>' for more details):")

    game: Game = game_state
    player_ship: Ship = game_state.get_player_ship()
    station = game_state.solar_system.get_object_within_interaction_radius(player_ship)
    if station is not None:
        is_docked = player_ship.is_docked
    else:
        is_docked = False
    field = game_state.solar_system.get_field_by_position(
        player_ship.space_object.get_position()
    )

    location = (
        "field" if field is not None else "station" if station is not None else "none"
    )

    def write_command(command, description, allowed: bool):
        if allowed:
            print(game_state.ui.format_text(f"{command}: {description}", fg=Fore.GREEN))
        else:
            print(game_state.ui.format_text(command, fg=Fore.RED) + f": {description}")

    write_command(
        "status (st) <selection_flag>",
        "Displays your current credits, ship status (fuel, cargo, location), and time elapsed.",
        True,
    )
    write_command(
        "scan (sc) <quantity>", "Scan for nearby asteroid fields and stations.", True
    )
    write_command(
        "scan_field (scf)", "Scan for nearby asteroid fields and stations.", True
    )
    write_command(
        "travel (tr) closest <field|station>",
        "Travel to the closest asteroid field or station.",
        True,
    )
    write_command(
        "direct_travel (dtr) <x> <y>",
        "Travel to specific coordinates in the solar system.",
        True,
    )
    write_command(
        "mine (mi) <time> <until_full> <ore_name: optional>",
        "Mine for ores at the current asteroid field.",
        True if location == "field" else False,
    )
    write_command(
        "dock (do)", "Dock with the nearest station.", True if not is_docked else False
    )
    write_command(
        "undock (ud)", "Undock from the current station.", True if is_docked else False
    )
    write_command(
        "buy (by) <ore_name> <amount>",
        "Buy ores from the docked station.",
        True if is_docked else False,
    )
    write_command(
        "sell (sl)", "Sell ores at the docked station.", True if is_docked else False
    )
    write_command(
        "refuel (ref) <amount>",
        "Refuel your ship at the docked station.",
        True if is_docked else False
    )
    write_command(
        "upgrade", "View and purchase ship upgrades.", True if is_docked else False
    )
    write_command(
        "color (co) <bg|fg> <color_name>", "Change the game_stateinal colors.", True
    )
    write_command(
        "reset (rs) <color|bg|fg|text|history|all>",
        "Reset game_stateinal settings.",
        True,
    )
    write_command("clear (cl)", "Clear the game_stateinal screen.", True)
    write_command("debug (dm)", "Enable the Debug Mode", True)
    write_command("toggle_sound (ts)", "Enable or disable the game's sound.", True)
    write_command(
        "add_credits (ac)",
        "Add credits to your account (debug mode command)",
        game_state.debug_flag,
    )
    write_command(
        "add_ores (ao)",
        "Add ores to your ship (debug mode command)",
        game_state.debug_flag,
    )
    write_command("exit", "Exit the game_state.", True)

    if command_name:
        command_name = command_name.lower()
        if command_name == "status" or command_name == "st":
            print(game_state.ui.format_text("status (st):", fg=Fore.CYAN))
            print(
                "  Displays your current credits, ship status (fuel, cargo, location), and time elapsed."
            )
            print("  Options:")
            print(
                "    selection_flag: (optional) 'player', 'ship', or 'both' (default is 'both')."
            )
            print("    Example: status both")
        elif command_name == "scan" or command_name == "sc":
            print(game_state.ui.format_text("scan (sc) <quantity>:", fg=Fore.CYAN))
            print(
                "  Scans for the specified number of nearby asteroid fields and stations."
            )
            print("  Example: scan 5")
        elif command_name == "travel" or command_name == "tr":
            print(game_state.ui.format_text("travel (tr) closest <field|station>:", fg=Fore.CYAN))
            print("  Travels to the closest asteroid field or station.")
            print("  Example: travel closest field")
        elif command_name == "direct_travel" or command_name == "dtr":
            print(game_state.ui.format_text("travel_direct (dtr) <x> <y>:", fg=Fore.CYAN))
            print("  Travels to the specified coordinates in the solar system.")
            print("  Example: travel 10.5 20.3")
        elif command_name == "mine" or command_name == "mi":
            print(game_state.ui.format_text("mine (mi) <time>:", fg=Fore.CYAN))
            print(
                "  Mines for ores at the current asteroid field for the specified amount of time, if you want to mine until full, you can do so by adding 'until_full'."
            )
            print(
                "  If you want to mine for a specific ore, you can add the ore name to the command."
            )
            print("  You must be within an asteroid field to mine.")
            print("  Options:")
            print("    time: The amount of time to mine for in seconds.")
            print(
                "    until_full: If you want to mine until the cargo hold is full, you can do so by adding 'until_full'."
            )
            print(
                "    ore_name: If you want to mine for a specific ore, you can add the ore name to the command."
            )
            print("  Example: mine 60 until_full")
            print("  Example: mine 60 Pyrogen")
        elif command_name == "dock" or command_name == "do":
            print(game_state.ui.format_text("dock (do):", fg=Fore.CYAN))
            print("  Docks with the nearest station if you are within range.")
        elif command_name == "undock" or command_name == "ud":
            print(game_state.ui.format_text("undock (ud):", fg=Fore.CYAN))
            print("  Undocks from the current station.")
        elif command_name == "buy" or command_name == "by":
            print(game_state.ui.format_text("buy (by) <ore_name> <amount>:", fg=Fore.CYAN))
            print("  Buys the specified amount of ore from the docked station.")
            print("  Example: buy Pyrogen 10")
        elif command_name == "sell" or command_name == "sl":
            print(game_state.ui.format_text("sell (sl):", fg=Fore.CYAN))
            print("  Sells all ores in your cargo hold to the docked station.")
        elif command_name == "refuel" or command_name == "ref":
            print(game_state.ui.format_text("refuel (ref) <amount>:", fg=Fore.CYAN))
            print(
                "  Refuels your ship with the specified amount of fuel at the docked station."
            )
            print("  Example: refuel 50")
        elif command_name == "upgrade":
            print(game_state.ui.format_text("upgrade:", fg=Fore.CYAN))
            print("  Displays available ship upgrades and allows you to purchase them.")
        elif command_name == "color" or command_name == "co":
            print(game_state.ui.format_text("color (co) <bg|fg> <color_name>:", fg=Fore.CYAN))
            print("  Changes the game_stateinal's background or foreground color.")
            print(
                "  Available colors: black, white, red, green, blue, yellow, magenta, cyan"
            )
            print("  Example: color bg blue")
        elif command_name == "reset" or command_name == "rs":
            print(game_state.ui.format_text("reset (rs) <color|bg|fg|text|history|all>:", fg=Fore.CYAN))
            print("  Resets various aspects of the game_stateinal.")
            print("  Options:")
            print("    color: Resets both foreground and background colors.")
            print("    bg: Resets the background color.")
            print("    fg: Resets the foreground color.")
            print("    text: Clears the game_stateinal screen.")
            print("    history: Clears the command history.")
            print("    all: Resets all game_stateinal settings.")
        elif command_name == "clear" or command_name == "cl":
            print(game_state.ui.format_text("clear (cl):", fg=Fore.CYAN))
            print("  Clears the game_stateinal screen.")
        elif command_name == "debug" or command_name == "dm":
            print(game_state.ui.format_text("debug (dm):", fg=Fore.CYAN))
            print("  Enables or Disables the Debug Mode.")
        elif command_name == "toggle_sound" or command_name == "ts":
            print(game_state.ui.format_text("toggle_sound (ts):", fg=Fore.CYAN))
            print("  Toggles the game's sound effects and music on or off.")
        elif command_name == "add_credits" or command_name == "ac":
            print(game_state.ui.format_text("add_credits (ac):", fg=Fore.CYAN))
            print("  Adds the specified amount of credits to your account.")
            print("  Example: add_credits 100")
            print("  Needs Debug Mode to be Enabled")
        elif command_name == "add_ores" or command_name == "ao":
            print(game_state.ui.format_text("add_ores (ao):", fg=Fore.CYAN))
            print("  Adds the specified amount of ores to your account.")
            print("  Example: add_ores 100 Pyrogen")
            print("  Needs Debug Mode to be Enabled")
        elif command_name == "exit":
            print(game_state.ui.format_text("exit:", fg=Fore.CYAN))
            print("  Exits the game_state.")
        else:
            print(Fore.RED + f"Unknown command: {command_name}" + Style.RESET_ALL)
