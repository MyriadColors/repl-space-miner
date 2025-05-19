import random
from src.classes.ore import Ore
from src.helpers import rnd_float, meters_cubed_to_km_cubed


class Asteroid:
    def __init__(self, name, volume, ore):
        self.name = name
        self.volume = volume  # in m³
        self.ore = ore

    def to_string(self):
        return f"Asteroid: {self.name}\nVolume: {self.volume} m³\nOre: {self.ore.to_string()}"

    def get_info(self):
        return f"{self.name} {self.volume} {self.ore.get_info()}"

    def to_dict(self):
        return {
            "name": self.name,
            "volume": self.volume,
            "ore_id": self.ore.id,
        }

    @classmethod
    def from_dict(cls, data):
        from src.classes.ore import ORES  # Local import to avoid circular dependency

        ore_obj = ORES.get(data["ore_id"])
        if ore_obj is None:
            raise ValueError(f"Ore with ID {data['ore_id']} not found.")
        return cls(
            name=data["name"],
            volume=data["volume"],
            ore=ore_obj,
        )


class AsteroidField:
    belt_counter: int = 0

    def __init__(self, asteroid_quantity, ores_available, radius, position) -> None:
        from src.classes.ship import IsSpaceObject

        self.asteroid_quantity: int = asteroid_quantity
        self.ores_available: list[Ore] = ores_available
        self.radius: float = radius  # in AU
        self.asteroids: list[Asteroid] = []
        self.space_object = IsSpaceObject(position, AsteroidField.belt_counter)
        self.visited: bool = False
        self.rarity_score: int = self._calculate_field_rarity()  # Added rarity score
        self.spawn_asteroids()
        AsteroidField.belt_counter += 1

    def to_string_short(self, position=None):
        if position is None:
            return f"Field id: {self.space_object.id}, Position: {self.space_object.position}, Radius: {self.radius}"
        return f"Field id: {self.space_object.id}, Position: {self.space_object.position}, Distance: {self.space_object.position.distance_to(position):.3f} AU"

    def to_string(self, position=None):
        asteroid_field_info = (
            f"====== Asteroid Field {self.space_object.id} =====\n"
            f"Position: {self.space_object.position.x:.3f} {self.space_object.position.y:.3f}\n"
        )
        if position:
            asteroid_field_info += (
                f"Distance: {self.space_object.position.distance_to(position):.3f} AU\n"
            )
        ore_list_info = "\n".join(ore.to_string() for ore in self.ores_available)
        asteroid_field_info += (
            f"Radius: {self.radius:.3f} AU\n"
            f"Ores available:\n{ore_list_info}\n"
            f"Asteroid Quantity: {self.asteroid_quantity}\n"
            f"Total Volume: {self.get_total_volume():.3f}m³ ({meters_cubed_to_km_cubed(self.get_total_volume()):.3f}km³)\n"
        )
        return asteroid_field_info

    def asteroids_to_string(self):
        return "\n".join([asteroid.to_string() for asteroid in self.asteroids])

    def get_info(self):
        return f"{self.asteroid_quantity} {self.radius} {self.ores_available} {self.asteroids}"

    def spawn_asteroids(self):
        for i in range(1, self.asteroid_quantity + 1):
            ore = random.choice(self.ores_available)
            volume = rnd_float(100.0, 100_000.0) * ore.volume
            self.asteroids.append(Asteroid(f"Asteroid {i}", volume, ore))

    def get_random_asteroid(self):
        return random.choice(self.asteroids)

    def get_total_volume(self):
        return sum(asteroid.volume for asteroid in self.asteroids)

    def _calculate_field_rarity(self) -> int:
        if not self.ores_available:
            return 1  # Default rarity if no ores specified

        max_rarity_score = 1
        for ore in self.ores_available:
            score = 1  # Common
            if ore.base_value >= 5000:  # Very Rare (e.g., Jonnite)
                score = 4
            elif ore.base_value >= 1000:  # Rare (e.g., Oxynite, Heron)
                score = 3
            elif ore.base_value >= 100:  # Uncommon (e.g., Cyclon, Magneton)
                score = 2

            if score > max_rarity_score:
                max_rarity_score = score
        return max_rarity_score

    def to_dict(self):
        return {
            # "asteroid_quantity": self.asteroid_quantity, # Removed, can be derived from len(self.asteroids)
            "ores_available_ids": [ore.id for ore in self.ores_available],
            "radius": self.radius,
            "asteroids": [asteroid.to_dict() for asteroid in self.asteroids],
            "position": {
                "x": self.space_object.position.x,
                "y": self.space_object.position.y,
            },
            "id": self.space_object.id,
            "visited": self.visited,
        }

    @classmethod
    def from_dict(cls, data):
        from src.classes.ore import ORES  # Local import
        from src.classes.ship import IsSpaceObject  # Local import
        from pygame import Vector2  # Add missing Vector2 import

        ores = [
            ORES.get(ore_id)
            for ore_id in data["ores_available_ids"]
            if ORES.get(ore_id) is not None
        ]
        # asteroid_quantity is now derived from the length of the loaded asteroids list
        asteroids_data = data["asteroids"]
        asteroid_quantity = len(asteroids_data)

        field = cls(
            asteroid_quantity=asteroid_quantity,  # Use derived quantity
            ores_available=ores,
            radius=data["radius"],
            position=Vector2(data["position"]["x"], data["position"]["y"]),
        )
        field.space_object = IsSpaceObject(
            Vector2(data["position"]["x"], data["position"]["y"]), data["id"]
        )
        # Clear asteroids spawned by __init__ and load from data
        field.asteroids = []
        for ast_data in asteroids_data:
            field.asteroids.append(Asteroid.from_dict(ast_data))

        # Ensure ores_available is reconstructed from the actual ores in the loaded asteroids,
        # not just the template ores_available_ids, to reflect the true state.
        actual_ores_in_asteroids = {ast.ore for ast in field.asteroids if ast.ore}
        field.ores_available = list(actual_ores_in_asteroids)

        field.rarity_score = field._calculate_field_rarity()  # Recalculate rarity score after loading

        field.visited = data.get("visited", False)
        return field
