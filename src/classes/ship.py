from dataclasses import dataclass
from typing import Optional, Tuple

from pygame import Vector2

from src.classes.asteroid import Asteroid, AsteroidField
from src.classes.station import Station
from src.data import OreCargo
from src.helpers import euclidean_distance, vector_to_string, format_seconds


class IsSpaceObject:
    
    def __init__(self, position: Vector2, id: int) -> None:
        self.position: Vector2 = position
        self.id: int = id

    def get_position(self) -> Vector2:
        return self.position

    def set_position(self, new_position: Vector2) -> None:
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
    ship_id_counter: int = 0
    def __init__(
        self,
        name: str,
        position: Vector2,
        speed,
        max_fuel,
        fuel_consumption,
        cargo_capacity,
        value,
        mining_speed,
    ):
        self.name = name
        self.space_object = IsSpaceObject(position, self.ship_id_counter)
        self.moves = CanMove(speed)  # in AU/s
        self.fuel = max_fuel  # in m3
        self.max_fuel = max_fuel  # in m3
        self.fuel_consumption = fuel_consumption  # in m3/AU
        self.cargohold: list = []
        self.cargohold_occupied: float = 0
        self.cargohold_capacity = cargo_capacity
        self.value = value
        self.mining_speed = mining_speed
        self.interaction_radius = 0.001  # Radius around the player ship where it can interact with other objects
        self.is_docked = False
        self.docked_at: Station | None = None
        self.calculate_cargo_occupancy()

    def get_ore_cargo_by_id(self, ore_id: int) -> OreCargo | None:
        return next((cargo for cargo in self.cargohold if cargo.ore.id == ore_id), None)

    def set_name(self, new_name):
        self.name = new_name

    def dock_into_station(self, station: Station):
        assert station is not None
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

    def travel(self, game_state, destination: Vector2):
        distance, travel_time, fuel_consumed = self.calculate_travel_data(destination)

        print(
            f"The ship will travel {distance} AUs in {format_seconds(travel_time)} using {fuel_consumed} fuel."
        )

        if self.fuel - fuel_consumed < 0:
            print("Not enough fuel to travel. Please refuel.")
            return

        confirm = input(f"Confirm travel? (y/n) ")

        if confirm != "y":
            print("Travel cancelled.")
            return

        self.consume_fuel(fuel_consumed)
        self.space_object.position = destination
        game_state.global_time += travel_time

        print(f"The ship has arrived at {vector_to_string(destination)}")

    def status_to_string(self) -> list[str]:
        ore_units_on_cargohold = sum(cargo.quantity for cargo in self.cargohold)
        docked_at_name = "Not docked" if self.docked_at is None else self.docked_at.name
        return [
            f"Ship Name: {self.name}",
            f"Position: {vector_to_string(self.space_object.get_position())}",
            f"Speed: {self.moves.speed:.2f} AU/s",
            f"Fuel: {self.fuel:.2f}/{self.max_fuel} m3",
            f"Cargohold: {self.cargohold_occupied:.2f}/{self.cargohold_capacity} m3",
            f"Amount of Ores: {ore_units_on_cargohold}",
            f"Docked at: {docked_at_name}",
        ]

    def cargo_to_string(self):
        return "\n".join(
            f"{cargo.quantity} units of {cargo.ore.name}" for cargo in self.cargohold
        )

    def get_docked_station(self) -> Station | None:
        return self.docked_at

    def mine_belt(
            self,
            game_state,
            asteroid_field: AsteroidField,
            time_to_mine: int,
            mine_until_full: bool,
            ores_selected_list: list[str] | None,
    ):
        # Ensure the asteroid field contains asteroids
        if not asteroid_field.asteroids:
            print("This field is empty.")
            return

        # Check if the cargo is already full
        if self.is_cargo_full():
            print("You have no cargo space left.")
            return

        # Validate ores if a list of selected ores is provided
        if ores_selected_list:
            available_ores = {ore.name.lower() for ore in asteroid_field.ores_available}
            invalid_ores = [
                ore for ore in ores_selected_list if ore.lower() not in available_ores
            ]
            if invalid_ores:
                print(
                    f"The following ores are not available in this field: {', '.join(invalid_ores)}"
                )
                return
        else:
            print("No ores were selected. All available ores will be mined.")
            print("List of available ores: ")
            for ore in asteroid_field.ores_available:
                print(f"- {ore.name}")
            ores_selected_list = None

        # Initialize mining variables
        asteroid_being_mined: Asteroid | None = None
        ores_mined: list[OreCargo] = []
        mined_volume = 0
        time_spent = 0

        # Begin mining loop
        while (not mine_until_full and int(time_spent) < int(time_to_mine)) or (
                mine_until_full and not self.is_cargo_full()
        ):
            # Find a new asteroid to mine if needed
            if asteroid_being_mined is None or asteroid_being_mined.volume <= 0:
                asteroid_being_mined = next(
                    (
                        asteroid
                        for asteroid in asteroid_field.asteroids
                        if asteroid.volume > 0
                    ),
                    None,
                )
                if asteroid_being_mined is None:
                    print("No more asteroids available to mine.")
                    break

            # Access the ore in the asteroid
            ore = asteroid_being_mined.ore

            # If specific ores are selected, validate they match the current asteroid's ore
            if ores_selected_list is not None:
                if ore.name.lower() not in (ore_name.lower() for ore_name in ores_selected_list):
                    print(f"Skipping {ore.name}, as it is not in the selected ores list.")
                    asteroid_being_mined = None
                    break

            # Check if the ore fits in the remaining cargo capacity
            if self.cargohold_occupied + ore.volume > self.cargohold_capacity:
                print(
                    f"Cannot mine more {ore.name} because it exceeds the ship's cargo capacity."
                )
                break  # Stop mining if no further ores can be added safely

            # Add the ore to mined cargo
            ore_cargo = next(
                (cargo for cargo in ores_mined if cargo.ore.id == ore.id), None
            )
            if ore_cargo:
                ore_cargo.quantity += 1
            else:
                ores_mined.append(OreCargo(ore, 1, ore.base_value, ore.base_value))

            # Decrease the asteroid's volume and update ship's cargo data
            asteroid_being_mined.volume -= ore.volume
            self.cargohold_occupied += ore.volume
            mined_volume += self.mining_speed
            time_spent += 1

        # Summarize mined results
        total_volume = sum(cargo.quantity * cargo.ore.volume for cargo in ores_mined)
        total_quantity = sum(cargo.quantity for cargo in ores_mined)
        ore_names = {cargo.ore.name for cargo in ores_mined}

        # Update the ship's cargo hold with mined ores
        for ore_cargo in ores_mined:
            existing_cargo = self.get_ore_cargo_by_id(ore_cargo.ore.id)
            if existing_cargo:
                existing_cargo.quantity += ore_cargo.quantity
            else:
                self.cargohold.append(ore_cargo)

        if total_quantity > 0:
            print(
                f"Mined {total_quantity} units of {', '.join(ore_names)} for {total_volume:.2f} m³"
            )
        else:
            print("No ores were mined.")

        # Recalculate cargo occupancy and update global game time
        self.calculate_cargo_occupancy()
        print(f"Time spent mining: {time_spent} seconds.")
        game_state.global_time += time_spent

    def calculate_cargo_occupancy(self):
        self.cargohold_occupied = sum(
            cargo.quantity * cargo.ore.volume for cargo in self.cargohold
        )

    def is_cargo_full(self) -> bool:
        return self.cargohold_occupied == self.cargohold_capacity

    def check_field_presence(
            self, game_state
    ) -> Tuple[bool, Optional[AsteroidField]]:
        for field in game_state.solar_system.asteroid_fields:
            if self.interaction_radius > euclidean_distance(
                    self.space_object.position, field.space_object.position
            ):
                return True, field
        return False, None

    def scan_field(self, game_state):
        fields: list[AsteroidField] = game_state.solar_system.asteroid_fields

        is_inside_field, field = self.check_field_presence(game_state)

        if not is_inside_field or field is None:
            print("You are not inside a field.")
            return

        for ore in field.ores_available:
            print(f"{ore.name} - {ore.volume} m3")
