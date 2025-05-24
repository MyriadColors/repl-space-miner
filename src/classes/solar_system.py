import random
import math
from typing import Union, List, Optional

from pygame import Vector2

from src import data
from src.data import SolarSystemZone
from src.classes.asteroid import AsteroidField
from src.classes.station import Station
from src.classes.celestial_body import Star, Planet, Moon, AsteroidBelt, CelestialBody
from src.helpers import (
    euclidean_distance,
    rnd_float,
    rnd_int,
)

# Extended HasSpaceObjectType to include new celestial bodies
HasSpaceObjectType = Union[AsteroidField,
                           Station, Star, Planet, Moon, AsteroidBelt]


class SolarSystem:

    def __init__(
        self,
        name: str,
        x: float,
        y: float,
        size: float = 100.0,
        field_quantity: int = 10,
        station_quantity: int = 1,
        description: Optional[str] = None,
        faction_id: Optional[str] = None,
        security_level: Optional[str] = None,
        economy_type: Optional[str] = None,
        population: Optional[int] = None,
        tech_level: Optional[int] = None,
        anomalies: Optional[List[str]] = None,  # Added anomalies
        # Default frost line, can be adjusted based on star type later
        frost_line_au: float = 3.0,
    ):
        self.x = x  # X position in region (LY)
        self.y = y  # Y position in region (LY)
        self.size: float = round(size, 2)
        self.name: str = name
        self.game_time: int = 0
        self.field_quantity: int = field_quantity
        self.station_quantity: int = station_quantity

        # Celestial body collections
        self.star: Optional[Star] = None
        self.planets: List[Planet] = []
        self.asteroid_belts: List[AsteroidBelt] = []
        # Holds all stars, planets, moons, belts
        self.celestial_bodies: List[CelestialBody] = []

        # Additional attributes
        self.description = description
        self.faction_id = faction_id
        self.security_level = security_level
        self.economy_type = economy_type
        self.population = population
        self.tech_level = tech_level
        self.anomalies = anomalies if anomalies is not None else []
        self.frost_line_au = frost_line_au

        # Generate celestial bodies
        self.generate_celestial_bodies()

    def print_all_objects(self):
        # Print celestial bodies
        for i, body in enumerate(self.celestial_bodies):
            print(f"Body {i}: {body.name} - {type(body).__name__}")

            # Print asteroid fields within belts
            if isinstance(body, AsteroidBelt):
                for j, field in enumerate(body.asteroid_fields):
                    print(
                        f"  Field {j}: {field.to_string()}"
                    )  # Print stations attached to bodies
            if hasattr(body, "stations") and body.stations:
                for j, station in enumerate(body.stations):
                    print(f"  Station {j}: {station.to_string()}")

    def get_size(self):
        return self.size

    def get_position(self):
        """Return the (x, y) position of the system in the region."""
        return (self.x, self.y)

    def get_zone_for_distance(self, distance_au: float) -> SolarSystemZone:
        """
        Determine the temperature zone based on orbital distance from the star.

        Args:
            distance_au: Distance from the star in Astronomical Units

        Returns:
            SolarSystemZone corresponding to the temperature zone
        """
        if distance_au < 2.0:
            return SolarSystemZone.INNER_HOT
        elif distance_au < self.frost_line_au:
            return SolarSystemZone.MIDDLE_WARM
        else:
            return SolarSystemZone.OUTER_COLD

    def _random_position_within_radius(self) -> Vector2:
        """
        Generate a random position within a circle of radius self.size (AU).
        Returns a Vector2.
        """
        angle = random.uniform(0, 2 * 3.141592653589793)
        radius = random.uniform(0, self.size)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        return Vector2(round(x, 2), round(y, 2))

    def generate_celestial_bodies(self) -> None:
        """Generates all celestial bodies for the solar system."""
        self.celestial_bodies = []  # Clear previous bodies
        self.planets = []  # Clear planets list
        self.asteroid_belts = []  # Clear asteroid belts list
        self._generate_star()  # Central star
        self._generate_planets()  # Planets and their moons
        self._generate_asteroid_belts()  # Asteroid Belts and their fields
        self._generate_orbital_stations()  # Stations around various bodies
        # Independent stations are handled by _generate_orbital_stations

    def _generate_star(self) -> None:
        """Generate the central star at (0, 0)"""
        star_name = f"{self.name} Primary"
        self.star = Star(star_name, Vector2(0, 0))
        # Add star to celestial_bodies
        self.celestial_bodies.append(self.star)

    def _generate_planets(self) -> None:
        """Generates planets orbiting the central star."""
        if not any(isinstance(cb, Star) for cb in self.celestial_bodies):
            print("No star found to orbit. Skipping planet generation.")
            return

        star = next(cb for cb in self.celestial_bodies if isinstance(cb, Star))
        num_planets = rnd_int(
            data.PLANET_MIN_MAX_NUM[0], data.PLANET_MIN_MAX_NUM[1])
        used_orbital_distances: List[float] = []

        for i in range(num_planets):
            planet_name = f"{self.name} {self._get_planet_designation(i)}"
            orbital_distance = self._select_orbital_distance(
                used_orbital_distances)
            if orbital_distance is None:  # Should not happen with fallback
                print(
                    f"Could not find orbital distance for planet {i+1}, skipping.")
                continue
            used_orbital_distances.append(orbital_distance)
            position = self._calculate_orbital_position(orbital_distance)
            # Planet constructor only takes name, position, and orbital_distance parameters
            # Other properties are calculated internally based on orbital_distance
            planet = Planet(
                name=planet_name, position=position, orbital_distance=orbital_distance
            )
            star.add_child(planet)  # Star is the parent
            self.celestial_bodies.append(planet)
            # Add to planets list for easier access
            self.planets.append(planet)
            self._generate_moons(planet)  # Generate moons for this planet

    def _generate_asteroid_belts(self) -> None:
        """Generates asteroid belts in the solar system."""
        num_belts = rnd_int(
            data.ASTEROID_BELT_MIN_MAX_NUM[0], data.ASTEROID_BELT_MIN_MAX_NUM[1]
        )
        if not num_belts:
            return

        star = next(
            (cb for cb in self.celestial_bodies if isinstance(cb, Star)), None)
        if not star:
            print("Cannot generate asteroid belts without a star.")
            return

        # Try to place belts beyond the outermost planet or in gaps
        # For simplicity, let's use a range based on system size for now
        # This logic can be refined to be more dynamic based on planet orbits

        # Get distances of existing planets to avoid direct overlap with belts
        planet_distances = sorted(
            [p.orbital_distance for p in self.celestial_bodies if isinstance(
                p, Planet)]
        )

        # Define a potential zone for asteroid belts
        # Example: from 1.5x the outermost planet to 0.8 * system_radius, or a default if no planets
        min_belt_zone_start = 2.0  # Default start if no planets
        if planet_distances:
            min_belt_zone_start = planet_distances[-1] * 1.5

        max_belt_zone_end = self.size * 0.8  # Outer limit for belts
        if min_belt_zone_start >= max_belt_zone_end:
            # Fallback if planet orbits are too far out, place belts closer
            min_belt_zone_start = self.size * 0.3
            max_belt_zone_end = self.size * 0.6
            if min_belt_zone_start >= max_belt_zone_end:  # Ensure valid range
                print("Warning: Cannot determine a valid zone for asteroid belts.")
                return

        used_belt_middles: List[float] = []

        for i in range(num_belts):
            belt_name = f"{self.name} Belt {chr(65+i)}"  # Belt A, Belt B, etc.

            # Attempt to find a clear middle point for the belt
            attempts = 0
            belt_middle_dist = None
            while attempts < 10:
                temp_middle = rnd_float(min_belt_zone_start, max_belt_zone_end)
                # Check if too close to other belts (simplified check)
                if not any(
                    abs(temp_middle - ub_middle)
                    < (data.ASTEROID_BELT_WIDTH_MIN_MAX[1] * 2)
                    for ub_middle in used_belt_middles
                ):
                    belt_middle_dist = temp_middle
                    break
                attempts += 1

            if belt_middle_dist is None:
                # Fallback: just pick a random spot, might overlap
                belt_middle_dist = rnd_float(
                    min_belt_zone_start, max_belt_zone_end)

            used_belt_middles.append(belt_middle_dist)

            belt_width = rnd_float(
                data.ASTEROID_BELT_WIDTH_MIN_MAX[0], data.ASTEROID_BELT_WIDTH_MIN_MAX[1]
            )
            inner_radius = belt_middle_dist - belt_width / 2
            outer_radius = belt_middle_dist + belt_width / 2

            if inner_radius <= 0 or inner_radius >= outer_radius:
                print(
                    f"Skipping belt {belt_name} due to invalid radii ({inner_radius:.2f}-{outer_radius:.2f} AU)."
                )
                continue

            num_fields = rnd_int(
                data.ASTEROID_BELT_FIELDS_MIN_MAX[0],
                data.ASTEROID_BELT_FIELDS_MIN_MAX[1],
            )

            # Calculate belt position based on its middle orbital distance
            # This gives the belt a representative position for scanning/display purposes
            belt_position = self._calculate_orbital_position(belt_middle_dist)

            belt = AsteroidBelt(
                name=belt_name,
                center_position=belt_position,  # Belt positioned at its orbital distance
                inner_radius=inner_radius,
                outer_radius=outer_radius,
                num_fields=num_fields,
                parent_system=self,  # Pass reference to this solar system
            )

            # Set the orbital distance for proper celestial body behavior
            belt.orbital_distance = belt_middle_dist
            star.add_child(belt)  # Belt is a child of the star
            self.celestial_bodies.append(belt)
            # Keep a specific list of belts too
            self.asteroid_belts.append(belt)

    def _generate_moons(self, planet: Planet) -> None:
        """Generate moons for planets"""
        # Larger planets more likely to have moons
        moon_chance = min(0.8, planet.radius * 10)  # Up to 80% chance

        if random.random() < moon_chance:
            num_moons = random.randint(1, 3)
            for i in range(num_moons):
                # Position moon around planet
                moon_distance = random.uniform(
                    0.1, 0.5)  # Distance from planet
                angle = random.uniform(0, 2 * math.pi)

                moon_x = planet.space_object.position.x + moon_distance * math.cos(
                    angle
                )
                moon_y = planet.space_object.position.y + moon_distance * math.sin(
                    angle
                )
                moon_position = Vector2(round(moon_x, 2), round(moon_y, 2))

                moon_name = f"{planet.name} {self._get_moon_designation(i)}"
                moon = Moon(moon_name, moon_position, planet)
                planet.add_child(moon)
                # Add moon to celestial_bodies list
                self.celestial_bodies.append(moon)

    def _generate_orbital_stations(self) -> None:
        """Generate orbital stations around celestial bodies"""
        # Generate stations around star
        if self.star and random.random() < 0.3:  # 30% chance
            self._create_orbital_station(self.star, "Solar Station")

        # Generate stations around planets
        for planet in self.planets:
            if random.random() < 0.4:  # 40% chance per planet
                self._create_orbital_station(planet, "Orbital Station")

        # Generate independent stations (directly attached to star)
        station_count = self._count_all_stations()
        remaining_stations = max(0, self.station_quantity - station_count)
        for i in range(remaining_stations):
            self._create_independent_station(i)

    def _create_orbital_station(
        self, celestial_body: CelestialBody, station_type: str
    ) -> None:
        """Create a station orbiting a celestial body"""
        # Position station in orbit around the celestial body
        orbital_distance = celestial_body.radius + random.uniform(0.05, 0.2)
        angle = random.uniform(0, 2 * math.pi)

        station_x = (
            celestial_body.space_object.position.x +
            orbital_distance * math.cos(angle)
        )
        station_y = (
            celestial_body.space_object.position.y +
            orbital_distance * math.sin(angle)
        )
        station_position = Vector2(round(station_x, 2), round(station_y, 2))

        station_name = f"{data.generate_random_name(rnd_int(2, 4))} {station_type}"
        station_id = len(self.get_all_stations())

        station = Station(
            station_name, station_id, station_position, orbital_parent=celestial_body
        )
        celestial_body.add_station(station)

    def _create_independent_station(self, station_index: int) -> None:
        """Create an independent station in free space (attached to star for structure)"""
        for attempt in range(20):
            position = self._random_position_within_radius()
            # Avoid overlap with asteroid belts, fields and planets
            overlapping = False

            # Check against asteroid belts and their fields
            for belt in self.asteroid_belts:
                for field in belt.asteroid_fields:
                    if position.distance_to(field.space_object.position) < field.radius:
                        overlapping = True
                        break
                if overlapping:
                    break

            # Check against celestial bodies
            if not overlapping:
                for planet in self.planets:
                    if (
                        position.distance_to(planet.space_object.position)
                        < planet.radius + 0.1
                    ):
                        overlapping = True
                        break

            if not overlapping:
                break
        else:
            print(
                f"Warning: Could not place independent station {station_index} without overlap"
            )
            return

        rnd_name = data.generate_random_name(rnd_int(2, 4))
        station_name = f"Station {rnd_name}"
        station_id = (
            self._count_all_stations()
            # Create the station and attach it to the star (as a parent) for hierarchy
        )
        if self.star:
            station = Station(
                station_name, station_id, position, orbital_parent=self.star
            )
            self.star.add_station(station)
        else:
            # Fallback if no star exists (should not happen)
            print("Warning: Creating truly independent station because no star exists")
            station = Station(station_name, station_id, position)
            # Since we don't have legacy collections anymore, this station will be truly independent
            # It won't be attached to any celestial body

    def _count_all_stations(self) -> int:
        """Count all stations in the solar system."""
        count = 0
        for body in self.celestial_bodies:
            if hasattr(body, "stations"):
                count += len(body.stations)
        return count

    def _calculate_orbital_position(
        self, orbital_distance: float, angle: Optional[float] = None
    ) -> Vector2:
        """Calculate position based on orbital distance and angle"""
        if angle is None:
            angle = random.uniform(0, 2 * math.pi)

        x = orbital_distance * math.cos(angle)
        y = orbital_distance * math.sin(angle)
        return Vector2(round(x, 2), round(y, 2))

    def _select_orbital_distance(self, used_distances: List[float]) -> float:
        """Select an orbital distance avoiding conflicts"""
        zones = [
            (0.3, 1.5),  # Inner rocky planets
            (0.8, 2.0),  # Habitable zone overlap
            (2.0, 6.0),  # Outer rocky/gas giants
            (6.0, 30.0),  # Far outer planets
        ]

        for zone_inner, zone_outer in zones:
            for _ in range(20):  # Max attempts
                distance = random.uniform(zone_inner, zone_outer)
                if all(abs(distance - used) > 0.8 for used in used_distances):
                    return distance

        # Fallback: find any valid distance
        return self._find_fallback_distance(used_distances)

    def _get_planet_designation(self, index: int) -> str:
        """Get planet designation (A, B, C, etc.)"""
        return chr(ord("A") + index)

    def _get_moon_designation(self, index: int) -> str:
        """Get moon designation (I, II, III, etc.)"""
        roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
        return roman_numerals[index] if index < len(roman_numerals) else str(index + 1)

    def _find_fallback_distance(self, used_distances: List[float]) -> float:
        """Find any valid orbital distance when zones are full"""
        for distance in [0.4, 1.2, 2.5, 4.0, 8.0, 15.0, 25.0]:
            if all(abs(distance - used) > 0.5 for used in used_distances):
                return distance
        return 30.0 + len(used_distances)  # Emergency fallback

    def get_all_asteroid_fields(self) -> list[AsteroidField]:
        """Returns all asteroid fields in the system, gathered from AsteroidBelts."""
        fields = []
        for body in self.celestial_bodies:
            if isinstance(body, AsteroidBelt):
                fields.extend(body.asteroid_fields)
        return fields

    def get_all_stations(self) -> list[Station]:
        """Returns all stations in the system."""
        all_stations = []
        for body in self.celestial_bodies:
            if hasattr(body, "stations"):
                all_stations.extend(body.stations)
        return all_stations

    def get_all_space_objects(self) -> List[HasSpaceObjectType]:
        """Returns a list of all major space objects in the system for scanning etc."""
        # This should include Stars, Planets, Moons, AsteroidBelt (as a whole),
        # and Stations. Asteroid fields are accessed through their parent belts.

        scan_list: List[HasSpaceObjectType] = []

        # Add all celestial bodies
        for body in self.celestial_bodies:
            # Only append bodies that are explicitly part of HasSpaceObjectType
            if isinstance(body, (Star, Planet, Moon, AsteroidBelt)):
                scan_list.append(body)

            # Add all stations from this celestial body
            if hasattr(body, "stations") and body.stations:
                scan_list.extend(body.stations)

        # NOTE: Asteroid fields are NOT added as separate scan targets
        # They are accessible through their parent asteroid belts

        # Remove duplicates if any were introduced
        final_scan_list = []
        seen_ids = set()
        for obj in scan_list:
            if hasattr(obj, "space_object") and hasattr(obj.space_object, "id"):
                # Use a tuple of type and ID to ensure uniqueness across different object types with same ID
                obj_unique_id = (type(obj).__name__, obj.space_object.id)
                if obj_unique_id not in seen_ids:
                    final_scan_list.append(obj)
                    seen_ids.add(obj_unique_id)
            else:
                # If no space_object.id, add it directly (less robust for uniqueness)
                if obj not in final_scan_list:
                    final_scan_list.append(obj)

        return final_scan_list

    def is_object_at_position(self, position: Vector2) -> bool:
        # Check if the coordinates are occupied by an asteroid field or station
        for space_object in self.get_all_space_objects():
            if space_object.space_object.get_position() == position:
                return True

        return False

    def is_object_within_an_asteroid_field_radius(self, object_position):
        # Check against all fields from all belts
        for field in self.get_all_asteroid_fields():
            distance = object_position.distance_to(field.space_object.position)
            if distance <= field.radius:
                return True
        return False

    def get_field_by_position(self, position):
        # Check against all fields from all belts
        for field in self.get_all_asteroid_fields():
            if (
                euclidean_distance(position, field.space_object.position)
                <= field.radius
            ):
                return field
        return None

    def sort_fields(self, sort_order, sort_type, position_flag=None):

        def sort_key(field: AsteroidField):
            if sort_type in ("radius", "r"):
                return field.radius
            elif sort_type in ("asteroids", "a"):
                return field.asteroid_quantity
            elif sort_type in ("distance", "d"):
                if position_flag is None:
                    raise ValueError(
                        "Position flag is required for distance sorting")
                return field.space_object.position.distance_to(position_flag)
            else:
                raise ValueError(f"Invalid sort type: {sort_type}")

        # Get fields from all belts
        all_fields = self.get_all_asteroid_fields()
        sorted_fields = sorted(
            all_fields, key=sort_key, reverse=(sort_order in ["des", "d"])
        )
        return sorted_fields

    def sort_stations(self, sort_order, sort_type, position_flag=None) -> list[Station]:

        def sort_key(station_key):
            if sort_type in ("distance", "d"):
                if position_flag is None:
                    raise ValueError(
                        "Position flag is required for distance sorting")
                return station_key.space_object.position.distance_to(position_flag)
            else:
                raise ValueError(f"Invalid sort type: {sort_type}")

        # Get all stations from celestial bodies
        all_stations = self.get_all_stations()
        sorted_stations = sorted(
            all_stations, key=sort_key, reverse=(sort_order in ["des", "d"])
        )

        if len(sorted_stations) == 0:
            print("No stations found")

        return sorted_stations

    @staticmethod
    def sort_objects_by_distance(objects: list[HasSpaceObjectType], position: Vector2):
        sorted_objects = sorted(
            objects,
            key=lambda obj: euclidean_distance(
                position, obj.space_object.position),
        )
        return sorted_objects

    def scan_system_objects(self, player_position, amount) -> List[HasSpaceObjectType]:
        """Enhanced scanning that respects celestial hierarchy"""
        all_objects = self.get_all_space_objects()

        # Sort by distance and significance
        def scan_priority(obj):
            distance = euclidean_distance(
                player_position, obj.space_object.position)

            # Priority multipliers based on object type
            if isinstance(obj, Star):
                return distance * 0.1  # Stars are always visible
            elif isinstance(obj, Planet):
                return distance * 0.3  # Planets are highly visible
            elif isinstance(obj, AsteroidBelt):
                return distance * 0.7  # Belts are moderately visible
            elif isinstance(obj, Moon):
                return distance * 0.8  # Moons are less visible
            else:
                # Standard visibility (stations, asteroid fields)
                return distance

        sorted_objects = sorted(all_objects, key=scan_priority)
        return sorted_objects[: min(amount, len(sorted_objects))]

    def is_object_within_interaction_radius(self, player_ship):
        for station in self.get_all_stations():
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
        for station in self.get_all_stations():
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
            # Save all celestial bodies. Stations and fields are part of their parents.
            "celestial_bodies": [cb.to_dict() for cb in self.celestial_bodies],
        }

    @classmethod
    def from_dict(cls, data):
        solar_system = cls(
            name=data["name"],
            x=data.get("x", 0),  # Provide default if missing (for older saves)
            y=data.get("y", 0),  # Provide default if missing
            size=data["size"],
            # field_quantity and station_quantity are for generation, not loading
        )
        solar_system.game_time = data.get("game_time", 0)
        solar_system.celestial_bodies = []
        solar_system.planets = []
        solar_system.asteroid_belts = []  # Initialize this list

        if "celestial_bodies" in data:
            for cb_data in data["celestial_bodies"]:
                body_type_str = cb_data.get("body_type")
                body: Optional[CelestialBody] = (
                    None  # General variable for any celestial body
                )

                try:
                    from src.classes.celestial_body import CelestialBodyType

                    if body_type_str == CelestialBodyType.STAR.value:
                        body = Star.from_dict(cb_data)
                        solar_system.star = body
                    elif body_type_str == CelestialBodyType.PLANET.value:
                        body = Planet.from_dict(cb_data)
                        solar_system.planets.append(body)
                    elif body_type_str == CelestialBodyType.MOON.value:
                        body = Moon.from_dict(cb_data)
                    elif body_type_str == CelestialBodyType.ASTEROID_BELT.value:
                        belt_body: Optional[AsteroidBelt] = AsteroidBelt.from_dict(
                            cb_data
                        )
                        if belt_body:
                            solar_system.asteroid_belts.append(
                                belt_body
                            )  # Add to asteroid_belts list
                        body = belt_body  # Assign to general body variable for celestial_bodies list
                    else:
                        # Fallback for unknown or base CelestialBody type if necessary
                        print(
                            f"Warning: Unknown or base celestial body type encountered during loading: {body_type_str}"
                        )
                        continue  # Skip this body

                    if body:
                        solar_system.celestial_bodies.append(body)
                except Exception as e:
                    print(
                        f"Error loading celestial body {cb_data.get('name', 'Unknown')} from dict: {e}"
                    )

        elif "asteroid_fields" in data or "stations" in data:  # Legacy save
            print(
                "Legacy save format detected. Please save again to update to the new format."
            )
            # Create minimal structure with a star
            if not solar_system.star:
                star = Star(f"{solar_system.name} Primary", Vector2(0, 0))
                solar_system.star = star
                solar_system.celestial_bodies.append(star)

        return solar_system
        # Migration methods removed as they are no longer needed

    # We're now using only the new celestial bodies structure
