from dataclasses import dataclass

import helpers
from helpers import take_input, rnd_float
from ore import Ore

@dataclass
class OreCargo:
    ore: Ore
    quantity: int
    price: float

class Station:
    def __init__(self, name, station_id, position):
        self.name = name
        self.position = position
        self.id = station_id
        self.fueltank_cap = helpers.rnd_float(5_000, 20_000)
        self.fueltank = self.fueltank_cap / helpers.rnd_int(1, 4)
        self.fuel_price = helpers.rnd_float(8, 20)
        self.ores_available: list[Ore] = []
        self.ore_cargo: list[OreCargo] = []  # ore, quantity, price
        self.ore_cargo_volume = 0.0
        self.ore_capacity = helpers.rnd_float(25_000, 75_000)
        self.generate_ores_availability()
        self.generate_ore_cargo_instances()
        self.generate_ore_cargo()

    def get_ore_price(self, ore_name):
        for ore_cargo in self.ore_cargo:
            if ore_cargo.ore.name == ore_name:
                return ore_cargo.price

    def is_ore_available(self, ore_to_check: OreCargo):
        for ore_cargo in self.ore_cargo:
            if ore_cargo.ore.id == ore_to_check.ore.id:
                return True
        return False

    def generate_ores_availability(self):
        selected = []
        for _ in range(5):
            selected.append(helpers.select_random_ore())

        self.ores_available = selected

    def generate_ore_cargo_instances(self):
        # create the OreCargo instances
        for ore in self.ores_available:
            ore_quantity: int = 0
            ore_price: float = ore.base_value * rnd_float(0.8, 1.2)
            ore_cargo = OreCargo(ore, ore_quantity, ore_price)

            self.ore_cargo.append(ore_cargo)
    def generate_ore_cargo(self):
        # Fill the cargo until the capacity is filled
        while self.ore_cargo_volume < self.ore_capacity:
            how_many_ore_types_available = len(self.ores_available)
            for ore_type in range(how_many_ore_types_available):
                self.ore_cargo[ore_type].quantity += 1
                self.ore_cargo_volume += self.ores_available[ore_type].volume

    def get_ore_by_name(self, name):
        for ore in self.ore_cargo:
            if ore.ore.name == name:
                return ore
    def calculate_cargo(self):
        occupancy = 0
        for ore_cargo in self.ore_cargo:
            occupancy += ore_cargo.quantity
        return occupancy

    def get_ore_price_to_string(self):
        string = ""
        for ore_cargo in self.ore_cargo:
            string += f"{ore_cargo.ore.name}: {ore_cargo.price}\n"
        return string

    def get_ore_info_to_string(self):
        string = ""
        for ore in self.ores_available:
            volume = ore.volume * self.ore_capacity
            string += f"{ore.name}: {volume} m³\n"
        return string

    def get_info(self):
        return f"{self.name} {self.position} {self.id} {self.fueltank_cap} {self.fueltank} {self.ore_cargo} {self.ore_cargo_volume} {self.ore_capacity} {self.fuel_price}"

    def to_string_short(self, position=None):
        if position is None:
            return f"{self.name}, Position: {self.position}, ID: {self.id}"
        return f"{self.name}, Position: {self.position}, ID: {self.id}, Distance: {self.position.distance(position):.3f} AU"

    def ores_available_to_string(self):
        return "\n".join([ore.to_string() for ore in self.ores_available])

    def to_string(self):
        return f"{self.name}\nPosition: {self.position}\nID: {self.id}\nFuel Tank: {self.fueltank}/{self.fueltank_cap}m³\nFuel price: {self.fuel_price} credits\n\nOre cargo: {self.ore_cargo} {self.ore_cargo_volume}/{self.ore_capacity}m³\n\nOre prices:\n{self.get_ore_price_to_string()}"

    def buy_fuel(self, player_ship, amount):
        print(f"Price: {amount * self.fuel_price} credits ({self.fuel_price} credits per m³)")
        response = take_input("Do you want to buy fuel? (y/n) ")
        if response != "y":
            return
        if player_ship.credits < amount * self.fuel_price:
            print("You don't have enough credits")
            return
        player_ship.credits -= amount * self.fuel_price
        player_ship.fueltank += amount
        self.fueltank -= amount
        print(f"You bought {amount} m³ of fuel for {amount * self.fuel_price} credits")
        print(f"You now have {player_ship.fueltank} m³ of fuel and {player_ship.credits} credits")
        print(f"The station has {self.fueltank} m³ of fuel left out of {self.fueltank_cap} m³")

    def sell_fuel(self, player_ship, amount):
        print(f"Price: {amount * self.fuel_price} credits ({self.fuel_price} credits per m³)")
        response = take_input("Do you want to sell fuel? (y/n) ")
        if response != "y":
            print("Fuel not sold")
            return
        if player_ship.fueltank < amount:
            print("You don't have enough fuel")
            return
        player_ship.fueltank -= amount
        player_ship.credits += amount * self.fuel_price
        self.fueltank += amount
        print(f"You sold {amount} m³ of fuel for {amount * self.fuel_price} credits")
        print(f"You now have {player_ship.fueltank} m³ of fuel and {player_ship.credits} credits")
        print(f"The station has {self.fueltank} m³ of fuel left out of {self.fueltank_cap} m³")

    def buy_ore(self, player_ship, amount):
        print(f"Price: {amount * self.ore_cargo[player_ship.ore]} credits ({self.ore_cargo[player_ship.ore]} credits per m³)")
        response = take_input("Do you want to buy ore? (y/n) ")
        if response != "y":
            return
        if player_ship.credits < amount * self.ore_cargo[player_ship.ore]:
            print("You don't have enough credits")
            return
        player_ship.credits -= amount * self.ore_cargo[player_ship.ore]
        player_ship.ore += amount
        self.ore_cargo -= amount
        self.ore_cargo_volume = self.calculate_cargo()
        print(f"You bought {amount} m³ of ore for {amount * self.ore_cargo[player_ship.ore]} credits")
        print(f"You now have {player_ship.ore} m³ of ore and {player_ship.credits} credits")
        print(f"The station has {self.ore_cargo} m³ of ore left out of {self.ore_capacity} m³")

    def sell_ore(self, player_ship, amount):
        print(f"Price: {amount * self.ore_cargo[player_ship.ore]} credits ({self.ore_cargo[player_ship.ore]} credits per m³)")
        response = take_input("Do you want to sell ore? (y/n) ")
        if response != "y":
            return
        if player_ship.ore < amount:
            print("You don't have enough ore")
            return
        player_ship.credits += amount * self.ore_cargo[player_ship.ore]
        player_ship.ore -= amount
        self.ore_cargo += amount
        self.ore_cargo_volume = self.calculate_cargo()
        print(f"You sold {amount} m³ of ore for {amount * self.ore_cargo[player_ship.ore]} credits")
        print(f"You now have {player_ship.ore} m³ of ore and {player_ship.credits} credits")
        print(f"The station has {self.ore_cargo} m³ of ore left out of {self.ore_capacity} m³")