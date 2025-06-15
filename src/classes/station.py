from typing import Optional, TYPE_CHECKING
from src import helpers
from src.classes.ore import Ore
from src.data import OreCargo
from src.helpers import take_input, rnd_float, rnd_int

if TYPE_CHECKING:
    from src.classes.celestial_body import CelestialBody


class Station:
    def __init__(
        self,
        name,
        station_id,
        position,
        orbital_parent: Optional["CelestialBody"] = None,
    ) -> None:
        from src.classes.ship import IsSpaceObject

        self.name: str = name
        self.space_object = IsSpaceObject(position, station_id)
        self.orbital_parent: Optional["CelestialBody"] = orbital_parent
        self.fuel_tank_capacity: float = helpers.rnd_float(5_000, 20_000)
        self.fuel_tank: float = self.fuel_tank_capacity / helpers.rnd_int(1, 4)
        self.fuel_price: float = helpers.rnd_float(8, 20)
        self.ores_available: list[Ore] = []
        self.ore_cargo: list[OreCargo] = []
        self.ore_cargo_volume: float = 0.0
        self.ore_capacity: float = helpers.rnd_float(25_000, 75_000)
        self.visited: bool = False

        # For serialization - store celestial body parent info
        self.orbital_parent_id: Optional[int] = None
        self.orbital_parent_type: Optional[str] = None
        self.orbital_parent_name: Optional[str] = None

        if orbital_parent:
            self.orbital_parent_id = orbital_parent.space_object.id
            self.orbital_parent_type = orbital_parent.body_type.value
            self.orbital_parent_name = orbital_parent.name

        self.generate_ores_availability()
        self.generate_ore_cargo_instances()
        self.generate_ore_cargo()

    @property
    def position(self):
        """Access the station's position directly."""
        return self.space_object.position

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
        # Make all ores available at every station
        from src.classes.ore import ORES

        self.ores_available = list(ORES.values())

    def generate_ore_cargo_instances(self) -> None:
        # Create OreCargo instances for all available ores, with randomized prices
        from src.helpers import rnd_float

        self.ore_cargo = []
        for ore in self.ores_available:
            ore_quantity: int = 0  # Will be set in generate_ore_cargo
            ore_buy_price: float = round(
                ore.base_value * rnd_float(0.75, 1.25), 2)
            ore_sell_price: float = round(
                ore_buy_price * rnd_float(0.5, 1.0), 2)
            ore_cargo = OreCargo(
                ore, ore_quantity, ore_buy_price, ore_sell_price)
            self.ore_cargo.append(ore_cargo)

    def generate_ore_cargo(self):
        # Assign a random quantity to each ore type, respecting ore capacity
        # All stations will have all products but with varied quantities
        import random

        self.ore_cargo_volume = 0.0
        # More generous allocation        # First pass - ensure every ore has at least some quantity
        max_total_volume = self.ore_capacity / rnd_int(1, 3)
        min_qty_per_ore = 5  # Minimum quantity of each ore type

        for ore_cargo in self.ore_cargo:
            # Ensure there's at least some of each ore type (for trade diversity)
            ore_cargo.quantity = min_qty_per_ore
            self.ore_cargo_volume += ore_cargo.ore.volume * min_qty_per_ore

        # Second pass - distribute remaining capacity randomly
        remaining_volume = max_total_volume - self.ore_cargo_volume

        for ore_cargo in self.ore_cargo:
            # Calculate max additional quantity for this ore based on remaining volume
            if remaining_volume <= 0:
                break

            # Check for zero volume_per_unit to prevent division by zero
            if ore_cargo.ore.commodity.volume_per_unit <= 0:
                continue

            max_quantity = int(
                remaining_volume // ore_cargo.ore.commodity.volume_per_unit
            )
            if max_quantity <= 0:
                continue

            # Generate a random quantity, but avoid using all remaining volume on one ore
            max_for_this_ore = min(
                max_quantity, 1000, int(max_quantity * random.random() * 0.8)
            )
            additional_quantity = random.randint(0, max_for_this_ore)
            # Update quantity and remaining volume
            ore_cargo.quantity += additional_quantity
            remaining_volume -= ore_cargo.ore.volume * additional_quantity
            self.ore_cargo_volume += ore_cargo.ore.volume * additional_quantity
            if self.ore_cargo_volume >= max_total_volume:
                break

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
        return f"{self.name} {self.space_object.position} {self.space_object.id} {self.fuel_tank_capacity} {self.fuel_tank} {self.ore_cargo} {self.ore_cargo_volume} {self.ore_capacity} {self.fuel_price}"

    def to_string_short(self, position=None):
        if position is None:
            return f"{self.name}, Position: {self.space_object.position}, ID: {self.space_object.id}"
        return f"{self.name}, Position: {self.space_object.position}, ID: {self.space_object.id}, Distance: {self.space_object.position.distance_to(position):.3f} AU"

    def ores_available_to_string(self):
        for ore_cargo in self.ore_cargo:
            print("----------------------------------")
            print(f"Ore:       {ore_cargo.ore.name}")
            print(f"Volume:    {ore_cargo.ore.volume}")
            print(f"Sell for:  {ore_cargo.sell_price}")
            print(f"Buy at:    {ore_cargo.buy_price}")
            print("----------------------------------")

    def to_string(self):
        return f"{self.name}\nPosition: {self.space_object.position}\nID: {self.space_object.id}\nFuel Tank: {self.fuel_tank}/{self.fuel_tank_capacity}m³\nFuel price: {self.fuel_price} credits\n\nOre cargo: {self.ore_cargo} {self.ore_cargo_volume}/{self.ore_capacity}m³\n\nOre prices:\n{self.get_ore_buy_price_to_string()}"

    def buy_fuel(self, player_ship, amount, game_state):
        total_cost = round(amount * self.fuel_price, 2)
        print(
            f"Price: {total_cost} credits ({self.fuel_price} credits per m³)")
        response = take_input("Do you want to buy fuel? (y/n) ")
        if response != "y":
            return
        if player_ship.credits < total_cost:
            print("You don't have enough credits")
            return
        player_ship.remove_credits(game_state, total_cost)
        player_ship.fueltank += amount
        self.fuel_tank -= amount
        print(f"You bought {amount} m³ of fuel for {total_cost} credits")
        print(
            f"You now have {player_ship.fueltank} m³ of fuel and {player_ship.credits} credits"
        )
        print(
            f"The station has {self.fuel_tank} m³ of fuel left out of {self.fuel_tank_capacity} m³"
        )

    def sell_fuel(self, player_ship, amount, game_state):
        total_price = round(amount * self.fuel_price, 2)
        print(
            f"Price: {total_price} credits ({self.fuel_price} credits per m³)")
        response = take_input("Do you want to sell fuel? (y/n) ")
        if response != "y":
            print("Fuel not sold")
            return
        if player_ship.fueltank < amount:
            print("You don't have enough fuel")
            return
        player_ship.fueltank -= amount
        player_ship.add_credits(game_state, total_price)
        self.fuel_tank += amount
        print(f"You sold {amount} m³ of fuel for {total_price} credits")
        print(
            f"You now have {player_ship.fueltank} m³ of fuel and {player_ship.credits} credits"
        )
        print(
            f"The station has {self.fuel_tank} m³ of fuel left out of {self.fuel_tank_capacity} m³"
        )

    def to_dict(self):
        data = {
            "name": self.name,
            "position": {
                "x": self.space_object.position.x,
                "y": self.space_object.position.y,
            },
            "id": self.space_object.id,
            "fueltank_cap": self.fuel_tank_capacity,
            "fueltank": self.fuel_tank,
            "fuel_price": self.fuel_price,
            "ore_cargo": [oc.to_dict() for oc in self.ore_cargo],
            "ore_capacity": self.ore_capacity,
            "visited": self.visited,
        }

        # Add orbital parent information if applicable
        if self.orbital_parent:
            data["orbital_parent_id"] = self.orbital_parent.space_object.id
            data["orbital_parent_type"] = self.orbital_parent.body_type.value
            data["orbital_parent_name"] = self.orbital_parent.name
        elif self.orbital_parent_id is not None:
            # Use the stored information if a real parent object isn't linked yet
            data["orbital_parent_id"] = self.orbital_parent_id
            data["orbital_parent_type"] = self.orbital_parent_type
            data["orbital_parent_name"] = self.orbital_parent_name

        return data

    @classmethod
    def from_dict(cls, data):
        from src.classes.ship import IsSpaceObject  # Local import
        from pygame import Vector2
        from src.data import OreCargo  # Ensure OreCargo is imported for from_dict

        station = cls(
            name=data["name"],
            station_id=data["id"],
            position=Vector2(data["position"]["x"], data["position"]["y"]),
        )

        station.space_object = IsSpaceObject(
            Vector2(data["position"]["x"], data["position"]["y"]), data["id"]
        )
        station.fuel_tank_capacity = data["fueltank_cap"]
        station.fuel_tank = data["fueltank"]
        station.fuel_price = data["fuel_price"]

        station.ore_cargo = [
            OreCargo.from_dict(oc_data) for oc_data in data["ore_cargo"]
        ]
        station.ores_available = [
            oc.ore for oc in station.ore_cargo if oc.ore is not None
        ]
        station.ore_cargo_volume = sum(
            oc.ore.volume * oc.quantity
            for oc in station.ore_cargo
            if oc.ore is not None
        )
        station.ore_capacity = data["ore_capacity"]
        station.visited = data.get("visited", False)

        # Orbital parent will be set when the system loads celestial bodies
        # Just store the information temporarily (full linking happens after all objects are loaded)
        if "orbital_parent_id" in data:
            station.orbital_parent_id = data["orbital_parent_id"]
            station.orbital_parent_type = data["orbital_parent_type"]
            station.orbital_parent_name = data["orbital_parent_name"]

        return station

    def add_item(self, item_ore: Ore, item_quantity: int):
        """Add an item to the station's inventory."""
        ore_cargo = next(
            (cargo for cargo in self.ore_cargo if cargo.ore.id == item_ore.id), None
        )
        if ore_cargo:
            ore_cargo.quantity += item_quantity
        else:
            # Create new ore cargo if this ore type isn't in inventory yet
            buy_price = round(item_ore.base_value * rnd_float(0.75, 1.25), 2)
            sell_price = round(buy_price * rnd_float(0.5, 1.0), 2)
            self.ore_cargo.append(
                OreCargo(item_ore, item_quantity, buy_price, sell_price)
            )
        # Update ores_available and ore_cargo_volume after adding item
        self.ores_available = [
            oc.ore for oc in self.ore_cargo if oc.ore is not None]
        self.ore_cargo_volume = sum(
            oc.ore.volume * oc.quantity for oc in self.ore_cargo if oc.ore is not None
        )

    def remove_item(self, item_ore: Ore, item_quantity: int):
        """Remove an item from the station's inventory."""
        ore_cargo = next(
            (cargo for cargo in self.ore_cargo if cargo.ore.id == item_ore.id), None
        )
        if ore_cargo:
            if ore_cargo.quantity >= item_quantity:
                ore_cargo.quantity -= item_quantity
                if ore_cargo.quantity <= 0:
                    self.ore_cargo.remove(ore_cargo)
                # Update ores_available and ore_cargo_volume after removing item
                self.ores_available = [
                    oc.ore for oc in self.ore_cargo if oc.ore is not None
                ]
                self.ore_cargo_volume = sum(
                    oc.ore.volume * oc.quantity
                    for oc in self.ore_cargo
                    if oc.ore is not None
                )
                return True
        return False

    def get_orbital_info(self) -> str:
        """Return information about orbital status"""
        if self.orbital_parent:
            distance = self.space_object.position.distance_to(
                self.orbital_parent.space_object.position
            )
            return f"Orbiting {self.orbital_parent.name} at {distance:.2f} AU"
        else:
            return "Independent station"

    def is_orbital_station(self) -> bool:
        """Check if this station is orbiting a celestial body"""
        return self.orbital_parent is not None
