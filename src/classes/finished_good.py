from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from src.classes.commodity import Commodity, Category
from src.classes.resource import Resource, ProductionStage


class FinishedGoodQuality(Enum):
    """Represents the quality level of a finished good."""
    ECONOMY = auto()     # Economy quality, minimal features
    STANDARD = auto()    # Standard quality, normal features
    PREMIUM = auto()     # Premium quality, enhanced features
    LUXURY = auto()      # Luxury quality, high-end features
    MILITARY = auto()    # Military quality, specialized features


class FinishedGoodType(Enum):
    """Represents the type of finished good."""
    CONSUMER = auto()     # Consumer goods (electronics, appliances)
    INDUSTRIAL = auto()   # Industrial goods (machinery, tools)
    MILITARY = auto()     # Military goods (weapons, armor)
    MEDICAL = auto()      # Medical goods (equipment, supplies)
    SCIENTIFIC = auto()   # Scientific goods (research equipment)
    LUXURY = auto()       # Luxury goods (jewelry, art)
    SHIP_EQUIPMENT = auto()  # Ship equipment (modules, upgrades)


@dataclass
class FinishedGood(Resource):
    """
    Represents a finished good in the game.
    
    Finished goods are the final stage in the production chain, assembled from
    components. They are ready for use by consumers or as equipment for ships.
    """
    quality: FinishedGoodQuality = FinishedGoodQuality.STANDARD
    good_type: FinishedGoodType = FinishedGoodType.CONSUMER
    assembly_complexity: float = 1.0  # Higher values mean more difficult to assemble
    required_components: Dict[int, float] = field(default_factory=dict)  # Component ID to quantity mapping
    tech_level: int = 1  # Minimum tech level required to produce
    durability: float = 1.0  # Durability factor (1.0 = standard)
    efficiency: float = 1.0  # Efficiency factor (1.0 = standard)
    performance_rating: float = 1.0  # Performance rating (1.0 = standard)
    maintenance_interval: float = 100.0  # Hours between maintenance
    maintenance_cost: float = 0.0  # Cost per maintenance cycle
    compatible_ship_classes: List[str] = field(default_factory=list)  # Ship classes this good is compatible with
    power_requirement: float = 0.0  # Power required to operate (0.0 = passive item)
    special_effects: Dict[str, float] = field(default_factory=dict)  # Special effects and their magnitudes
    
    def __post_init__(self):
        """Ensure production stage is set to FINISHED."""
        if not hasattr(self, 'production_stage') or self.production_stage is None:
            self.production_stage = ProductionStage.FINISHED
    
    def to_string(self) -> str:
        """Get a string representation of the finished good."""
        quality_str = self.quality.name.capitalize()
        type_str = self.good_type.name.capitalize().replace("_", " ")
        return f"{quality_str} {self.commodity.name} ({type_str}): {self.get_value()} credits, {self.commodity.volume_per_unit} m³ per unit"
    
    def get_info(self) -> str:
        """Get information about the finished good."""
        quality_str = self.quality.name.capitalize()
        type_str = self.good_type.name.capitalize().replace("_", " ")
        return f"{quality_str} {self.commodity.name} ({type_str}) {self.get_value()} {self.commodity.volume_per_unit}"
    
    def get_value(self) -> float:
        """Calculate the actual value based on quality level."""
        quality_modifiers = {
            FinishedGoodQuality.ECONOMY: 0.7,
            FinishedGoodQuality.STANDARD: 1.0,
            FinishedGoodQuality.PREMIUM: 1.8,
            FinishedGoodQuality.LUXURY: 3.0,
            FinishedGoodQuality.MILITARY: 2.5,
        }
        
        # Apply complexity modifier - more complex goods are more valuable
        complexity_factor = 1.0 + (self.assembly_complexity - 1.0) * 0.3
        
        # Apply tech level modifier - higher tech level goods are more valuable
        tech_factor = 1.0 + (self.tech_level - 1) * 0.2
        
        return round(
            self.commodity.base_price * 
            quality_modifiers.get(self.quality, 1.0) * 
            complexity_factor * 
            tech_factor, 
            2
        )
    
    def create_higher_quality_version(self) -> Optional["FinishedGood"]:
        """Create a new finished good object with the next quality level."""
        # For military goods, the progression is different
        if self.good_type == FinishedGoodType.MILITARY:
            quality_order = [
                FinishedGoodQuality.STANDARD,
                FinishedGoodQuality.PREMIUM,
                FinishedGoodQuality.MILITARY,
            ]
        else:
            quality_order = [
                FinishedGoodQuality.ECONOMY,
                FinishedGoodQuality.STANDARD,
                FinishedGoodQuality.PREMIUM,
                FinishedGoodQuality.LUXURY,
            ]
        
        try:
            current_index = quality_order.index(self.quality)
            if current_index >= len(quality_order) - 1:
                return None
                
            next_quality = quality_order[current_index + 1]
        except ValueError:
            # If the current quality is not in the progression (e.g., MILITARY for non-military goods)
            return None
        
        # Create a new finished good with the same properties but higher quality
        return FinishedGood(
            commodity=self.commodity,
            quality=next_quality,
            good_type=self.good_type,
            assembly_complexity=self.assembly_complexity,
            required_components=self.required_components.copy() if self.required_components else {},
            tech_level=self.tech_level,
            production_stage=ProductionStage.FINISHED,
        )
    
    def __hash__(self):
        # Use the ID and quality for hashing since they together form a unique identifier
        return hash((self.commodity.commodity_id, self.quality))
    
    def __eq__(self, other):
        if not isinstance(other, FinishedGood):
            return False
        return (
            self.commodity.commodity_id == other.commodity.commodity_id and 
            self.quality == other.quality
        )
    
    def get_waste_products(self) -> Dict[int, float]:
        """
        Calculate the waste products generated when assembling this finished good.
        
        Returns:
            Dictionary mapping waste_product_id to the amount produced per finished good unit.
        """
        # This is a placeholder implementation. The actual waste product generation
        # will be implemented in the waste management system.
        waste_base_rate = 0.05  # 5% waste by default for assembly
        
        # Quality affects waste generation - higher quality means more waste due to precision requirements
        quality_waste_modifiers = {
            FinishedGoodQuality.ECONOMY: 0.8,    # 4% waste
            FinishedGoodQuality.STANDARD: 1.0,   # 5% waste
            FinishedGoodQuality.PREMIUM: 1.2,    # 6% waste
            FinishedGoodQuality.LUXURY: 1.5,     # 7.5% waste
            FinishedGoodQuality.MILITARY: 1.3,   # 6.5% waste
        }
        
        # Complexity affects waste generation - more complex assembly generates more waste
        complexity_factor = 1.0 + (self.assembly_complexity - 1.0) * 0.1
        
        waste_modifier = quality_waste_modifiers.get(self.quality, 1.0) * complexity_factor
        waste_rate = waste_base_rate * waste_modifier
        
        # For now, we'll just return a generic waste product with ID 3
        # This will be expanded in the waste management system implementation
        return {3: round(waste_rate, 2)}


