from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, List, Tuple

from src.classes.commodity import Commodity, Category
from src.classes.resource import Resource, ProductionStage


class PurityLevel(Enum):
    """Represents the purity level of an ore."""

    RAW = auto()  # Unrefined, as mined
    LOW = auto()  # Low purity, basic refinement
    MEDIUM = auto()  # Medium purity, standard refinement
    HIGH = auto()  # High purity, advanced refinement
    ULTRA = auto()  # Ultra pure, highest quality


@dataclass
class Ore(Resource):
    """
    Represents a raw ore resource in the game.
    
    Ores are the first stage in the production chain, extracted directly from
    asteroids and other celestial bodies. They can be refined into minerals.
    """
    mineral_yield: List[Tuple[int, float]] = field(default_factory=list)
    purity: PurityLevel = PurityLevel.RAW  # Default purity is RAW
    refining_difficulty: float = 1.0
    extraction_difficulty: float = 1.0  # Higher values mean harder to mine
    region_availability: Dict[str, float] = field(default_factory=dict)  # Region name to availability factor mapping
    
    def __post_init__(self):
        """Ensure production stage is set to RAW."""
        if not hasattr(self, 'production_stage') or self.production_stage is None:
            self.production_stage = ProductionStage.RAW
    
    def to_string(self):
        """Get a string representation of the ore."""
        purity_str = self.purity.name.capitalize()
        return f"{purity_str} {self.commodity.name}: {self.get_value()} credits, {self.commodity.volume_per_unit} m³ per unit"

    def get_info(self):
        """Get information about the ore."""
        purity_str = self.purity.name.capitalize()
        return f"{purity_str} {self.commodity.name} {self.get_value()} {self.commodity.volume_per_unit}"

    def get_value(self) -> float:
        """Calculate the actual value based on purity level."""
        purity_modifiers = {
            PurityLevel.RAW: 1.0,
            PurityLevel.LOW: 1.5,
            PurityLevel.MEDIUM: 2.0,
            PurityLevel.HIGH: 3.0,
            PurityLevel.ULTRA: 5.0,
        }
        return round(
            self.commodity.base_price *
            purity_modifiers.get(self.purity, 1.0), 2
        )

    def can_refine(self) -> bool:
        """Check if the ore can be refined further."""
        if self.purity == PurityLevel.ULTRA:
            return False
        return True

    def get_next_purity_level(self) -> Optional[PurityLevel]:
        """Get the next purity level for refining."""
        purity_order = [
            PurityLevel.RAW,
            PurityLevel.LOW,
            PurityLevel.MEDIUM,
            PurityLevel.HIGH,
            PurityLevel.ULTRA,
        ]
        current_index = purity_order.index(self.purity)
        if current_index >= len(purity_order) - 1:
            return None
        return purity_order[current_index + 1]

    def create_refined_version(self) -> 'Ore':
        next_purity = self.get_next_purity_level()
        if next_purity is None:
            raise ValueError(f"Cannot refine ore with purity level {self.purity.name}")
        
        return Ore(
            commodity=Commodity(
                commodity_id=self.commodity.commodity_id + 1000,
                name=f"Refined {self.commodity.name}",
                description=f"Refined version of {self.commodity.description}",
                base_price=self.commodity.base_price * 2.5,
                volume_per_unit=self.commodity.volume_per_unit * 0.8,
                mass_per_unit=self.commodity.mass_per_unit * 0.9,
                category=self.commodity.category,
                price_volatility=self.commodity.price_volatility * 0.8,
                volatility_range=self.commodity.volatility_range,
            ),
            production_stage=ProductionStage.REFINED,
            purity=next_purity,
            refining_difficulty=self.refining_difficulty,
        )

    def __hash__(self):
        # Use the ID and purity for hashing since they together form a unique identifier
        return hash((self.commodity.commodity_id, self.purity))

    def __eq__(self, other):
        if not isinstance(other, Ore):
            return False
        return (
            self.commodity.commodity_id == other.commodity.commodity_id
            and self.purity == other.purity
        )
        
    def to_dict(self) -> Dict:
        """Convert the ore to a dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            "mineral_yield": self.mineral_yield,
            "purity": self.purity.name,
            "refining_difficulty": self.refining_difficulty,
            "extraction_difficulty": self.extraction_difficulty,
            "region_availability": self.region_availability
        })
        return base_dict
        
    @classmethod
    def from_dict(cls, data: Dict, commodity: Commodity) -> 'Ore':
        """Create an ore from a dictionary representation."""
        # First create a base Resource object
        resource = Resource.from_dict(data, commodity)
        
        # Extract ore-specific properties
        mineral_yield = data.get("mineral_yield", [])
        purity = PurityLevel[data.get("purity", "RAW")]
        refining_difficulty = data.get("refining_difficulty", 1.0)
        extraction_difficulty = data.get("extraction_difficulty", 1.0)
        region_availability = data.get("region_availability", {})
        
        # Create and return the Ore object
        return cls(
            commodity=commodity,
            production_stage=resource.production_stage,
            market_demand=resource.market_demand,
            market_supply=resource.market_supply,
            price_history=resource.price_history,
            mineral_yield=mineral_yield,
            purity=purity,
            refining_difficulty=refining_difficulty,
            extraction_difficulty=extraction_difficulty,
            region_availability=region_availability
        )

    def get_mineral_yield(self) -> Dict[int, float]:
        """
        Calculate the mineral yield from this ore based on purity.

        Returns:
            Dictionary mapping mineral_id to the amount of that mineral produced per ore unit.
        """
        # Apply purity modifier to yields
        purity_yield_modifiers = {
            PurityLevel.RAW: 0.5,  # Lower yield from raw ore
            PurityLevel.LOW: 0.60,
            PurityLevel.MEDIUM: 0.75,
            PurityLevel.HIGH: 0.85,
            PurityLevel.ULTRA: 0.95,  # Maximum yield
        }

        purity_modifier = purity_yield_modifiers.get(self.purity, 0.6)

        # Calculate yield for each mineral
        yields = {}
        for mineral_id, base_yield in self.mineral_yield:
            yields[mineral_id] = round(base_yield * purity_modifier, 2)

        return yields
    
    def get_waste_products(self) -> Dict[int, float]:
        """
        Calculate the waste products generated when refining this ore.
        
        Returns:
            Dictionary mapping waste_product_id to the amount produced per ore unit.
        """
        # This is a placeholder implementation. The actual waste product generation
        # will be implemented in the waste management system.
        waste_base_rate = 0.2  # 20% waste by default
        
        # Purity affects waste generation - higher purity means less waste
        purity_waste_modifiers = {
            PurityLevel.RAW: 1.5,     # 30% waste
            PurityLevel.LOW: 1.2,     # 24% waste
            PurityLevel.MEDIUM: 1.0,  # 20% waste
            PurityLevel.HIGH: 0.75,   # 15% waste
            PurityLevel.ULTRA: 0.5,   # 10% waste
        }
        
        waste_modifier = purity_waste_modifiers.get(self.purity, 1.0)
        waste_rate = waste_base_rate * waste_modifier
        
        # For now, we'll just return a generic waste product with ID 0
        # This will be expanded in the waste management system implementation
        return {0: round(waste_rate, 2)}


# Define ores in a dictionary
ORES = {
    0: Ore(
        commodity=Commodity(
            commodity_id=0,
            name="Pyrogen",
            category=Category.RAW_MATERIAL,
            base_price=29.0,
            price_volatility=0.3,
            volatility_range=(0.0, 0.0),
            volume_per_unit=1.0,
            mass_per_unit=0.8,
            description="A common mineral with moderate energy potential",
        ),
        mineral_yield=[(0, 0.7), (1, 0.2)],
        purity=PurityLevel.RAW,
        refining_difficulty=1.0,
        production_stage=ProductionStage.RAW,
    ),
    1: Ore(
        commodity=Commodity(
            commodity_id=1,
            name="Ascorbon",
            category=Category.RAW_MATERIAL,
            base_price=16.0,
            price_volatility=0.15,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.8,
            mass_per_unit=0.7,
            description="A lightweight ore with good structural properties",
        ),
        mineral_yield=[(1, 0.8)],
        purity=PurityLevel.LOW,
        refining_difficulty=1.2,
        production_stage=ProductionStage.RAW,
    ),
    2: Ore(
        commodity=Commodity(
            commodity_id=2,
            name="Angion",
            category=Category.RAW_MATERIAL,
            base_price=55.0,
            price_volatility=0.35,
            volatility_range=(0.0, 0.0),
            volume_per_unit=1.2,
            mass_per_unit=1.1,
            description="A dense ore with high mineral content",
        ),
        mineral_yield=[(3, 0.6), (4, 0.3)],
        purity=PurityLevel.MEDIUM,
        refining_difficulty=1.5,
        production_stage=ProductionStage.RAW,
    ),
    3: Ore(
        commodity=Commodity(
            commodity_id=3,
            name="Varite",
            category=Category.RAW_MATERIAL,
            base_price=18.0,
            price_volatility=0.1,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.9,
            mass_per_unit=0.6,
            description="A stable ore with consistent properties",
        ),
        mineral_yield=[(10, 0.5)],
        purity=PurityLevel.HIGH,
        refining_difficulty=0.8,
        production_stage=ProductionStage.RAW,
    ),
    4: Ore(
        commodity=Commodity(
            commodity_id=4,
            name="Oxynite",
            category=Category.RAW_MATERIAL,
            base_price=3500.0,
            price_volatility=16.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.3,
            mass_per_unit=2.5,
            description="An extremely valuable and dense rare ore",
        ),
        mineral_yield=[(11, 0.3)],
        purity=PurityLevel.ULTRA,
        refining_difficulty=2.5,
        production_stage=ProductionStage.RAW,
    ),
    5: Ore(
        commodity=Commodity(
            commodity_id=5,
            name="Cyclon",
            category=Category.RAW_MATERIAL,
            base_price=600.0,
            price_volatility=2.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.7,
            mass_per_unit=1.3,
            description="A valuable ore with unique crystalline structure",
        ),
        mineral_yield=[(2, 0.7), (5, 0.2)],
        purity=PurityLevel.RAW,
        refining_difficulty=1.8,
        production_stage=ProductionStage.RAW,
    ),
    6: Ore(
        commodity=Commodity(
            commodity_id=6,
            name="Heron",
            category=Category.RAW_MATERIAL,
            base_price=1200.0,
            price_volatility=3.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.5,
            mass_per_unit=1.8,
            description="A premium ore with excellent conductivity properties",
        ),
        mineral_yield=[(6, 0.5), (7, 0.4)],
        purity=PurityLevel.LOW,
        refining_difficulty=2.0,
        production_stage=ProductionStage.RAW,
    ),
    7: Ore(
        commodity=Commodity(
            commodity_id=7,
            name="Jonnite",
            category=Category.RAW_MATERIAL,
            base_price=7250.0,
            price_volatility=16.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.2,
            mass_per_unit=3.0,
            description="An extremely rare and valuable exotic ore",
        ),
        mineral_yield=[(9, 0.2), (10, 0.1)],
        purity=PurityLevel.MEDIUM,
        refining_difficulty=3.0,
        production_stage=ProductionStage.RAW,
    ),
    8: Ore(
        commodity=Commodity(
            commodity_id=8,
            name="Magneton",
            category=Category.RAW_MATERIAL,
            base_price=580.0,
            price_volatility=1.2,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.6,
            mass_per_unit=1.5,
            description="A magnetic ore with industrial applications",
        ),
        mineral_yield=[(0, 0.4), (8, 0.5)],
        purity=PurityLevel.HIGH,
        refining_difficulty=2.2,
        production_stage=ProductionStage.RAW,
    ),
}


def get_ore_by_name(name: str) -> Ore | None:
    for ore in ORES.values():
        if ore.commodity.name.lower() == name.lower():
            return ore
    return None