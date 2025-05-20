from dataclasses import dataclass
from random import choice
from enum import Enum, auto
from typing import Dict, Optional, List

from src.classes.ore import Ore, ORES, PurityLevel

# Import Mineral and MineralQuality at the top level
from src.classes.mineral import Mineral, MineralQuality
from src.classes.engine import Engine, EngineType

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
    "ni", "ler",
    "der",
    "ber",
    "shar",
    "sher",
    "mer",
    "wer",
    "fer",
    "fra" "gra",
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
            "ore_id": self.ore.id,
            "quantity": self.quantity,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "purity": self.ore.purity.name if hasattr(self.ore, 'purity') else "RAW"
        }

    @classmethod
    def from_dict(cls, data):
        from src.classes.ore import ORES, PurityLevel
        
        ore_obj = ORES.get(data["ore_id"])
        if (ore_obj is None):
            # Handle missing ore, perhaps raise an error or return None
            raise ValueError(f"Ore with ID {data['ore_id']} not found in ORES map.")
            
        # Handle purity if present
        if "purity" in data:
            try:
                purity_level = PurityLevel[data["purity"]]
                # Create a copy of the ore with the saved purity level
                ore_obj = Ore(
                    name=ore_obj.name,
                    base_value=ore_obj.base_value,
                    volume=ore_obj.volume,
                    mineral_yield=ore_obj.mineral_yield.copy() if ore_obj.mineral_yield else [],
                    id=ore_obj.id,
                    purity=purity_level,
                    refining_difficulty=ore_obj.refining_difficulty if hasattr(ore_obj, 'refining_difficulty') else 1.0
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
            "quality": self.mineral.quality.name if hasattr(self.mineral, 'quality') else "STANDARD"
        }

    @classmethod
    def from_dict(cls, data):
        from src.classes.mineral import MINERALS, MineralQuality
        
        mineral_obj = MINERALS.get(data["mineral_id"])
        if (mineral_obj is None):
            # Handle missing mineral, raise an error
            raise ValueError(f"Mineral with ID {data['mineral_id']} not found in MINERALS map.")
            
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
                    quality=quality_level
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
    ),    # Defense upgrades
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
        "speed": 0.8,  # Slower due to heavy armor
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
        "antimatter_consumption": 0.07,  # Higher consumption due to mass (0.07g/LY)
    },    
    "agile_interceptor": {
        "name": "Agile Interceptor",
        "description": "Streamlined and fast. Prioritizes speed and maneuverability over raw power.",
        "speed": 1.4,  # Significantly faster
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
        "speed": 1.0,  # Balanced speed
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
        "speed": 0.9,  # Slightly slower
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
        "antimatter_consumption": 0.065,  # Higher consumption due to bulk (0.065g/LY)
    },
    # Special ships for contacts
    "merc_veteran": {
        "name": "Mercenary Veteran",
        "description": "A battle-hardened vessel with custom combat modifications and stealth capabilities.",
        "speed": 1.1,  # Good speed
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
        "antimatter_consumption": 0.048,  # Efficient military-grade system (0.048g/LY)
    },    
    "hunter_ship": {
        "name": "Bounty Hunter's Pursuit",
        "description": "A sleek, customized vessel with advanced tracking systems and reinforced hull.",
        "speed": 1.3,  # Very fast
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
        "speed": 0.9,
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
        "speed": 1.2,
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
