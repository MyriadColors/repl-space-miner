from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from src.classes.commodity import Commodity, Category
from src.classes.resource import Resource, ProductionStage


class ComponentQuality(Enum):
    """Represents the quality level of a component."""
    BASIC = auto()       # Basic quality, minimal performance
    STANDARD = auto()    # Standard quality, normal performance
    ADVANCED = auto()    # Advanced quality, improved performance
    PREMIUM = auto()     # Premium quality, high performance
    PROTOTYPE = auto()   # Prototype quality, experimental performance


class ComponentType(Enum):
    """Represents the type of component."""
    STRUCTURAL = auto()   # Structural components (frames, supports)
    ELECTRONIC = auto()   # Electronic components (circuits, processors)
    MECHANICAL = auto()   # Mechanical components (gears, actuators)
    POWER = auto()        # Power components (generators, batteries)
    PROPULSION = auto()   # Propulsion components (engines, thrusters)
    LIFE_SUPPORT = auto() # Life support components (air filters, water recyclers)
    WEAPONS = auto()      # Weapon components (barrels, targeting systems)
    SHIELDS = auto()      # Shield components (emitters, capacitors)
    SENSORS = auto()      # Sensor components (scanners, detectors)


@dataclass
class Component(Resource):
    """
    Represents a manufactured component in the game.
    
    Components are created from minerals and are used to assemble finished goods.
    Their quality and performance are affected by the input mineral quality,
    manufacturing equipment, and the operator's engineering skill.
    """
    quality: ComponentQuality = ComponentQuality.STANDARD
    component_type: ComponentType = ComponentType.STRUCTURAL
    manufacturing_complexity: float = 1.0  # Higher values mean more difficult to manufacture
    required_minerals: Dict[int, float] = field(default_factory=dict)  # Mineral ID to quantity mapping
    tech_level: int = 1  # Minimum tech level required to manufacture
    production_stage: ProductionStage = ProductionStage.COMPONENT
    durability: float = 1.0  # Durability factor (1.0 = standard)
    efficiency: float = 1.0  # Efficiency factor (1.0 = standard)
    compatible_ship_classes: List[str] = field(default_factory=list)  # Ship classes this component is compatible with
    power_requirement: float = 0.0  # Power required to operate (0.0 = passive component)
    
    def __post_init__(self):
        """Ensure production stage is set to COMPONENT."""
        if not hasattr(self, 'production_stage') or self.production_stage is None:
            self.production_stage = ProductionStage.COMPONENT
    
    def to_string(self) -> str:
        """Get a string representation of the component."""
        quality_str = self.quality.name.capitalize()
        type_str = self.component_type.name.capitalize().replace("_", " ")
        return f"{quality_str} {self.commodity.name} ({type_str}): {self.get_value()} credits, {self.commodity.volume_per_unit} m³ per unit"
    
    def get_info(self) -> str:
        """Get information about the component."""
        quality_str = self.quality.name.capitalize()
        type_str = self.component_type.name.capitalize().replace("_", " ")
        return f"{quality_str} {self.commodity.name} ({type_str}) {self.get_value()} {self.commodity.volume_per_unit}"
    
    def get_value(self) -> float:
        """Calculate the actual value based on quality level."""
        quality_modifiers = {
            ComponentQuality.BASIC: 0.8,
            ComponentQuality.STANDARD: 1.0,
            ComponentQuality.ADVANCED: 1.5,
            ComponentQuality.PREMIUM: 2.5,
            ComponentQuality.PROTOTYPE: 4.0,
        }
        
        # Apply complexity modifier - more complex components are more valuable
        complexity_factor = 1.0 + (self.manufacturing_complexity - 1.0) * 0.2
        
        # Apply tech level modifier - higher tech level components are more valuable
        tech_factor = 1.0 + (self.tech_level - 1) * 0.15
        
        return round(
            self.commodity.base_price * 
            quality_modifiers.get(self.quality, 1.0) * 
            complexity_factor * 
            tech_factor, 
            2
        )
    
    def create_higher_quality_version(self) -> Optional["Component"]:
        """Create a new component object with the next quality level."""
        quality_order = [
            ComponentQuality.BASIC,
            ComponentQuality.STANDARD,
            ComponentQuality.ADVANCED,
            ComponentQuality.PREMIUM,
            ComponentQuality.PROTOTYPE,
        ]
        
        current_index = quality_order.index(self.quality)
        if current_index >= len(quality_order) - 1:
            return None
            
        next_quality = quality_order[current_index + 1]
        
        # Create a new component with the same properties but higher quality
        return Component(
            commodity=self.commodity,
            quality=next_quality,
            component_type=self.component_type,
            manufacturing_complexity=self.manufacturing_complexity,
            required_minerals=self.required_minerals.copy() if self.required_minerals else {},
            tech_level=self.tech_level,
            production_stage=ProductionStage.COMPONENT,
        )
    
    def __hash__(self):
        # Use the ID and quality for hashing since they together form a unique identifier
        return hash((self.commodity.commodity_id, self.quality))
    
    def __eq__(self, other):
        if not isinstance(other, Component):
            return False
        return (
            self.commodity.commodity_id == other.commodity.commodity_id and 
            self.quality == other.quality
        )
    
    def get_waste_products(self) -> Dict[int, float]:
        """
        Calculate the waste products generated when manufacturing this component.
        
        Returns:
            Dictionary mapping waste_product_id to the amount produced per component unit.
        """
        # This is a placeholder implementation. The actual waste product generation
        # will be implemented in the waste management system.
        waste_base_rate = 0.15  # 15% waste by default
        
        # Quality affects waste generation - higher quality means more waste due to precision requirements
        quality_waste_modifiers = {
            ComponentQuality.BASIC: 0.8,      # 12% waste
            ComponentQuality.STANDARD: 1.0,   # 15% waste
            ComponentQuality.ADVANCED: 1.2,   # 18% waste
            ComponentQuality.PREMIUM: 1.5,    # 22.5% waste
            ComponentQuality.PROTOTYPE: 2.0,  # 30% waste
        }
        
        # Complexity affects waste generation - more complex components generate more waste
        complexity_factor = 1.0 + (self.manufacturing_complexity - 1.0) * 0.1
        
        waste_modifier = quality_waste_modifiers.get(self.quality, 1.0) * complexity_factor
        waste_rate = waste_base_rate * waste_modifier
        
        # For now, we'll just return a generic waste product with ID 2
        # This will be expanded in the waste management system implementation
        return {2: round(waste_rate, 2)}


