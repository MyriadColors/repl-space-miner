from typing import List, Optional

from pygame import Vector2
from src import helpers
from src.classes.solar_system import SolarSystem
import random

class Region:
    """
    Represents a sector of the galaxy containing multiple solar systems.
    Coordinates are in light years, from (-100, -100) to (100, 100).
    """
    def __init__(self, name: str):
        self.name = name
        self.solar_systems: List[SolarSystem] = []

    def add_system(self, system: SolarSystem) -> None:
        self.solar_systems.append(system)

    def get_system_by_name(self, name: str) -> Optional[SolarSystem]:
        for system in self.solar_systems:
            if system.name == name:
                return system
        return None

    def calculate_distance(self, system1_name: str, system2_name: str) -> float:
        s1 = self.get_system_by_name(system1_name)
        s2 = self.get_system_by_name(system2_name)
        if s1 is None or s2 is None:
            raise ValueError("One or both systems not found in region.")
        # Ensure x and y are floats
        x1, y1 = float(s1.x), float(s1.y)
        x2, y2 = float(s2.x), float(s2.y)
        # Convert to Vector2 for distance calculation
        return float(helpers.euclidean_distance(Vector2(x1, y1), Vector2(x2, y2)))

    @staticmethod
    def generate_random_region(name: str, num_systems: int = 30) -> 'Region':
        from src.classes.solar_system import SolarSystem
        region = Region(name)
        used_coords = set()
        for i in range(num_systems):
            while True:
                x = round(random.uniform(-100, 100), 2)
                y = round(random.uniform(-100, 100), 2)
                if (x, y) not in used_coords:
                    used_coords.add((x, y))
                    break
            system_name = f"System_{i+1}"
            # Todo, add templates for system generation so we can have different parameters for generating systems
            system = SolarSystem(system_name, x, y, random.uniform(50, 150), random.randrange(15, 50), random.randrange(1, 10))
            region.add_system(system)
        return region
