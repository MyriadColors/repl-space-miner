"""
Unified cargo management system for ships.

This module provides the CargoItem and CargoHold classes that replace the
separate cargohold and mineralhold lists with a single, unified cargo system.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Any
from src.classes.ore import Ore
from src.classes.mineral import Mineral
from src.classes.component import Component
from src.classes.finished_good import FinishedGood
from src.classes.result import Result, CargoError, CargoErrorDetails, CargoResult, VoidResult


@dataclass
class CargoItem:
    """
    Unified cargo item that can hold any type of tradeable item.
    
    This class provides a consistent interface for all cargo items regardless
    of their underlying type (Ore, Mineral, Component, or FinishedGood).
    """
    item: Union[Ore, Mineral, Component, FinishedGood]
    quantity: int
    buy_price: float
    sell_price: float
    
    def __post_init__(self):
        """Validate cargo item after initialization."""
        validation_result = self.validate()
        if validation_result.is_err():
            error_details = validation_result.unwrap_err()
            raise ValueError(error_details.message)
    
    def validate(self) -> VoidResult:
        """
        Validate cargo item properties.
        
        Returns:
            Result[None, CargoErrorDetails]: Success or validation error
        """
        if self.quantity < 0:
            return Result.err(CargoErrorDetails(
                CargoError.NEGATIVE_QUANTITY,
                f"Quantity cannot be negative: {self.quantity}",
                {"quantity": self.quantity}
            ))
        
        if self.buy_price < 0 or self.sell_price < 0:
            return Result.err(CargoErrorDetails(
                CargoError.NEGATIVE_PRICE,
                f"Prices cannot be negative: buy_price={self.buy_price}, sell_price={self.sell_price}",
                {"buy_price": self.buy_price, "sell_price": self.sell_price}
            ))
        
        return Result.ok(None)
    
    @property
    def volume_per_unit(self) -> float:
        """Get volume per unit for this item type."""
        return self.item.commodity.volume_per_unit
    
    @property
    def total_volume(self) -> float:
        """Get total volume occupied by this cargo stack."""
        return self.quantity * self.volume_per_unit
    
    @property
    def item_id(self) -> str:
        """Get unique identifier for this item."""
        return str(self.item.commodity.commodity_id)
    
    @property
    def item_name(self) -> str:
        """Get display name for this item."""
        return self.item.commodity.name
    
    @property
    def item_type(self) -> str:
        """Get the type name of the item."""
        return type(self.item).__name__
    
    def to_dict(self) -> CargoResult[Dict[str, Any]]:
        """
        Serialize to dictionary.
        
        Returns:
            Result[Dict[str, Any], CargoErrorDetails]: Serialized data or error
        """
        try:
            item_data_result = self._item_to_dict()
            if item_data_result.is_err():
                return item_data_result
            
            return Result.ok({
                "item_type": self.item_type,
                "item_data": item_data_result.unwrap(),
                "quantity": self.quantity,
                "buy_price": self.buy_price,
                "sell_price": self.sell_price
            })
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.SERIALIZATION_ERROR,
                f"Failed to serialize CargoItem: {str(e)}",
                {"item_type": self.item_type, "item_id": self.item_id}
            ))
    
    def _item_to_dict(self) -> CargoResult[Dict[str, Any]]:
        """
        Convert item to dict for serialization.
        
        Returns:
            Result[Dict[str, Any], CargoErrorDetails]: Item data or error
        """
        try:
            if hasattr(self.item, 'to_dict'):
                return Result.ok(self.item.to_dict())
            
            # Fallback for items without to_dict method
            base_dict: Dict[str, Any] = {
                "commodity_id": self.item.commodity.commodity_id,
            }
            
            if isinstance(self.item, Ore):
                base_dict["purity"] = self.item.purity.name if hasattr(self.item, "purity") else "RAW"
            elif isinstance(self.item, Mineral):
                base_dict["quality"] = self.item.quality.name if hasattr(self.item, "quality") else "STANDARD"
            elif isinstance(self.item, Component):
                base_dict["quality"] = self.item.quality.name if hasattr(self.item, "quality") else "STANDARD"
            elif isinstance(self.item, FinishedGood):
                base_dict["quality"] = self.item.quality.name if hasattr(self.item, "quality") else "STANDARD"
            
            return Result.ok(base_dict)
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.SERIALIZATION_ERROR,
                f"Failed to convert item to dict: {str(e)}",
                {"item_type": type(self.item).__name__}
            ))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CargoResult['CargoItem']:
        try:
            item_type = data.get("item_type")
            item_data = data.get("item_data")
            
            if not item_type or not item_data:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    "Missing required fields: item_type or item_data",
                    {"available_keys": list(data.keys())}
                ))
            
            # Create appropriate item based on type
            item_result = cls._create_item_from_dict(item_type, item_data)
            if item_result.is_err():
                return Result.err(item_result.unwrap_err())
            
            cargo_item = cls(
                item=item_result.unwrap(),
                quantity=data.get("quantity", 0),
                buy_price=data.get("buy_price", 0.0),
                sell_price=data.get("sell_price", 0.0)
            )
            
            # Validate the created item
            validation_result = cargo_item.validate()
            if validation_result.is_err():
                return Result.err(validation_result.unwrap_err())
            
            return Result.ok(cargo_item)
            
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.DESERIALIZATION_ERROR,
                f"Failed to deserialize CargoItem: {str(e)}",
                {"data_keys": list(data.keys()) if isinstance(data, dict) else None}
            ))
    
    @classmethod
    def _create_item_from_dict(cls, item_type: str, item_data: Dict[str, Any]) -> CargoResult[Union[Ore, Mineral, Component, FinishedGood]]:
        try:
            if item_type == "Ore":
                ore_result = cls._create_ore_from_dict(item_data)
                if ore_result.is_ok():
                    return Result.ok(ore_result.unwrap())
                else:
                    return Result.err(ore_result.unwrap_err())
            elif item_type == "Mineral":
                mineral_result = cls._create_mineral_from_dict(item_data)
                if mineral_result.is_ok():
                    return Result.ok(mineral_result.unwrap())
                else:
                    return Result.err(mineral_result.unwrap_err())
            elif item_type == "Component":
                component_result = cls._create_component_from_dict(item_data)
                if component_result.is_ok():
                    return Result.ok(component_result.unwrap())
                else:
                    return Result.err(component_result.unwrap_err())
            elif item_type == "FinishedGood":
                finished_good_result = cls._create_finished_good_from_dict(item_data)
                if finished_good_result.is_ok():
                    return Result.ok(finished_good_result.unwrap())
                else:
                    return Result.err(finished_good_result.unwrap_err())
            else:
                return Result.err(CargoErrorDetails(
                    CargoError.UNKNOWN_ITEM_TYPE,
                    f"Unknown item type: {item_type}",
                    {"item_type": item_type, "item_data": item_data}
                ))
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.DESERIALIZATION_ERROR,
                f"Failed to create item from dict: {str(e)}",
                {"item_type": item_type}
            ))
    
    @classmethod
    def _create_ore_from_dict(cls, data: Dict[str, Any]) -> CargoResult[Ore]:
        """
        Create an Ore from dictionary data.
        
        Args:
            data: Dictionary containing ore data
            
        Returns:
            Result[Ore, CargoErrorDetails]: Created ore or error
        """
        try:
            from src.classes.ore import ORES, PurityLevel
            
            ore_id = data.get("commodity_id")
            if not ore_id:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    "Missing commodity_id in ore data",
                    {"data": data}
                ))
            
            ore_template = ORES.get(ore_id)
            if ore_template is None:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    f"Ore with ID {ore_id} not found in ORES",
                    {"ore_id": ore_id, "available_ores": list(ORES.keys())}
                ))
            
            # Handle purity if present
            purity = PurityLevel.RAW
            if "purity" in data:
                try:
                    purity = PurityLevel[data["purity"]]
                except KeyError:
                    return Result.err(CargoErrorDetails(
                        CargoError.DESERIALIZATION_ERROR,
                        f"Invalid purity level: {data['purity']}",
                        {"purity": data["purity"], "valid_purities": [p.name for p in PurityLevel]}
                    ))
            
            # Create a copy with the correct purity
            ore = Ore(
                commodity=ore_template.commodity,
                mineral_yield=ore_template.mineral_yield.copy() if ore_template.mineral_yield else [],
                purity=purity,
                refining_difficulty=ore_template.refining_difficulty,
                extraction_difficulty=ore_template.extraction_difficulty,
                region_availability=ore_template.region_availability.copy() if ore_template.region_availability else {},
                production_stage=ore_template.production_stage,
                market_demand=ore_template.market_demand,
                market_supply=ore_template.market_supply,
                price_history=ore_template.price_history.copy() if ore_template.price_history else []
            )
            
            return Result.ok(ore)
            
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.DESERIALIZATION_ERROR,
                f"Failed to create ore from dict: {str(e)}",
                {"data": data}
            ))
    
    @classmethod
    def _create_mineral_from_dict(cls, data: Dict[str, Any]) -> CargoResult[Mineral]:
        """
        Create a Mineral from dictionary data.
        
        Args:
            data: Dictionary containing mineral data
            
        Returns:
            Result[Mineral, CargoErrorDetails]: Created mineral or error
        """
        try:
            from src.classes.mineral import MINERALS, MineralQuality
            
            mineral_id = data.get("commodity_id")
            if not mineral_id:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    "Missing commodity_id in mineral data",
                    {"data": data}
                ))
            
            mineral_template = MINERALS.get(mineral_id)
            if mineral_template is None:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    f"Mineral with ID {mineral_id} not found in MINERALS",
                    {"mineral_id": mineral_id, "available_minerals": list(MINERALS.keys())}
                ))
            
            # Handle quality if present
            quality = MineralQuality.STANDARD
            if "quality" in data:
                try:
                    quality = MineralQuality[data["quality"]]
                except KeyError:
                    return Result.err(CargoErrorDetails(
                        CargoError.DESERIALIZATION_ERROR,
                        f"Invalid quality level: {data['quality']}",
                        {"quality": data["quality"], "valid_qualities": [q.name for q in MineralQuality]}
                    ))
            
            # Create a copy with the correct quality
            mineral = Mineral(
                commodity=mineral_template.commodity,
                quality=quality,
                source_ores=mineral_template.source_ores.copy() if mineral_template.source_ores else [],
                material_category=mineral_template.material_category,
                processing_difficulty=mineral_template.processing_difficulty,
                purity=mineral_template.purity,
                production_stage=mineral_template.production_stage,
                market_demand=mineral_template.market_demand,
                market_supply=mineral_template.market_supply,
                price_history=mineral_template.price_history.copy() if mineral_template.price_history else []
            )
            
            return Result.ok(mineral)
            
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.DESERIALIZATION_ERROR,
                f"Failed to create mineral from dict: {str(e)}",
                {"data": data}
            ))
    
    @classmethod
    def _create_component_from_dict(cls, data: Dict[str, Any]) -> CargoResult[Component]:
        """
        Create a Component from dictionary data.
        
        Args:
            data: Dictionary containing component data
            
        Returns:
            Result[Component, CargoErrorDetails]: Created component or error
        """
        try:
            from src.classes.component import COMPONENTS, ComponentQuality
            
            component_id = data.get("commodity_id")
            if not component_id:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    "Missing commodity_id in component data",
                    {"data": data}
                ))
            
            # Find component by commodity_id
            component_template = None
            for comp in COMPONENTS.values():
                if comp.commodity.commodity_id == component_id:
                    component_template = comp
                    break
                    
            if component_template is None:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    f"Component with commodity ID {component_id} not found in COMPONENTS",
                    {"component_id": component_id}
                ))
            
            # Handle quality if present
            quality = ComponentQuality.STANDARD
            if "quality" in data:
                try:
                    quality = ComponentQuality[data["quality"]]
                except KeyError:
                    return Result.err(CargoErrorDetails(
                        CargoError.DESERIALIZATION_ERROR,
                        f"Invalid quality level: {data['quality']}",
                        {"quality": data["quality"], "valid_qualities": [q.name for q in ComponentQuality]}
                    ))
            
            # Create a copy with the correct quality
            component = Component(
                commodity=component_template.commodity,
                quality=quality,
                component_type=component_template.component_type,
                manufacturing_complexity=component_template.manufacturing_complexity,
                required_minerals=component_template.required_minerals.copy() if component_template.required_minerals else {},
                tech_level=component_template.tech_level,
                production_stage=component_template.production_stage,
                durability=component_template.durability,
                efficiency=component_template.efficiency,
                compatible_ship_classes=component_template.compatible_ship_classes.copy() if component_template.compatible_ship_classes else [],
                power_requirement=component_template.power_requirement,
                market_demand=component_template.market_demand,
                market_supply=component_template.market_supply,
                price_history=component_template.price_history.copy() if component_template.price_history else []
            )
            
            return Result.ok(component)
            
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.DESERIALIZATION_ERROR,
                f"Failed to create component from dict: {str(e)}",
                {"data": data}
            ))
    
    @classmethod
    def _create_finished_good_from_dict(cls, data: Dict[str, Any]) -> CargoResult[FinishedGood]:
        """
        Create a FinishedGood from dictionary data.
        
        Args:
            data: Dictionary containing finished good data
            
        Returns:
            Result[FinishedGood, CargoErrorDetails]: Created finished good or error
        """
        try:
            from src.classes.finished_good import FINISHED_GOODS, FinishedGoodQuality
            
            good_id = data.get("commodity_id")
            if not good_id:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    "Missing commodity_id in finished good data",
                    {"data": data}
                ))
            
            # Find finished good by commodity_id
            good_template = None
            for good in FINISHED_GOODS.values():
                if good.commodity.commodity_id == good_id:
                    good_template = good
                    break
                    
            if good_template is None:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    f"FinishedGood with commodity ID {good_id} not found in FINISHED_GOODS",
                    {"good_id": good_id}
                ))
            
            # Handle quality if present
            quality = FinishedGoodQuality.STANDARD
            if "quality" in data:
                try:
                    quality = FinishedGoodQuality[data["quality"]]
                except KeyError:
                    return Result.err(CargoErrorDetails(
                        CargoError.DESERIALIZATION_ERROR,
                        f"Invalid quality level: {data['quality']}",
                        {"quality": data["quality"], "valid_qualities": [q.name for q in FinishedGoodQuality]}
                    ))
            
            # Create a copy with the correct quality
            finished_good = FinishedGood(
                commodity=good_template.commodity,
                quality=quality,
                good_type=good_template.good_type,
                assembly_complexity=good_template.assembly_complexity,
                required_components=good_template.required_components.copy() if good_template.required_components else {},
                tech_level=good_template.tech_level,
                durability=good_template.durability,
                efficiency=good_template.efficiency,
                performance_rating=good_template.performance_rating,
                maintenance_interval=good_template.maintenance_interval,
                maintenance_cost=good_template.maintenance_cost,
                compatible_ship_classes=good_template.compatible_ship_classes.copy() if good_template.compatible_ship_classes else [],
                power_requirement=good_template.power_requirement,
                special_effects=good_template.special_effects.copy() if good_template.special_effects else {},
                production_stage=good_template.production_stage,
                market_demand=good_template.market_demand,
                market_supply=good_template.market_supply,
                price_history=good_template.price_history.copy() if good_template.price_history else []
            )
            
            return Result.ok(finished_good)
            
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.DESERIALIZATION_ERROR,
                f"Failed to create finished good from dict: {str(e)}",
                {"data": data}
            ))


class CargoHold:
    """
    Unified cargo management system for ships.
    
    This class manages all types of cargo items in a single container,
    replacing the separate cargohold and mineralhold lists.
    """
    
    def __init__(self, capacity: float):
        """
        Initialize a new cargo hold.
        
        Args:
            capacity: Maximum cargo capacity in cubic meters
        """
        if capacity < 0:
            raise ValueError("Capacity cannot be negative")
        
        self.capacity = capacity
        self._items: Dict[str, CargoItem] = {}
    
    def _generate_item_key(self, item: Union[Ore, Mineral, Component, FinishedGood]) -> str:
        """
        Generate unique key for item including type-specific attributes.
        
        This ensures that items with different qualities/purities are stored separately.
        """
        base_id = str(item.commodity.commodity_id)
        item_type = type(item).__name__.lower()
        
        if isinstance(item, Ore) and hasattr(item, 'purity'):
            return f"{item_type}_{base_id}_{item.purity.name}"
        elif isinstance(item, Mineral) and hasattr(item, 'quality'):
            return f"{item_type}_{base_id}_{item.quality.name}"
        elif isinstance(item, Component) and hasattr(item, 'quality'):
            return f"{item_type}_{base_id}_{item.quality.name}"
        elif isinstance(item, FinishedGood) and hasattr(item, 'quality'):
            return f"{item_type}_{base_id}_{item.quality.name}"
        else:
            return f"{item_type}_{base_id}"
    
    def add_item(self, item: Union[Ore, Mineral, Component, FinishedGood], 
                 quantity: int, buy_price: float = 0.0, sell_price: float = 0.0) -> VoidResult:
        """
        Add items to cargo hold.
        
        Args:
            item: The item to add
            quantity: Number of items to add
            buy_price: Price paid for the items
            sell_price: Expected selling price
            
        Returns:
            Result[None, CargoErrorDetails]: Success or error details
        """
        if quantity <= 0:
            return Result.err(CargoErrorDetails(
                CargoError.INVALID_QUANTITY,
                f"Quantity must be positive: {quantity}",
                {"quantity": quantity}
            ))
        
        if not self.can_fit(item, quantity):
            required_space = quantity * item.commodity.volume_per_unit
            available_space = self.get_remaining_space()
            return Result.err(CargoErrorDetails(
                CargoError.INSUFFICIENT_SPACE,
                f"Not enough space: required {required_space}, available {available_space}",
                {
                    "required_space": required_space,
                    "available_space": available_space,
                    "item_name": item.commodity.name,
                    "quantity": quantity
                }
            ))
        
        try:
            item_key = self._generate_item_key(item)
            
            if item_key in self._items:
                # Add to existing stack
                self._items[item_key].quantity += quantity
                # Update prices if provided
                if buy_price > 0:
                    self._items[item_key].buy_price = buy_price
                if sell_price > 0:
                    self._items[item_key].sell_price = sell_price
            else:
                # Create new stack
                cargo_item = CargoItem(item, quantity, buy_price, sell_price)
                validation_result = cargo_item.validate()
                if validation_result.is_err():
                    return Result.err(validation_result.unwrap_err())
                self._items[item_key] = cargo_item
            
            return Result.ok(None)
            
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.SERIALIZATION_ERROR,
                f"Failed to add item to cargo: {str(e)}",
                {"item_name": getattr(item, 'name', 'unknown')}
            ))
    
    def remove_item(self, item_id: str, quantity: int) -> CargoResult[CargoItem]:
        """
        Remove items from cargo hold.
        
        Args:
            item_id: ID of the item to remove
            quantity: Number of items to remove
            
        Returns:
            Result[CargoItem, CargoErrorDetails]: Removed items or error details
        """
        if quantity <= 0:
            return Result.err(CargoErrorDetails(
                CargoError.INVALID_QUANTITY,
                f"Quantity must be positive: {quantity}",
                {"quantity": quantity}
            ))
        
        # Find item by ID (may need to search through keys)
        item_key_result = self._find_item_key(item_id)
        if item_key_result.is_err():
            return Result.err(item_key_result.unwrap_err())
        
        item_key = item_key_result.unwrap()
        if item_key not in self._items:
            return Result.err(CargoErrorDetails(
                CargoError.ITEM_NOT_FOUND,
                f"Item not found in cargo: {item_id}",
                {"item_id": item_id}
            ))
        
        cargo_item = self._items[item_key]
        if cargo_item.quantity < quantity:
            return Result.err(CargoErrorDetails(
                CargoError.INVALID_QUANTITY,
                f"Not enough items: requested {quantity}, available {cargo_item.quantity}",
                {
                    "requested": quantity,
                    "available": cargo_item.quantity,
                    "item_id": item_id
                }
            ))
        
        try:
            # Create return item
            removed_item = CargoItem(
                cargo_item.item,
                quantity,
                cargo_item.buy_price,
                cargo_item.sell_price
            )
            
            # Update or remove from cargo
            cargo_item.quantity -= quantity
            if cargo_item.quantity <= 0:
                del self._items[item_key]
            
            return Result.ok(removed_item)
            
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.SERIALIZATION_ERROR,
                f"Failed to remove item from cargo: {str(e)}",
                {"item_id": item_id}
            ))
    
    def get_item(self, item_id: str) -> CargoResult[CargoItem]:
        """
        Get cargo item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            Result[CargoItem, CargoErrorDetails]: Found item or error details
        """
        item_key_result = self._find_item_key(item_id)
        if item_key_result.is_err():
            return Result.err(item_key_result.unwrap_err())
        
        item_key = item_key_result.unwrap()
        if item_key in self._items:
            return Result.ok(self._items[item_key])
        
        return Result.err(CargoErrorDetails(
            CargoError.ITEM_NOT_FOUND,
            f"Item not found in cargo: {item_id}",
            {"item_id": item_id}
        ))
    
    def get_all_items(self) -> List[CargoItem]:
        """Get all cargo items."""
        return list(self._items.values())
    
    def get_items_by_type(self, item_type: type) -> List[CargoItem]:
        """Get all items of a specific type (Ore, Mineral, etc.)."""
        return [
            cargo_item for cargo_item in self._items.values()
            if isinstance(cargo_item.item, item_type)
        ]
    
    def get_occupied_space(self) -> float:
        """Get total space occupied by all cargo."""
        return sum(cargo_item.total_volume for cargo_item in self._items.values())
    
    def get_remaining_space(self) -> float:
        """Get remaining cargo space."""
        return max(0.0, self.capacity - self.get_occupied_space())
    
    def is_full(self) -> bool:
        """Check if cargo hold is full."""
        return self.get_occupied_space() >= self.capacity
    
    def can_fit(self, item: Union[Ore, Mineral, Component, FinishedGood], 
                quantity: int) -> bool:
        """Check if items can fit in remaining space."""
        if quantity <= 0:
            return False
        
        required_volume = quantity * item.commodity.volume_per_unit
        return required_volume <= self.get_remaining_space()
    
    def _find_item_key(self, item_id: str) -> CargoResult[str]:
        """
        Find item key by item ID.
        
        Args:
            item_id: ID of the item to find
            
        Returns:
            Result[str, CargoErrorDetails]: Item key or error details
        """
        try:
            for key, cargo_item in self._items.items():
                if cargo_item.item_id == item_id:
                    return Result.ok(key)
            
            return Result.err(CargoErrorDetails(
                CargoError.ITEM_NOT_FOUND,
                f"Item not found: {item_id}",
                {"item_id": item_id, "available_items": list(self._items.keys())}
            ))
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.SERIALIZATION_ERROR,
                f"Error searching for item: {str(e)}",
                {"item_id": item_id}
            ))
    
    def to_dict(self) -> CargoResult[Dict[str, Any]]:
        """
        Serialize cargo hold to dictionary.
        
        Returns:
            Result[Dict[str, Any], CargoErrorDetails]: Serialized data or error
        """
        try:
            items_dict = {}
            for key, item in self._items.items():
                item_dict_result = item.to_dict()
                if item_dict_result.is_err():
                    return Result.err(item_dict_result.unwrap_err())
                items_dict[key] = item_dict_result.unwrap()
            
            return Result.ok({
                "capacity": self.capacity,
                "items": items_dict
            })
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.SERIALIZATION_ERROR,
                f"Failed to serialize cargo hold: {str(e)}",
                {"capacity": self.capacity, "item_count": len(self._items)}
            ))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CargoResult['CargoHold']:
        """
        Deserialize cargo hold from dictionary.
        
        Args:
            data: Dictionary containing serialized cargo hold data
            
        Returns:
            Result[CargoHold, CargoErrorDetails]: Deserialized cargo hold or error
        """
        try:
            capacity = data.get("capacity")
            if capacity is None:
                return Result.err(CargoErrorDetails(
                    CargoError.DESERIALIZATION_ERROR,
                    "Missing capacity in cargo hold data",
                    {"data_keys": list(data.keys())}
                ))
            
            cargo_hold = cls(capacity)
            
            items_data = data.get("items", {})
            for key, item_data in items_data.items():
                cargo_item_result = CargoItem.from_dict(item_data)
                if cargo_item_result.is_err():
                    return Result.err(cargo_item_result.unwrap_err())
                cargo_hold._items[key] = cargo_item_result.unwrap()
            
            return Result.ok(cargo_hold)
            
        except Exception as e:
            return Result.err(CargoErrorDetails(
                CargoError.DESERIALIZATION_ERROR,
                f"Failed to deserialize cargo hold: {str(e)}",
                {"data_keys": list(data.keys()) if isinstance(data, dict) else None}
            ))
    
