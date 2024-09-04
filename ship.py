from pygame import Vector2
from asteroid import Asteroid
from helpers import euclidean_distance, vector_to_string, take_input
from station import Station
from data import OreCargo

class Ship:
    def __init__(self, position: Vector2, speed, max_fuel, fuel_consumption, cargo_capacity, value, mining_speed, name):
        self.position: Vector2 = position  # in AU
        self.speed: float = speed  # in AU/s
        self.fuel: float = max_fuel  # in m3
        self.max_fuel: float = max_fuel  # in m3
        self.fuel_consumption: float = fuel_consumption  # in m3/AU
        self.cargohold: list[OreCargo] = []
        self.cargohold_occupied: float = 0
        self.cargohold_capacity: float = cargo_capacity
        self.value: float = value
        self.mining_speed: float = mining_speed
        self.interaction_radius: float = 0.001 # Radius around the player ship where it can interact with other objects
        self.is_docked: bool = False
        self.docked_at: Station | None = None
        self.ship_name: str = name
        self.calculate_volume_occupied(True)

    def set_ship_name(self, new_name):
        self.ship_name = new_name

    def dock_into_station(self, station):
        self.is_docked = True
        self.docked_at = station

    def undock_from_station(self):
        self.is_docked = False
        self.docked_at = None

    def consume_fuel(self, value):
        self.fuel -= value

    def move_unit(self):
        self.position.x += self.speed

    def move_to(self, destination):
        self.position = destination

    def refuel(self, value):
        self.fuel += value

    def calculate_travel_data(self, destination):
        distance = round(euclidean_distance(self.position, destination), 3)
        time = round(distance / self.speed, 3)
        fuel_consumed = round(distance * self.fuel_consumption, 3)
        return distance, time, fuel_consumed

    def travel(self, destination, current_time):
        distance, travel_time, fuel_consumed = self.calculate_travel_data(destination)

        print(f"The ship will travel {distance} AUs in {travel_time} seconds, using {fuel_consumed} fuel.")

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

    def status_to_string(self):
        ore_units_on_cargohold = sum([ore_cargo.quantity for ore_cargo in self.cargohold])
        return f"Ship Name: {self.ship_name}\nPosition: {vector_to_string(self.position)}\nSpeed: {self.speed}\nm/s Fuel: {round(self.fuel, 2)}/{self.max_fuel} m3\nCargohold: {round(self.cargohold_occupied, 2)}/{self.cargohold_capacity} m3\nAmount of Ores: {ore_units_on_cargohold}"

    def cargo_to_string(self):
        output = ""
        for ore_cargo in self.cargohold:
            output += f"{ore_cargo.quantity} units of {ore_cargo.ore.name}\n"
        return output

    def mine_belt(self, asteroid_field, time_to_mine):
        if len(asteroid_field.asteroids) == 0:
            print("This field is empty.")
            return

        if self.is_cargo_full():
            print("You have no cargo space left.")
            return

        asteroid_being_mined: Asteroid | None = None
        ores_mined: list[OreCargo] = []
        time_spent = 0

        while time_spent < time_to_mine:
            if self.is_cargo_full():
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
                print("In the future you may be able to try again with another ore.")
                break

            # Mine the ore
            ore_cargo = next((cargo for cargo in ores_mined if cargo.ore.id == ore.id), None)
            if ore_cargo:
                ore_cargo.quantity += 1
            else:
                ores_mined.append(OreCargo(ore, 1, ore.base_value))

            asteroid_being_mined.volume -= ore.volume
            self.cargohold_occupied += ore.volume
            time_spent += 1

        total_volume = sum(ore_cargo.quantity * ore_cargo.ore.volume for ore_cargo in ores_mined)
        total_quantity = sum(ore_cargo.quantity for ore_cargo in ores_mined)
        ore_names = {ore.ore.name for ore in ores_mined}

        # Update ship
        for ore_cargo in ores_mined:
            existing_cargo = next((cargo for cargo in self.cargohold if cargo.ore.id == ore_cargo.ore.id), None)
            if existing_cargo:
                existing_cargo.quantity += ore_cargo.quantity
            else:
                self.cargohold.append(ore_cargo)

        if total_quantity > 0:
            print(f"Mined {total_quantity} units of {', '.join(ore_names)} for {round(total_volume, 2)} m³")
        else:
            print("No ores were mined.")

        self.calculate_volume_occupied(silence_flag=True)
        print(f"Time spent mining: {time_spent} seconds.")
        return time_spent

    def calculate_volume_occupied(self, silence_flag=False):
        total_volume = 0
        for ore_cargo in self.cargohold:
            total_volume += ore_cargo.quantity * ore_cargo.ore.volume
        self.cargohold_occupied = total_volume
        if not silence_flag:
            print(f"The ship has occupied {self.cargohold_occupied} m3 of cargohold.")

    def is_cargo_full(self) -> bool:
        return self.cargohold_occupied == self.cargohold_capacity