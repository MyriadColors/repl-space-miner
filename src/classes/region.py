from typing import List, Optional
import math

from src.classes.solar_system import SolarSystem
from src.data import STELLAR_SYSTEM_NAMES
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
        # Ensure x and y are floats for both systems
        x1, y1 = float(s1.x), float(s1.y)
        x2, y2 = float(s2.x), float(s2.y)

        # Calculate Euclidean distance manually to ensure we're using the correct values
        distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return round(distance, 2)

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
            A new Region object containing the generated solar systems        """
        from src.classes.solar_system import SolarSystem
        
        region = Region(name)
        used_positions: List[tuple[float, float]] = (
            []
        )  # Store positions as (x, y) tuples
        
        # Create a shuffled copy of stellar names to ensure uniqueness
        available_names = STELLAR_SYSTEM_NAMES.copy()
        random.shuffle(available_names)
        
        # If we need more systems than we have names, we'll need to generate additional names
        if num_systems > len(available_names):
            # Add numbered variants of existing names
            base_names = available_names.copy()
            for i in range(num_systems - len(available_names)):
                base_name = base_names[i % len(base_names)]
                available_names.append(f"{base_name} {(i // len(base_names)) + 2}")
        
        max_placement_attempts = 5000  # Prevent infinite loops

        for i in range(num_systems):
            attempt_count = 0
            valid_position = False
            x, y = 0.0, 0.0  # Initialize x and y here

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

            # If we couldn\'t find a valid position after max attempts, try with reduced constraints
            if not valid_position:  # Check if still not valid after initial attempts
                print(
                    f"Warning: Could not place system {i+1} with min_distance={min_distance} after {max_placement_attempts} attempts. Reducing constraints."
                )
                local_min_distance = min_distance
                fallback_attempts = 0
                max_fallback_attempts = 10  # Limit attempts with reduced constraints

                while (
                    not valid_position
                    and fallback_attempts < max_fallback_attempts
                    and local_min_distance > 0.01
                ):  # Ensure local_min_distance is positive
                    local_min_distance *= 0.5
                    if local_min_distance < 0.01:  # Prevent extremely small distances
                        local_min_distance = 0.01

                    # Try to find a position with the new local_min_distance
                    for _ in range(
                        max_placement_attempts // 5
                    ):  # Fewer attempts for fallback
                        x_candidate = round(random.uniform(-100, 100), 2)
                        y_candidate = round(random.uniform(-100, 100), 2)

                        candidate_ok = True
                        for pos_x, pos_y in used_positions:
                            distance = math.sqrt(
                                (x_candidate - pos_x) ** 2 + (y_candidate - pos_y) ** 2
                            )
                            if distance < local_min_distance:
                                candidate_ok = False
                                break
                        if candidate_ok:
                            x, y = x_candidate, y_candidate
                            valid_position = True
                            break
                    fallback_attempts += 1

                if not valid_position:
                    print(
                        f"Critical: Failed to place system {i+1} even with reduced constraints. Placing at a default offset to avoid (0,0)."
                    )
                    # Fallback to a slightly offset position to avoid stacking all at (0,0)
                    # This is a last resort and indicates a potential issue with density or region size.
                    x = round(random.uniform(0.1, 1.0) * (i + 1), 2)
                    y = round(random.uniform(0.1, 1.0) * (i + 1), 2)
                    # Ensure it's still within bounds, though this is less critical than avoiding (0,0)
                    x = max(-100, min(100, x))
                    y = max(-100, min(100, y))            # Add the position to our used positions list
            used_positions.append((x, y))

            # Use a unique name from our available names list
            system_name = available_names[i]
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
