from random import choice

from src.classes.ship import Ship
from src.classes.solar_system import SolarSystem


class Game:

    def __init__(self, debug_flag = False, mute_flag = False):
        self.global_time: int = 0
        self.solar_system: SolarSystem = SolarSystem(200, 100)
        rnd_station = choice(self.solar_system.stations)
        self.player_ship: Ship = Ship(rnd_station.position, 0.0001, 100, 0.05, 100,
                                      100, 0.01, "placeholder")
        self.player_credits: float = 1000
        self.debug_flag = debug_flag
        self.mute_flag = mute_flag
        self.sound_init = True if not mute_flag else False  # If the mute flag is false, then sound_init is true


    def get_credits(self):
        return round(self.player_credits, 2)
