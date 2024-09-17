from dataclasses import dataclass
from typing import Optional, Tuple

from pygame import Vector2

from src.classes.asteroid import Asteroid, AsteroidField
from src.classes.ore import get_ore_by_name
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
        self.space_object = IsSystemObject(position, 0)
        self.moves = CanMove(speed)  # in AU/s
        self.fuel = max_fuel  # in m3
        self.max_fuel = max_fuel  # in m3
        self.fuel_consumption = fuel_consumption  # in m3/AU
        self.cargohold = []
        self.cargohold_occupied = 0
        self.cargohold_capacity = cargo_capacity
        self.value = value
        self.mining_speed = mining_speed
        self.interaction_radius = 0.001  # Radius around the player ship where it can interact with other objects
        self.is_docked = False
        self.docked_at = None
        self.ship_name = name
        self.calculate_cargo_occupancy()
    
    def get_ore_cargo_by_id(self, ore_id: int) -> OreCargo | None:
        return next((cargo for cargo in self.cargohold if cargo.ore.id == ore_id), None)

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
        self.space_object.position.x += self.moves.speed

    def refuel(self, value):
        self.fuel += value

    def calculate_travel_data(self, destination: Vector2):
        distance = round(euclidean_distance(self.space_object.position, destination), 3)
        time = round(distance / self.moves.speed, 3)
        fuel_consumed = round(distance * self.fuel_consumption, 3)
        return distance, time, fuel_consumed

    def travel(self, term: PygameTerminal, destination: Vector2):
        distance, travel_time, fuel_consumed = self.calculate_travel_data(destination)

        term.writeLn(f"The ship will travel {distance} AUs in {format_seconds(travel_time)} using {fuel_consumed} fuel.")

        if self.fuel - fuel_consumed < 0:
            term.writeLn("Not enough fuel to travel. Please refuel.")
            return

        confirm = term.prompt_user(f"Confirm travel? (y/n)")

        if confirm != "y":
            term.writeLn("Travel cancelled.")
            return

        self.consume_fuel(fuel_consumed)
        self.space_object.position = destination
        term.app_state.global_time += travel_time

        term.writeLn(f"The ship has arrived at {vector_to_string(destination)}")

    def status_to_string(self) -> list[str]:
        ore_units_on_cargohold = sum(cargo.quantity for cargo in self.cargohold)
        docked_at_name = 'Not docked' if self.docked_at is None else self.docked_at.name
        return [
            f"Ship Name: {self.ship_name}",
            f"Position: {vector_to_string(self.space_object.position)}",
            f"Speed: {self.moves.speed:.2f} AU/s",
            f"Fuel: {self.fuel:.2f}/{self.max_fuel} m3",
            f"Cargohold: {self.cargohold_occupied:.2f}/{self.cargohold_capacity} m3",
            f"Amount of Ores: {ore_units_on_cargohold}",
            f"Docked at: {docked_at_name}"
        ]

    def cargo_to_string(self, term: PygameTerminal):
        return "\n".join(f"{cargo.quantity} units of {cargo.ore.name}" for cargo in self.cargohold)

    def get_docked_station(self) -> Station | None:
        return self.docked_at

    def mine_belt(self, terminal: PygameTerminal, asteroid_field, time_to_mine, mine_until_full,
                  ores_selected_list: str | None):
        if not asteroid_field.asteroids:
            terminal.writeLn("This field is empty.")
            return

        if self.is_cargo_full():
            terminal.writeLn("You have no cargo space left.")
            return

        # Check if the specified ores are available in the asteroid field
        if ores_selected_list:
            available_ores = {ore.name.lower() for ore in asteroid_field.ores_available}
            invalid_ores = [ore for ore in ores_selected_list if ore.lower() not in available_ores]
            if invalid_ores:
                terminal.writeLn(f"The following ores are not available in this field: {', '.join(invalid_ores)}")
                return

        asteroid_being_mined: Asteroid | None = None
        ores_mined = []
        time_spent = 0
        mined_volume = 0

        while (not mine_until_full and time_spent < time_to_mine) or (mine_until_full and not self.is_cargo_full()):
            if asteroid_being_mined is None or asteroid_being_mined.volume <= 0:
                asteroid_being_mined = next((asteroid for asteroid in asteroid_field.asteroids if asteroid.volume > 0),
                                            None)
                if asteroid_being_mined is None:
                    terminal.writeLn("This field is empty.")
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
                    terminal.writeLn(
                        f"Cannot mine this ore because the {ore.name} ore is too voluminous for the ship's cargohold.")
                    terminal.writeLn("In the future you may be able to try again with another ore.")
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
            terminal.writeLn(f"Mined {total_quantity} units of {', '.join(ore_names)} for {total_volume:.2f} m³")
        else:
            terminal.writeLn("No ores were mined.")

        self.calculate_cargo_occupancy()
        terminal.writeLn(f"Time spent mining: {time_spent} seconds.")
        terminal.app_state.global_time += time_spent

    def calculate_cargo_occupancy(self):
        self.cargohold_occupied = sum(cargo.quantity * cargo.ore.volume for cargo in self.cargohold)

    def is_cargo_full(self) -> bool:
        return self.cargohold_occupied == self.cargohold_capacity

    def check_field_presence(self, term: PygameTerminal) -> Tuple[bool, Optional[AsteroidField]]:
        game = term.app_state

        for field in game.solar_system.asteroid_fields:
            if self.interaction_radius > euclidean_distance(self.space_object.position, field.position):
                return True, field
        return False, None

    def scan_field(self, term: PygameTerminal):
        """Scans the field and returns the ores available."""
        game = term.app_state
        fields: list[AsteroidField] = game.solar_system.asteroid_fields

        is_inside_field, field = self.check_field_presence(term)

        if not is_inside_field:
            term.writeLn("You are not inside a field.")
            return

        for ore in field.ores_available:
            term.writeLn(f"{ore.name} - {ore.volume} m3")
