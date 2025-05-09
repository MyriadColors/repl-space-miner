from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, List, Optional


class EngineType(Enum):
    """Types of ship engines available"""

    STANDARD = auto()  # Balanced performance
    CARGO_HAULER = auto()  # Specialized for hauling Magneton
    HIGH_PERFORMANCE = auto()  # Optimized for speed
    STEALTH = auto()  # Low signature
    ECONOMY = auto()  # Fuel efficient


@dataclass
class Engine:
    """Engine class representing ship propulsion system"""

    id: str
    name: str
    description: str
    engine_type: EngineType
    price: float

    # Base stats modifiers
    speed_modifier: float = 1.0
    fuel_consumption_modifier: float = 1.0
    sensor_signature_modifier: float = 1.0
    maintenance_cost_modifier: float = 1.0

    # Special properties
    magneton_resistance: float = 0.0  # How much it reduces Magneton interference (0-1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "engine_type": self.engine_type.name,
            "price": self.price,
            "speed_modifier": self.speed_modifier,
            "fuel_consumption_modifier": self.fuel_consumption_modifier,
            "sensor_signature_modifier": self.sensor_signature_modifier,
            "maintenance_cost_modifier": self.maintenance_cost_modifier,
            "magneton_resistance": self.magneton_resistance,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Engine":
        """Create Engine from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            engine_type=EngineType[data["engine_type"]],
            price=data["price"],
            speed_modifier=data["speed_modifier"],
            fuel_consumption_modifier=data["fuel_consumption_modifier"],
            sensor_signature_modifier=data["sensor_signature_modifier"],
            maintenance_cost_modifier=data["maintenance_cost_modifier"],
            magneton_resistance=data.get("magneton_resistance", 0.0),
        )

    def copy(self) -> "Engine":
        """Create a copy of this engine"""
        return Engine(
            id=self.id,
            name=self.name,
            description=self.description,
            engine_type=self.engine_type,
            price=self.price,
            speed_modifier=self.speed_modifier,
            fuel_consumption_modifier=self.fuel_consumption_modifier,
            sensor_signature_modifier=self.sensor_signature_modifier,
            maintenance_cost_modifier=self.maintenance_cost_modifier,
            magneton_resistance=self.magneton_resistance,
        )
