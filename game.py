from ship import Ship
from solar_system import SolarSystem
from vector2d import Vector2d


class Game:

    def __init__(self, ship_name: str):
        self.global_time: int = 0
        self.solar_system: SolarSystem = SolarSystem(200, 50)
        self.player_ship: Ship = Ship(Vector2d(0, 0), 0.005, 100, 0.05, 100,
                                      100, 1, ship_name)
        self.player_credits = 1000

    def get_credits(self):
        return round(self.player_credits, 2)