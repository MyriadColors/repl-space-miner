from dataclasses import dataclass

from pygame import Vector2

from src.classes.asteroid import Asteroid
from src.classes.station import Station
from src.data import OreCargo
from src.helpers import euclidean_distance, vector_to_string, format_seconds
from src.pygameterm.terminal import PygameTerminal


@dataclass
class IsSystemObject:
    position: Vector2
    id: int

    def get_position(self):
        return self.position

    def set_position(self, new_position):
        self.position = new_position

    def get_id(self):
        return self.id


@dataclass
class CanMove:
    speed: float

    def get_speed(self):
        return self.speed

    def set_speed(self, new_speed):
        self.speed = new_speed


class Ship:
    def __init__(self, position: Vector2, speed, max_fuel, fuel_consumption, cargo_capacity, value, mining_speed, name):
        self.space_object: IsSystemObject = IsSystemObject(position, 0)
        self.moves: CanMove = CanMove(speed)  # in AU/s
        self.fuel: float = max_fuel  # in m3
        self.max_fuel: float = max_fuel  # in m3
        self.fuel_consumption: float = fuel_consumption  # in m3/AU
        self.cargohold: list[OreCargo] = []
        self.cargohold_occupied: float = 0
        self.cargohold_capacity: float = cargo_capacity
        self.value: float = value
        self.mining_speed: float = mining_speed
        self.interaction_radius: float = 0.001  # Radius around the player ship where it can interact with other objects
        self.is_docked: bool = False
        self.docked_at: Station | None = None
        self.ship_name: str = name
        self.calculate_cargo_occupancy()

    def get_ore_cargo_by_id(self, ore_id: int) -> OreCargo | None:
        for ore_cargo in self.cargohold:
            if ore_cargo.ore.id == ore_id:
                return ore_cargo
        return None

    def set_ship_name(self, new_name):
        self.ship_name = new_name

    def dock_into_station(self, station: Station):
        self.is_docked = True
        self.docked_at = station

    def get_station_docked_at(self):
        return self.docked_at

    def undock_from_station(self):
        self.is_docked = False
        self.docked_at = None

    def consume_fuel(self, value):
        self.fuel -= value

    def move_unit(self):
        self.space_object.get_position().x += self.moves.get_speed()

    def refuel(self, value):
        self.fuel += value

    def calculate_travel_data(self, destination: Vector2):
        distance = round(euclidean_distance(self.space_object.get_position(), destination), 3)
        time = round(distance / self.moves.get_speed(), 3)
        fuel_consumed = round(distance * self.fuel_consumption, 3)
        return distance, time, fuel_consumed

    def travel(self, term: PygameTerminal, destination: Vector2):
        distance, travel_time, fuel_consumed = self.calculate_travel_data(destination)

        term.write(f"The ship will travel {distance} AUs in {format_seconds(travel_time)} using {fuel_consumed} fuel.")

        if self.fuel - fuel_consumed < 0:
            term.write("Not enough fuel to travel. Please refuel.")
            return

        confirm = term.prompt_user(f"Confirm travel? (y/n)")

        if confirm != "y":
            term.write("Travel cancelled.")
            return

        self.consume_fuel(fuel_consumed)
        self.space_object.set_position(destination)
        term.app_state.global_time += travel_time

        term.write(f"The ship has arrived at {vector_to_string(destination)}")

    def status_to_string(self) -> list[str]:
        ore_units_on_cargohold = sum([ore_cargo.quantity for ore_cargo in self.cargohold])
        docked_at: Station | None
        docked_at_name = 'Not docked' if self.docked_at is None else self.docked_at.name
        return [f"Ship Name: {self.ship_name}",
                f"Position: {vector_to_string(self.space_object.get_position())}",
                f"Speed: {format(self.moves.get_speed(), '2f')} AU/s",
                f"m/s Fuel: {round(self.fuel, 2)}/{self.max_fuel} m3",
                f"Cargohold: {round(self.cargohold_occupied, 2)}/{self.cargohold_capacity} m3",
                f"Amount of Ores: {ore_units_on_cargohold}",
                f"Docked at: {docked_at_name}"]

    def cargo_to_string(self, term: PygameTerminal):
        output = ""
        for ore_cargo in self.cargohold:
            output += f"{ore_cargo.quantity} units of {ore_cargo.ore.name}{term.new_line()}"
        return output

    def get_docked_station(self) -> Station | None:
        return self.docked_at

    def mine_belt(self, terminal: PygameTerminal, asteroid_field, time_to_mine, mine_until_full, ores_selected_list: str | None):
        if not asteroid_field.asteroids:
            terminal.write("This field is empty.")
            return

        if self.is_cargo_full():
            terminal.write("You have no cargo space left.")
            return

        # Check if the specified ores are available in the asteroid field
        if ores_selected_list:
            available_ores = {ore.name.lower() for ore in asteroid_field.ores_available}
            invalid_ores = [ore for ore in ores_selected_list if ore.lower() not in available_ores]
            if invalid_ores:
                terminal.write(f"The following ores are not available in this field: {', '.join(invalid_ores)}")
                return

        asteroid_being_mined: Asteroid | None = None
        ores_mined = []
        time_spent = 0
        mined_volume = 0

        while (not mine_until_full and time_spent < time_to_mine) or (mine_until_full and not self.is_cargo_full()):
            if asteroid_being_mined is None or asteroid_being_mined.volume <= 0:
                asteroid_being_mined = next((asteroid for asteroid in asteroid_field.asteroids if asteroid.volume > 0), None)
                if asteroid_being_mined is None:
                    terminal.write("This field is empty.")
                    break

            ore = asteroid_being_mined.ore
            ores_to_mine = []

            if ores_selected_list is not None:
                for ore_selected_name in ores_selected_list:
                    ore_selected = get_ore_by_name(ore_selected_name)
                    if ore_selected and ore_selected.id == ore.id:
                        ores_to_mine.append(ore_selected)
                    else:
                        continue

            if mined_volume >= ore.volume:
                if self.cargohold_occupied + ore.volume > self.cargohold_capacity:
                    terminal.write(f"Cannot mine this ore because the {ore.name} ore is too voluminous for the ship's cargohold.")
                    terminal.write("In the future you may be able to try again with another ore.")
                    break

                ore_cargo = next((cargo for cargo in ores_mined if cargo.ore.id == ore.id), None)
                if ore_cargo:
                    ore_cargo.quantity += 1
                else:
                    ores_mined.append(OreCargo(ore, 1, ore.base_value, ore.base_value))

                asteroid_being_mined.volume -= ore.volume
                self.cargohold_occupied += ore.volume
                mined_volume -= ore.volume

            mined_volume += self.mining_speed
            time_spent += 1

        total_volume = sum(cargo.quantity * cargo.ore.volume for cargo in ores_mined)
        total_quantity = sum(cargo.quantity for cargo in ores_mined)
        ore_names = {cargo.ore.name for cargo in ores_mined}

        for ore_cargo in ores_mined:
            existing_cargo = self.get_ore_cargo_by_id(ore_cargo.ore.id)
            if existing_cargo:
                existing_cargo.quantity += ore_cargo.quantity
            else:
                self.cargohold.append(ore_cargo)

        if total_quantity > 0:
            terminal.write(f"Mined {total_quantity} units of {', '.join(ore_names)} for {total_volume:.2f} m³")
        else:
            terminal.write("No ores were mined.")

        self.calculate_cargo_occupancy()
        terminal.write(f"Time spent mining: {time_spent} seconds.")
        terminal.app_state.global_time += time_spent

    def calculate_cargo_occupancy(self):
        total_volume: float = 0
        for ore_cargo in self.cargohold:
            total_volume += ore_cargo.quantity * ore_cargo.ore.volume
        self.cargohold_occupied = total_volume

    def is_cargo_full(self) -> bool:
        return self.cargohold_occupied == self.cargohold_capacity