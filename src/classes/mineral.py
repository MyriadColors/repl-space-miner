from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, List

from src.classes.commodity import Commodity, Category
from src.classes.resource import Resource, ProductionStage


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
class Mineral(Resource):
    """
    Represents a refined mineral in the game.

    Minerals are the direct products of refining raw ores. Their quality and yield
    are affected by input ore purity, the refinery's technology level, the Template
    used for refining, and the operator's engineering skill.
    """
    quality: MineralQuality = MineralQuality.STANDARD  # Default quality is STANDARD
    source_ores: List[int] = field(default_factory=list)  # IDs of ores that can produce this mineral
    material_category: MaterialCategory = MaterialCategory.MID_TEMP  # Physical category of the mineral
    processing_difficulty: float = 1.0  # Higher values mean more difficult to process into components
    purity: float = 0.8  # Purity level (0.0-1.0), affects component quality
    
    def __post_init__(self):
        """Ensure production stage is set to REFINED."""
        if not hasattr(self, 'production_stage') or self.production_stage is None:
            self.production_stage = ProductionStage.REFINED

    def to_string(self):
        """Get a string representation of the mineral."""
        quality_str = self.quality.name.capitalize().replace("_", "-")
        return f"{quality_str} {self.commodity.name}: {self.get_value()} credits, {self.commodity.volume_per_unit} m³ per unit"

    def get_info(self):
        """Get information about the mineral."""
        quality_str = self.quality.name.capitalize().replace("_", "-")
        return f"{quality_str} {self.commodity.name} {self.get_value()} {self.commodity.volume_per_unit}"

    def get_value(self) -> float:
        """Calculate the actual value based on quality level."""
        quality_modifiers = {
            MineralQuality.STANDARD: 1.0,
            MineralQuality.HIGH_GRADE: 1.75,
            MineralQuality.SPECIALIZED: 3.0,
        }
        return round(self.commodity.base_price * quality_modifiers.get(self.quality, 1.0), 2)

    def create_higher_quality_version(self) -> Optional["Mineral"]:
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
            source_ores=self.source_ores.copy() if self.source_ores else [],
            production_stage=self.production_stage,
        )

    def __hash__(self):
        # Use the ID and quality for hashing since they together form a unique identifier
        return hash((self.commodity.commodity_id, self.quality))

    def __eq__(self, other):
        if not isinstance(other, Mineral):
            return False
        return self.commodity.commodity_id == other.commodity.commodity_id and self.quality == other.quality
    
    def get_waste_products(self) -> Dict[int, float]:
        """
        Calculate the waste products generated when processing this mineral into components.
        
        Returns:
            Dictionary mapping waste_product_id to the amount produced per mineral unit.
        """
        # This is a placeholder implementation. The actual waste product generation
        # will be implemented in the waste management system.
        waste_base_rate = 0.1  # 10% waste by default
        
        # Quality affects waste generation - higher quality means less waste
        quality_waste_modifiers = {
            MineralQuality.STANDARD: 1.2,     # 12% waste
            MineralQuality.HIGH_GRADE: 0.8,   # 8% waste
            MineralQuality.SPECIALIZED: 0.5,  # 5% waste
        }
        
        waste_modifier = quality_waste_modifiers.get(self.quality, 1.0)
        waste_rate = waste_base_rate * waste_modifier
        
        # For now, we'll just return a generic waste product with ID 1
        # This will be expanded in the waste management system implementation
        return {1: round(waste_rate, 2)}


