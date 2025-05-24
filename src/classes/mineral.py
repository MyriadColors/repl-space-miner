from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict


class MineralQuality(Enum):
    """Represents the quality level of a mineral."""

    STANDARD = auto()  # Standard quality
    HIGH_GRADE = auto()  # High-grade quality
    SPECIALIZED = auto()  # Specialized grades (e.g., Ultra-Pure, Mil-Grade)


class MaterialCategory(Enum):
    HIGH_TEMP = auto()  # Condensed at high temperatures (e.g., rock, metal)
    MID_TEMP = auto()  # Condensed at moderate temperatures
    LOW_TEMP = auto()  # Condensed at low temperatures (e.g., ices, some organics)


@dataclass
class Mineral:
    """
    Represents a refined mineral in the game.

    Minerals are the direct products of refining raw ores. Their quality and yield
    are affected by input ore purity, the refinery's technology level, the Template
    used for refining, and the operator's engineering skill.
    """

    name: str
    base_value: float  # in credits
    volume: float  # in m³ per unit
    id: int
    quality: MineralQuality = MineralQuality.STANDARD  # Default quality is STANDARD
    category: MaterialCategory = (
        MaterialCategory.HIGH_TEMP
    )  # Default category, will be overridden

    def to_string(self):
        """Get a string representation of the mineral."""
        quality_str = self.quality.name.capitalize().replace("_", "-")
        return f"{quality_str} {self.name}: {self.get_value()} credits, {self.volume} m³ per unit"

    def get_info(self):
        """Get information about the mineral."""
        quality_str = self.quality.name.capitalize().replace("_", "-")
        return f"{quality_str} {self.name} {self.get_value()} {self.volume}"

    def get_name(self) -> str:
        """Get the lowercase name of the mineral."""
        return self.name.lower()

    def get_value(self) -> float:
        """Calculate the actual value based on quality level."""
        quality_modifiers = {
            MineralQuality.STANDARD: 1.0,
            MineralQuality.HIGH_GRADE: 1.75,
            MineralQuality.SPECIALIZED: 3.0,
        }
        return round(self.base_value * quality_modifiers.get(self.quality, 1.0), 2)

    def create_higher_quality_version(self) -> Optional["Mineral"]:
        """Create a new mineral object with the next quality level."""
        quality_order = [
            MineralQuality.STANDARD,
            MineralQuality.HIGH_GRADE,
            MineralQuality.SPECIALIZED,
        ]
        current_index = quality_order.index(self.quality)
        if current_index >= len(quality_order) - 1:
            return None

        next_quality = quality_order[current_index + 1]

        # Create a new mineral with the same properties but higher quality
        return Mineral(
            name=self.name,
            base_value=self.base_value,
            volume=self.volume
            * 0.95,  # Higher quality minerals have slightly less volume
            id=self.id,
            quality=next_quality,
        )

    def __hash__(self):
        # Use the ID and quality for hashing since they together form a unique identifier
        return hash((self.id, self.quality))

    def __eq__(self, other):
        if not isinstance(other, Mineral):
            return False
        return self.id == other.id and self.quality == other.quality


# Define minerals in a dictionary
MINERALS: Dict[int, Mineral] = {
    0: Mineral("Iron", 75.0, 0.2, 0, category=MaterialCategory.HIGH_TEMP),
    1: Mineral(
        "Carbon", 45.0, 0.1, 1, category=MaterialCategory.LOW_TEMP
    ),  # Representing volatile carbon or less refractory forms
    2: Mineral("Silicon", 90.0, 0.15, 2, category=MaterialCategory.HIGH_TEMP),
    3: Mineral("Copper", 110.0, 0.25, 3, category=MaterialCategory.MID_TEMP),
    4: Mineral("Zinc", 85.0, 0.2, 4, category=MaterialCategory.MID_TEMP),
    5: Mineral("Aluminum", 95.0, 0.18, 5, category=MaterialCategory.HIGH_TEMP),
    6: Mineral("Titanium", 200.0, 0.3, 6, category=MaterialCategory.HIGH_TEMP),
    7: Mineral("Nickel", 150.0, 0.22, 7, category=MaterialCategory.HIGH_TEMP),
    8: Mineral("Neodymium", 300.0, 0.25, 8, category=MaterialCategory.HIGH_TEMP),
    9: Mineral("Gold", 500.0, 0.1, 9, category=MaterialCategory.HIGH_TEMP),
    10: Mineral(
        "Rare Earth Elements", 450.0, 0.15, 10, category=MaterialCategory.HIGH_TEMP
    ),
    11: Mineral(
        "Exotic Materials", 1200.0, 0.5, 11, category=MaterialCategory.HIGH_TEMP
    ),  # Assumption
}


def get_mineral_by_name(name: str) -> Mineral | None:
    """Get a mineral by its name."""
    for mineral in MINERALS.values():
        if mineral.name.lower() == name.lower():
            return mineral
    return None
