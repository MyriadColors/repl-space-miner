"""
Market data models for the expanded economy system.

This module implements the MarketData and StationMarket classes that provide
price history tracking, trend analysis, and market management functionality.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


@dataclass
class MarketData:
    """
    Market data for a specific item at a station.
    
    Tracks pricing information, supply/demand levels, price trends,
    and transaction history for market analysis.
    """
    item_id: str
    base_price: float
    current_price: float
    supply_level: float = 0.5  # 0.0 (none) to 1.0 (abundant)
    demand_level: float = 0.5  # 0.0 (none) to 1.0 (high demand)
    price_trend: float = 0.0  # Negative for falling, positive for rising
    price_history: List[Tuple[float, float]] = field(default_factory=list)  # (timestamp, price) pairs
    transaction_volume: float = 0.0  # Recent transaction volume
    last_update: float = field(default_factory=time.time)
    
    def update_price(self, new_price: float) -> None:
        """
        Update the current price and add to price history.
        
        Args:
            new_price: The new price for this item
        """
        current_time = time.time()
        
        # Calculate price trend
        if self.current_price > 0:
            self.price_trend = (new_price - self.current_price) / self.current_price
        
        # Add to price history
        self.price_history.append((current_time, new_price))
        
        # Keep only recent history (last 100 entries)
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
        
        # Update current price and timestamp
        self.current_price = new_price
        self.last_update = current_time
    
    def get_price_trend_description(self) -> str:
        """
        Get a human-readable description of the price trend.
        
        Returns:
            String description of the price trend
        """
        if abs(self.price_trend) < 0.01:
            return "Stable"
        elif self.price_trend > 0.05:
            return "Rising Rapidly"
        elif self.price_trend > 0.01:
            return "Rising"
        elif self.price_trend < -0.05:
            return "Falling Rapidly"
        elif self.price_trend < -0.01:
            return "Falling"
        else:
            return "Stable"
    
    def get_supply_demand_status(self) -> str:
        """
        Get a description of supply and demand balance.
        
        Returns:
            String description of market conditions
        """
        if self.supply_level > 0.8:
            supply_desc = "Oversupplied"
        elif self.supply_level > 0.6:
            supply_desc = "Well Supplied"
        elif self.supply_level > 0.4:
            supply_desc = "Adequate Supply"
        elif self.supply_level > 0.2:
            supply_desc = "Low Supply"
        else:
            supply_desc = "Critical Shortage"
        
        if self.demand_level > 0.8:
            demand_desc = "High Demand"
        elif self.demand_level > 0.6:
            demand_desc = "Good Demand"
        elif self.demand_level > 0.4:
            demand_desc = "Moderate Demand"
        elif self.demand_level > 0.2:
            demand_desc = "Low Demand"
        else:
            demand_desc = "No Demand"
        
        return f"{supply_desc}, {demand_desc}"
    
    def calculate_price_volatility(self) -> float:
        """
        Calculate price volatility based on recent price history.
        
        Returns:
            Volatility measure (0.0 = stable, higher = more volatile)
        """
        if len(self.price_history) < 2:
            return 0.0
        
        # Calculate standard deviation of recent price changes
        recent_prices = [price for _, price in self.price_history[-20:]]
        if len(recent_prices) < 2:
            return 0.0
        
        mean_price = sum(recent_prices) / len(recent_prices)
        variance = sum((price - mean_price) ** 2 for price in recent_prices) / len(recent_prices)
        volatility = (variance ** 0.5) / mean_price if mean_price > 0 else 0.0
        
        return volatility
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "item_id": self.item_id,
            "base_price": self.base_price,
            "current_price": self.current_price,
            "supply_level": self.supply_level,
            "demand_level": self.demand_level,
            "price_trend": self.price_trend,
            "price_history": self.price_history,
            "transaction_volume": self.transaction_volume,
            "last_update": self.last_update,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketData":
        """Create from dictionary for deserialization."""
        return cls(
            item_id=data["item_id"],
            base_price=data["base_price"],
            current_price=data["current_price"],
            supply_level=data.get("supply_level", 0.5),
            demand_level=data.get("demand_level", 0.5),
            price_trend=data.get("price_trend", 0.0),
            price_history=data.get("price_history", []),
            transaction_volume=data.get("transaction_volume", 0.0),
            last_update=data.get("last_update", time.time()),
        )


class StationMarket:
    """
    Market at a specific station.
    
    Manages market items, pricing, and provides market analysis functionality.
    Handles price queries and market data for all items available at the station.
    """
    
    def __init__(
        self,
        station_id: str,
        specialization: str = "General",
        price_volatility: float = 0.1,
        market_size: float = 1.0,
    ):
        """
        Initialize a station market.
        
        Args:
            station_id: Unique identifier for the station
            specialization: Economic specialization of the station
            price_volatility: How quickly prices change (0.0-1.0)
            market_size: Size factor affecting transaction impact (0.1-10.0)
        """
        self.station_id = station_id
        self.specialization = specialization
        self.market_items: Dict[str, MarketData] = {}
        self.price_volatility = max(0.0, min(1.0, price_volatility))
        self.market_size = max(0.1, min(10.0, market_size))
        self.connected_markets: List[str] = []
        self.last_market_update = time.time()
    
    def add_market_item(self, item_id: str, base_price: float, current_price: Optional[float] = None) -> None:
        """
        Add an item to the market.
        
        Args:
            item_id: Unique identifier for the item
            base_price: Base price for the item
            current_price: Current market price (defaults to base_price)
        """
        if current_price is None:
            current_price = base_price
        
        self.market_items[item_id] = MarketData(
            item_id=item_id,
            base_price=base_price,
            current_price=current_price,
        )
    
    def get_market_data(self, item_id: str) -> Optional[MarketData]:
        """
        Get market data for a specific item.
        
        Args:
            item_id: Identifier for the item
            
        Returns:
            MarketData object or None if item not found
        """
        return self.market_items.get(item_id)
    
    def get_current_price(self, item_id: str) -> Optional[float]:
        """
        Get the current price for an item.
        
        Args:
            item_id: Identifier for the item
            
        Returns:
            Current price or None if item not found
        """
        market_data = self.market_items.get(item_id)
        return market_data.current_price if market_data else None
    
    def get_price_data(self, item_id: str) -> Dict[str, Any]:
        """
        Get detailed price information for an item.
        
        Args:
            item_id: Identifier for the item
            
        Returns:
            Dictionary with price, trend, supply/demand status
        """
        market_data = self.market_items.get(item_id)
        if not market_data:
            return {}
        
        return {
            "item_id": item_id,
            "current_price": market_data.current_price,
            "base_price": market_data.base_price,
            "price_trend": market_data.get_price_trend_description(),
            "supply_demand": market_data.get_supply_demand_status(),
            "volatility": market_data.calculate_price_volatility(),
            "last_update": market_data.last_update,
        }
    
    def get_all_market_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get price data for all items in the market.
        
        Returns:
            Dictionary mapping item IDs to their price data
        """
        return {item_id: self.get_price_data(item_id) for item_id in self.market_items.keys()}
    
    def update_supply_demand(self, item_id: str, supply_change: float, demand_change: float) -> None:
        """
        Update supply and demand levels for an item.
        
        Args:
            item_id: Identifier for the item
            supply_change: Change in supply level (-1.0 to 1.0)
            demand_change: Change in demand level (-1.0 to 1.0)
        """
        market_data = self.market_items.get(item_id)
        if not market_data:
            return
        
        # Update supply and demand levels (clamped to 0.0-1.0)
        market_data.supply_level = max(0.0, min(1.0, market_data.supply_level + supply_change))
        market_data.demand_level = max(0.0, min(1.0, market_data.demand_level + demand_change))
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the entire market.
        
        Returns:
            Dictionary with market statistics and information
        """
        if not self.market_items:
            return {
                "station_id": self.station_id,
                "specialization": self.specialization,
                "total_items": 0,
                "average_volatility": 0.0,
                "market_trends": "No data",
            }
        
        total_volatility = sum(data.calculate_price_volatility() for data in self.market_items.values())
        avg_volatility = total_volatility / len(self.market_items)
        
        rising_count = sum(1 for data in self.market_items.values() if data.price_trend > 0.01)
        falling_count = sum(1 for data in self.market_items.values() if data.price_trend < -0.01)
        stable_count = len(self.market_items) - rising_count - falling_count
        
        if rising_count > falling_count:
            trend_desc = "Generally Rising"
        elif falling_count > rising_count:
            trend_desc = "Generally Falling"
        else:
            trend_desc = "Mixed Trends"
        
        return {
            "station_id": self.station_id,
            "specialization": self.specialization,
            "total_items": len(self.market_items),
            "average_volatility": avg_volatility,
            "market_trends": trend_desc,
            "rising_items": rising_count,
            "falling_items": falling_count,
            "stable_items": stable_count,
            "last_update": self.last_market_update,
        }
    
    def add_connected_market(self, market_id: str) -> None:
        """
        Add a connection to another market for price propagation.
        
        Args:
            market_id: Identifier for the connected market
        """
        if market_id not in self.connected_markets:
            self.connected_markets.append(market_id)
    
    def remove_connected_market(self, market_id: str) -> None:
        """
        Remove a connection to another market.
        
        Args:
            market_id: Identifier for the market to disconnect
        """
        if market_id in self.connected_markets:
            self.connected_markets.remove(market_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "station_id": self.station_id,
            "specialization": self.specialization,
            "market_items": {item_id: data.to_dict() for item_id, data in self.market_items.items()},
            "price_volatility": self.price_volatility,
            "market_size": self.market_size,
            "connected_markets": self.connected_markets,
            "last_market_update": self.last_market_update,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StationMarket":
        """Create from dictionary for deserialization."""
        market = cls(
            station_id=data["station_id"],
            specialization=data.get("specialization", "General"),
            price_volatility=data.get("price_volatility", 0.1),
            market_size=data.get("market_size", 1.0),
        )
        
        # Restore market items
        market_items_data = data.get("market_items", {})
        for item_id, item_data in market_items_data.items():
            market.market_items[item_id] = MarketData.from_dict(item_data)
        
        # Restore connections and timestamps
        market.connected_markets = data.get("connected_markets", [])
        market.last_market_update = data.get("last_market_update", time.time())
        
        return market