# Define some example components
COMPONENTS: Dict[int, Component] = {
    0: Component(
        commodity=Commodity(
            commodity_id=100,
            name="Basic Circuit Board",
            category=Category.COMPONENT,
            base_price=250.0,
            price_volatility=0.2,
            volatility_range=(0.0, 0.0),
            description="A simple electronic circuit board",
            volume_per_unit=0.05,
            mass_per_unit=0.1
        ),
        quality=ComponentQuality.BASIC,
        component_type=ComponentType.ELECTRONIC,
        manufacturing_complexity=1.2,
        required_minerals={3: 0.2, 2: 0.3},  # Copper and Silicon
        tech_level=1
    ),
    1: Component(
        commodity=Commodity(
            commodity_id=101,
            name="Steel Frame",
            category=Category.COMPONENT,
            base_price=180.0,
            price_volatility=0.1,
            volatility_range=(0.0, 0.0),
            description="A sturdy structural frame made of steel",
            volume_per_unit=0.4,
            mass_per_unit=2.0
        ),
        quality=ComponentQuality.STANDARD,
        component_type=ComponentType.STRUCTURAL,
        manufacturing_complexity=1.0,
        required_minerals={0: 0.8, 1: 0.1},  # Iron and Carbon
        tech_level=1,
        production_stage=ProductionStage.COMPONENT
    ),
    2: Component(
        commodity=Commodity(
            commodity_id=102,
            name="Power Converter",
            category=Category.COMPONENT,
            base_price=350.0,
            price_volatility=0.25,
            volatility_range=(0.0, 0.0),
            description="A device that converts power between different forms",
            volume_per_unit=0.2,
            mass_per_unit=0.8
        ),
        quality=ComponentQuality.ADVANCED,
        component_type=ComponentType.POWER,
        manufacturing_complexity=1.8,
        required_minerals={3: 0.3, 8: 0.2, 5: 0.2},  # Copper, Neodymium, Aluminum
        tech_level=2,
        production_stage=ProductionStage.COMPONENT
    ),
    3: Component(
        commodity=Commodity(
            commodity_id=103,
            name="Thruster Nozzle",
            category=Category.COMPONENT,
            base_price=420.0,
            price_volatility=0.15,
            volatility_range=(0.0, 0.0),
            description="A high-temperature nozzle for spacecraft thrusters",
            volume_per_unit=0.3,
            mass_per_unit=1.5
        ),
        quality=ComponentQuality.STANDARD,
        component_type=ComponentType.PROPULSION,
        manufacturing_complexity=1.5,
        required_minerals={6: 0.5, 5: 0.3},  # Titanium and Aluminum
        tech_level=2,
        production_stage=ProductionStage.COMPONENT
    ),
    4: Component(
        commodity=Commodity(
            commodity_id=104,
            name="Sensor Array",
            category=Category.COMPONENT,
            base_price=580.0,
            price_volatility=0.3,
            volatility_range=(0.0, 0.0),
            description="A sophisticated array of sensors for detecting various phenomena",
            volume_per_unit=0.15,
            mass_per_unit=0.4
        ),
        quality=ComponentQuality.PREMIUM,
        component_type=ComponentType.SENSORS,
        manufacturing_complexity=2.2,
        required_minerals={10: 0.2, 3: 0.3, 2: 0.4},  # Rare Earth Elements, Copper, Silicon
        tech_level=3,
        production_stage=ProductionStage.COMPONENT
    ),
    5: Component(
        commodity=Commodity(
            commodity_id=105,
            name="Shield Emitter",
            category=Category.COMPONENT,
            base_price=1200.0,
            price_volatility=0.4,
            volatility_range=(0.0, 0.0),
            description="A device that generates protective energy fields",
            volume_per_unit=0.25,
            mass_per_unit=1.2
        ),
        quality=ComponentQuality.PROTOTYPE,
        component_type=ComponentType.SHIELDS,
        manufacturing_complexity=3.0,
        required_minerals={11: 0.1, 8: 0.3, 10: 0.4},  # Exotic Materials, Neodymium, Rare Earth Elements
        tech_level=4,
        production_stage=ProductionStage.COMPONENT
    ),
}


def get_component_by_name(name: str) -> Component | None:
    """Get a component by its name."""
    for component in COMPONENTS.values():
        if component.commodity.name.lower() == name.lower():
            return component
    return None