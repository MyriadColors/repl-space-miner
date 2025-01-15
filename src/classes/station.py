from src import helpers
from src.classes.ore import Ore
from src.data import OreCargo
from src.helpers import take_input, rnd_float, rnd_int


class Station:
    def __init__(self, name, station_id, position) -> None:
        from src.classes.ship import IsSpaceObject
        self.name: str = name
        self.space_object = IsSpaceObject(position, station_id)
        self.fueltank_cap: float = helpers.rnd_float(5_000, 20_000)
        self.fueltank: float = self.fueltank_cap / helpers.rnd_int(1, 4)
        self.fuel_price: float = helpers.rnd_float(8, 20)
        self.ores_available: list[Ore] = []
        self.ore_cargo: list[OreCargo] = []
        self.ore_cargo_volume: float = 0.0
        self.ore_capacity: float = helpers.rnd_float(25_000, 75_000)
        self.visited: bool = False
        self.generate_ores_availability()
        self.generate_ore_cargo_instances()
        self.generate_ore_cargo()

    def get_ore_buy_price(self, ore_name):
        for ore_cargo in self.ore_cargo:
            if ore_cargo.ore.name == ore_name:
                return ore_cargo.buy_price

    def get_ore_sell_price(self, ore_name):
        for ore_cargo in self.ore_cargo:
            if ore_cargo.ore.name == ore_name:
                return ore_cargo.sell_price

    def is_ore_available(self, ore_to_check: OreCargo):
        for ore_cargo in self.ore_cargo:
            if ore_cargo.ore.id == ore_to_check.ore.id:
                return True
        return False

    def generate_ores_availability(self):
        selected = []
        for _ in range(5):
            rnd_ore = helpers.select_random_ore()
            if rnd_ore not in selected:
                selected.append(rnd_ore)

        self.ores_available = selected

    def generate_ore_cargo_instances(self) -> None:
        # create the OreCargo instances
        for ore in self.ores_available:
            ore_quantity: int = 0
            ore_buy_price: float = round(ore.base_value * rnd_float(0.75, 1.25), 2)
            ore_sell_price: float = round(ore_buy_price * rnd_float(0.5, 1.0), 2)
            ore_cargo = OreCargo(ore, ore_quantity, ore_buy_price, ore_sell_price)

            self.ore_cargo.append(ore_cargo)

    def generate_ore_cargo(self):
        # Fill the cargo until the capacity is filled
        while self.ore_cargo_volume < self.ore_capacity / rnd_int(2, 4):
            how_many_ore_types_available = len(self.ores_available)
            for ore_type in range(how_many_ore_types_available):
                self.ore_cargo[ore_type].quantity += 1
                self.ore_cargo_volume += round(self.ores_available[ore_type].volume, 2)

    def get_ore_by_name(self, name) -> OreCargo | None:
        for ore_cargo in self.ore_cargo:
            if ore_cargo.ore.name.lower() == name.lower():
                return ore_cargo
        return None

    def calculate_cargo(self):
        occupancy = 0
        for ore_cargo in self.ore_cargo:
            occupancy += ore_cargo.quantity
        return occupancy

    def get_ore_buy_price_to_string(self):
        string = ""
        for ore_cargo in self.ore_cargo:
            string += f"{ore_cargo.ore.name}: {ore_cargo.buy_price}\n"
        return string

    def get_ore_sell_price_to_string(self):
        string = ""
        for ore_cargo in self.ore_cargo:
            string += f"{ore_cargo.ore.name}: {ore_cargo.sell_price}\n"
        return string

    def get_ore_info_to_string(self):
        string = ""
        for ore in self.ores_available:
            volume = ore.volume * self.ore_capacity
            string += f"{ore.name}: {volume} m³\n"
        return string

    def get_info(self):
        return f"{self.name} {self.space_object.position} {self.space_object.id} {self.fueltank_cap} {self.fueltank} {self.ore_cargo} {self.ore_cargo_volume} {self.ore_capacity} {self.fuel_price}"

    def to_string_short(self, position=None):
        if position is None:
            return f"{self.name}, Position: {self.space_object.position}, ID: {self.space_object.id}"
        return f"{self.name}, Position: {self.space_object.position}, ID: {self.space_object.id}, Distance: {self.space_object.position.distance_to(position):.3f} AU"

    def ores_available_to_string(self, game_state: 'Game'):
        for ore_cargo in self.ore_cargo:
            print("----------------------------------")
            print(f"Ore:       {ore_cargo.ore.name}")
            print(f"Volume:    {ore_cargo.ore.volume}")
            print(f"Sell for:  {ore_cargo.sell_price}")
            print(f"Buy at:    {ore_cargo.buy_price}")
            print("----------------------------------")

    def to_string(self):
        return f"{self.name}\nPosition: {self.space_object.position}\nID: {self.space_object.id}\nFuel Tank: {self.fueltank}/{self.fueltank_cap}m³\nFuel price: {self.fuel_price} credits\n\nOre cargo: {self.ore_cargo} {self.ore_cargo_volume}/{self.ore_capacity}m³\n\nOre prices:\n{self.get_ore_buy_price_to_string()}"

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
