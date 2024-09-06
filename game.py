from random import choice

from ship import Ship
from solar_system import SolarSystem


class Game:

    def __init__(self, ship_name: str):
        self.global_time: int = 0
        self.solar_system: SolarSystem = SolarSystem(200, 100)
        rnd_field = choice(self.solar_system.asteroid_fields)
        self.player_ship: Ship = Ship(rnd_field.position, 0.00001, 100, 0.05, 100,
                                      100, 1, ship_name)
        self.player_credits = 1000

    def get_credits(self):
        return round(self.player_credits, 2)
