"""
Celestial Body Classes for REPL Space Miner

This module implements the celestial body hierarchy including stars, planets,
moons, and asteroid belts while maintaining full compatibility with existing
game systems through composition with IsSpaceObject.
"""

import math
import random
from enum import Enum
from typing import List, Optional, Union, TYPE_CHECKING
from pygame import Vector2
from src.classes.space_object import IsSpaceObject
from src.helpers import rnd_float, rnd_int
from src.classes.asteroid import AsteroidField
from src.classes.ore import Ore
from src.data import ORES, PlanetType, SolarSystemZone, StellarClass, STELLAR_PROPERTIES
from src.classes.mineral import MaterialCategory

if TYPE_CHECKING:
    from src.classes.station import Station
    from src.classes.asteroid import AsteroidField
    from src.classes.solar_system import SolarSystem


class CelestialBodyType(Enum):
    """Enumeration of celestial body types"""

    STAR = "star"
    PLANET = "planet"
    MOON = "moon"
    ASTEROID_BELT = "asteroid_belt"


class CelestialBody:
    """Base class for all celestial bodies (stars, planets, moons)"""

    # Class-level counters for ID management (following existing pattern)
    star_counter: int = 0
    planet_counter: int = 0
    moon_counter: int = 0
    belt_counter: int = 0

    def __init__(
        self,
        name: str,
        body_type: CelestialBodyType,
        position: Vector2,
        radius: float,
        mass: float = 1.0,
    ):
        """
        Initialize a celestial body.

        Args:
            name: Name of the celestial body
            body_type: Type of celestial body
            position: Position in space (Vector2)
            radius: Physical radius in AU
            mass: Relative mass (Earth = 1.0)
        """
        self.name = name
        self.body_type = body_type

        # Use composition with IsSpaceObject (following existing pattern)
        self.space_object = IsSpaceObject(position, self._get_next_id())

        self.radius = radius  # Physical radius in AU
        self.mass = mass  # Relative mass (Earth = 1.0)
        self.orbital_distance = 0.0  # Distance from parent body
        self.children: List["CelestialBody"] = []
        self.stations: List[
            "Station"
        ] = []  # Assuming Station is defined or TYPE_CHECKED

    def _get_next_id(self) -> int:
        """Get next ID based on body type (following existing pattern)"""
        if self.body_type == CelestialBodyType.STAR:
            CelestialBody.star_counter += 1
            return CelestialBody.star_counter
        elif self.body_type == CelestialBodyType.PLANET:
            CelestialBody.planet_counter += 1
            return CelestialBody.planet_counter
        elif self.body_type == CelestialBodyType.MOON:
            CelestialBody.moon_counter += 1
            return CelestialBody.moon_counter
        elif self.body_type == CelestialBodyType.ASTEROID_BELT:  # Added ASTEROID_BELT
            CelestialBody.belt_counter += 1
            return CelestialBody.belt_counter
        else:
            # Fallback or error for unknown type
            # For now, let's assume all types are handled above or raise error
            raise ValueError(f"Unknown body type for ID generation: {self.body_type}")

    def add_child(self, child: "CelestialBody") -> None:
        """Add a child celestial body (e.g., moon to planet)"""
        self.children.append(child)

    def add_station(self, station: "Station") -> None:
        """Add a station orbiting this celestial body"""
        self.stations.append(station)

    def get_all_objects_in_orbit(self) -> List[Union["CelestialBody", "Station"]]:
        """Return all objects orbiting this celestial body"""
        return self.children + self.stations

    def to_string_short(self, position=None):
        """Short description for scanning (base implementation)"""
        if position is None:
            return f"{self.name} ({self.body_type.value.title()}), Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}"
        return f"{self.name} ({self.body_type.value.title()}), Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}, Distance: {self.space_object.position.distance_to(position):.2f} AU"

    def to_dict(self) -> dict:
        """Serialize to dictionary (following existing pattern)"""
        # This is based on the plan, may need adjustment if IsSpaceObject ID isn't part of it
        data = {
            "name": self.name,
            "body_type": self.body_type.value,
            "id": self.space_object.id,  # Added ID
            "position": {
                "x": self.space_object.position.x,
                "y": self.space_object.position.y,
            },
            "radius": self.radius,
            "mass": self.mass,
            "orbital_distance": self.orbital_distance,
            "stations": [station.to_dict() for station in self.stations],
            # Added children
            "children": [child.to_dict() for child in self.children],
        }
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "CelestialBody":
        """Deserialize from dictionary (following existing pattern)"""
        from src.classes.station import (
            Station,
        )  # Local import to avoid circular dependencies

        position = Vector2(data["position"]["x"], data["position"]["y"])
        body_type = CelestialBodyType(data["body_type"])

        # The 'cls' call here assumes derived class __init__ can handle these base parameters
        # or that this method is primarily for the CelestialBody class itself.
        # For inherited from_dict, derived classes often call their own 'cls' with their specific signature.
        body = cls(data["name"], body_type, position, data["radius"], data["mass"])

        # Override the auto-generated ID with the one from data
        if hasattr(body, "space_object") and "id" in data:
            body.space_object.id = data["id"]
        else:  # If space_object wasn't created or id is missing, this might be an issue
            pass

        body.orbital_distance = data.get("orbital_distance", 0.0)

        # Deserialize stations
        if "stations" in data:
            body.stations = [Station.from_dict(st_data) for st_data in data["stations"]]

        # Deserialize children (recursive call to from_dict)
        if "children" in data:
            body.children = [
                CelestialBody.from_dict(ch_data) for ch_data in data["children"]
            ]
            # Note: This assumes children are always base CelestialBody or their from_dict can handle it.
            # A more robust system might store child_type and call specific from_dict methods.

        return body


