from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Tuple, Any

from src.classes.commodity import Commodity, Category


class ProductionStage(Enum):
    """Represents the stage in the production chain."""
    RAW = auto()         # Raw materials (ores)
    REFINED = auto()     # Refined materials (minerals)
    COMPONENT = auto()   # Manufactured components
    FINISHED = auto()    # Finished goods


@dataclass
class Resource:
    """
    Base class for all resources in the economy.
    
    This class serves as the foundation for the complete resource production chain,
    providing common properties and methods for all resource types.
    """
    commodity: Commodity
    production_stage: ProductionStage
    market_demand: float = 1.0  # Demand multiplier (1.0 = normal)
    market_supply: float = 1.0  # Supply multiplier (1.0 = normal)
    price_history: List[Tuple[float, float]] = field(default_factory=list)  # List of (timestamp, price) tuples
    
    def __post_init__(self):
        """Initialize production stage if not set."""
        if self.production_stage is None:
            # Default to RAW - subclasses should override this
            self.production_stage = ProductionStage.RAW
    
    @property
    def id(self) -> int:
        """Get the resource ID from the commodity."""
        return self.commodity.commodity_id
    
    @property
    def name(self) -> str:
        """Get the resource name from the commodity."""
        return self.commodity.name
    
    @property
    def base_value(self) -> float:
        """Get the base value from the commodity."""
        return self.commodity.base_price
    
    @property
    def volume(self) -> float:
        """Get the volume per unit from the commodity."""
        return self.commodity.volume_per_unit
    
    @property
    def mass(self) -> float:
        """Get the mass per unit from the commodity."""
        return self.commodity.mass_per_unit
    
    @property
    def description(self) -> str:
        """Get the description from the commodity."""
        return self.commodity.description
    
    @property
    def category(self) -> Category:
        """Get the category from the commodity."""
        return self.commodity.category
    
    @property
    def price_volatility(self) -> float:
        """Get the price volatility from the commodity."""
        return self.commodity.price_volatility
    
    def get_name(self) -> str:
        """Get the lowercase name of the resource."""
        return self.commodity.name.lower()
    
    def get_value(self) -> float:
        """
        Calculate the actual value of the resource.
        
        This method should be overridden by subclasses to implement
        specific value calculations based on quality, purity, etc.
        """
        return round(self.commodity.base_price, 2)
    
    def get_market_price(self, market_modifier: float = 1.0) -> float:
        """
        Calculate the current market price based on supply and demand.
        
        Args:
            market_modifier: Station-specific market modifier
            
        Returns:
            Current market price
        """
        # Base calculation using supply and demand
        supply_demand_factor = (self.market_demand / self.market_supply) if self.market_supply > 0 else 2.0
        
        # Clamp the factor to reasonable limits
        supply_demand_factor = max(0.5, min(supply_demand_factor, 2.0))
        
        # Calculate final price
        return round(self.get_value() * supply_demand_factor * market_modifier, 2)
    
    def update_price_history(self, timestamp: float, price: float) -> None:
        """
        Add a price point to the resource's price history.
        
        Args:
            timestamp: Game time when the price was recorded
            price: The price at that time
        """
        self.price_history.append((timestamp, price))
        
        # Keep history at a reasonable size (last 50 entries)
        if len(self.price_history) > 50:
            self.price_history = self.price_history[-50:]
    
    def get_price_trend(self) -> float:
        """
        Calculate the current price trend.
        
        Returns:
            A value between -1.0 (strongly decreasing) and 1.0 (strongly increasing)
        """
        if len(self.price_history) < 2:
            return 0.0
            
        # Calculate trend based on recent history
        recent_history = self.price_history[-10:]  # Last 10 entries
        if len(recent_history) < 2:
            return 0.0
            
        first_price = recent_history[0][1]
        last_price = recent_history[-1][1]
        
        if first_price == 0:
            return 0.0
            
        # Calculate percentage change and normalize to [-1, 1]
        change = (last_price - first_price) / first_price
        return max(-1.0, min(change, 1.0))
    
    def to_string(self) -> str:
        """
        Get a string representation of the resource.
        
        This method should be overridden by subclasses to provide
        specific string representations.
        """
        return f"{self.commodity.name}: {self.get_value()} credits, {self.commodity.volume_per_unit} m³ per unit"
    
    def get_info(self) -> str:
        """
        Get information about the resource.
        
        This method should be overridden by subclasses to provide
        specific information.
        """
        return f"{self.commodity.name} {self.get_value()} {self.commodity.volume_per_unit}"
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the resource.
        
        Returns:
            Dictionary with detailed resource information
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "base_value": self.base_value,
            "current_value": self.get_value(),
            "volume": self.volume,
            "mass": self.mass,
            "category": self.category.name,
            "production_stage": self.production_stage.name,
            "market_demand": self.market_demand,
            "market_supply": self.market_supply,
            "price_trend": self.get_price_trend()
        }
    
    def get_waste_products(self) -> Dict[int, float]:
        """
        Calculate the waste products generated when processing this resource.
        
        Returns:
            Dictionary mapping waste_product_id to the amount produced per resource unit.
        """
        # Base implementation returns no waste
        # Subclasses should override this method
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the resource to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the resource
        """
        return {
            "commodity_id": self.commodity.commodity_id,
            "production_stage": self.production_stage.name if self.production_stage else None,
            "market_demand": self.market_demand,
            "market_supply": self.market_supply,
            "price_history": self.price_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], commodity: Commodity) -> 'Resource':
        """
        Create a Resource instance from a dictionary representation.
        
        This class method deserializes a Resource object from a dictionary,
        typically used when loading saved game data or receiving data from
        external sources.
        
        Args:
            data: Dictionary containing the resource data with keys:
                - production_stage (str, optional): Name of the production stage.
                  Defaults to "RAW" if not provided or None.
                - market_demand (float, optional): Market demand multiplier.
                  Defaults to 1.0 if not provided.
                - market_supply (float, optional): Market supply multiplier.
                  Defaults to 1.0 if not provided.
                - price_history (List[Tuple[float, float]], optional): Historical
                  price data as list of (timestamp, price) tuples.
                  Defaults to empty list if not provided.
            commodity: The Commodity object associated with this resource.
        
        Returns:
            Resource: A new Resource instance initialized with the provided data
            and commodity information.
        """
        production_stage = ProductionStage[data.get("production_stage", "RAW")] if data.get("production_stage") else ProductionStage.RAW
    
        return cls(
            commodity=commodity,
            production_stage=production_stage,
            market_demand=data.get("market_demand", 1.0),
            market_supply=data.get("market_supply", 1.0),
            price_history=data.get("price_history", [])
        )
    def __hash__(self):
        """Hash method for resource objects."""
        # Use the ID for hashing since it forms a unique identifier
        return hash(self.commodity.commodity_id)
    
    def __eq__(self, other):
        """Equality method for resource objects."""
        if not isinstance(other, Resource):
            return False
        return self.commodity.commodity_id == other.commodity.commodity_id