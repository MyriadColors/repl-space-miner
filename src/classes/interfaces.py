from pygame import Vector2
from src.classes.asteroid import Asteroid
from src.helpers import euclidean_distance, vector_to_string, take_input, format_seconds
from src.classes.station import Station
from src.data import OreCargo

class ShipInterface:
    def __init__(self, name):
        self.ship_name: str = name

    def set_ship_name(self, new_name):
        self.ship_name = new_name

class CanMove:
    def __init__(self, position: Vector2, speed, max_fuel, fuel_consumption):
        self.position: Vector2 = position  # in AU
        self.speed: float = speed  # in AU/s
        self.fuel: float = max_fuel  # in m3
        self.max_fuel: float = max_fuel  # in m3
        self.fuel_consumption: float = fuel_consumption  # in m3/AU

    def consume_fuel(self, value):
        self.fuel -= value

    def calculate_travel_data(self, destination):
        distance = round(euclidean_distance(self.position, destination), 3)
        time = round(distance / self.speed, 3)
        fuel_consumed = round(distance * self.fuel_consumption, 3)
        return distance, time, fuel_consumed

    def move_to(self, destination):
        self.position = destination

    def travel(self, destination: Vector2, current_time: float):
        distance = round(euclidean_distance(self.position, destination), 3)
        travel_time = round(distance / self.speed, 3)
        fuel_consumed = round(distance * self.fuel_consumption, 3)

        print(f"The ship will travel {distance} AUs in {format_seconds(travel_time)} using {fuel_consumed} fuel.")

        if self.fuel - fuel_consumed < 0:
            print("Not enough fuel to travel. Please refuel.")
            return current_time

        confirm = take_input("Are you sure you want to travel? (y/n) ")

        if confirm != "y":
            print("Travel cancelled.")
            return current_time

        self.consume_fuel(fuel_consumed)
        self.move_to(destination)
        current_time += travel_time

        print(f"The ship has arrived at {vector_to_string(destination)}")

        return current_time

class HasCargoHold:
    def __init__(self, cargo_capacity):
        self.cargohold: list[OreCargo] = []
        self.cargohold_occupied: float = 0
        self.cargohold_capacity: float = cargo_capacity

    def calculate_volume_occupied(self, silence_flag=False):
        total_volume = sum(ore_cargo.quantity * ore_cargo.ore.volume for ore_cargo in self.cargohold)
        self.cargohold_occupied = total_volume
        if not silence_flag:
            print(f"The ship has occupied {self.cargohold_occupied} m3 of cargohold.")

    def is_cargo_full(self) -> bool:
        return self.cargohold_occupied == self.cargohold_capacity

    def cargo_to_string(self):
        output = ""
        for ore_cargo in self.cargohold:
            output += f"{ore_cargo.quantity} units of {ore_cargo.ore.name}\n"
        return output

    def get_ore_cargo_by_id(self, ore_id: int) -> (bool, OreCargo):
        for ore_cargo in self.cargohold:
            if ore_cargo.ore.id == ore_id:
                return True, ore_cargo
        return False, None

    def load_ore(self, ores_mined: list[OreCargo]):
        """Loads the mined ores into the cargohold."""
        for ore_cargo in ores_mined:
            existing_cargo = next((cargo for cargo in self.cargohold if cargo.ore.id == ore_cargo.ore.id), None)
            if existing_cargo:
                existing_cargo.quantity += ore_cargo.quantity
            else:
                self.cargohold.append(ore_cargo)
        self.calculate_volume_occupied()

class CanDock:
    def __init__(self):
        self.is_docked: bool = False
        self.docked_at: Station | None = None
        self.interaction_radius: float = 0.001

    def dock_into_station(self, station):
        self.is_docked = True
        self.docked_at = station

    def undock_from_station(self):
        self.is_docked = False
        self.docked_at = None


class CanMine:
    def __init__(self, cargohold_capacity):
        self.cargohold_occupied: float = 0
        self.cargohold_capacity: float = cargohold_capacity

    def mine_belt(self, asteroid_field, time_to_mine, is_cargo_full_func, load_ore_func):
        """Handles mining process."""
        if len(asteroid_field.asteroids) == 0:
            print("This field is empty.")
            return

        if is_cargo_full_func():
            print("You have no cargo space left.")
            return

        asteroid_being_mined: Asteroid | None = None
        ores_mined: list[OreCargo] = []
        time_spent = 0

        while time_spent < time_to_mine:
            if is_cargo_full_func():
                print("Your cargo is now full.")
                break

            if asteroid_being_mined is None or asteroid_being_mined.volume <= 0:
                asteroid_being_mined = next((asteroid for asteroid in asteroid_field.asteroids if asteroid.volume > 0),
                                            None)
                if asteroid_being_mined is None:
                    print("This field is empty.")
                    break

            ore = asteroid_being_mined.ore
            if self.cargohold_occupied + ore.volume > self.cargohold_capacity:
                print(f"Cannot mine this ore because the {ore.name} ore is too voluminous for the ship's cargohold.")
                break

            # Mine the ore
            ore_cargo = next((cargo for cargo in ores_mined if cargo.ore.id == ore.id), None)
            if ore_cargo:
                ore_cargo.quantity += 1
            else:
                ores_mined.append(OreCargo(ore, 1, ore.base_value))

            asteroid_being_mined.volume -= ore.volume
            time_spent += 1

        load_ore_func(ores_mined)

        if ores_mined:
            total_volume = sum(ore_cargo.quantity * ore_cargo.ore.volume for ore_cargo in ores_mined)
            total_quantity = sum(ore_cargo.quantity for ore_cargo in ores_mined)
            ore_names = {ore.ore.name for ore in ores_mined}
            print(f"Mined {total_quantity} units of {', '.join(ore_names)} for {round(total_volume, 2)} m³")
        else:
            print("No ores were mined.")

        print(f"Time spent mining: {time_spent} seconds.")
        return time_spent
