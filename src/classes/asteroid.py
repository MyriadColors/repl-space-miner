import random
from pygame import Vector2
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
            asteroid_field_info += f"Distance: {self.space_object.position.distance_to(position):.3f} AU\n"
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
