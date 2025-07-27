from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Tuple, Any, Optional

from src.classes.commodity import Commodity, Category
from src.classes.resource import Resource, ProductionStage


class HazardLevel(Enum):
    """Represents the hazard level of a waste product."""
    HARMLESS = auto()      # No special handling required
    LOW = auto()           # Minor precautions needed
    MODERATE = auto()      # Standard safety protocols required
    HIGH = auto()          # Specialized handling required
    EXTREME = auto()       # Extremely hazardous, strict containment needed


class WasteType(Enum):
    """Represents the type of waste product."""
    SLAG = auto()          # Metallic waste from refining
    TAILINGS = auto()      # Rock waste from ore processing
    CHEMICAL = auto()      # Chemical byproducts
    RADIOACTIVE = auto()   # Radioactive waste materials
    TOXIC = auto()         # Toxic chemical compounds
    ORGANIC = auto()       # Organic waste materials
    INERT = auto()         # Inert solid waste


@dataclass
class WasteProduct(Resource):
    """
    Represents a waste product generated from industrial processes.
    
    Waste products are byproducts of refining, manufacturing, and assembly processes.
    They require proper disposal or can potentially be recycled into useful materials.
    """
    hazard_level: HazardLevel = HazardLevel.HARMLESS
    waste_type: WasteType = WasteType.INERT
    disposal_cost: float = 0.0  # Cost per unit to dispose legally
    illegal_to_dump: bool = False  # Whether illegal dumping is prohibited
    recyclable: bool = False  # Whether this waste can be recycled
    recycling_products: Dict[int, float] = field(default_factory=dict)  # Resource ID to yield ratio
    decay_rate: float = 0.0  # Rate at which hazard level decreases over time (per day)
    containment_requirement: str = "standard"  # Type of containment needed
    environmental_impact: float = 1.0  # Environmental damage multiplier if dumped illegally
    detection_difficulty: float = 1.0  # How hard it is to detect illegal dumping (higher = harder)
    
    def __post_init__(self):
        """Initialize waste product specific properties."""
        # Waste products are not part of the normal production chain
        self.production_stage = ProductionStage.RAW  # Use RAW as default, but waste is special
        
        # Set disposal cost based on hazard level if not explicitly set
        if self.disposal_cost == 0.0:
            self.disposal_cost = self._calculate_base_disposal_cost()
    
    def _calculate_base_disposal_cost(self) -> float:
        """Calculate base disposal cost based on hazard level and waste type."""
        hazard_cost_multipliers = {
            HazardLevel.HARMLESS: 1.0,
            HazardLevel.LOW: 2.0,
            HazardLevel.MODERATE: 5.0,
            HazardLevel.HIGH: 15.0,
            HazardLevel.EXTREME: 50.0,
        }
        
        waste_type_multipliers = {
            WasteType.SLAG: 1.0,
            WasteType.TAILINGS: 0.8,
            WasteType.CHEMICAL: 2.0,
            WasteType.RADIOACTIVE: 10.0,
            WasteType.TOXIC: 5.0,
            WasteType.ORGANIC: 0.5,
            WasteType.INERT: 0.3,
        }
        
        base_cost = 10.0  # Base disposal cost per unit
        hazard_multiplier = hazard_cost_multipliers.get(self.hazard_level, 1.0)
        type_multiplier = waste_type_multipliers.get(self.waste_type, 1.0)
        
        return round(base_cost * hazard_multiplier * type_multiplier, 2)
    
    def get_value(self) -> float:
        """
        Calculate the value of the waste product.
        
        Waste products typically have negative value (disposal cost),
        but recyclable waste may have positive value.
        """
        if self.recyclable and self.recycling_products:
            # Calculate value based on recyclable materials
            recycling_value = sum(
                yield_amount * 10.0  # Assume 10 credits per unit of recyclable material
                for yield_amount in self.recycling_products.values()
            )
            # Subtract disposal cost to get net value
            return round(recycling_value - self.disposal_cost, 2)
        else:
            # Non-recyclable waste has negative value (disposal cost)
            return round(-self.disposal_cost, 2)
    
    def get_disposal_cost(self, disposal_method: str = "legal") -> float:
        """
        Get the cost of disposing this waste product.
        
        Args:
            disposal_method: "legal" for proper disposal, "illegal" for dumping
            
        Returns:
            Cost per unit to dispose of the waste
        """
        if disposal_method == "legal":
            return self.disposal_cost
        elif disposal_method == "illegal":
            # Illegal dumping has no immediate cost but carries risks
            return 0.0
        else:
            return self.disposal_cost
    
    def get_illegal_dumping_risk(self, location_type: str = "space") -> Dict[str, float]:
        """
        Calculate the risks associated with illegal dumping.
        
        Args:
            location_type: Type of location where dumping occurs
            
        Returns:
            Dictionary with risk factors
        """
        base_detection_chance = 0.1  # 10% base chance of detection
        
        # Location affects detection chance
        location_modifiers = {
            "space": 0.5,      # Lower detection in open space
            "asteroid": 0.7,   # Moderate detection near asteroids
            "station": 2.0,    # High detection near stations
            "planet": 1.5,     # High detection near planets
        }
        
        location_modifier = location_modifiers.get(location_type, 1.0)
        detection_chance = min(0.9, base_detection_chance * location_modifier / self.detection_difficulty)
        
        # Calculate potential penalties
        reputation_penalty = self.environmental_impact * 10.0
        fine_amount = self.disposal_cost * 5.0  # Fine is 5x the legal disposal cost
        
        return {
            "detection_chance": round(detection_chance, 3),
            "reputation_penalty": round(reputation_penalty, 1),
            "fine_amount": round(fine_amount, 2),
            "environmental_damage": round(self.environmental_impact, 2)
        }
    
    def can_recycle(self, equipment_quality: float = 1.0) -> bool:
        """
        Check if this waste product can be recycled with given equipment.
        
        Args:
            equipment_quality: Quality of recycling equipment (0.0-1.0)
            
        Returns:
            True if recycling is possible
        """
        if not self.recyclable:
            return False
        
        # Some waste types require higher quality equipment
        min_quality_requirements = {
            WasteType.SLAG: 0.3,
            WasteType.TAILINGS: 0.2,
            WasteType.CHEMICAL: 0.7,
            WasteType.RADIOACTIVE: 0.9,
            WasteType.TOXIC: 0.8,
            WasteType.ORGANIC: 0.1,
            WasteType.INERT: 0.1,
        }
        
        min_quality = min_quality_requirements.get(self.waste_type, 0.5)
        return equipment_quality >= min_quality
    
    def recycle(self, equipment_quality: float = 1.0, operator_skill: float = 1.0) -> Dict[int, float]:
        """
        Recycle this waste product into useful materials.
        
        Args:
            equipment_quality: Quality of recycling equipment (0.0-1.0)
            operator_skill: Skill level of the operator (0.0-2.0)
            
        Returns:
            Dictionary mapping resource_id to amount recovered
        """
        if not self.can_recycle(equipment_quality):
            return {}
        
        # Calculate efficiency based on equipment and skill
        base_efficiency = 0.6  # 60% base recovery rate
        equipment_bonus = (equipment_quality - 0.5) * 0.4  # Up to 20% bonus from equipment
        skill_bonus = (operator_skill - 1.0) * 0.2  # Up to 20% bonus from skill
        
        total_efficiency = max(0.1, min(0.95, base_efficiency + equipment_bonus + skill_bonus))
        
        # Apply efficiency to recycling products
        recovered_materials = {}
        for resource_id, base_yield in self.recycling_products.items():
            recovered_amount = base_yield * total_efficiency
            if recovered_amount > 0.01:  # Only include meaningful amounts
                recovered_materials[resource_id] = round(recovered_amount, 3)
        
        return recovered_materials
    
    def update_hazard_over_time(self, days_elapsed: float) -> None:
        """
        Update the hazard level of the waste product over time.
        
        Some waste products become less hazardous over time due to decay.
        
        Args:
            days_elapsed: Number of days that have passed
        """
        if self.decay_rate <= 0.0:
            return
        
        # Calculate decay
        decay_amount = self.decay_rate * days_elapsed
        
        # For simplicity, we'll reduce environmental impact rather than changing hazard level
        self.environmental_impact = max(0.1, self.environmental_impact - decay_amount)
    
    def to_string(self) -> str:
        """Get a string representation of the waste product."""
        hazard_str = self.hazard_level.name.capitalize()
        return f"{hazard_str} {self.commodity.name}: {self.get_value()} credits, {self.commodity.volume_per_unit} m³ per unit"
    
    def get_info(self) -> str:
        """Get information about the waste product."""
        hazard_str = self.hazard_level.name.capitalize()
        recyclable_str = "Recyclable" if self.recyclable else "Non-recyclable"
        return f"{hazard_str} {self.commodity.name} ({recyclable_str}) {self.get_value()} {self.commodity.volume_per_unit}"
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Get detailed information about the waste product."""
        base_info = super().get_detailed_info()
        base_info.update({
            "hazard_level": self.hazard_level.name,
            "waste_type": self.waste_type.name,
            "disposal_cost": self.disposal_cost,
            "illegal_to_dump": self.illegal_to_dump,
            "recyclable": self.recyclable,
            "recycling_products": self.recycling_products,
            "containment_requirement": self.containment_requirement,
            "environmental_impact": self.environmental_impact,
            "detection_difficulty": self.detection_difficulty
        })
        return base_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the waste product to a dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            "hazard_level": self.hazard_level.name,
            "waste_type": self.waste_type.name,
            "disposal_cost": self.disposal_cost,
            "illegal_to_dump": self.illegal_to_dump,
            "recyclable": self.recyclable,
            "recycling_products": self.recycling_products,
            "decay_rate": self.decay_rate,
            "containment_requirement": self.containment_requirement,
            "environmental_impact": self.environmental_impact,
            "detection_difficulty": self.detection_difficulty
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], commodity: Commodity) -> 'WasteProduct':
        """Create a WasteProduct instance from a dictionary representation."""
        # First create a base Resource object
        resource = Resource.from_dict(data, commodity)
        
        # Extract waste-specific properties
        hazard_level = HazardLevel[data.get("hazard_level", "HARMLESS")]
        waste_type = WasteType[data.get("waste_type", "INERT")]
        disposal_cost = data.get("disposal_cost", 0.0)
        illegal_to_dump = data.get("illegal_to_dump", False)
        recyclable = data.get("recyclable", False)
        recycling_products = data.get("recycling_products", {})
        decay_rate = data.get("decay_rate", 0.0)
        containment_requirement = data.get("containment_requirement", "standard")
        environmental_impact = data.get("environmental_impact", 1.0)
        detection_difficulty = data.get("detection_difficulty", 1.0)
        
        # Create and return the WasteProduct object
        return cls(
            commodity=commodity,
            production_stage=resource.production_stage,
            market_demand=resource.market_demand,
            market_supply=resource.market_supply,
            price_history=resource.price_history,
            hazard_level=hazard_level,
            waste_type=waste_type,
            disposal_cost=disposal_cost,
            illegal_to_dump=illegal_to_dump,
            recyclable=recyclable,
            recycling_products=recycling_products,
            decay_rate=decay_rate,
            containment_requirement=containment_requirement,
            environmental_impact=environmental_impact,
            detection_difficulty=detection_difficulty
        )


class WasteGenerator:
    """
    Utility class for generating waste products from different production processes.
    
    This class contains formulas and logic for calculating waste generation
    based on input materials, process type, and equipment quality.
    """
    
    @staticmethod
    def calculate_refining_waste(ore_type: str, ore_quantity: float, 
                               equipment_quality: float = 1.0,
                               operator_skill: float = 1.0) -> Dict[int, float]:
        """
        Calculate waste products generated from ore refining.
        
        Args:
            ore_type: Type of ore being refined
            ore_quantity: Amount of ore being processed
            equipment_quality: Quality of refining equipment (0.0-1.0)
            operator_skill: Skill level of the operator (0.0-2.0)
            
        Returns:
            Dictionary mapping waste_product_id to amount generated
        """
        # Base waste generation rates by ore type
        ore_waste_rates = {
            "pyrogen": {"slag": 0.25, "tailings": 0.15},
            "ascorbon": {"tailings": 0.20, "inert": 0.10},
            "angion": {"slag": 0.30, "chemical": 0.05},
            "varite": {"tailings": 0.18, "inert": 0.12},
            "oxynite": {"radioactive": 0.08, "toxic": 0.12},
            "cyclon": {"chemical": 0.15, "slag": 0.20},
            "heron": {"toxic": 0.10, "slag": 0.25},
            "jonnite": {"radioactive": 0.15, "toxic": 0.20},
            "magneton": {"slag": 0.22, "inert": 0.08},
        }
        
        base_rates = ore_waste_rates.get(ore_type.lower(), {"inert": 0.20})
        
        # Calculate efficiency factors
        equipment_efficiency = 0.5 + (equipment_quality * 0.4)  # 0.5 to 0.9
        skill_efficiency = 0.8 + (operator_skill - 1.0) * 0.2  # 0.6 to 1.0
        total_efficiency = equipment_efficiency * skill_efficiency
        
        # Higher efficiency means less waste
        waste_multiplier = max(0.3, 2.0 - total_efficiency)
        
        # Calculate actual waste amounts
        waste_products = {}
        waste_id_mapping = {
            "slag": 1000,      # Metallic slag waste
            "tailings": 1001,  # Rock tailings waste
            "chemical": 1002,  # Chemical waste
            "radioactive": 1003, # Radioactive waste
            "toxic": 1004,     # Toxic waste
            "inert": 1005,     # Inert solid waste
        }
        
        for waste_type, base_rate in base_rates.items():
            waste_id = waste_id_mapping.get(waste_type, 1005)
            waste_amount = ore_quantity * base_rate * waste_multiplier
            if waste_amount > 0.01:  # Only include meaningful amounts
                waste_products[waste_id] = round(waste_amount, 3)
        
        return waste_products
    
    @staticmethod
    def calculate_manufacturing_waste(mineral_type: str, mineral_quantity: float,
                                    equipment_quality: float = 1.0,
                                    operator_skill: float = 1.0) -> Dict[int, float]:
        """
        Calculate waste products generated from component manufacturing.
        
        Args:
            mineral_type: Type of mineral being processed
            mineral_quantity: Amount of mineral being processed
            equipment_quality: Quality of manufacturing equipment (0.0-1.0)
            operator_skill: Skill level of the operator (0.0-2.0)
            
        Returns:
            Dictionary mapping waste_product_id to amount generated
        """
        # Base waste generation rates by mineral type
        mineral_waste_rates = {
            "iron": {"slag": 0.15, "inert": 0.05},
            "carbon": {"organic": 0.10, "inert": 0.08},
            "silicon": {"chemical": 0.12, "inert": 0.06},
            "copper": {"slag": 0.18, "chemical": 0.04},
            "zinc": {"slag": 0.16, "toxic": 0.03},
            "aluminum": {"slag": 0.14, "inert": 0.07},
            "titanium": {"slag": 0.20, "inert": 0.05},
            "nickel": {"slag": 0.17, "toxic": 0.02},
            "neodymium": {"toxic": 0.08, "chemical": 0.10},
            "gold": {"chemical": 0.05, "inert": 0.03},
            "rare earth elements": {"toxic": 0.12, "radioactive": 0.03},
            "exotic materials": {"radioactive": 0.10, "toxic": 0.15},
        }
        
        base_rates = mineral_waste_rates.get(mineral_type.lower(), {"inert": 0.10})
        
        # Calculate efficiency factors
        equipment_efficiency = 0.6 + (equipment_quality * 0.3)  # 0.6 to 0.9
        skill_efficiency = 0.8 + (operator_skill - 1.0) * 0.2  # 0.6 to 1.0
        total_efficiency = equipment_efficiency * skill_efficiency
        
        # Higher efficiency means less waste
        waste_multiplier = max(0.4, 1.8 - total_efficiency)
        
        # Calculate actual waste amounts
        waste_products = {}
        waste_id_mapping = {
            "slag": 1000,
            "chemical": 1002,
            "toxic": 1004,
            "organic": 1006,
            "inert": 1005,
            "radioactive": 1003,
        }
        
        for waste_type, base_rate in base_rates.items():
            waste_id = waste_id_mapping.get(waste_type, 1005)
            waste_amount = mineral_quantity * base_rate * waste_multiplier
            if waste_amount > 0.01:
                waste_products[waste_id] = round(waste_amount, 3)
        
        return waste_products
    
    @staticmethod
    def calculate_assembly_waste(component_type: str, component_quantity: float,
                               equipment_quality: float = 1.0,
                               operator_skill: float = 1.0) -> Dict[int, float]:
        """
        Calculate waste products generated from finished goods assembly.
        
        Args:
            component_type: Type of component being assembled
            component_quantity: Amount of components being processed
            equipment_quality: Quality of assembly equipment (0.0-1.0)
            operator_skill: Skill level of the operator (0.0-2.0)
            
        Returns:
            Dictionary mapping waste_product_id to amount generated
        """
        # Assembly generally produces less waste than refining or manufacturing
        base_waste_rate = 0.05  # 5% base waste rate
        
        # Calculate efficiency factors
        equipment_efficiency = 0.7 + (equipment_quality * 0.2)  # 0.7 to 0.9
        skill_efficiency = 0.8 + (operator_skill - 1.0) * 0.2  # 0.6 to 1.0
        total_efficiency = equipment_efficiency * skill_efficiency
        
        # Higher efficiency means less waste
        waste_multiplier = max(0.2, 1.5 - total_efficiency)
        
        # Assembly waste is typically inert material (packaging, offcuts, etc.)
        waste_amount = component_quantity * base_waste_rate * waste_multiplier
        
        if waste_amount > 0.01:
            return {1005: round(waste_amount, 3)}  # Inert waste
        else:
            return {}


# Define common waste products
WASTE_PRODUCTS: Dict[int, WasteProduct] = {
    1000: WasteProduct(
        commodity=Commodity(
            commodity_id=1000,
            name="Metallic Slag",
            category=Category.RAW_MATERIAL,
            base_price=0.0,  # Waste has no base value
            price_volatility=0.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.8,
            mass_per_unit=1.2,
            description="Metallic waste byproduct from ore refining processes"
        ),
        production_stage=ProductionStage.RAW,  # Waste products use RAW as default
        hazard_level=HazardLevel.LOW,
        waste_type=WasteType.SLAG,
        illegal_to_dump=False,
        recyclable=True,
        recycling_products={0: 0.3, 1: 0.1},  # Can recover some iron and carbon
        environmental_impact=0.5,
        detection_difficulty=1.2
    ),
    
    1001: WasteProduct(
        commodity=Commodity(
            commodity_id=1001,
            name="Rock Tailings",
            category=Category.RAW_MATERIAL,
            base_price=0.0,
            price_volatility=0.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=1.5,
            mass_per_unit=2.0,
            description="Rock waste from ore processing and mining operations"
        ),
        production_stage=ProductionStage.RAW,
        hazard_level=HazardLevel.HARMLESS,
        waste_type=WasteType.TAILINGS,
        illegal_to_dump=False,
        recyclable=False,
        environmental_impact=0.3,
        detection_difficulty=0.8
    ),
    
    1002: WasteProduct(
        commodity=Commodity(
            commodity_id=1002,
            name="Chemical Waste",
            category=Category.RAW_MATERIAL,
            base_price=0.0,
            price_volatility=0.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.5,
            mass_per_unit=0.8,
            description="Chemical byproducts from industrial processing"
        ),
        production_stage=ProductionStage.RAW,
        hazard_level=HazardLevel.MODERATE,
        waste_type=WasteType.CHEMICAL,
        illegal_to_dump=True,
        recyclable=True,
        recycling_products={2: 0.2},  # Can recover some silicon
        containment_requirement="chemical_resistant",
        environmental_impact=2.0,
        detection_difficulty=1.5
    ),
    
    1003: WasteProduct(
        commodity=Commodity(
            commodity_id=1003,
            name="Radioactive Waste",
            category=Category.RAW_MATERIAL,
            base_price=0.0,
            price_volatility=0.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.3,
            mass_per_unit=1.5,
            description="Radioactive waste materials requiring special handling"
        ),
        production_stage=ProductionStage.RAW,
        hazard_level=HazardLevel.EXTREME,
        waste_type=WasteType.RADIOACTIVE,
        illegal_to_dump=True,
        recyclable=False,
        decay_rate=0.01,  # Slowly becomes less hazardous over time
        containment_requirement="radiation_shielded",
        environmental_impact=10.0,
        detection_difficulty=0.5  # Easy to detect due to radiation
    ),
    
    1004: WasteProduct(
        commodity=Commodity(
            commodity_id=1004,
            name="Toxic Waste",
            category=Category.RAW_MATERIAL,
            base_price=0.0,
            price_volatility=0.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.4,
            mass_per_unit=0.9,
            description="Toxic chemical compounds requiring careful disposal"
        ),
        production_stage=ProductionStage.RAW,
        hazard_level=HazardLevel.HIGH,
        waste_type=WasteType.TOXIC,
        illegal_to_dump=True,
        recyclable=False,
        containment_requirement="hazmat",
        environmental_impact=5.0,
        detection_difficulty=1.8
    ),
    
    1005: WasteProduct(
        commodity=Commodity(
            commodity_id=1005,
            name="Inert Waste",
            category=Category.RAW_MATERIAL,
            base_price=0.0,
            price_volatility=0.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=1.0,
            mass_per_unit=1.0,
            description="Inert solid waste materials with no special hazards"
        ),
        production_stage=ProductionStage.RAW,
        hazard_level=HazardLevel.HARMLESS,
        waste_type=WasteType.INERT,
        illegal_to_dump=False,
        recyclable=False,
        environmental_impact=0.1,
        detection_difficulty=2.0
    ),
    
    1006: WasteProduct(
        commodity=Commodity(
            commodity_id=1006,
            name="Organic Waste",
            category=Category.RAW_MATERIAL,
            base_price=0.0,
            price_volatility=0.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.6,
            mass_per_unit=0.4,
            description="Organic waste materials from processing operations"
        ),
        production_stage=ProductionStage.RAW,
        hazard_level=HazardLevel.HARMLESS,
        waste_type=WasteType.ORGANIC,
        illegal_to_dump=False,
        recyclable=True,
        recycling_products={1: 0.4},  # Can recover carbon
        decay_rate=0.05,  # Decomposes over time
        environmental_impact=0.2,
        detection_difficulty=1.5
    ),
}


def get_waste_product_by_name(name: str) -> Optional[WasteProduct]:
    """Get a waste product by its name."""
    for waste_product in WASTE_PRODUCTS.values():
        if waste_product.commodity.name.lower() == name.lower():
            return waste_product
    return None


def get_waste_product_by_id(waste_id: int) -> Optional[WasteProduct]:
    """Get a waste product by its ID."""
    return WASTE_PRODUCTS.get(waste_id)