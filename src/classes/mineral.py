from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict

from src.classes.commodity import Commodity, Category


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

    commodity: Commodity
    quality: MineralQuality = MineralQuality.STANDARD  # Default quality is STANDARD
    category: MaterialCategory = (
        MaterialCategory.HIGH_TEMP
    )  # Default category, will be overridden

    def to_string(self):
        """Get a string representation of the mineral."""
        quality_str = self.quality.name.capitalize().replace("_", "-")
        return f"{quality_str} {self.commodity.name}: {self.get_value()} credits, {self.commodity.volume_per_unit} m³ per unit"

    def get_info(self):
        """Get information about the mineral."""
        quality_str = self.quality.name.capitalize().replace("_", "-")
        return f"{quality_str} {self.commodity.name} {self.get_value()} {self.commodity.volume_per_unit}"

    def get_name(self) -> str:
        """Get the lowercase name of the mineral."""
        return self.commodity.name.lower()

    def get_value(self) -> float:
        """Calculate the actual value based on quality level."""
        quality_modifiers = {
            MineralQuality.STANDARD: 1.0,
            MineralQuality.HIGH_GRADE: 1.75,
            MineralQuality.SPECIALIZED: 3.0,
        }
        return round(self.commodity.base_price * quality_modifiers.get(self.quality, 1.0), 2)

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
            commodity=self.commodity,
            quality=next_quality,
            category=self.category,
        )

    def __hash__(self):
        # Use the ID and quality for hashing since they together form a unique identifier
        return hash((self.commodity.commodity_id, self.quality))

    def __eq__(self, other):
        if not isinstance(other, Mineral):
            return False
        return self.commodity.commodity_id == other.commodity.commodity_id and self.quality == other.quality


# Define minerals in a dictionary
MINERALS: Dict[int, Mineral] = {
    0: Mineral(Commodity(commodity_id=0, name="Iron", category=Category.RAW_MATERIAL, base_price=75.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Iron ore", volume_per_unit=0.2, mass_per_unit=1.0), category=MaterialCategory.HIGH_TEMP),
    1: Mineral(
        Commodity(commodity_id=1, name="Carbon", category=Category.RAW_MATERIAL, base_price=45.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Carbon-based material", volume_per_unit=0.1, mass_per_unit=0.5), category=MaterialCategory.LOW_TEMP
    ),  # Representing volatile carbon or less refractory forms
    2: Mineral(Commodity(commodity_id=2, name="Silicon", category=Category.RAW_MATERIAL, base_price=90.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Silicon-based material", volume_per_unit=0.15, mass_per_unit=0.8), category=MaterialCategory.HIGH_TEMP),
    3: Mineral(Commodity(commodity_id=3, name="Copper", category=Category.RAW_MATERIAL, base_price=110.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Copper ore", volume_per_unit=0.25, mass_per_unit=1.2), category=MaterialCategory.MID_TEMP),
    4: Mineral(Commodity(commodity_id=4, name="Zinc", category=Category.RAW_MATERIAL, base_price=85.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Zinc ore", volume_per_unit=0.2, mass_per_unit=1.1), category=MaterialCategory.MID_TEMP),
    5: Mineral(Commodity(commodity_id=5, name="Aluminum", category=Category.RAW_MATERIAL, base_price=95.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Aluminum ore", volume_per_unit=0.18, mass_per_unit=0.9), category=MaterialCategory.HIGH_TEMP),
    6: Mineral(Commodity(commodity_id=6, name="Titanium", category=Category.RAW_MATERIAL, base_price=200.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Titanium ore", volume_per_unit=0.3, mass_per_unit=1.5), category=MaterialCategory.HIGH_TEMP),
    7: Mineral(Commodity(commodity_id=7, name="Nickel", category=Category.RAW_MATERIAL, base_price=150.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Nickel ore", volume_per_unit=0.22, mass_per_unit=1.3), category=MaterialCategory.HIGH_TEMP),
    8: Mineral(Commodity(commodity_id=8, name="Neodymium", category=Category.RAW_MATERIAL, base_price=300.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Neodymium ore", volume_per_unit=0.25, mass_per_unit=1.8), category=MaterialCategory.HIGH_TEMP),
    9: Mineral(Commodity(commodity_id=9, name="Gold", category=Category.RAW_MATERIAL, base_price=500.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Gold ore", volume_per_unit=0.1, mass_per_unit=2.0), category=MaterialCategory.HIGH_TEMP),
    10: Mineral(
        Commodity(commodity_id=10, name="Rare Earth Elements", category=Category.RAW_MATERIAL, base_price=450.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Rare earth elements", volume_per_unit=0.15, mass_per_unit=1.6), category=MaterialCategory.HIGH_TEMP
    ),
    11: Mineral(
        Commodity(commodity_id=11, name="Exotic Materials", category=Category.RAW_MATERIAL, base_price=1200.0, price_volatility=0.1, volatility_range=(0.0, 0.0), description="Exotic materials", volume_per_unit=0.5, mass_per_unit=2.5), category=MaterialCategory.HIGH_TEMP
    ),  # Assumption
}


def get_mineral_by_name(name: str) -> Mineral | None:
    """Get a mineral by its name."""
    for mineral in MINERALS.values():
        if mineral.commodity.name.lower() == name.lower():
            return mineral
    return None
