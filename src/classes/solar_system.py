import random
from typing import Union

from pygame import Vector2

from src import data
from src.classes.asteroid import AsteroidField
from src.classes.station import Station
from src.classes.space_object import IsSpaceObject
from src.helpers import (
    euclidean_distance,
    rnd_float,
    rnd_vector,
    select_random_ore,
    rnd_int,
)

HasSpaceObjectType = Union[AsteroidField, Station]


class SolarSystem:

    def __init__(
        self,
        name: str,
        x: float,
        y: float,
        size: float = 100.0,
        field_quantity: int = 0,
        station_quantity: int = 0,
    ):
        self.x = x  # X position in region (LY)
        self.y = y  # Y position in region (LY)
        self.size: float = round(size, 2)
        self.name: str = name
        self.game_time: int = 0
        self.field_quantity: int = field_quantity
        self.station_quantity: int = station_quantity
        self.asteroid_fields: list[AsteroidField] = []
        self.stations: list[Station] = []
        self.generate_fields()
        self.generate_stations()

    def print_all_objects(self):
        for (i, field) in enumerate(self.asteroid_fields):
            print(f"Field {i}: {field.to_string()}")
        for (i, station) in enumerate(self.stations):
            print(f"Station {i}: {station.to_string()}")
    
    def get_size(self):
        return self.size

    def get_position(self):
        """Return the (x, y) position of the system in the region."""
        return (self.x, self.y)

    def generate_fields(self):
        for _ in range(self.field_quantity):
            selected_ores = []
            for _ in range(3):
                selected_ores.append(select_random_ore())
            rnd_quantity = random.randint(2, 10)
            rnd_radius = rnd_float(0.5, 2.0)

            max_attempts = self.field_quantity
            for attempt in range(max_attempts):
                rnd_position = rnd_vector(-self.size, self.size)

                # Check distance from center
                if rnd_position.distance_to(Vector2(0, 0)) < 0.2:
                    continue

                # Check overlap with existing fields
                overlapping = False
                for existing_field in self.asteroid_fields:
                    distance = rnd_position.distance_to(
                        existing_field.space_object.position
                    )
                    if distance < (rnd_radius + existing_field.radius):
                        overlapping = True
                        break

                if not overlapping:
                    # Valid position found
                    asteroid_field = AsteroidField(
                        rnd_quantity, selected_ores, rnd_radius, rnd_position
                    )
                    self.asteroid_fields.append(asteroid_field)
                    break

            else:
                # If we've exhausted all attempts without finding a valid position
                print(
                    f"Warning: Could not place asteroid field {len(self.asteroid_fields) + 1} without overlap"
                )

    def get_all_asteroid_fields(self) -> list[AsteroidField]:
        return self.asteroid_fields

    def get_all_stations(self) -> list[Station]:
        return self.stations

    def get_all_space_objects(self) -> list[HasSpaceObjectType]:
        return self.asteroid_fields + self.stations

    def is_object_at_position(self, position: Vector2) -> bool:
        # Check if the coordinates are occupied by an asteroid field or station
        for space_object in self.get_all_space_objects():
            if space_object.space_object.get_position() == position:
                return True

        return False

    def is_object_within_an_asteroid_field_radius(self, object_position):
        for asteroid_field in self.asteroid_fields:
            distance = object_position.distance_to(asteroid_field.space_object.position)
            if distance <= asteroid_field.radius:
                return True
        return False

    def get_field_by_position(self, position):
        for asteroid_field in self.asteroid_fields:
            if (
                euclidean_distance(position, asteroid_field.space_object.position)
                <= asteroid_field.radius
            ):
                return asteroid_field
        return None

    def sort_fields(self, sort_order, sort_type, position_flag=None):

        def sort_key(field: AsteroidField):
            if sort_type in ("radius", "r"):
                return field.radius
            elif sort_type in ("asteroids", "a"):
                return field.asteroid_quantity
            elif sort_type in ("distance", "d"):
                if position_flag is None:
                    raise ValueError("Position flag is required for distance sorting")
                return field.space_object.position.distance_to(position_flag)
            else:
                raise ValueError(f"Invalid sort type: {sort_type}")

        sorted_fields = sorted(
            self.asteroid_fields, key=sort_key, reverse=(sort_order in ["des", "d"])
        )
        return sorted_fields

    def generate_stations(self):
        """Generate stations in the game world."""
        if self.station_quantity == 0:
            return

        for i in range(self.station_quantity):
            position = Vector2(
                round(random.uniform(-self.size, self.size), 2),
                round(random.uniform(-self.size, self.size), 2),
            )
            rnd_name = data.generate_random_name(rnd_int(2, 4))
            station = Station(f"Station {rnd_name}", i, position)
            self.stations.append(station)

    def sort_stations(self, sort_order, sort_type, position_flag=None) -> list[Station]:

        def sort_key(station_key):
            if sort_type in ("distance", "d"):
                if position_flag is None:
                    raise ValueError("Position flag is required for distance sorting")
                return station_key.space_object.position.distance_to(position_flag)
            else:
                raise ValueError(f"Invalid sort type: {sort_type}")

        sorted_stations: list[Station]
        selected_stations: list[Station] = self.stations
        sorted_stations = sorted(
            selected_stations, key=sort_key, reverse=(sort_order in ["des", "d"])
        )

        if position_flag is not None:
            sorted_stations = sorted(
                sorted_stations,
                key=lambda station: station.space_object.position.distance_to(
                    position_flag
                ),
            )

        if len(sorted_stations) == 0:
            print("No stations found")

        return sorted_stations

    @staticmethod
    def sort_objects_by_distance(objects: list[HasSpaceObjectType], position: Vector2):
        sorted_objects = sorted(
            objects,
            key=lambda obj: euclidean_distance(position, obj.space_object.position),
        )
        return sorted_objects

    def scan_system_objects(self, player_position, amount) -> list[HasSpaceObjectType]:
        """Scan the system for objects within a certain distance."""

        # Get all fields and stations
        all_fields = self.asteroid_fields
        all_stations = self.stations

        # Combine all objects
        all_objects = all_fields + all_stations

        # Sort by distance (closest first)
        sorted_scanned_objects: list[HasSpaceObjectType] = (
            self.sort_objects_by_distance(all_objects, player_position)[
                0 : min(amount, len(all_objects))
            ]
        )

        return sorted_scanned_objects

    def is_object_within_interaction_radius(self, player_ship):
        for station in self.stations:
            if (
                euclidean_distance(
                    player_ship.space_object.get_position(),
                    station.space_object.position,
                )
                <= player_ship.interaction_radius
            ):
                return True
        return False

    def get_object_within_interaction_radius(self, player_ship):
        for station in self.stations:
            if (
                euclidean_distance(
                    player_ship.space_object.get_position(),
                    station.space_object.position,
                )
                <= player_ship.interaction_radius
            ):
                return station
        return None

    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "game_time": self.game_time,
            "field_quantity": self.field_quantity,
            "station_quantity": self.station_quantity,
            "asteroid_fields": [field.to_dict() for field in self.asteroid_fields],
            "stations": [station.to_dict() for station in self.stations],
        }

    @classmethod
    def from_dict(cls, data):
        solar_system = cls(
            name=data["name"],
            x=data["x"],
            y=data["y"],
            size=data.get("size", 100.0),
            field_quantity=data.get("field_quantity", 0),
            station_quantity=data.get("station_quantity", 0),
        )
        solar_system.game_time = data.get("game_time", 0)
        solar_system.asteroid_fields = [
            AsteroidField.from_dict(field_data)
            for field_data in data.get("asteroid_fields", [])
        ]
        solar_system.stations = [
            Station.from_dict(station_data) for station_data in data.get("stations", [])
        ]
        return solar_system
