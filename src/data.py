from dataclasses import dataclass
from random import choice
from enum import Enum, auto
from typing import Optional, List

from src.classes.ore import Ore, ORES

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
    "ni" "ler",
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
        }

    @classmethod
    def from_dict(cls, data):
        ore_obj = ORES.get(data["ore_id"])
        if ore_obj is None:
            # Handle missing ore, perhaps raise an error or return None
            raise ValueError(f"Ore with ID {data['ore_id']} not found in ORES map.")
        return cls(
            ore=ore_obj,
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
    ),
    # Defense upgrades
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
