from dataclasses import dataclass
import random
from random import choice
from enum import Enum, auto
from typing import Dict, Optional, List, Tuple

from src.classes.ore import Ore, ORES, PurityLevel

# Import Mineral and MineralQuality at the top level
from src.classes.mineral import Mineral, MineralQuality
from src.classes.engine import Engine, EngineType


class StellarClass(Enum):
    """
    Stellar classification system based on spectral type.
    Each class has different temperature, luminosity, and size characteristics.
    """

    O = "O"  # Blue supergiant stars - very hot, very luminous, very rare
    B = "B"  # Blue-white stars - hot and luminous
    A = "A"  # White stars - hot
    F = "F"  # Yellow-white stars - slightly hotter than Sun
    G = "G"  # Yellow stars - Sun-like
    K = "K"  # Orange stars - cooler than Sun
    M = "M"  # Red dwarf stars - cool, dim, most common


# Stellar class properties for realistic star generation
STELLAR_PROPERTIES = {
    StellarClass.O: {
        "temperature_range": (30000, 50000),  # Kelvin
        "luminosity_range": (30000, 1000000),  # Solar luminosities
        "mass_range": (15, 90),  # Solar masses
        # Solar radii (for game purposes, scaled down)
        "radius_range": (6.6, 10.0),
        "rarity_weight": 1,  # Very rare
        "color": "blue",
    },
    StellarClass.B: {
        "temperature_range": (10000, 30000),
        "luminosity_range": (25, 30000),
        "mass_range": (2.1, 16),
        "radius_range": (1.8, 6.6),
        "rarity_weight": 3,  # Rare
        "color": "blue-white",
    },
    StellarClass.A: {
        "temperature_range": (7500, 10000),
        "luminosity_range": (5, 25),
        "mass_range": (1.4, 2.1),
        "radius_range": (1.4, 1.8),
        "rarity_weight": 10,  # Uncommon
        "color": "white",
    },
    StellarClass.F: {
        "temperature_range": (6000, 7500),
        "luminosity_range": (1.5, 5),
        "mass_range": (1.04, 1.4),
        "radius_range": (1.15, 1.4),
        "rarity_weight": 15,  # Less common
        "color": "yellow-white",
    },
    StellarClass.G: {
        "temperature_range": (5200, 6000),
        "luminosity_range": (0.6, 1.5),
        "mass_range": (0.8, 1.04),
        "radius_range": (0.96, 1.15),
        "rarity_weight": 25,  # Common (Sun-like)
        "color": "yellow",
    },
    StellarClass.K: {
        "temperature_range": (3700, 5200),
        "luminosity_range": (0.08, 0.6),
        "mass_range": (0.45, 0.8),
        "radius_range": (0.7, 0.96),
        "rarity_weight": 30,  # Very common
        "color": "orange",
    },
    StellarClass.M: {
        "temperature_range": (2400, 3700),
        "luminosity_range": (0.0001, 0.08),
        "mass_range": (0.08, 0.45),
        "radius_range": (0.1, 0.7),
        "rarity_weight": 50,  # Most common
        "color": "red",
    },
}


class SolarSystemZone(Enum):
    """
    Represents different temperature zones in a solar system based on distance from the star.
    These zones determine the types of materials that can condense and form solid bodies.
    """

    INNER_HOT = auto()  # Close to star, only high-temperature materials condense
    MIDDLE_WARM = auto()  # Moderate distance, mid-temperature materials condense
    OUTER_COLD = auto()  # Far from star, all materials including ices can condense


class PlanetType(Enum):
    """
    Types of planets that can form in different zones of a solar system.
    """

    ROCKY = auto()  # Small, dense planets made of rock and metal (inner zone)
    GAS_GIANT = auto()  # Large planets with thick atmospheres (outer zone)
    ICE_GIANT = auto()  # Planets with significant ice content (outer zone)
    SUPER_EARTH = auto()  # Larger rocky planets (can form in various zones)


# Constants for celestial body generation
# Min/max number of planets to generate
PLANET_MIN_MAX_NUM: Tuple[int, int] = (3, 8)
ASTEROID_BELT_MIN_MAX_NUM: Tuple[int, int] = (1, 3)  # Min/max number of asteroid belts
ASTEROID_BELT_WIDTH_MIN_MAX: Tuple[float, float] = (0.5, 2.0)  # Belt width in AU
ASTEROID_BELT_FIELDS_MIN_MAX: Tuple[int, int] = (3, 8)  # Fields per belt

# System generation templates for creating diverse solar systems


@dataclass
class SystemTemplate:
    """
    Template for generating solar systems with specific characteristics.
    Defines ranges and probabilities for system properties.
    """

    name: str
    description: str

    # System size and structure
    size_range: Tuple[float, float]  # AU, system radius
    field_quantity_range: Tuple[int, int]  # Number of asteroid fields
    station_quantity_range: Tuple[int, int]  # Number of stations

    # Preferred stellar classes (weighted selection)
    stellar_class_weights: Dict[StellarClass, float]

    # Economic and political characteristics
    security_levels: List[str]  # Possible security levels
    economy_types: List[str]  # Possible economy types
    population_range: Tuple[int, int]  # Population range
    tech_level_range: Tuple[int, int]  # Technology level range
    # Special characteristics
    faction_preference: Optional[str] = None  # Preferred faction
    anomaly_chance: float = 0.1  # Chance of having anomalies
    possible_anomalies: Optional[List[str]] = None  # Types of anomalies

    # Generation weight for template selection
    generation_weight: float = 1.0