class Star(CelestialBody):
    """Central star of the solar system"""

    def __init__(self, name: str, position: Vector2 = Vector2(0, 0)):
        """
        Initialize a star with realistic properties based on stellar classification.

        Args:
            name: Name of the star
            position: Position in space (defaults to 0,0 for central star)
        """  # Generate random stellar class based on rarity weights
        stellar_class = self._generate_stellar_class()
        properties = STELLAR_PROPERTIES[stellar_class]

        # Generate random properties within the stellar class ranges
        temp_range = properties["temperature_range"]
        lum_range = properties["luminosity_range"]
        mass_range = properties["mass_range"]
        radius_range = properties["radius_range"]

        # Cast ranges to tuples to ensure they are indexable
        temp_tuple = (
            tuple(temp_range)
            if hasattr(temp_range, "__iter__")
            else (temp_range, temp_range)
        )
        lum_tuple = (
            tuple(lum_range)
            if hasattr(lum_range, "__iter__")
            else (lum_range, lum_range)
        )
        mass_tuple = (
            tuple(mass_range)
            if hasattr(mass_range, "__iter__")
            else (mass_range, mass_range)
        )
        radius_tuple = (
            tuple(radius_range)
            if hasattr(radius_range, "__iter__")
            else (radius_range, radius_range)
        )

        temperature = random.uniform(temp_tuple[0], temp_tuple[1])
        luminosity = random.uniform(lum_tuple[0], lum_tuple[1])
        mass = random.uniform(mass_tuple[0], mass_tuple[1])
        # Scale down for game purposes
        radius = random.uniform(radius_tuple[0], radius_tuple[1]) * 0.01

        super().__init__(
            name, CelestialBodyType.STAR, position, radius=radius, mass=mass
        )

        self.stellar_class = stellar_class.value  # Store as string for compatibility
        self.temperature = temperature  # Kelvin
        self.luminosity = luminosity  # Solar luminosities
        self.color = properties["color"]

        # Calculate frost line based on luminosity
        # Frost line distance is approximately proportional to sqrt(luminosity)
        # Base frost line for Sun (G-type, luminosity=1.0) is ~2.7 AU
        self.frost_line_au = 2.7 * math.sqrt(luminosity)

    def _generate_stellar_class(self) -> StellarClass:
        """Generate a random stellar class based on rarity weights"""
        classes = list(StellarClass)
        weights = []
        for cls in classes:
            weight_value = STELLAR_PROPERTIES[cls]["rarity_weight"]
            # Ensure weight_value is properly converted to float
            if isinstance(weight_value, (int, float)):
                weights.append(float(weight_value))
            elif isinstance(weight_value, str):
                try:
                    weights.append(float(weight_value))
                except ValueError:
                    weights.append(1.0)  # Default weight if conversion fails
            else:
                weights.append(1.0)  # Default weight for unknown types
        # Use weighted random selection
        total_weight = sum(weights)
        random_value = random.uniform(0, total_weight)

        cumulative_weight = 0.0
        for cls, weight in zip(classes, weights):
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                return cls
        # Fallback to most common class (M-type)
        return StellarClass.M

    def get_frost_line(self) -> float:
        """Get the frost line distance for this star in AU"""
        return self.frost_line_au

    def to_string_short(self, position=None):
        """Short description for scanning (following existing pattern)"""
        star_info = f"★ {self.name} ({self.stellar_class}-type {self.color} star)"
        if position is None:
            return f"{star_info}, Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}"
        return f"{star_info}, Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}, Distance: {self.space_object.position.distance_to(position):.2f} AU"

    def to_dict(self) -> dict:
        """Serialize star to dictionary with specialized properties"""
        base_dict = super().to_dict()
        # Add star-specific properties
        base_dict.update(
            {
                "stellar_class": self.stellar_class,
                "temperature": self.temperature,
                "luminosity": self.luminosity,
                "color": self.color,
                "frost_line_au": self.frost_line_au,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> "Star":
        """Deserialize star from dictionary"""
        position = Vector2(data["position"]["x"], data["position"]["y"])
        star = cls(data["name"], position)
        star.space_object = IsSpaceObject(position, data["id"])
        star.orbital_distance = data.get("orbital_distance", 0.0)
        star.radius = data.get("radius", 0.01)
        star.mass = data.get("mass", 1.0)  # Set star-specific properties
        star.stellar_class = data.get("stellar_class", "G")
        star.temperature = data.get("temperature", 5778)
        star.luminosity = data.get("luminosity", 1.0)
        star.color = data.get("color", "yellow")
        star.frost_line_au = data.get("frost_line_au", 2.7)
        # Reconstruct children and stations
        for child_data in data.get("children", []):
            child_type = CelestialBodyType(child_data["body_type"])
            child: CelestialBody
            if child_type == CelestialBodyType.PLANET:
                child = Planet.from_dict(child_data)
            elif child_type == CelestialBodyType.MOON:
                child = Moon.from_dict(child_data)
            elif child_type == CelestialBodyType.ASTEROID_BELT:
                child = AsteroidBelt.from_dict(child_data)
            else:
                child = CelestialBody.from_dict(child_data)
            star.add_child(child)

        from src.classes.station import Station

        for station_data in data.get("stations", []):
            station = Station.from_dict(station_data)
            star.add_station(station)

        return star


class Planet(CelestialBody):
    """A planet orbiting a star"""

    def __init__(
        self,
        name: str,
        position: Vector2,
        orbital_distance: float,
        stellar_class: str = "G",
        stellar_age: float = 5.0,
    ):
        """
        Initialize a planet with procedural generation based on orbital distance.

        Args:
            name: Name of the planet
            position: Position in space
            orbital_distance: Distance from the star in AU
            stellar_class: Spectral class of the host star
            stellar_age: Age of the host star in billion years
        """
        # Generate physical properties based on orbital distance and zone
        planet_type, radius, mass = self._generate_physical_properties(orbital_distance)

        super().__init__(name, CelestialBodyType.PLANET, position, radius, mass)

        self.orbital_distance = orbital_distance
        self.planet_type = planet_type
        self.temperature_zone = self._get_temperature_zone()
        self.atmosphere = self._generate_atmosphere()
        self.stellar_class = stellar_class
        self.stellar_age = stellar_age

        # Calculate UHS (Universal Habitability Score)
        self.habitability_result = self._calculate_uhs()
        self.habitability_score = self.habitability_result.uhs_score

    def _generate_physical_properties(self, orbital_distance: float):
        """Generate planet physical properties based on orbital distance."""
        # Simplified model: inner planets smaller, outer planets larger
        if orbital_distance < 1.5:
            radius = float(rnd_float(0.05, 0.15))  # Rocky planet size
            mass = float(rnd_float(0.5, 1.5))  # Rocky planet mass
            planet_type = PlanetType.ROCKY
        elif orbital_distance < 5.0:
            radius = float(rnd_float(0.3, 0.8))  # Gas giant size
            mass = float(rnd_float(1.5, 3.0))  # Gas giant mass
            planet_type = PlanetType.GAS_GIANT
        else:
            radius = float(rnd_float(0.2, 0.6))  # Ice giant size
            mass = float(rnd_float(0.8, 2.0))  # Ice giant mass
            planet_type = PlanetType.ICE_GIANT

        return planet_type, radius, mass

    def _get_temperature_zone(self) -> SolarSystemZone:
        """Determine the temperature zone based on orbital distance"""
        # Using the same logic as SolarSystem.get_zone_for_distance
        # Frost line is typically around 4.0-5.0 AU for G-type stars
        frost_line_au = 4.5  # Default frost line distance

        if self.orbital_distance < 2.0:
            return SolarSystemZone.INNER_HOT
        elif self.orbital_distance < frost_line_au:
            return SolarSystemZone.MIDDLE_WARM
        else:
            return SolarSystemZone.OUTER_COLD

    def _generate_atmosphere(self) -> str:
        """Generate atmospheric composition based on planet type and zone"""
        if self.planet_type == PlanetType.GAS_GIANT:
            return random.choice(["thick", "dense", "toxic"])
        elif self.planet_type == PlanetType.ICE_GIANT:
            return random.choice(["thick", "dense", "corrosive"])
        else:  # Rocky or Super Earth
            if self.temperature_zone == SolarSystemZone.INNER_HOT:
                # Hot planets lose atmosphere or have toxic ones
                atmospheres = ["none", "thin", "toxic", "corrosive"]
                weights = [0.4, 0.3, 0.2, 0.1]
            elif self.temperature_zone == SolarSystemZone.MIDDLE_WARM:
                # Habitable zone - more variety including breathable
                atmospheres = ["none", "thin", "dense", "breathable", "ideal"]
                weights = [0.1, 0.2, 0.3, 0.3, 0.1]
            else:  # OUTER_COLD
                # Cold planets might retain thick atmospheres
                atmospheres = ["none", "thin", "thick", "dense"]
                weights = [0.2, 0.2, 0.3, 0.3]

            return random.choices(atmospheres, weights=weights)[0]

    def _calculate_uhs(self):
        """Calculate Universal Habitability Score using the specified distribution model"""
        # Use the new distribution-based scoring instead of the realistic calculation
        score = self._generate_habitability_score_distribution()

        # Create a simple result object that matches the expected interface
        # We still use the original calculation for some metadata, but override the score
        from src.classes.habitability import PlanetaryHabitabilityAssessor

        # Prepare planet data for assessment (for metadata)
        planet_data = {
            "orbital_distance": self.orbital_distance,
            "planet_type": self.planet_type.name.lower(),
            "atmosphere": self.atmosphere,
            "radius": self.radius,
            "mass": self.mass,
            "temperature_zone": self.temperature_zone.name.lower(),
            "stellar_class": self.stellar_class,
            "stellar_age": self.stellar_age,
        }

        # Get the original assessment for structure and metadata
        original_result = PlanetaryHabitabilityAssessor.assess_planet(planet_data)

        # Override the UHS score with our distribution-based score
        original_result.uhs_score = score

        # Update viability and rating based on new score
        original_result.is_viable = score >= 40  # Adjust viability threshold as needed

        # Update rating text based on new score
        if score >= 80:
            original_result.rating_text = "Highly Habitable"
        elif score >= 60:
            original_result.rating_text = "Moderately Habitable"
        elif score >= 40:
            original_result.rating_text = "Marginally Habitable"
        elif score >= 20:
            original_result.rating_text = "Barely Habitable"
        else:
            original_result.rating_text = "Inhospitable"

        return original_result

    def _generate_habitability_score_distribution(self) -> float:
        """
        Generate habitability score using the specified probability distribution:
        - UHS 0-50: 75%
        - UHS 51-75: 15%
        - UHS 76-90: 9%
        - UHS 91-100: 1%
        """
        # Generate random number to determine which range to use
        rand = random.random()

        if rand < 0.75:  # 75% chance for 0-50 range
            return float(random.uniform(0, 50))
        elif rand < 0.90:  # 15% chance for 51-75 range (0.75 + 0.15 = 0.90)
            return float(random.uniform(51, 75))
        elif rand < 0.99:  # 9% chance for 76-90 range (0.90 + 0.09 = 0.99)
            return float(random.uniform(76, 90))
        else:  # 1% chance for 91-100 range
            return float(random.uniform(91, 100))

    def update_stellar_properties(self, stellar_class: str, stellar_age: float):
        """Update stellar properties and recalculate habitability"""
        self.stellar_class = stellar_class
        self.stellar_age = stellar_age
        self.habitability_result = self._calculate_uhs()
        self.habitability_score = self.habitability_result.uhs_score

    def get_habitability_details(self) -> str:
        """Get detailed habitability information"""
        if not hasattr(self, "habitability_result"):
            return "Habitability data not available"

        result = self.habitability_result
        details = []

        details.append(f"Universal Habitability Score: {result.uhs_score}/100")
        details.append(f"Rating: {result.rating_text}")
        details.append(f"Viable for Life: {'Yes' if result.is_viable else 'No'}")
        details.append("")
        details.append("Critical Viability Factors:")
        details.append(f"  Overall CVF: {result.cvf_score:.4f}")
        details.append(
            f"  Liquid Water: {result.factors.liquid_water_availability:.2f}"
        )
        details.append(f"  Temperature: {result.factors.biocompatible_temperature:.2f}")
        details.append(
            f"  Radiation Protection: {result.factors.radiation_protection:.2f}"
        )
        details.append("")
        details.append("Primary Habitability Factors:")
        details.append(f"  Overall PHF: {result.phf_score:.1f}/100")
        details.append(f"  Atmosphere: {result.factors.atmospheric_conditions:.1f}/100")
        details.append(
            f"  Geochemistry: {result.factors.substrate_geochemistry:.1f}/100"
        )
        details.append(f"  Energy: {result.factors.energy_availability:.1f}/100")
        details.append(f"  Stability: {result.factors.environmental_stability:.1f}/100")
        details.append(
            f"  Planetary: {result.factors.planetary_characteristics:.1f}/100"
        )
        details.append(f"  Stellar: {result.factors.stellar_characteristics:.1f}/100")

        return "\n".join(details)

    def _calculate_habitability(self) -> float:
        """Legacy method - now uses UHS system"""
        if not hasattr(self, "habitability_result"):
            self.habitability_result = self._calculate_uhs()
        return float(self.habitability_result.uhs_score)

    def to_string_short(self, position=None):
        """Short description for scanning (following existing pattern)"""
        planet_type_str = self.planet_type.name.replace("_", " ").title()
        if position is None:
            return f"🪐 {self.name} ({planet_type_str}), Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}"
        return f"🪐 {self.name} ({planet_type_str}), Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}, Distance: {self.space_object.position.distance_to(position):.2f} AU"

    def to_dict(self) -> dict:
        """Serialize planet to dictionary with specialized properties"""
        base_dict = super().to_dict()
        # Add planet-specific properties
        base_dict.update(
            {
                "planet_type": self.planet_type.name,
                "temperature_zone": self.temperature_zone.name,
                "atmosphere": self.atmosphere,
                "stellar_class": self.stellar_class,
                "stellar_age": self.stellar_age,
                "habitability_score": self.habitability_score,
                # Save UHS details if available
                "uhs_score": getattr(
                    self.habitability_result, "uhs_score", self.habitability_score
                ),
                "uhs_rating": getattr(
                    self.habitability_result, "rating_text", "Unknown"
                ),
                "uhs_viable": getattr(self.habitability_result, "is_viable", False),
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> "Planet":
        """Deserialize planet from dictionary"""
        position = Vector2(data["position"]["x"], data["position"]["y"])
        orbital_distance = data.get("orbital_distance", 1.0)
        planet = cls(data["name"], position, orbital_distance)

        planet.space_object = IsSpaceObject(position, data["id"])
        planet.radius = data.get("radius", 0.1)
        planet.mass = data.get("mass", 1.0)  # Set planet-specific properties
        planet_type_str = data.get("planet_type", "ROCKY")
        if isinstance(planet_type_str, str):
            # Handle both old string format and new enum format
            if planet_type_str == "Rocky":
                planet.planet_type = PlanetType.ROCKY
            elif planet_type_str == "Gas Giant":
                planet.planet_type = PlanetType.GAS_GIANT
            elif planet_type_str == "Ice Giant":
                planet.planet_type = PlanetType.ICE_GIANT
            elif planet_type_str == "Super Earth":
                planet.planet_type = PlanetType.SUPER_EARTH
            else:
                # Try to get enum by name
                try:
                    planet.planet_type = PlanetType[planet_type_str]
                except KeyError:
                    planet.planet_type = PlanetType.ROCKY  # Default fallback
        else:
            planet.planet_type = planet_type_str
        # Set temperature zone if available, otherwise calculate it
        temperature_zone_str = data.get("temperature_zone")
        if temperature_zone_str:
            try:
                planet.temperature_zone = SolarSystemZone[temperature_zone_str]
            except KeyError:
                planet.temperature_zone = planet._get_temperature_zone()
        else:
            planet.temperature_zone = planet._get_temperature_zone()

        planet.atmosphere = data.get("atmosphere", "none")
        planet.stellar_class = data.get("stellar_class", "G")
        planet.stellar_age = data.get("stellar_age", 5.0)
        planet.habitability_score = data.get("habitability_score", 0.0)

        # Recalculate UHS with loaded properties
        planet.habitability_result = planet._calculate_uhs()
        planet.habitability_score = planet.habitability_result.uhs_score

        # Reconstruct children (moons) and stations
        for child_data in data.get("children", []):
            child_type = CelestialBodyType(child_data["body_type"])
            if child_type == CelestialBodyType.MOON:
                child = Moon.from_dict(child_data)
                planet.add_child(child)

        from src.classes.station import Station

        for station_data in data.get("stations", []):
            station = Station.from_dict(station_data)
            planet.add_station(station)

        return planet


class Moon(CelestialBody):
    """Moon orbiting a planet"""

    def __init__(self, name: str, position: Vector2, parent_planet: Planet):
        """
        Initialize a moon.

        Args:
            name: Name of the moon
            position: Position in space
            parent_planet: Planet this moon orbits
        """
        super().__init__(
            name, CelestialBodyType.MOON, position, radius=0.03, mass=0.012
        )  # Luna-like defaults
        self.parent_planet = parent_planet
        self.orbital_distance = position.distance_to(
            parent_planet.space_object.position
        )
        # Calculate UHS (Universal Habitability Score) for moons
        self.habitability_result = self._calculate_uhs()
        self.habitability_score = self.habitability_result.uhs_score

    def to_string_short(self, position=None):
        """Short description for scanning (following existing pattern)"""
        if position is None:
            return f"🌙 {self.name} (Moon of {self.parent_planet.name}), Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}"
        return f"🌙 {self.name} (Moon of {self.parent_planet.name}), Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}, Distance: {self.space_object.position.distance_to(position):.2f} AU"

    def _calculate_uhs(self):
        """Calculate Universal Habitability Score for moons using the UHS system"""
        from src.classes.habitability import MoonHabitabilityAssessor

        # Prepare moon data for assessment
        moon_data = {
            "orbital_distance": self.orbital_distance,
            "radius": self.radius,
            "mass": self.mass,
            "parent_planet": {
                "mass": self.parent_planet.mass,
                "radius": self.parent_planet.radius,
                "planet_type": self.parent_planet.planet_type.name.lower(),
                "atmosphere": self.parent_planet.atmosphere,
                "orbital_distance": self.parent_planet.orbital_distance,
                "stellar_class": getattr(self.parent_planet, "stellar_class", "G2V"),
                "stellar_age": getattr(self.parent_planet, "stellar_age", 4.6),
            },
        }

        return MoonHabitabilityAssessor.assess_moon(moon_data)

    def get_habitability_details(self) -> str:
        """Get detailed habitability information"""
        if not hasattr(self, "habitability_result"):
            return "Habitability assessment not available"

        result = self.habitability_result
        details = [
            f"Universal Habitability Score: {result.uhs_score}/100",
            f"Rating: {result.rating_text}",
            f"Viable for Life: {'Yes' if result.is_viable else 'No'}",
            f"Critical Viability Factor: {result.cvf_score:.3f}",
            f"Primary Habitability Factor: {result.phf_score:.1f}/100",
        ]
        return "\n".join(details)

    def to_dict(self) -> dict:
        """Serialize moon to dictionary with specialized properties"""
        base_dict = super().to_dict()
        # Add moon-specific properties - store the parent planet's ID
        base_dict.update(
            {
                "parent_planet_id": self.parent_planet.space_object.id,
                # Store name for easier debugging/reconstruction
                "parent_planet_name": self.parent_planet.name,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> "Moon":
        """Deserialize moon from dictionary"""
        # Note: parent_planet linkage will need to be fixed by the caller
        # after all planets and moons are loaded
        position = Vector2(data["position"]["x"], data["position"]["y"])

        # Create a temporary Planet object as parent (will be replaced later)
        from src.classes.celestial_body import Planet

        temp_parent = Planet(
            data["parent_planet_name"],
            Vector2(0, 0),  # Temporary position
            0.0,  # Temporary orbital distance
        )
        temp_parent.space_object.id = data["parent_planet_id"]

        moon = cls(data["name"], position, temp_parent)
        moon.space_object = IsSpaceObject(position, data["id"])
        moon.radius = data.get("radius", 0.03)
        moon.mass = data.get("mass", 0.012)
        moon.orbital_distance = data.get("orbital_distance", 0.0)

        # Reconstruct stations
        from src.classes.station import Station

        for station_data in data.get("stations", []):
            station = Station.from_dict(station_data)
            moon.add_station(station)

        return moon


class AsteroidBelt(CelestialBody):
    """Ring-shaped asteroid belt containing multiple asteroid fields"""

    def __init__(
        self,
        name: str,
        center_position: Vector2,
        inner_radius: float,
        outer_radius: float,
        num_fields: int,
        parent_system: Optional["SolarSystem"] = None,
    ):
        super().__init__(
            name,
            CelestialBodyType.ASTEROID_BELT,
            center_position,
            outer_radius,
            mass=0.01,
        )  # Use outer_radius as CB radius
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.asteroid_fields: List[AsteroidField] = []
        self.num_fields = num_fields  # Store if needed, e.g. for to_dict
        self.parent_system = parent_system  # Reference to parent solar system
        self.generate_asteroid_fields(num_fields)

    def generate_asteroid_fields(self, num_fields: int) -> None:
        """Generates asteroid fields within the belt."""
        if not ORES:  # Ensure ORES is populated
            print(
                "Warning: ORES dictionary is empty. Cannot generate ores for asteroid fields."
            )
            return

        for _ in range(num_fields):
            field_pos = self._random_position_in_belt()
            # Radius of the asteroid field itself
            field_radius = rnd_float(0.05, 0.2)
            # Number of asteroids in this field
            num_asteroids = rnd_int(15, 50)

            # Select 1 to 3 ore types for this field
            ores_for_field = self._select_belt_ores()
            if not ores_for_field:  # Fallback if ore selection fails
                print(
                    f"Warning: Could not select ores for a field in belt {self.name}."
                )
                # Pick a default ore if possible, or skip field generation
                if list(ORES.values()):
                    ores_for_field = [random.choice(list(ORES.values()))]
                else:
                    continue  # Skip this field if no ores can be assigned

            try:
                new_field = AsteroidField(
                    asteroid_quantity=num_asteroids,
                    ores_available=ores_for_field,
                    radius=field_radius,
                    position=field_pos,
                )
                self.asteroid_fields.append(new_field)
            except Exception as e:
                print(f"Error creating AsteroidField in belt {self.name}: {e}")

    def _random_position_in_belt(self) -> Vector2:
        """Calculates a random position within the annulus of the belt.

        Asteroid fields are positioned relative to the star (0, 0), not the belt's
        representative position, since they orbit within the belt's radius range.
        """
        angle = random.uniform(0, 2 * math.pi)
        # Ensure inner_radius < outer_radius to avoid issues with random.uniform
        if self.inner_radius >= self.outer_radius:
            # Default to a small range around inner_radius if radii are problematic
            dist_radius = self.inner_radius + rnd_float(0.01, 0.1)
        else:
            dist_radius = random.uniform(self.inner_radius, self.outer_radius)

        # Position relative to the star (0, 0), not the belt's representative position
        # The asteroid fields orbit the star within the belt's radius range
        offset_x = dist_radius * math.cos(angle)
        offset_y = dist_radius * math.sin(angle)

        return Vector2(offset_x, offset_y)

    def _calculate_density(self) -> float:
        """Calculate asteroid density in belt.

        Returns the density score as fields per square AU area.
        """
        belt_area = math.pi * (self.outer_radius**2 - self.inner_radius**2)
        if belt_area <= 0:
            return 0.0
        return len(self.asteroid_fields) / belt_area

    @property
    def density(self) -> float:
        """Property for accessing belt density score."""
        return self._calculate_density()

    def _select_belt_ores(self) -> List[Ore]:
        """Selects ores for an asteroid field based on temperature zones of nearby planets."""
        if not ORES:
            return []

        # Get the temperature zone influence for this belt
        zone_weights = self._calculate_zone_influence()

        # Select ores based on temperature zone weights
        selected_ores = self._select_ores_by_zone_weights(zone_weights)

        # Fallback to random selection if zone-based selection fails
        if not selected_ores:
            selected_ores = self._select_random_ores()

        return selected_ores

    def _calculate_zone_influence(self) -> dict:
        """Calculate the influence of different temperature zones on this asteroid belt."""
        from src.classes.mineral import MaterialCategory

        # Initialize zone weights
        zone_weights = {
            MaterialCategory.HIGH_TEMP: 0.0,
            MaterialCategory.MID_TEMP: 0.0,
            MaterialCategory.LOW_TEMP: 0.0,
        }

        # Get nearby planets (within reasonable influence distance)
        belt_center = (self.inner_radius + self.outer_radius) / 2
        max_influence_distance = (
            2.0  # AU - planets within this distance affect the belt
        )

        # Find parent solar system to get planet list
        # For now, we'll use a simplified approach - get all planets from parent
        planets = self._get_nearby_planets(belt_center, max_influence_distance)

        if not planets:
            # If no nearby planets, use distance-based zone determination
            return self._get_zone_weights_from_distance(belt_center)

        # Calculate weighted influence from nearby planets
        total_weight = 0.0
        for planet in planets:
            distance = abs(planet.orbital_distance - belt_center)
            influence = max(
                0.0, (max_influence_distance - distance) / max_influence_distance
            )

            if influence > 0:
                total_weight += influence
                zone = planet.temperature_zone

                # Map SolarSystemZone to MaterialCategory
                if zone == SolarSystemZone.INNER_HOT:
                    zone_weights[MaterialCategory.HIGH_TEMP] += influence
                elif zone == SolarSystemZone.MIDDLE_WARM:
                    zone_weights[MaterialCategory.MID_TEMP] += influence
                elif zone == SolarSystemZone.OUTER_COLD:
                    zone_weights[MaterialCategory.LOW_TEMP] += influence

        # Normalize weights
        if total_weight > 0:
            for category in zone_weights:
                zone_weights[category] /= total_weight

        return zone_weights

    def _get_nearby_planets(
        self, belt_center: float, max_distance: float
    ) -> List["Planet"]:
        """Get planets that are within influence distance of this asteroid belt."""
        nearby_planets = []

        # If we have a reference to the parent solar system, get planets from it
        if self.parent_system and hasattr(self.parent_system, "planets"):
            for planet in self.parent_system.planets:
                distance = abs(planet.orbital_distance - belt_center)
                if distance <= max_distance:
                    nearby_planets.append(planet)

        return nearby_planets

    def _get_zone_weights_from_distance(self, belt_center: float) -> dict:
        """Get zone weights based on belt distance from star when no planets are nearby."""
        from src.classes.mineral import MaterialCategory

        # Use similar logic to planet zone determination
        if belt_center < 2.0:
            return {
                MaterialCategory.HIGH_TEMP: 0.7,
                MaterialCategory.MID_TEMP: 0.2,
                MaterialCategory.LOW_TEMP: 0.1,
            }
        elif belt_center < 4.5:  # Before frost line
            return {
                MaterialCategory.HIGH_TEMP: 0.3,
                MaterialCategory.MID_TEMP: 0.5,
                MaterialCategory.LOW_TEMP: 0.2,
            }
        else:  # Beyond frost line
            return {
                MaterialCategory.HIGH_TEMP: 0.1,
                MaterialCategory.MID_TEMP: 0.3,
                MaterialCategory.LOW_TEMP: 0.6,
            }

    def _select_ores_by_zone_weights(self, zone_weights: dict) -> List[Ore]:
        """Select ores based on temperature zone weights."""
        from src.classes.mineral import MaterialCategory

        if not ORES or not zone_weights:
            return []

        # Categorize ores by their material categories
        categorized_ores: dict[MaterialCategory, list[Ore]] = {
            MaterialCategory.HIGH_TEMP: [],
            MaterialCategory.MID_TEMP: [],
            MaterialCategory.LOW_TEMP: [],
        }

        # Categorize ores based on their primary mineral yields
        for ore in ORES.values():
            ore_category = self._determine_ore_category(ore)
            categorized_ores[ore_category].append(ore)

        # Select ores based on zone weights
        selected_ores = []
        num_ore_types = rnd_int(1, min(3, len(ORES)))

        for _ in range(num_ore_types):
            # Choose category based on weights
            categories = list(zone_weights.keys())
            weights = list(zone_weights.values())

            # Ensure we have non-zero weights
            if sum(weights) == 0:
                weights = [1.0, 1.0, 1.0]  # Equal weights as fallback

            chosen_category = random.choices(categories, weights=weights)[0]

            # Select ore from chosen category
            available_ores = categorized_ores[chosen_category]
            if available_ores:
                chosen_ore = random.choice(available_ores)
                if chosen_ore not in selected_ores:
                    selected_ores.append(chosen_ore)

        return selected_ores

    def _determine_ore_category(self, ore: Ore) -> MaterialCategory:
        """Determine the material category of an ore based on its mineral yields."""
        from src.classes.mineral import MINERALS

        if not ore.mineral_yield:
            return MaterialCategory.MID_TEMP  # Default for ores without mineral data

        # Count the categories of minerals this ore produces
        category_weights = {
            MaterialCategory.HIGH_TEMP: 0.0,
            MaterialCategory.MID_TEMP: 0.0,
            MaterialCategory.LOW_TEMP: 0.0,
        }

        total_yield = 0.0
        for mineral_id, yield_amount in ore.mineral_yield:
            mineral = MINERALS.get(mineral_id)
            if mineral:
                category_weights[mineral.category] += float(yield_amount)
                total_yield += float(yield_amount)

        # Return the category with the highest yield
        if total_yield > 0:
            max_category = MaterialCategory.MID_TEMP
            max_weight = 0.0
            for category, weight in category_weights.items():
                if weight > max_weight:
                    max_weight = weight
                    max_category = category
            return max_category
        else:
            return MaterialCategory.MID_TEMP  # Default fallback

    def _select_random_ores(self) -> List[Ore]:
        """Fallback method for random ore selection (original behavior)."""
        if not ORES:
            return []

        num_ore_types = rnd_int(1, min(3, len(ORES)))
        available_ores_list = list(ORES.values())

        if not available_ores_list:
            return []

        selected_ores = random.sample(
            available_ores_list, k=min(num_ore_types, len(available_ores_list))
        )
        return selected_ores

    def to_string_short(self, position=None):
        """Short description for scanning (following existing pattern)"""
        if position is None:
            return f"🪨 {self.name} (Asteroid Belt), Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}"
        return f"🪨 {self.name} (Asteroid Belt), Position: [{self.space_object.position.x:.2f}, {self.space_object.position.y:.2f}], ID: {self.space_object.id}, Distance: {self.space_object.position.distance_to(position):.2f} AU"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            {
                "inner_radius": self.inner_radius,
                "outer_radius": self.outer_radius,
                "num_fields_init": self.num_fields,  # Number of fields requested at init
                "asteroid_fields": [field.to_dict() for field in self.asteroid_fields],
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "AsteroidBelt":
        center_position = Vector2(data["position"]["x"], data["position"]["y"])

        # num_fields for constructor: use "num_fields_init" or derive from loaded fields
        num_fields_for_init = data.get(
            "num_fields_init", len(data.get("asteroid_fields", []))
        )

        belt = cls(
            name=data["name"],
            center_position=center_position,
            inner_radius=data["inner_radius"],
            outer_radius=data["outer_radius"],
            num_fields=num_fields_for_init,  # This will call generate_asteroid_fields
        )

        # Override auto-generated ID and potentially other base class attributes
        if hasattr(belt, "space_object") and "id" in data:
            belt.space_object.id = data["id"]

        belt.orbital_distance = data.get(
            "orbital_distance", 0.0
        )  # from CelestialBody.from_dict

        # Instead of re-generating, we load the saved fields.
        # Clear any fields generated by __init__ and load from data.
        belt.asteroid_fields = []
        if "asteroid_fields" in data:
            for field_data in data["asteroid_fields"]:
                try:
                    belt.asteroid_fields.append(AsteroidField.from_dict(field_data))
                except Exception as e:
                    print(
                        f"Error loading AsteroidField from dict for belt {belt.name}: {e}"
                    )

        # Potentially load stations and children if AsteroidBelts can have them directly
        # (currently CelestialBody.from_dict handles this, which super().from_dict would call if structured that way)
        # For now, assuming stations/children are handled by base from_dict if it were properly cascaded.
        # The current CelestialBody.from_dict is a @classmethod, so direct super call is not typical.
        # We are essentially re-implementing parts of CelestialBody.from_dict logic here for belt-specifics.
        if "stations" in data:  # Copied from CelestialBody.from_dict logic
            from src.classes.station import Station

            belt.stations = [Station.from_dict(st_data) for st_data in data["stations"]]
        if "children" in data:  # Copied from CelestialBody.from_dict logic
            # This recursive call might need adjustment if children can be specific types like Planet, Moon
            belt.children = [
                CelestialBody.from_dict(ch_data) for ch_data in data["children"]
            ]

        return belt
