from typing import List, Optional
import math

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
        x2, y2 = float(s2.x), float(s2.y)  # Convert to Vector2 for distance calculation
        return float(helpers.euclidean_distance(Vector2(x1, y1), Vector2(x2, y2)))

    @staticmethod
    def generate_random_region(
        name: str, num_systems: int = 30, min_distance: float = 2.0
    ) -> "Region":
        """
        Generate a random region with the specified number of solar systems.

        Args:
            name: Name of the region
            num_systems: Number of solar systems to generate
            min_distance: Minimum distance between any two systems (in light years)

        Returns:
            A new Region object containing the generated solar systems
        """
        from src.classes.solar_system import SolarSystem

        region = Region(name)
        used_positions: List[tuple[float, float]] = (
            []
        )  # Store positions as (x, y) tuples
        max_placement_attempts = 5000  # Prevent infinite loops

        for i in range(num_systems):
            attempt_count = 0
            valid_position = False

            while not valid_position and attempt_count < max_placement_attempts:
                # Generate random coordinates
                x = round(random.uniform(-100, 100), 2)
                y = round(random.uniform(-100, 100), 2)

                # Check if this position is far enough from existing systems
                valid_position = True
                for pos_x, pos_y in used_positions:
                    distance = math.sqrt((x - pos_x) ** 2 + (y - pos_y) ** 2)
                    if distance < min_distance:
                        valid_position = False
                        break

                attempt_count += 1
            # Initialize default position in case of failure
            x = 0.0
            y = 0.0

            # If we couldn't find a valid position after max attempts, adjust min_distance
            if attempt_count >= max_placement_attempts:
                print(
                    f"Warning: Could not place system {i+1} with min_distance={min_distance}. Reducing constraints."
                )
                # Try again with reduced distance constraint
                local_min_distance = (
                    min_distance  # Use a local copy to not affect future systems
                )
                while not valid_position and local_min_distance > 0.1:
                    local_min_distance *= 0.5
                    x = round(random.uniform(-100, 100), 2)
                    y = round(random.uniform(-100, 100), 2)

                    valid_position = True
                    for pos_x, pos_y in used_positions:
                        distance = math.sqrt((x - pos_x) ** 2 + (y - pos_y) ** 2)
                        if distance < local_min_distance:
                            valid_position = False
                            break

            # Add the position to our used positions list
            used_positions.append((x, y))

            system_name = f"System_{i+1}"
            # Todo, add templates for system generation so we can have different parameters for generating systems
            system = SolarSystem(
                system_name,
                x,
                y,
                round(random.uniform(50, 150), 2),
                random.randrange(25, 50),
                random.randrange(5, 15),
            )
            region.add_system(system)
        return region
