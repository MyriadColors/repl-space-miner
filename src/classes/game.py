from random import choice

from src.classes.ship import Ship
from src.classes.solar_system import SolarSystem


class Game:

    def __init__(self):
        self.global_time: int = 0
        self.solar_system: SolarSystem = SolarSystem(200, 100)
        rnd_station = choice(self.solar_system.stations)
        self.player_ship: Ship = Ship(rnd_station.position, 0.00001, 100, 0.05, 100,
                                      100, 1, "placeholder")
        self.player_credits: float = 1000

    def get_credits(self):
        return round(self.player_credits, 2)