# Define minerals in a dictionary
MINERALS: Dict[int, Mineral] = {
    0: Mineral(
        commodity=Commodity(
            commodity_id=0, 
            name="Iron", 
            category=Category.RAW_MATERIAL, 
            base_price=75.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Iron ore", 
            volume_per_unit=0.2, 
            mass_per_unit=1.0
        ), 
        source_ores=[0, 8],
        production_stage=ProductionStage.REFINED
    ),
    1: Mineral(
        commodity=Commodity(
            commodity_id=1, 
            name="Carbon", 
            category=Category.RAW_MATERIAL, 
            base_price=45.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Carbon-based material", 
            volume_per_unit=0.1, 
            mass_per_unit=0.5
        ), 
        source_ores=[0, 1],
        production_stage=ProductionStage.REFINED
    ),
    2: Mineral(
        commodity=Commodity(
            commodity_id=2, 
            name="Silicon", 
            category=Category.RAW_MATERIAL, 
            base_price=90.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Silicon-based material", 
            volume_per_unit=0.15, 
            mass_per_unit=0.8
        ), 
        source_ores=[5],
        production_stage=ProductionStage.REFINED
    ),
    3: Mineral(
        commodity=Commodity(
            commodity_id=3, 
            name="Copper", 
            category=Category.RAW_MATERIAL, 
            base_price=110.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Copper ore", 
            volume_per_unit=0.25, 
            mass_per_unit=1.2
        ), 
        source_ores=[2],
        production_stage=ProductionStage.REFINED
    ),
    4: Mineral(
        commodity=Commodity(
            commodity_id=4, 
            name="Zinc", 
            category=Category.RAW_MATERIAL, 
            base_price=85.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Zinc ore", 
            volume_per_unit=0.2, 
            mass_per_unit=1.1
        ), 
        source_ores=[2],
        production_stage=ProductionStage.REFINED
    ),
    5: Mineral(
        commodity=Commodity(
            commodity_id=5, 
            name="Aluminum", 
            category=Category.RAW_MATERIAL, 
            base_price=95.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Aluminum ore", 
            volume_per_unit=0.18, 
            mass_per_unit=0.9
        ), 
        source_ores=[5],
        production_stage=ProductionStage.REFINED
    ),
    6: Mineral(
        commodity=Commodity(
            commodity_id=6, 
            name="Titanium", 
            category=Category.RAW_MATERIAL, 
            base_price=200.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Titanium ore", 
            volume_per_unit=0.3, 
            mass_per_unit=1.5
        ), 
        source_ores=[6],
        production_stage=ProductionStage.REFINED
    ),
    7: Mineral(
        commodity=Commodity(
            commodity_id=7, 
            name="Nickel", 
            category=Category.RAW_MATERIAL, 
            base_price=150.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Nickel ore", 
            volume_per_unit=0.22, 
            mass_per_unit=1.3
        ), 
        source_ores=[6],
        production_stage=ProductionStage.REFINED
    ),
    8: Mineral(
        commodity=Commodity(
            commodity_id=8, 
            name="Neodymium", 
            category=Category.RAW_MATERIAL, 
            base_price=300.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Neodymium ore", 
            volume_per_unit=0.25, 
            mass_per_unit=1.8
        ), 
        source_ores=[8],
        production_stage=ProductionStage.REFINED
    ),
    9: Mineral(
        commodity=Commodity(
            commodity_id=9, 
            name="Gold", 
            category=Category.RAW_MATERIAL, 
            base_price=500.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Gold ore", 
            volume_per_unit=0.1, 
            mass_per_unit=2.0
        ), 
        source_ores=[7],
        production_stage=ProductionStage.REFINED
    ),
    10: Mineral(
        commodity=Commodity(
            commodity_id=10, 
            name="Rare Earth Elements", 
            category=Category.RAW_MATERIAL, 
            base_price=450.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Rare earth elements", 
            volume_per_unit=0.15, 
            mass_per_unit=1.6
        ), 
        source_ores=[3, 7],
        production_stage=ProductionStage.REFINED
    ),
    11: Mineral(
        commodity=Commodity(
            commodity_id=11, 
            name="Exotic Materials", 
            category=Category.RAW_MATERIAL, 
            base_price=1200.0, 
            price_volatility=0.1, 
            volatility_range=(0.0, 0.0), 
            description="Exotic materials", 
            volume_per_unit=0.5, 
            mass_per_unit=2.5
        ), 
        source_ores=[4],
        production_stage=ProductionStage.REFINED
    ),
}


def get_mineral_by_name(name: str) -> Mineral | None:
    """Get a mineral by its name."""
    for mineral in MINERALS.values():
        if mineral.commodity.name.lower() == name.lower():
            return mineral
    return None
