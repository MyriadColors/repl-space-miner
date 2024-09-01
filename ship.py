from helpers import euclidean_distance, vector_to_string, take_input
from ore import Ore
from station import Station


class Ship:
    def __init__(self, position, speed, max_fuel, fuel_consumption, cargo_capacity, value, mining_speed, name):
        self.position = position  # in AU
        self.speed = speed  # in AU/s
        self.fuel = max_fuel  # in m3
        self.max_fuel = max_fuel  # in m3
        self.fuel_consumption = fuel_consumption  # in m3/AU
        self.cargohold: list[Ore] = []
        self.cargohold_occupied = 0
        self.cargohold_capacity = cargo_capacity
        self.value = value
        self.mining_speed = mining_speed
        self.interaction_radius = 0.001 # Radius around the player ship where it can interact with other objects
        self.is_docked: bool = False
        self.docked_at: Station = None
        self.ship_name = name

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
        return f"Ship Name: {self.ship_name}\nPosition: {vector_to_string(self.position)}\nSpeed: {self.speed}\nm/s Fuel: {round(self.fuel, 2)}/{self.max_fuel} m3\nCargohold: {round(self.cargohold_occupied, 2)}/{self.cargohold_capacity} m3\nOres: {self.cargohold}"

    def mine_belt(self, asteroid_field, time_to_mine):
        if len(asteroid_field.asteroids) == 0:
            return "No asteroids in this field"

        ores_mined = []
        asteroid_being_mined = None
        list_of_ores_names = []

        while time_to_mine > 0:
            if asteroid_being_mined is None or asteroid_being_mined.volume <= 0:
                # Find the next available asteroid with ore
                for asteroid in asteroid_field.asteroids:
                    if asteroid.volume > 0:
                        asteroid_being_mined = asteroid
                        break

                if asteroid_being_mined is None:
                    return "This field seems to be depleted."

            ore = asteroid_being_mined.ore

            # Calculate ore yield based on mining speed
            ore_yield_per_second = min(self.mining_speed, asteroid_being_mined.volume)

            if self.cargohold_occupied + ore_yield_per_second > self.cargohold_capacity:
                available_capacity = self.cargohold_capacity - self.cargohold_occupied
                ore_yield_per_second = available_capacity  # Adjust yield to fit remaining capacity
                if ore_yield_per_second <= 0:
                    print("Not enough space in cargohold. Mining stopped.")
                    return f"Mining Report:\nOres mined: {ores_mined} of {set(list_of_ores_names) if len(list_of_ores_names) > 0 else 'none'} Ore\nVolume occupied: {round(self.cargohold_occupied, 2)}/{self.cargohold_capacity} m3"

            # Update list of ore names
            list_of_ores_names.append(ore.name)

            # Simulate adding ore to the cargohold
            for _ in range(int(ore_yield_per_second)):
                ores_mined.append(ore)  # Create new instances of the ore if necessary

            # Update the volume occupied in the cargohold and decrease asteroid volume
            self.cargohold_occupied += ore_yield_per_second
            asteroid_being_mined.volume -= ore_yield_per_second

            # Add ore to cargohold
            self.cargohold.extend([ore] * int(ore_yield_per_second))

            time_to_mine -= 1

        for ore in ores_mined:
            list_of_ores_names.append(ore.name)

        return f"Mining Report:\nOres mined: {len(ores_mined)} of {set(list_of_ores_names)} ores\nVolume occupied: {round(self.cargohold_occupied, 2)}/{self.cargohold_capacity} m3"

    def calculate_volume_occupied(self):
        total_volume = 0
        for ore in self.cargohold:
            total_volume += ore.volume
        self.cargohold_occupied = total_volume
        print(f"The ship has occupied {self.cargohold_occupied} m3 of cargohold.")