# Define system templates for different types of solar systems
SYSTEM_TEMPLATES = {
    "frontier": SystemTemplate(
        name="Frontier System",
        description="Remote, sparsely populated system on the edge of known space",
        size_range=(80.0, 120.0),
        field_quantity_range=(15, 35),
        station_quantity_range=(1, 3),
        stellar_class_weights={
            StellarClass.M: 60.0,  # Red dwarfs common in frontier
            StellarClass.K: 25.0,
            StellarClass.G: 10.0,
            StellarClass.F: 4.0,
            StellarClass.A: 1.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Low", "Minimal", "Lawless"],
        economy_types=["Mining", "Salvage", "Independent"],
        population_range=(100, 10000),
        tech_level_range=(1, 4),
        anomaly_chance=0.15,
        possible_anomalies=["Sensor Ghost", "Gravity Well", "Ancient Wreck"],
        generation_weight=30.0,
    ),
    "core_world": SystemTemplate(
        name="Core World System",
        description="Heavily populated and developed system in civilized space",
        size_range=(60.0, 100.0),
        field_quantity_range=(5, 15),
        station_quantity_range=(3, 8),
        stellar_class_weights={
            StellarClass.G: 40.0,  # Sun-like stars preferred for habitable worlds
            StellarClass.F: 25.0,
            StellarClass.K: 20.0,
            StellarClass.A: 10.0,
            StellarClass.M: 5.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["High", "Maximum", "Corporate"],
        economy_types=["Industrial", "Commercial", "Financial", "Research"],
        population_range=(100000, 50000000),
        tech_level_range=(6, 10),
        faction_preference="Core Federation",
        anomaly_chance=0.05,
        possible_anomalies=["Trade Beacon", "Security Grid"],
        generation_weight=15.0,
    ),
    "mining_hub": SystemTemplate(
        name="Mining Hub System",
        description="System rich in asteroids and mineral resources",
        size_range=(100.0, 180.0),
        field_quantity_range=(25, 60),
        station_quantity_range=(2, 6),
        stellar_class_weights={
            StellarClass.M: 35.0,
            StellarClass.K: 30.0,
            StellarClass.G: 20.0,
            StellarClass.F: 10.0,
            StellarClass.A: 4.0,
            StellarClass.B: 1.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Medium", "Low", "Corporate"],
        economy_types=["Mining", "Heavy Industry", "Refining"],
        population_range=(5000, 500000),
        tech_level_range=(3, 7),
        anomaly_chance=0.08,
        possible_anomalies=["Rich Asteroid Belt", "Depleted Field", "Mining Accident"],
        generation_weight=25.0,
    ),
    "research_outpost": SystemTemplate(
        name="Research Outpost System",
        description="Scientific research system with unique phenomena",
        size_range=(70.0, 130.0),
        field_quantity_range=(8, 20),
        station_quantity_range=(1, 4),
        stellar_class_weights={
            StellarClass.A: 25.0,  # Interesting stellar phenomena
            StellarClass.B: 20.0,
            StellarClass.F: 20.0,
            StellarClass.G: 15.0,
            StellarClass.K: 10.0,
            StellarClass.M: 5.0,
            StellarClass.O: 5.0,  # Rare but scientifically interesting
        },
        security_levels=["High", "Restricted", "Research"],
        economy_types=["Research", "Scientific", "Experimental"],
        population_range=(50, 5000),
        tech_level_range=(7, 10),
        faction_preference="Research Consortium",
        anomaly_chance=0.25,
        possible_anomalies=[
            "Stellar Anomaly",
            "Quantum Field",
            "Exotic Matter",
            "Time Dilation",
        ],
        generation_weight=10.0,
    ),
    "trade_crossroads": SystemTemplate(
        name="Trade Crossroads System",
        description="Strategic system along major trade routes",
        size_range=(80.0, 120.0),
        field_quantity_range=(10, 25),
        station_quantity_range=(4, 10),
        stellar_class_weights={
            StellarClass.G: 35.0,
            StellarClass.F: 25.0,
            StellarClass.K: 25.0,
            StellarClass.A: 10.0,
            StellarClass.M: 5.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Medium", "High", "Neutral"],
        economy_types=["Trade", "Commercial", "Transit Hub", "Logistics"],
        population_range=(10000, 1000000),
        tech_level_range=(5, 8),
        anomaly_chance=0.12,
        possible_anomalies=["Trade Beacon", "Pirate Activity", "Navigation Hazard"],
        generation_weight=20.0,
    ),
    # New diverse system templates for expanded variety
    "abandoned_ruins": SystemTemplate(
        name="Abandoned Ruins System",
        description="Derelict system with remnants of an ancient civilization",
        size_range=(90.0, 140.0),
        field_quantity_range=(20, 45),
        station_quantity_range=(0, 2),
        stellar_class_weights={
            StellarClass.M: 40.0,  # Older, cooler stars
            StellarClass.K: 30.0,
            StellarClass.G: 15.0,
            StellarClass.F: 10.0,
            StellarClass.A: 3.0,
            StellarClass.B: 2.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Minimal", "Lawless", "Hazardous"],
        economy_types=["Salvage", "Archaeological", "Scavenging"],
        population_range=(0, 1000),
        tech_level_range=(0, 6),
        faction_preference=None,
        anomaly_chance=0.40,
        possible_anomalies=[
            "Ancient Wreck",
            "Derelict Station",
            "Quantum Signature",
            "Ruins",
            "Data Cache",
            "Defense Grid",
        ],
        generation_weight=8.0,
    ),
    "military_outpost": SystemTemplate(
        name="Military Outpost System",
        description="Fortified system under military control with heavy security",
        size_range=(70.0, 110.0),
        field_quantity_range=(8, 18),
        station_quantity_range=(2, 5),
        stellar_class_weights={
            StellarClass.G: 30.0,
            StellarClass.F: 25.0,
            StellarClass.K: 25.0,
            StellarClass.A: 15.0,
            StellarClass.M: 5.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Maximum", "Restricted", "Military"],
        economy_types=["Military", "Defense", "Strategic"],
        population_range=(1000, 100000),
        tech_level_range=(6, 10),
        faction_preference="Military Command",
        anomaly_chance=0.08,
        possible_anomalies=["Security Grid", "Defense Platform", "Patrol Route"],
        generation_weight=12.0,
    ),
    "pirate_haven": SystemTemplate(
        name="Pirate Haven System",
        description="Lawless system controlled by pirate factions and smugglers",
        size_range=(110.0, 160.0),
        field_quantity_range=(18, 40),
        station_quantity_range=(2, 6),
        stellar_class_weights={
            StellarClass.M: 45.0,
            StellarClass.K: 30.0,
            StellarClass.G: 15.0,
            StellarClass.F: 8.0,
            StellarClass.A: 2.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Lawless", "Hostile", "Dangerous"],
        economy_types=["Piracy", "Smuggling", "Black Market"],
        population_range=(500, 50000),
        tech_level_range=(2, 6),
        faction_preference="Pirate Brotherhood",
        anomaly_chance=0.18,
        possible_anomalies=[
            "Pirate Activity",
            "Hidden Base",
            "Ambush Point",
            "Stolen Cargo",
        ],
        generation_weight=15.0,
    ),
    "corporate_domain": SystemTemplate(
        name="Corporate Domain System",
        description="System under direct corporate control with heavy industrial presence",
        size_range=(80.0, 130.0),
        field_quantity_range=(12, 30),
        station_quantity_range=(3, 8),
        stellar_class_weights={
            StellarClass.G: 35.0,
            StellarClass.F: 30.0,
            StellarClass.K: 20.0,
            StellarClass.A: 12.0,
            StellarClass.M: 3.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Corporate", "High", "Restricted"],
        economy_types=["Corporate", "Industrial", "Manufacturing"],
        population_range=(50000, 10000000),
        tech_level_range=(7, 10),
        faction_preference="Mega Corporation",
        anomaly_chance=0.06,
        possible_anomalies=["Corporate Facility", "Production Line", "Trade Beacon"],
        generation_weight=18.0,
    ),
    "agricultural_colony": SystemTemplate(
        name="Agricultural Colony System",
        description="Peaceful farming system providing food for nearby regions",
        size_range=(60.0, 100.0),
        field_quantity_range=(5, 15),
        station_quantity_range=(1, 4),
        stellar_class_weights={
            StellarClass.G: 50.0,  # Sun-like stars ideal for agriculture
            StellarClass.K: 30.0,
            StellarClass.F: 15.0,
            StellarClass.A: 5.0,
            StellarClass.M: 0.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Medium", "High", "Peaceful"],
        economy_types=["Agricultural", "Food Production", "Colonial"],
        population_range=(5000, 500000),
        tech_level_range=(4, 7),
        faction_preference="Colonial Authority",
        anomaly_chance=0.05,
        possible_anomalies=["Fertile Zone", "Weather Control", "Harvest Festival"],
        generation_weight=14.0,
    ),
    "hazardous_zone": SystemTemplate(
        name="Hazardous Zone System",
        description="Dangerous system with extreme stellar phenomena and environmental hazards",
        size_range=(120.0, 200.0),
        field_quantity_range=(30, 70),
        station_quantity_range=(0, 3),
        stellar_class_weights={
            StellarClass.O: 25.0,  # Extremely hot stars
            StellarClass.B: 30.0,
            StellarClass.A: 20.0,
            StellarClass.F: 15.0,
            StellarClass.G: 8.0,
            StellarClass.K: 2.0,
            StellarClass.M: 0.0,
        },
        security_levels=["Hazardous", "Extreme", "Lethal"],
        economy_types=["Extreme Mining", "Hazmat", "Research"],
        population_range=(0, 5000),
        tech_level_range=(5, 9),
        faction_preference=None,
        anomaly_chance=0.35,
        possible_anomalies=[
            "Solar Flare",
            "Radiation Storm",
            "Magnetic Field",
            "Plasma Eruption",
            "Stellar Wind",
        ],
        generation_weight=6.0,
    ),
    "border_disputed": SystemTemplate(
        name="Border Disputed System",
        description="Contested system on the frontier between major factions",
        size_range=(85.0, 125.0),
        field_quantity_range=(12, 28),
        station_quantity_range=(2, 6),
        stellar_class_weights={
            StellarClass.K: 35.0,
            StellarClass.G: 25.0,
            StellarClass.M: 25.0,
            StellarClass.F: 10.0,
            StellarClass.A: 5.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Low", "Variable", "Contested"],
        economy_types=["War Economy", "Mercenary", "Supply Hub"],
        population_range=(1000, 200000),
        tech_level_range=(4, 8),
        faction_preference=None,
        anomaly_chance=0.15,
        possible_anomalies=[
            "Patrol Route",
            "Border Beacon",
            "Conflict Zone",
            "Neutral Ground",
        ],
        generation_weight=13.0,
    ),
    "refinery_complex": SystemTemplate(
        name="Refinery Complex System",
        description="Industrial system specialized in ore processing and material refinement",
        size_range=(90.0, 140.0),
        field_quantity_range=(35, 55),
        station_quantity_range=(4, 9),
        stellar_class_weights={
            StellarClass.M: 30.0,
            StellarClass.K: 35.0,
            StellarClass.G: 25.0,
            StellarClass.F: 8.0,
            StellarClass.A: 2.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Medium", "Corporate", "Industrial"],
        economy_types=["Refining", "Processing", "Heavy Industry"],
        population_range=(20000, 800000),
        tech_level_range=(5, 8),
        faction_preference="Industrial Syndicate",
        anomaly_chance=0.10,
        possible_anomalies=["Processing Plant", "Refinery Station", "Material Cache"],
        generation_weight=16.0,
    ),
    "ancient_mystery": SystemTemplate(
        name="Ancient Mystery System",
        description="System containing artifacts and phenomena from a lost civilization",
        size_range=(100.0, 150.0),
        field_quantity_range=(15, 35),
        station_quantity_range=(1, 4),
        stellar_class_weights={
            StellarClass.A: 20.0,
            StellarClass.B: 15.0,
            StellarClass.F: 25.0,
            StellarClass.G: 20.0,
            StellarClass.K: 15.0,
            StellarClass.M: 5.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Restricted", "Research", "Unknown"],
        economy_types=["Archaeological", "Xenological", "Research"],
        population_range=(100, 10000),
        tech_level_range=(6, 10),
        faction_preference="Archaeological Institute",
        anomaly_chance=0.50,
        possible_anomalies=[
            "Ancient Artifact",
            "Xenotech",
            "Psionic Field",
            "Stasis Chamber",
            "Energy Signature",
            "Precursor Tech",
        ],
        generation_weight=5.0,
    ),
    "nomadic_fleet": SystemTemplate(
        name="Nomadic Fleet System",
        description="System serving as a temporary home for wandering space nomads",
        size_range=(80.0, 120.0),
        field_quantity_range=(10, 25),
        station_quantity_range=(2, 7),
        stellar_class_weights={
            StellarClass.M: 40.0,
            StellarClass.K: 35.0,
            StellarClass.G: 20.0,
            StellarClass.F: 5.0,
            StellarClass.A: 0.0,
            StellarClass.B: 0.0,
            StellarClass.O: 0.0,
        },
        security_levels=["Neutral", "Nomadic", "Transient"],
        economy_types=["Nomadic Trade", "Barter", "Fleet Support"],
        population_range=(5000, 150000),
        tech_level_range=(3, 7),
        faction_preference="Nomad Flotilla",
        anomaly_chance=0.12,
        possible_anomalies=["Fleet Gathering", "Trade Convoy", "Nomad Camp"],
        generation_weight=9.0,
    ),
}


def select_system_template() -> SystemTemplate:
    """
    Select a random system template based on generation weights.

    Returns:
        A SystemTemplate to use for generating a solar system
    """
    templates = list(SYSTEM_TEMPLATES.values())
    weights = [template.generation_weight for template in templates]

    # Use weighted random selection
    total_weight = sum(weights)
    random_value = random.uniform(0, total_weight)

    cumulative_weight = 0.0
    for template, weight in zip(templates, weights):
        cumulative_weight += weight
        if random_value <= cumulative_weight:
            return template

    # Fallback to frontier system
    return SYSTEM_TEMPLATES["frontier"]


def generate_system_from_template(
    name: str, x: float, y: float, template: SystemTemplate
) -> dict:
    """
    Generate solar system parameters from a template.

    Args:
        name: Name of the system
        x: X coordinate in the region
        y: Y coordinate in the region
        template: SystemTemplate to use for generation

    Returns:
        Dictionary of parameters for SolarSystem constructor
    """
    import random

    # Generate basic system parameters
    size = round(random.uniform(*template.size_range), 2)
    field_quantity = random.randint(*template.field_quantity_range)
    station_quantity = random.randint(*template.station_quantity_range)

    # Select security level and economy type
    security_level = random.choice(template.security_levels)
    economy_type = random.choice(template.economy_types)

    # Generate population and tech level
    population = random.randint(*template.population_range)
    tech_level = random.randint(*template.tech_level_range)

    # Generate anomalies if applicable
    anomalies = []
    if template.possible_anomalies and random.random() < template.anomaly_chance:
        num_anomalies = random.randint(1, min(2, len(template.possible_anomalies)))
        anomalies = random.sample(template.possible_anomalies, num_anomalies)

    return {
        "name": name,
        "x": x,
        "y": y,
        "size": size,
        "field_quantity": field_quantity,
        "station_quantity": station_quantity,
        "description": f"{template.description} - {economy_type} economy",
        "faction_id": template.faction_preference,
        "security_level": security_level,
        "economy_type": economy_type,
        "population": population,
        "tech_level": tech_level,
        "anomalies": anomalies,
    }


# This will be used to generate random names
name_parts = [
    "ha",
    "he",
    "hi",
    "ho",
    "hu",
    "ca",
    "ce",
    "ci",
    "co",
    "cu",
    "sa",
    "se",
    "si",
    "so",
    "su",
    "ja",
    "ji",
    "je",
    "jo",
    "ju",
    "an",
    "pa",
    "pe",
    "pi",
    "po",
    "pu",
    "ta",
    "te",
    "ti",
    "to",
    "tu",
    "kle",
    "ke",
    "ki",
    "ko",
    "ku",
    "sha",
    "she",
    "shi",
    "sho",
    "shu",
    "hor",
    "cer",
    "cur",
    "her",
    "hur",
    "sar",
    "arn",
    "irn",
    "kler",
    "ka",
    "la",
    "nar",
    "kar",
    "bar",
    "dar",
    "blar",
    "ger",
    "yur",
    "zor",
    "for",
    "wor",
    "gor",
    "noth",
    "roth",
    "moth",
    "zoth",
    "loth",
    "nith",
    "lith",
    "sith",
    "dith",
    "ith",
    "oth",
    "orb",
    "urb",
    "er",
    "zer",
    "ze",
    "zera",
    "ter",
    "nor",
    "za",
    "zi",
    "di",
    "mi",
    "per",
    "pir",
    "pera",
    "par",
    "sta",
    "mor",
    "kur",
    "ker",
    "ni",
    "ler",
    "der",
    "ber",
    "shar",
    "sher",
    "mer",
    "wer",
    "fer",
    "fragra",
    "bra",
    "zir",
    "dir",
    "tir",
    "sir",
    "mir",
    "nir",
    "por",
    "lir",
    "bir",
    "dra",
    "tha",
    "the",
    "tho",
    "ta",
    "te",
    "ti",
    "to",
    "tu",
    "ba",
    "be",
    "bi",
    "bo",
    "tis",
    "ris",
    "beur",
    "bu",
    "cu",
    "lur",
    "mur",
    "da",
    "de",
    "di",
    "do",
    "ka",
    "ke",
    "ki",
    "ko",
    "ku",
    "la",
    "le",
    "li",
    "lo",
    "lu",
    "loo",
    "koo",
    "lee",
    "kee",
    "du",
    "lor",
    "der",
    "ser",
    "per",
    "fu",
    "fer",
    "ler",
    "zer",
    "wi",
    "na",
    "ne",
    "no",
    "noo",
    "ra",
    "ri",
    "ro",
    "roo",
    "va",
    "ve",
    "vi",
    "vo",
    "vu",
    "bre",
    "dre",
    "pre",
    "tre",
    "gre",
]


def generate_random_name(parts_num: int) -> str:
    return ("".join(choice(name_parts) for _ in range(parts_num))).capitalize()


@dataclass
class OreCargo:
    ore: Ore
    quantity: int
    buy_price: float
    sell_price: float

    def to_dict(self):
        return {
            "ore_id": self.ore.commodity.commodity_id,
            "quantity": self.quantity,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "purity": self.ore.purity.name if hasattr(self.ore, "purity") else "RAW",
        }

    @classmethod
    def from_dict(cls, data):
        ore_obj = ORES.get(data["ore_id"])
        if ore_obj is None:
            # Handle missing ore, perhaps raise an error or return None
            # Handle purity if present
            raise ValueError(f"Ore with ID {data['ore_id']} not found in ORES map.")
        if "purity" in data:
            try:
                purity_level = PurityLevel[data["purity"]]
                # Create a copy of the ore with the saved purity level
                ore_obj = Ore(
                    commodity=ore_obj.commodity,
                    mineral_yield=(
                        ore_obj.mineral_yield.copy() if ore_obj.mineral_yield else []
                    ),
                    purity=purity_level,
                    refining_difficulty=(
                        ore_obj.refining_difficulty
                        if hasattr(ore_obj, "refining_difficulty")
                        else 1.0
                    ),
                )
            except (KeyError, AttributeError):
                # If there's an error with purity, use the default ore
                pass

        return cls(
            ore=ore_obj,
            quantity=data["quantity"],
            buy_price=data["buy_price"],
            sell_price=data["sell_price"],
        )


@dataclass
class MineralCargo:
    """
    Represents a quantity of minerals in the player's cargo or a station's inventory.
    """

    mineral: Mineral
    quantity: int
    buy_price: float
    sell_price: float

    def to_dict(self):
        return {
            "mineral_id": self.mineral.id,
            "quantity": self.quantity,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "quality": (
                self.mineral.quality.name
                if hasattr(self.mineral, "quality")
                else "STANDARD"
            ),
        }

    @classmethod
    def from_dict(cls, data):
        from src.classes.mineral import MINERALS

        mineral_obj = MINERALS.get(data["mineral_id"])
        if mineral_obj is None:
            # Handle missing mineral, raise an error
            raise ValueError(
                f"Mineral with ID {data['mineral_id']} not found in MINERALS map."
            )

        # Handle quality if present
        if "quality" in data:
            try:
                quality_level = MineralQuality[data["quality"]]
                # Create a copy of the mineral with the saved quality level
                mineral_obj = Mineral(
                    name=mineral_obj.name,
                    base_value=mineral_obj.base_value,
                    volume=mineral_obj.volume,
                    id=mineral_obj.id,
                    quality=quality_level,
                )
            except (KeyError, AttributeError):
                # If there's an error with quality, use the default mineral
                pass

        return cls(
            mineral=mineral_obj,
            quantity=data["quantity"],
            buy_price=data["buy_price"],
            sell_price=data["sell_price"],
        )


class UpgradeCategory(Enum):
    """Categories of ship upgrades"""

    PROPULSION = auto()
    MINING = auto()
    CARGO = auto()
    SENSORS = auto()
    UTILITY = auto()
    DEFENSE = auto()


class UpgradeTarget(Enum):
    """Ship attributes that can be upgraded"""

    SPEED = auto()
    MINING_SPEED = auto()
    FUEL_CONSUMPTION = auto()
    FUEL_CAPACITY = auto()
    CARGO_CAPACITY = auto()
    SENSOR_RANGE = auto()
    HULL_INTEGRITY = auto()
    SHIELD_CAPACITY = auto()


@dataclass
class Upgrade:
    """A template for ship upgrades"""

    id: str
    name: str
    description: str
    price: float
    category: UpgradeCategory
    target: UpgradeTarget
    multiplier: float
    level: int = 1
    max_level: int = 5
    prerequisites: Optional[List[str]] = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category.name,
            "target": self.target.name,
            "multiplier": self.multiplier,
            "level": self.level,
            "max_level": self.max_level,
            "prerequisites": self.prerequisites,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            price=data["price"],
            category=UpgradeCategory[data["category"]],
            target=UpgradeTarget[data["target"]],
            multiplier=data["multiplier"],
            level=data["level"],
            max_level=data["max_level"],
            prerequisites=data["prerequisites"],
        )

    def get_next_level_price(self) -> float:
        """Calculate the price for the next upgrade level"""
        if self.level >= self.max_level:
            return float("inf")  # Can't upgrade past max level
        return self.price * (self.level + 1)

    def upgrade(self) -> bool:
        """Attempt to upgrade to the next level"""
        if self.level < self.max_level:
            self.level += 1
            return True
        return False

    def get_total_multiplier(self) -> float:
        """Get the cumulative multiplier effect based on current level"""
        return 1.0 + (self.multiplier - 1.0) * self.level

    def copy(self) -> "Upgrade":
        """Create a copy of this upgrade"""
        return Upgrade(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            category=self.category,
            target=self.target,
            multiplier=self.multiplier,
            level=self.level,
            max_level=self.max_level,
            prerequisites=self.prerequisites.copy() if self.prerequisites else None,
        )


# Ship upgrade templates
UPGRADES = {
    # Propulsion upgrades
    "engine_tune": Upgrade(
        id="engine_tune",
        name="Engine Tuning",
        description="Increases the ship's speed",
        price=100_000,
        category=UpgradeCategory.PROPULSION,
        target=UpgradeTarget.SPEED,
        multiplier=1.05,
    ),
    # Mining upgrades
    "mining_laser": Upgrade(
        id="mining_laser",
        name="Advanced Mining Laser",
        description="Increases the ship's mining speed",
        price=250_000,
        category=UpgradeCategory.MINING,
        target=UpgradeTarget.MINING_SPEED,
        multiplier=1.05,
    ),
    # Utility upgrades
    "fuel_optimizer": Upgrade(
        id="fuel_optimizer",
        name="Fuel Optimization System",
        description="Decreases the ship's fuel consumption",
        price=100_000,
        category=UpgradeCategory.UTILITY,
        target=UpgradeTarget.FUEL_CONSUMPTION,
        multiplier=0.95,  # Note: This is a reduction, so < 1.0
    ),
    "extended_tank": Upgrade(
        id="extended_tank",
        name="Extended Fuel Tank",
        description="Increases the ship's fuel capacity",
        price=150_000,
        category=UpgradeCategory.UTILITY,
        target=UpgradeTarget.FUEL_CAPACITY,
        multiplier=1.05,
    ),
    # Cargo upgrades
    "cargo_expander": Upgrade(
        id="cargo_expander",
        name="Cargo Bay Expansion",
        description="Increases the ship's cargo capacity",
        price=150_000,
        category=UpgradeCategory.CARGO,
        target=UpgradeTarget.CARGO_CAPACITY,
        multiplier=1.05,
    ),
    # Sensor upgrades
    "sensor_array": Upgrade(
        id="sensor_array",
        name="Enhanced Sensor Array",
        description="Increases the ship's sensor range",
        price=120_000,
        category=UpgradeCategory.SENSORS,
        target=UpgradeTarget.SENSOR_RANGE,
        multiplier=1.1,
    ),  # Defense upgrades
    "hull_plating": Upgrade(
        id="hull_plating",
        name="Reinforced Hull Plating",
        description="Increases the ship's hull integrity",
        price=200_000,
        category=UpgradeCategory.DEFENSE,
        target=UpgradeTarget.HULL_INTEGRITY,
        multiplier=1.08,
    ),
}

# Engine types available in the game
ENGINES = {
    "standard": Engine(
        id="standard",
        name="Standard Drive",
        description="The common, workhorse engine with balanced performance.",
        engine_type=EngineType.STANDARD,
        price=50_000,
        speed_modifier=1.0,
        fuel_consumption_modifier=1.0,
        sensor_signature_modifier=1.0,
        maintenance_cost_modifier=1.0,
        magneton_resistance=0.0,
    ),
    "cargo_hauler": Engine(
        id="cargo_hauler",
        name="Cargo Hauler Drive",
        description="Designed for bulk transport with built-in shielding to counteract magnetic interference from ores like Magneton.",
        engine_type=EngineType.CARGO_HAULER,
        price=85_000,
        speed_modifier=0.9,  # Slightly lower speed
        fuel_consumption_modifier=1.0,  # Baseline fuel consumption
        sensor_signature_modifier=1.1,  # Slightly higher signature due to dampeners
        maintenance_cost_modifier=1.2,  # Medium maintenance cost
        magneton_resistance=0.85,  # Reduces magneton penalties by 85%
    ),
    "high_performance": Engine(
        id="high_performance",
        name="High-Performance Drive",
        description="Optimized for maximum speed and acceleration, using advanced magnetic coils.",
        engine_type=EngineType.HIGH_PERFORMANCE,
        price=120_000,
        speed_modifier=1.4,  # Significantly faster
        fuel_consumption_modifier=1.5,  # Higher fuel consumption
        sensor_signature_modifier=1.2,  # Higher signature
        maintenance_cost_modifier=1.4,  # Higher maintenance
        magneton_resistance=0.0,  # Standard magneton sensitivity
    ),
    "stealth": Engine(
        id="stealth",
        name="Stealth Drive",
        description="Uses advanced dampening technology to minimize detection.",
        engine_type=EngineType.STEALTH,
        price=150_000,
        speed_modifier=0.8,  # Slower speed due to stealth systems
        fuel_consumption_modifier=1.1,  # Slightly more fuel consumption
        sensor_signature_modifier=0.4,  # Very low signature
        maintenance_cost_modifier=1.5,  # High maintenance
        magneton_resistance=0.0,  # Standard magneton sensitivity
    ),
    "economy": Engine(
        id="economy",
        name="Economy Drive",
        description="Optimized for minimal fuel consumption.",
        engine_type=EngineType.ECONOMY,
        price=70_000,
        speed_modifier=0.9,  # Slightly slower speed
        fuel_consumption_modifier=0.5,  # Very low fuel consumption
        sensor_signature_modifier=0.8,  # Low signature
        maintenance_cost_modifier=0.9,  # Low maintenance
        magneton_resistance=0.0,  # Standard magneton sensitivity
    ),
}

# Ship templates for character creation
SHIP_TEMPLATES = {
    "armored_behemoth": {
        "name": "Armored Behemoth",
        "description": "Thick plating, heavy weapon mounts. Built to take a beating and dish one out.",
        "speed": 1e-10,  # Slowest ship (1e-10 AU/s)
        "max_fuel": 120.0,  # Higher fuel capacity
        "fuel_consumption": 1.2,  # Higher fuel consumption due to weight
        "cargo_capacity": 120.0,  # Large cargo hold
        "value": 12000.0,
        "mining_speed": 1.0,
        "sensor_range": 0.8,  # Reduced sensor range
        "hull_integrity": 150.0,  # High hull strength
        "shield_capacity": 20.0,  # Basic shields
        "engine_id": "standard",  # Default standard engine
        "sensor_signature": 1.2,  # Higher signature due to bulk
        "antimatter_capacity": 5.0,  # Standard antimatter capacity
        # Higher consumption due to mass (0.07g/LY)
        "antimatter_consumption": 0.07,
    },
    "agile_interceptor": {
        "name": "Agile Interceptor",
        "description": "Streamlined and fast. Prioritizes speed and maneuverability over raw power.",
        "speed": 1e-04,  # Fastest ship (1e-04 AU/s or 0.0001 AU/s)
        "max_fuel": 80.0,  # Lower fuel capacity
        "fuel_consumption": 0.8,  # More efficient due to streamlining
        "cargo_capacity": 70.0,  # Smaller cargo capacity
        "value": 11000.0,
        "mining_speed": 0.9,  # Slightly lower mining speed
        "sensor_range": 1.2,  # Enhanced sensors
        "hull_integrity": 80.0,  # Lower hull integrity
        "shield_capacity": 10.0,  # Minimal shields
        "engine_id": "high_performance",  # High performance engine
        "sensor_signature": 0.8,  # Lower signature due to smaller profile
        "antimatter_capacity": 6.0,  # Enhanced antimatter capacity
        "antimatter_consumption": 0.04,  # Efficient antimatter use (0.04g/LY)
    },
    "balanced_cruiser": {
        "name": "Balanced Cruiser",
        "description": "A versatile design. Decent armor, speed, and firepower for most situations.",
        "speed": 5e-05,  # Balanced speed (5e-05 AU/s)
        "max_fuel": 100.0,  # Standard fuel capacity
        "fuel_consumption": 1.0,  # Standard fuel consumption
        "cargo_capacity": 100.0,  # Standard cargo
        "value": 10000.0,
        "mining_speed": 1.0,  # Standard mining speed
        "sensor_range": 1.0,  # Standard sensor range
        "hull_integrity": 100.0,  # Standard hull
        "shield_capacity": 15.0,  # Standard shields
        "engine_id": "standard",  # Standard engine
        "sensor_signature": 1.0,  # Standard signature
        "antimatter_capacity": 5.0,  # Standard antimatter capacity
        "antimatter_consumption": 0.05,  # Standard consumption rate (0.05g/LY)
    },
    "mining_vessel": {
        "name": "Mining Vessel",
        "description": "Specialized for asteroid mining with enhanced ore extraction systems.",
        "speed": 3e-05,  # Slightly slower (3e-05 AU/s)
        "max_fuel": 110.0,  # More fuel for mining operations
        "fuel_consumption": 1.1,  # Higher consumption due to mining equipment
        "cargo_capacity": 140.0,  # Large cargo for ore storage
        "value": 10500.0,
        "mining_speed": 1.5,  # Significantly higher mining speed
        "sensor_range": 1.4,  # Better at detecting ore deposits
        "hull_integrity": 110.0,  # Reinforced hull
        "shield_capacity": 10.0,  # Basic shields
        "engine_id": "cargo_hauler",  # Better for hauling cargo
        "sensor_signature": 1.1,  # Higher signature due to mining equipment
        "antimatter_capacity": 4.0,  # Lower antimatter capacity
        # Higher consumption due to bulk (0.065g/LY)
        "antimatter_consumption": 0.065,
    },  # Special ships for contacts
    "merc_veteran": {
        "name": "Mercenary Veteran",
        "description": "A battle-hardened vessel with custom combat modifications and stealth capabilities.",
        "speed": 7e-05,  # Good speed
        "max_fuel": 100.0,
        "fuel_consumption": 0.9,  # Efficient
        "cargo_capacity": 90.0,
        "value": 15000.0,
        "mining_speed": 0.8,  # Not optimized for mining
        "sensor_range": 1.3,  # Enhanced sensors for combat
        "hull_integrity": 120.0,  # Reinforced hull
        "shield_capacity": 25.0,  # Better shields
        "engine_id": "stealth",  # Stealth engine
        "sensor_signature": 0.7,  # Low signature for stealth operations
        "antimatter_capacity": 6.0,  # Enhanced antimatter capacity
        # Efficient military-grade system (0.048g/LY)
        "antimatter_consumption": 0.048,
    },
    "hunter_ship": {
        "name": "Bounty Hunter's Pursuit",
        "description": "A sleek, customized vessel with advanced tracking systems and reinforced hull.",
        "speed": 8e-05,  # Very fast
        "max_fuel": 90.0,
        "fuel_consumption": 1.0,
        "cargo_capacity": 80.0,  # Lower cargo capacity
        "value": 14000.0,
        "mining_speed": 0.9,
        "sensor_range": 1.5,  # Excellent sensors for tracking
        "hull_integrity": 110.0,
        "shield_capacity": 20.0,
        "engine_id": "high_performance",
        "sensor_signature": 0.9,
        "antimatter_capacity": 5.5,
        "antimatter_consumption": 0.045,  # Efficient jump drive (0.045g/LY)
    },
    "research_vessel": {
        "name": "Scientific Explorer",
        "description": "A research vessel equipped with advanced sensors and analytical equipment.",
        "speed": 2e-05,  # Moderate speed
        "max_fuel": 110.0,
        "fuel_consumption": 0.7,  # Fuel efficient
        "cargo_capacity": 80.0,
        "value": 12000.0,
        "mining_speed": 0.8,
        "sensor_range": 1.7,  # Exceptional sensors
        "hull_integrity": 90.0,
        "shield_capacity": 10.0,
        "engine_id": "economy",
        "sensor_signature": 1.3,  # Higher signature due to scientific equipment
        "antimatter_capacity": 7.0,  # Higher antimatter for research purposes
    },
    "smuggler_ship": {
        "name": "Smuggler's Edge",
        "description": "A customized freighter with hidden compartments and stealth modifications.",
        "speed": 6e-05,  # Good speed
        "max_fuel": 95.0,
        "fuel_consumption": 0.8,
        "cargo_capacity": 110.0,  # Good cargo capacity with hidden compartments
        "value": 13000.0,
        "mining_speed": 0.9,
        "sensor_range": 1.1,
        "hull_integrity": 90.0,
        "shield_capacity": 15.0,
        "engine_id": "stealth",
        "sensor_signature": 0.5,  # Very low signature
        "antimatter_capacity": 5.0,
    },
}


# Stellar system names for procedural generation
# Mix of real star names, mythological names, and sci-fi inspired names
STELLAR_SYSTEM_NAMES = [
    # Real star names and constellations
    "Vega",
    "Altair",
    "Deneb",
    "Rigel",
    "Betelgeuse",
    "Aldebaran",
    "Arcturus",
    "Spica",
    "Antares",
    "Pollux",
    "Regulus",
    "Adhara",
    "Shaula",
    "Bellatrix",
    "Elnath",
    "Miaplacidus",
    "Alnilam",
    "Regor",
    "Alioth",
    "Dubhe",
    "Mirfak",
    "Wezen",
    "Sargas",
    "Kaus Australis",
    "Avior",
    "Alkaid",
    "Menkalinan",
    "Atria",
    "Alhena",
    "Peacock",
    "Alsephina",
    "Mirzam",
    "Polaris",
    "Alphard",
    "Hamal",
    "Almaaz",
    "Rasalgethi",
    "Eltanin",
    "Schedar",
    "Naos",
    "Almach",
    "Caph",
    "Izar",
    "Diphda",
    "Nunki",
    "Mizar",
    "Kochab",
    "Sarin",
    "Ruchbah",
    # Mythological and classical names
    "Andromeda",
    "Cassiopeia",
    "Perseus",
    "Orion",
    "Centauri",
    "Lyra",
    "Aquila",
    "Cygnus",
    "Draco",
    "Hercules",
    "Pegasus",
    "Phoenix",
    "Hydra",
    "Serpentis",
    "Corona",
    "Vulpecula",
    "Delphinus",
    "Sagitta",
    "Equuleus",
    "Lacerta",
    "Triangulum",
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Virgo",
    "Libra",
    "Scorpius",
    "Sagittarius",
    "Capricornus",
    "Aquarius",
    "Pisces",
    # Greek/Roman inspired
    "Aethon",
    "Pyrois",
    "Stilbon",
    "Phaethon",
    "Phosphoros",
    "Hesperos",
    "Kronos",
    "Zeus",
    "Ares",
    "Aphrodite",
    "Hermes",
    "Athena",
    "Apollo",
    "Artemis",
    "Hephaestus",
    "Demeter",
    "Hestia",
    "Dionysus",
    "Hades",
    "Poseidon",
    "Helios",
    "Selene",
    "Eos",
    "Nyx",
    "Erebus",
    "Chaos",
    # Sci-fi inspired mining/industrial names
    "Kepler",
    "Newton",
    "Galileo",
    "Copernicus",
    "Brahe",
    "Hubble",
    "Sagan",
    "Hawking",
    "Einstein",
    "Tesla",
    "Edison",
    "Faraday",
    "Maxwell",
    "Bohr",
    "Heisenberg",
    "Schrodinger",
    "Planck",
    "Curie",
    "Nobel",
    "Fermi",
    # Gemstone and mineral inspired (fitting for mining game)
    "Crystalline",
    "Obsidian",
    "Quartzite",
    "Beryllium",
    "Rhodium",
    "Iridium",
    "Osmium",
    "Platinum",
    "Palladium",
    "Titanium",
    "Tungsten",
    "Molybdenum",
    "Vanadium",
    "Chromium",
    "Cobalt",
    "Nickel",
    "Copper",
    "Zinc",
    "Silver",
    "Indium",
    "Thallium",
    "Bismuth",
    "Thorium",
    "Uranium",
    "Neptunium",
    # Frontier/exploration themed
    "Meridian",
    "Zenith",
    "Nexus",
    "Apex",
    "Vertex",
    "Pinnacle",
    "Summit",
    "Horizon",
    "Threshold",
    "Gateway",
    "Portal",
    "Beacon",
    "Waypoint",
    "Outpost",
    "Haven",
    "Refuge",
    "Sanctuary",
    "Bastion",
    "Fortress",
    "Citadel",
    "Stronghold",
    "Bulwark",
    "Rampart",
    "Aegis",
    "Shield",
    # Atmospheric/space themed
    "Nebula",
    "Pulsar",
    "Quasar",
    "Magnetar",
    "Neutron",
    "Supernova",
    "Hypernova",
    "Gamma",
    "Cosmic",
    "Stellar",
    "Galactic",
    "Universal",
    "Infinity",
    "Eternity",
    "Perpetual",
    "Eternal",
    "Endless",
    "Boundless",
    "Limitless",
    "Immense",
    "Vast",
    "Colossal",
    "Massive",
    "Gigantic",
    # Discovery/exploration themed
    "Discovery",
    "Venture",
    "Quest",
    "Journey",
    "Odyssey",
    "Expedition",
    "Pioneer",
    "Explorer",
    "Pathfinder",
    "Trailblazer",
    "Voyager",
    "Navigator",
    "Compass",
    "Guide",
    "Herald",
    "Messenger",
    "Courier",
    "Envoy",
    "Ambassador",
    "Emissary",
    "Delegate",
    "Representative",
    "Agent",
    # Resource/mining themed
    "Abundance",
    "Prosperity",
    "Fortune",
    "Wealth",
    "Treasure",
    "Bounty",
    "Harvest",
    "Yield",
    "Profit",
    "Gain",
    "Benefit",
    "Advantage",
    "Asset",
    "Resource",
    "Reserve",
    "Deposit",
    "Vein",
    "Lode",
    "Seam",
    "Ore",
    "Mine",
    "Quarry",
    "Excavation",
    "Extraction",
    "Refinement",
    "Processing",
    # Additional stellar names for expanded variety
    # Celtic and Norse inspired
    "Brigid",
    "Cerridwen",
    "Lugh",
    "Morrigan",
    "Nuada",
    "Scathach",
    "Baldr",
    "Frigg",
    "Heimdall",
    "Loki",
    "Odin",
    "Thor",
    "Freyja",
    "Tyr",
    "Vidar",
    "Sigyn",
    "Hel",
    "Jormungandr",
    "Fenrir",
    "Sleipnir",
    # Egyptian and Mesopotamian
    "Anubis",
    "Bastet",
    "Horus",
    "Isis",
    "Osiris",
    "Ra",
    "Sekhmet",
    "Thoth",
    "Ptah",
    "Sobek",
    "Enlil",
    "Inanna",
    "Marduk",
    "Tiamat",
    "Anu",
    "Ereshkigal",
    "Nergal",
    "Shamash",
    "Sin",
    "Ishtar",
    # Japanese and Chinese inspired
    "Amaterasu",
    "Susanoo",
    "Tsukuyomi",
    "Inari",
    "Raijin",
    "Fujin",
    "Benzaiten",
    "Kaguya",
    "Yamato",
    "Akatsuki",
    "Chang'e",
    "Houyi",
    "Nuwa",
    "Fuxi",
    "Jade Emperor",
    "Dragon King",
    "Phoenix",
    "Qilin",
    "Bixie",
    "Tengu",
    # Hindu and Sanskrit
    "Agni",
    "Brahma",
    "Durga",
    "Ganesha",
    "Hanuman",
    "Indra",
    "Kali",
    "Krishna",
    "Lakshmi",
    "Rama",
    "Saraswati",
    "Shiva",
    "Surya",
    "Varuna",
    "Vishnu",
    "Yama",
    "Garuda",
    "Kartikeya",
    "Parvati",
    "Rudra",
    # Industrial and technological names
    "Forge",
    "Anvil",
    "Hammer",
    "Crucible",
    "Foundry",
    "Furnace",
    "Kiln",
    "Smelter",
    "Reactor",
    "Generator",
    "Dynamo",
    "Turbine",
    "Engine",
    "Motor",
    "Circuit",
    "Matrix",
    "Network",
    "Grid",
    "Node",
    "Hub",
    "Core",
    "Mainframe",
    "Server",
    "Database",
    "Archive",
    "Registry",
    "Protocol",
    "Algorithm",
    "Cipher",
    "Code",
    # Space phenomena and structures
    "Accretion",
    "Heliosphere",
    "Magnetosphere",
    "Chromosphere",
    "Photosphere",
    "Corona",
    "Prominence",
    "Sunspot",
    "Coronal Mass",
    "Solar Wind",
    "Asteroid",
    "Comet",
    "Meteor",
    "Planetoid",
    "Moonlet",
    "Satellite",
    "Orbit",
    "Ellipse",
    "Periapsis",
    "Apoapsis",
    "Lagrange",
    "Trojans",
    "Resonance",
    "Perturbation",
    "Precession",
    "Libration",
    # Frontier and exploration terms
    "Frontier",
    "Outland",
    "Wildspace",
    "Rimward",
    "Coreward",
    "Spinward",
    "Antispinward",
    "Terminus",
    "Crossroads",
    "Junction",
    "Confluence",
    "Convergence",
    "Divergence",
    "Branch",
    "Fork",
    "Split",
    "Merge",
    "Union",
    "Alliance",
    "Coalition",
    "Federation",
    "Republic",
    "Empire",
    "Kingdom",
    "Domain",
    "Territory",
    "Province",
    "Sector",
    # Weather and atmospheric phenomena
    "Storm",
    "Tempest",
    "Cyclone",
    "Hurricane",
    "Typhoon",
    "Blizzard",
    "Gale",
    "Zephyr",
    "Breeze",
    "Current",
    "Stream",
    "Flow",
    "Tide",
    "Wave",
    "Ripple",
    "Eddy",
    "Vortex",
    "Whirlpool",
    "Maelstrom",
    "Spiral",
    # Geological and terrestrial features
    "Canyon",
    "Crater",
    "Mesa",
    "Plateau",
    "Ridge",
    "Valley",
    "Peak",
    "Summit",
    "Crest",
    "Slope",
    "Cliff",
    "Chasm",
    "Gorge",
    "Ravine",
    "Fjord",
    "Delta",
    "Estuary",
    "Basin",
    "Caldera",
    "Geyser",
    # Colors and visual phenomena
    "Crimson",
    "Scarlet",
    "Vermillion",
    "Azure",
    "Cerulean",
    "Cobalt",
    "Emerald",
    "Jade",
    "Amber",
    "Topaz",
    "Sapphire",
    "Ruby",
    "Diamond",
    "Pearl",
    "Coral",
    "Ivory",
    "Ebony",
    "Onyx",
    "Opal",
    "Amethyst",
    # Musical and artistic terms
    "Harmony",
    "Melody",
    "Rhythm",
    "Symphony",
    "Concerto",
    "Sonata",
    "Prelude",
    "Fugue",
    "Aria",
    "Ballad",
    "Canvas",
    "Palette",
    "Sculpture",
    "Fresco",
    "Mosaic",
    "Tapestry",
    "Gallery",
    "Studio",
    "Atelier",
    "Masterpiece",
]


# Personality traits with gameplay effects
PERSONALITY_TRAITS = {
    "Positive": {
        "Resilient": "Recover from setbacks faster. +10% damage resistance.",
        "Resourceful": "Find more resources when mining. +5% ore yield.",
        "Charismatic": "Better prices when trading. -5% on purchases, +5% on sales.",
        "Perceptive": "Better chance to detect valuable items. +15% sensor range.",
        "Quick": "Faster reaction times. +10% evasion chance in combat.",
        "Methodical": "More efficient with resources. -8% fuel consumption.",
    },
    "Negative": {
        "Reckless": "Higher chance of accidents. +10% damage taken.",
        "Paranoid": "Overreact to threats. -5% trading prices due to rush decisions.",
        "Forgetful": "Miss details. 5% chance to lose small amounts of cargo.",
        "Impatient": "Rush through tasks. -10% mining efficiency.",
        "Superstitious": "Avoid 'unlucky' opportunities. Miss occasional deals.",
        "Indebted": "Poor money management. +10% interest on debt.",
    },
}

# Background skill bonuses - expanded to fully determine character skills
BACKGROUND_BONUSES: Dict[str, Dict[str, int]] = {
    "Ex-Miner": {
        # Stats
        "technical_aptitude": 2,
        "resilience": 2,
        # Skills
        "piloting": 4,
        "engineering": 8,
        "combat": 4,
        "education": 3,
        "charisma": 3,
        # Factions
        "belters": 20,
    },
    "Corp Dropout": {
        # Stats
        "intellect": 2,
        "presence": 2,
        # Skills
        "piloting": 3,
        "engineering": 4,
        "combat": 3,
        "education": 8,
        "charisma": 7,
        # Factions
        "corporations": -20,
        "traders": 15,
    },
    "Lunar Drifter": {
        # Stats
        "adaptability": 2,
        "perception": 2,
        # Skills
        "piloting": 6,
        "engineering": 3,
        "combat": 7,
        "education": 3,
        "charisma": 5,
        # Factions
        "pirates": 15,
    },
    "Void Runner": {
        # Stats
        "perception": 3,
        "adaptability": 1,
        # Skills
        "piloting": 8,
        "engineering": 5,
        "combat": 4,
        "education": 4,
        "charisma": 3,
        # Factions
        "explorers": 25,
    },
    "Xeno-Biologist": {
        # Stats
        "intellect": 3,
        "technical_aptitude": 1,
        # Skills
        "piloting": 3,
        "engineering": 5,
        "combat": 2,
        "education": 9,
        "charisma": 5,
        # Factions
        "scientists": 30,
    },
    "Discharged Trooper": {
        # Stats
        "resilience": 3,
        "perception": 1,
        # Skills
        "piloting": 5,
        "engineering": 4,
        "combat": 9,
        "education": 4,
        "charisma": 2,
        # Factions
        "military": -10,
        "pirates": 15,
    },
    # Special backgrounds unique to each NPC
    "Battle-Scarred Mercenary": {  # Kell Voss's special background
        # Stats
        "resilience": 4,
        "perception": 2,
        # Skills
        "piloting": 5,
        "engineering": 3,
        "combat": 10,
        "education": 3,
        "charisma": 3,
        # Factions
        "military": 10,
        "pirates": 5,
        "belters": 10,
    },
    "Shadow Operative": {  # Nova Valen's special background
        # Stats
        "adaptability": 3,
        "perception": 3,
        # Skills
        "piloting": 7,
        "engineering": 4,
        "combat": 8,
        "education": 5,
        "charisma": 6,
        # Factions
        "corporations": -10,
        "explorers": 15,
        "traders": 10,
    },
    "Tech Savant": {  # Zeta-9's special background
        # Stats
        "technical_aptitude": 4,
        "intellect": 3,
        # Skills
        "piloting": 5,
        "engineering": 10,
        "combat": 2,
        "education": 8,
        "charisma": 3,
        # Factions
        "scientists": 20,
        "corporations": 10,
        "traders": 5,
    },
    "Station Fixer": {  # Obsidian's special background
        # Stats
        "presence": 3,
        "intellect": 2,
        "adaptability": 1,
        # Skills
        "piloting": 4,
        "engineering": 5,
        "combat": 4,
        "education": 6,
        "charisma": 9,
        # Factions
        "traders": 20,
        "corporations": 5,
        "pirates": 5,
        "belters": 5,
    },
}