# Define some example finished goods
FINISHED_GOODS: Dict[int, FinishedGood] = {
    0: FinishedGood(
        commodity=Commodity(
            commodity_id=200,
            name="Personal Computer",
            category=Category.MANUFACTURED_GOOD,
            base_price=800.0,
            price_volatility=0.2,
            volatility_range=(0.0, 0.0),
            description="A standard personal computing device",
            volume_per_unit=0.1,
            mass_per_unit=0.5
        ),
        quality=FinishedGoodQuality.STANDARD,
        good_type=FinishedGoodType.CONSUMER,
        assembly_complexity=1.5,
        required_components={0: 2, 1: 1, 2: 1},  # 2 Circuit Boards, 1 Steel Frame, 1 Power Converter
        tech_level=2,
        production_stage=ProductionStage.FINISHED
    ),
    1: FinishedGood(
        commodity=Commodity(
            commodity_id=201,
            name="Mining Laser",
            category=Category.MANUFACTURED_GOOD,
            base_price=1500.0,
            price_volatility=0.25,
            volatility_range=(0.0, 0.0),
            description="A laser tool for mining operations",
            volume_per_unit=0.3,
            mass_per_unit=1.2
        ),
        quality=FinishedGoodQuality.STANDARD,
        good_type=FinishedGoodType.INDUSTRIAL,
        assembly_complexity=2.0,
        required_components={0: 1, 2: 2, 3: 1},  # 1 Circuit Board, 2 Power Converters, 1 Thruster Nozzle (for heat management)
        tech_level=2,
        production_stage=ProductionStage.FINISHED
    ),
    2: FinishedGood(
        commodity=Commodity(
            commodity_id=202,
            name="Medical Scanner",
            category=Category.MANUFACTURED_GOOD,
            base_price=2200.0,
            price_volatility=0.15,
            volatility_range=(0.0, 0.0),
            description="A device for medical diagnostics",
            volume_per_unit=0.2,
            mass_per_unit=0.8
        ),
        quality=FinishedGoodQuality.PREMIUM,
        good_type=FinishedGoodType.MEDICAL,
        assembly_complexity=2.5,
        required_components={0: 3, 2: 1, 4: 2},  # 3 Circuit Boards, 1 Power Converter, 2 Sensor Arrays
        tech_level=3,
        production_stage=ProductionStage.FINISHED
    ),
    3: FinishedGood(
        commodity=Commodity(
            commodity_id=203,
            name="Shield Generator",
            category=Category.MANUFACTURED_GOOD,
            base_price=5000.0,
            price_volatility=0.3,
            volatility_range=(0.0, 0.0),
            description="A device that generates protective shields for ships",
            volume_per_unit=0.5,
            mass_per_unit=2.5
        ),
        quality=FinishedGoodQuality.MILITARY,
        good_type=FinishedGoodType.SHIP_EQUIPMENT,
        assembly_complexity=3.0,
        required_components={0: 2, 2: 3, 5: 2},  # 2 Circuit Boards, 3 Power Converters, 2 Shield Emitters
        tech_level=4,
        production_stage=ProductionStage.FINISHED
    ),
    4: FinishedGood(
        commodity=Commodity(
            commodity_id=204,
            name="Luxury Wristwatch",
            category=Category.MANUFACTURED_GOOD,
            base_price=3500.0,
            price_volatility=0.4,
            volatility_range=(0.0, 0.0),
            description="A high-end timepiece made with precious materials",
            volume_per_unit=0.01,
            mass_per_unit=0.05
        ),
        quality=FinishedGoodQuality.LUXURY,
        good_type=FinishedGoodType.LUXURY,
        assembly_complexity=2.2,
        required_components={0: 1, 1: 0.1},  # 1 Circuit Board, 0.1 Steel Frame (small amount for casing)
        tech_level=2,
        production_stage=ProductionStage.FINISHED
    ),
    5: FinishedGood(
        commodity=Commodity(
            commodity_id=205,
            name="Research Instrument",
            category=Category.MANUFACTURED_GOOD,
            base_price=4200.0,
            price_volatility=0.2,
            volatility_range=(0.0, 0.0),
            description="A specialized instrument for scientific research",
            volume_per_unit=0.3,
            mass_per_unit=1.0
        ),
        quality=FinishedGoodQuality.PREMIUM,
        good_type=FinishedGoodType.SCIENTIFIC,
        assembly_complexity=2.8,
        required_components={0: 4, 2: 2, 4: 3},  # 4 Circuit Boards, 2 Power Converters, 3 Sensor Arrays
        tech_level=3,
        production_stage=ProductionStage.FINISHED
    ),
}


def get_finished_good_by_name(name: str) -> FinishedGood | None:
    """Get a finished good by its name."""
    for finished_good in FINISHED_GOODS.values():
        if finished_good.commodity.name.lower() == name.lower():
            return finished_good
    return None