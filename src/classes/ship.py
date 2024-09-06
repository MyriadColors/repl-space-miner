from pygame import Vector2

from src.classes.interfaces import CanMove, HasCargoHold, CanDock, CanMine, ShipInterface
from src.helpers import vector_to_string


class Ship(ShipInterface, CanMove, HasCargoHold, CanDock, CanMine):
    def __init__(self, position: Vector2, speed, max_fuel, fuel_consumption, cargo_capacity, mining_speed, name):
        ShipInterface.__init__(self, name)
        HasCargoHold.__init__(self, cargo_capacity)
        CanDock.__init__(self)
        CanMove.__init__(self, position, speed, max_fuel, fuel_consumption)
        CanMine.__init__(self, mining_speed)

    def status_to_string(self):
        return f"Ship Name: {self.ship_name}\nPosition: {vector_to_string(self.position)}\nSpeed: {self.speed} m/s\nFuel: {round(self.fuel, 2)}/{self.max_fuel} m3"

