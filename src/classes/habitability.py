"""
Universal Habitability Score (UHS) System

This module implements a comprehensive habitability assessment system for celestial bodies,
rating them from 0 (completely uninhabitable) to 100 (paradise world) based on their
suitability for carbon-based life requiring liquid water.

The UHS system works in two stages:
1. Critical Viability Factors (CVF): Deal-breaker factors (0-1 scale)
2. Primary Habitability Factors (PHF): Quality assessment (0-100 scale)

Final UHS = CVF × PHF
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class WaterAvailability(Enum):
    """Categories for liquid water availability"""

    NONE = "none"  # No liquid water
    SUBSURFACE_ONLY = "subsurface"  # Only subsurface liquid water
    SURFACE_LIMITED = "limited"  # Limited surface water
    SURFACE_ABUNDANT = "abundant"  # Abundant surface water


class RadiationLevel(Enum):
    """Radiation exposure levels"""

    LETHAL = "lethal"  # Lethal radiation levels
    HIGH = "high"  # High but potentially survivable
    MODERATE = "moderate"  # Moderate radiation
    LOW = "low"  # Low, Earth-like radiation
    PROTECTED = "protected"  # Well-protected (magnetic field + atmosphere)


class AtmosphereType(Enum):
    """Atmospheric composition types"""

    NONE = "none"  # No atmosphere
    TOXIC = "toxic"  # Toxic atmosphere
    CORROSIVE = "corrosive"  # Corrosive atmosphere
    THIN = "thin"  # Thin atmosphere
    DENSE = "dense"  # Dense atmosphere
    BREATHABLE = "breathable"  # Breathable atmosphere
    IDEAL = "ideal"  # Ideal atmospheric composition


class GeologyType(Enum):
    """Geological characteristics"""

    MOLTEN = "molten"  # Molten surface
    FROZEN = "frozen"  # Permanently frozen
    ROCKY = "rocky"  # Rocky, minimal geology
    ACTIVE = "active"  # Geologically active
    DIVERSE = "diverse"  # Diverse geological features


class OrbitalStability(Enum):
    """Orbital stability classification"""

    CHAOTIC = "chaotic"  # Highly unstable orbit
    UNSTABLE = "unstable"  # Somewhat unstable
    STABLE = "stable"  # Stable orbit
    VERY_STABLE = "very_stable"  # Very stable orbit


@dataclass
class HabitabilityFactors:
    """Container for all habitability assessment factors"""

    # Critical Viability Factors (CVF) - Deal breakers (0-1 scale)
    liquid_water_availability: float = 0.0
    biocompatible_temperature: float = 0.0
    radiation_protection: float = 0.0

    # Primary Habitability Factors (PHF) - Quality assessment (0-100 scale)
    atmospheric_conditions: float = 0.0
    substrate_geochemistry: float = 0.0
    energy_availability: float = 0.0
    environmental_stability: float = 0.0
    planetary_characteristics: float = 0.0
    stellar_characteristics: float = 0.0


@dataclass
class HabitabilityResult:
    """Result of habitability assessment"""

    uhs_score: float  # Final Universal Habitability Score (0-100)
    cvf_score: float  # Critical Viability Factor (0-1)
    phf_score: float  # Primary Habitability Factor (0-100)
    factors: HabitabilityFactors
    rating_text: str  # Human-readable rating
    is_viable: bool  # Whether the body passes CVF threshold


class HabitabilityCalculator:
    """Main calculator for Universal Habitability Score"""

    # Weights for Primary Habitability Factors (must sum to 1.0)
    PHF_WEIGHTS = {
        "atmospheric_conditions": 0.20,
        "substrate_geochemistry": 0.15,
        "energy_availability": 0.20,
        "environmental_stability": 0.15,
        "planetary_characteristics": 0.15,
        "stellar_characteristics": 0.15,
    }

    # CVF minimum threshold for viability
    CVF_THRESHOLD = 0.01  # Even minimal viability allows rating

    @classmethod
    def calculate_uhs(cls, factors: HabitabilityFactors) -> HabitabilityResult:
        """
        Calculate the Universal Habitability Score

        Args:
            factors: All habitability factors

        Returns:
            HabitabilityResult with UHS score and details
        """
        # Calculate Critical Viability Factor (CVF)
        cvf = cls._calculate_cvf(factors)

        # Calculate Primary Habitability Factor (PHF)
        phf = cls._calculate_phf(factors)

        # Final UHS = CVF × PHF
        uhs = cvf * phf

        # Determine if viable and rating text
        is_viable = cvf >= cls.CVF_THRESHOLD
        rating_text = cls._get_rating_text(uhs, is_viable)

        return HabitabilityResult(
            uhs_score=round(uhs, 2),
            cvf_score=round(cvf, 4),
            phf_score=round(phf, 2),
            factors=factors,
            rating_text=rating_text,
            is_viable=is_viable,
        )

    @classmethod
    def _calculate_cvf(cls, factors: HabitabilityFactors) -> float:
        """Calculate Critical Viability Factor (multiplication of deal-breakers)"""
        return (
            factors.liquid_water_availability
            * factors.biocompatible_temperature
            * factors.radiation_protection
        )

    @classmethod
    def _calculate_phf(cls, factors: HabitabilityFactors) -> float:
        """Calculate Primary Habitability Factor (weighted average)"""
        return (
            factors.atmospheric_conditions * cls.PHF_WEIGHTS["atmospheric_conditions"]
            + factors.substrate_geochemistry * cls.PHF_WEIGHTS["substrate_geochemistry"]
            + factors.energy_availability * cls.PHF_WEIGHTS["energy_availability"]
            + factors.environmental_stability
            * cls.PHF_WEIGHTS["environmental_stability"]
            + factors.planetary_characteristics
            * cls.PHF_WEIGHTS["planetary_characteristics"]
            + factors.stellar_characteristics
            * cls.PHF_WEIGHTS["stellar_characteristics"]
        )

    @classmethod
    def _get_rating_text(cls, uhs: float, is_viable: bool) -> str:
        """Get human-readable rating text"""
        if not is_viable:
            return "Uninhabitable"
        elif uhs >= 90:
            return "Paradise World"
        elif uhs >= 80:
            return "Excellent"
        elif uhs >= 70:
            return "Very Good"
        elif uhs >= 60:
            return "Good"
        elif uhs >= 50:
            return "Moderate"
        elif uhs >= 40:
            return "Challenging"
        elif uhs >= 30:
            return "Difficult"
        elif uhs >= 20:
            return "Harsh"
        elif uhs >= 10:
            return "Extreme"
        else:
            return "Barely Habitable"


class PlanetaryHabitabilityAssessor:
    """Specialized assessor for planetary bodies"""

    @classmethod
    def assess_planet(cls, planet_data: Dict) -> HabitabilityResult:
        """
        Assess habitability of a planet

        Args:
            planet_data: Dictionary containing planet characteristics

        Returns:
            HabitabilityResult
        """
        factors = HabitabilityFactors()

        # Extract data with defaults
        orbital_distance = planet_data.get("orbital_distance", 0.0)
        planet_type = planet_data.get("planet_type", "rocky")
        atmosphere = planet_data.get("atmosphere", "none")
        radius = planet_data.get("radius", 0.1)
        mass = planet_data.get("mass", 1.0)
        temperature_zone = planet_data.get("temperature_zone", "inner_hot")
        stellar_class = planet_data.get("stellar_class", "G")
        stellar_age = planet_data.get("stellar_age", 5.0)  # Billion years

        # Calculate Critical Viability Factors
        factors.liquid_water_availability = cls._assess_water_availability(
            orbital_distance, planet_type, atmosphere, temperature_zone
        )
        factors.biocompatible_temperature = cls._assess_temperature_compatibility(
            orbital_distance, atmosphere, planet_type
        )
        factors.radiation_protection = cls._assess_radiation_protection(
            atmosphere, planet_type, mass, stellar_class
        )

        # Calculate Primary Habitability Factors
        factors.atmospheric_conditions = cls._assess_atmospheric_conditions(
            atmosphere, planet_type, mass
        )
        factors.substrate_geochemistry = cls._assess_substrate_geochemistry(
            planet_type, orbital_distance, temperature_zone
        )
        factors.energy_availability = cls._assess_energy_availability(
            orbital_distance, stellar_class, atmosphere
        )
        factors.environmental_stability = cls._assess_environmental_stability(
            orbital_distance, planet_type, mass
        )
        factors.planetary_characteristics = cls._assess_planetary_characteristics(
            radius, mass, planet_type
        )
        factors.stellar_characteristics = cls._assess_stellar_characteristics(
            stellar_class, stellar_age, orbital_distance
        )

        return HabitabilityCalculator.calculate_uhs(factors)

    @classmethod
    def _assess_water_availability(
        cls,
        orbital_distance: float,
        planet_type: str,
        atmosphere: str,
        temperature_zone: str,
    ) -> float:
        """Assess liquid water availability (CVF)"""
        # Gas giants can't have surface liquid water
        if planet_type in ["gas_giant", "ice_giant"]:
            return 0.0

        # Temperature zone assessment
        if temperature_zone == "inner_hot":
            if orbital_distance > 0.7:  # Venus-like distance might allow some water
                return 0.2
            return 0.0
        elif temperature_zone == "outer_cold":
            if atmosphere in ["dense", "breathable"]:  # Greenhouse effect
                return 0.6
            elif orbital_distance < 10.0:  # Subsurface only
                return 0.3
            return 0.0
        else:  # middle_warm - habitable zone
            if atmosphere in ["breathable", "ideal"]:
                return 1.0
            elif atmosphere in ["thin", "dense"]:
                return 0.8
            elif atmosphere == "none":
                return 0.1  # Subsurface only
            return 0.4

    @classmethod
    def _assess_temperature_compatibility(
        cls, orbital_distance: float, atmosphere: str, planet_type: str
    ) -> float:
        """Assess biocompatible temperature (CVF)"""
        # Gas giants have extreme conditions
        if planet_type in ["gas_giant", "ice_giant"]:
            return 0.0

        # Rough habitable zone for G-type star: 0.8 - 1.5 AU
        optimal_min, optimal_max = 0.8, 1.5
        extended_min, extended_max = 0.5, 2.5

        if optimal_min <= orbital_distance <= optimal_max:
            base_score = 1.0
        elif extended_min <= orbital_distance <= extended_max:
            base_score = 0.6
        elif orbital_distance < extended_min:
            base_score = max(0.0, 0.8 - (extended_min - orbital_distance) * 0.4)
        else:  # orbital_distance > extended_max
            base_score = max(0.0, 0.8 - (orbital_distance - extended_max) * 0.2)

        # Atmospheric effects
        if atmosphere in ["breathable", "ideal"]:
            return base_score
        elif atmosphere == "dense":
            return base_score * 0.8  # Greenhouse effect might be too much
        elif atmosphere == "thin":
            return base_score * 0.6  # Limited temperature regulation
        elif atmosphere == "none":
            return base_score * 0.2  # Extreme temperature swings
        else:  # toxic, corrosive
            return 0.0

    @classmethod
    def _assess_radiation_protection(
        cls, atmosphere: str, planet_type: str, mass: float, stellar_class: str
    ) -> float:
        """Assess radiation protection (CVF)"""
        if planet_type in ["gas_giant", "ice_giant"]:
            return 0.0  # Extreme radiation environment

        # Base protection from planetary characteristics
        base_protection = min(
            1.0, mass * 0.8
        )  # Larger planets have stronger magnetic fields

        # Atmospheric protection
        atmo_protection = {
            "none": 0.0,
            "thin": 0.3,
            "dense": 0.8,
            "breathable": 1.0,
            "ideal": 1.0,
            "toxic": 0.6,
            "corrosive": 0.4,
        }.get(atmosphere, 0.0)

        # Stellar radiation factor
        stellar_factor = {
            "M": 1.0,  # Red dwarfs - low radiation
            "K": 1.0,  # Orange dwarfs - good
            "G": 1.0,  # Sun-like - ideal
            "F": 0.7,  # Hotter - more radiation
            "A": 0.3,  # Much hotter
            "B": 0.1,  # Very hot
            "O": 0.0,  # Extremely hot
        }.get(stellar_class, 0.8)

        # Combined protection (both magnetic field and atmosphere needed)
        combined_protection = (base_protection + atmo_protection) / 2.0
        return min(1.0, combined_protection * stellar_factor)

    @classmethod
    def _assess_atmospheric_conditions(
        cls, atmosphere: str, planet_type: str, mass: float
    ) -> float:
        """Assess atmospheric conditions (PHF)"""
        if planet_type in ["gas_giant", "ice_giant"]:
            return 0.0

        base_scores = {
            "ideal": 100.0,
            "breathable": 90.0,
            "dense": 60.0,
            "thin": 40.0,
            "toxic": 20.0,
            "corrosive": 10.0,
            "none": 5.0,
        }

        base_score = base_scores.get(atmosphere, 0.0)

        # Mass affects atmospheric retention
        # Larger planets retain atmosphere better
        mass_factor = min(1.0, mass * 1.2)

        return base_score * mass_factor

    @classmethod
    def _assess_substrate_geochemistry(
        cls, planet_type: str, orbital_distance: float, temperature_zone: str
    ) -> float:
        """Assess substrate and geochemistry (PHF)"""
        type_scores = {
            "rocky": 80.0,
            "super_earth": 85.0,
            "gas_giant": 0.0,
            "ice_giant": 10.0,
        }

        base_score = type_scores.get(planet_type, 50.0)

        # Temperature zone affects available chemistry
        zone_multipliers = {
            "inner_hot": 0.6,  # Limited chemistry due to heat
            "middle_warm": 1.0,  # Optimal chemistry
            "outer_cold": 0.8,  # Some chemistry limited by cold
        }

        zone_factor = zone_multipliers.get(temperature_zone, 0.5)

        return base_score * zone_factor

    @classmethod
    def _assess_energy_availability(
        cls, orbital_distance: float, stellar_class: str, atmosphere: str
    ) -> float:
        """Assess energy availability and quality (PHF)"""
        # Solar energy decreases with distance (inverse square law)
        solar_energy = min(100.0, 100.0 / (orbital_distance**2))

        # Stellar class affects energy quality
        stellar_factors = {
            "M": 0.6,  # Red dwarfs - mainly infrared
            "K": 0.8,  # Orange dwarfs
            "G": 1.0,  # Sun-like - ideal
            "F": 0.9,  # Slightly too much UV
            "A": 0.7,  # Too much UV
            "B": 0.3,  # Dangerous radiation
            "O": 0.1,  # Lethal radiation
        }

        stellar_factor = stellar_factors.get(stellar_class, 0.8)

        # Atmospheric filtering
        atmo_factors = {
            "ideal": 1.0,
            "breathable": 0.95,
            "dense": 0.7,  # Filters too much
            "thin": 0.9,
            "toxic": 0.6,
            "corrosive": 0.4,
            "none": 0.8,  # No filtering, but also no protection
        }

        atmo_factor = atmo_factors.get(atmosphere, 0.5)

        return solar_energy * stellar_factor * atmo_factor

    @classmethod
    def _assess_environmental_stability(
        cls, orbital_distance: float, planet_type: str, mass: float
    ) -> float:
        """Assess environmental and orbital stability (PHF)"""
        # Orbital stability (simplified)
        if 0.5 <= orbital_distance <= 5.0:
            orbital_stability = 90.0
        elif 0.3 <= orbital_distance <= 10.0:
            orbital_stability = 70.0
        else:
            orbital_stability = 30.0

        # Mass affects geological stability
        if planet_type in ["gas_giant", "ice_giant"]:
            geological_stability = 20.0  # Chaotic atmospheres
        else:
            # Larger planets more geologically active (can be good or bad)
            if 0.5 <= mass <= 2.0:
                geological_stability = 80.0
            elif 0.1 <= mass <= 0.5:
                geological_stability = 60.0  # Less active
            else:
                geological_stability = 40.0  # Too active or too small

        return (orbital_stability + geological_stability) / 2.0

    @classmethod
    def _assess_planetary_characteristics(
        cls, radius: float, mass: float, planet_type: str
    ) -> float:
        """Assess planetary body characteristics (PHF)"""
        if planet_type in ["gas_giant", "ice_giant"]:
            return 10.0  # Not suitable for surface life

        # Ideal characteristics similar to Earth
        radius_score = max(0, 100 - abs(1.0 - radius) * 100)  # Earth radius = ~1.0
        mass_score = max(0, 100 - abs(1.0 - mass) * 80)  # Earth mass = 1.0

        # Gravity assessment (derived from mass and radius)
        gravity = mass / (radius**2) if radius > 0 else 0
        gravity_score = max(0, 100 - abs(1.0 - gravity) * 50)  # Earth gravity = 1.0

        return (radius_score + mass_score + gravity_score) / 3.0

    @classmethod
    def _assess_stellar_characteristics(
        cls, stellar_class: str, stellar_age: float, orbital_distance: float
    ) -> float:
        """Assess stellar host characteristics (PHF)"""
        # Stellar class suitability
        class_scores = {
            "M": 60.0,  # Red dwarfs - long-lived but tidal locking issues
            "K": 85.0,  # Orange dwarfs - excellent
            "G": 90.0,  # Sun-like - ideal
            "F": 70.0,  # Hotter, shorter-lived
            "A": 40.0,  # Much hotter, short-lived
            "B": 10.0,  # Very hot, very short-lived
            "O": 5.0,  # Extremely hot, extremely short-lived
        }

        class_score = class_scores.get(stellar_class, 50.0)

        # Stellar age assessment (life needs time to develop)
        if stellar_age < 1.0:
            age_score = stellar_age * 50  # Too young
        elif stellar_age <= 8.0:
            age_score = 80.0  # Good age
        elif stellar_age <= 12.0:
            age_score = 60.0  # Getting old but okay
        else:
            age_score = 20.0  # Too old, star becoming unstable

        return (class_score + age_score) / 2.0


class MoonHabitabilityAssessor:
    """Specialized assessor for moon habitability"""

    @classmethod
    def assess_moon(cls, moon_data: Dict) -> HabitabilityResult:
        """
        Assess habitability of a moon

        Moons have different considerations than planets, including:
        - Tidal heating from parent planet
        - Radiation from parent planet (if gas giant)
        - Reduced solar energy due to distance
        """
        # For now, use a simplified assessment
        # Moons are generally less habitable than planets
        factors = HabitabilityFactors()

        # Most moons don't have substantial atmospheres or liquid water
        factors.liquid_water_availability = 0.1  # Subsurface only
        factors.biocompatible_temperature = 0.3  # Usually too cold
        factors.radiation_protection = 0.2  # Limited protection

        # PHF scores are generally lower for moons
        factors.atmospheric_conditions = 10.0
        factors.substrate_geochemistry = 40.0
        factors.energy_availability = 20.0
        factors.environmental_stability = 30.0
        factors.planetary_characteristics = 20.0
        factors.stellar_characteristics = 50.0

        return HabitabilityCalculator.calculate_uhs(factors)
