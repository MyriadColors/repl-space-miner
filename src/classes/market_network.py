"""
Market network system for connecting markets and price propagation.

This module implements the MarketNetwork class that manages connections between
station markets and handles price effect propagation based on trade routes.
"""

import time
import random
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum, auto

from src.classes.market_data import StationMarket
from src.classes.market_simulator import MarketSimulator


class MarketEventType(Enum):
    """Types of market events that can propagate through the network."""
    PRICE_SHOCK = auto()
    SUPPLY_DISRUPTION = auto()
    DEMAND_SURGE = auto()
    TRADE_ROUTE_DISRUPTION = auto()
    ECONOMIC_BOOM = auto()
    MARKET_CRASH = auto()


@dataclass
class MarketConnection:
    """
    Represents a connection between two markets.
    
    Defines the strength and characteristics of trade relationships
    that affect price propagation between markets.
    """
    from_market: str
    to_market: str
    connection_strength: float  # 0.0 to 1.0, affects propagation speed
    distance: float  # Distance in AU, affects propagation delay
    trade_volume: float  # Average trade volume, affects propagation magnitude
    connection_type: str  # "trade_route", "corporate", "military", etc.
    is_active: bool = True
    last_propagation: float = 0.0
    
    def get_propagation_delay(self) -> float:
        """
        Calculate propagation delay based on distance and connection type.
        
        Returns:
            Delay in seconds for price effects to propagate
        """
        base_delay = self.distance * 3600  # 1 hour per AU base delay
        
        # Connection type modifiers
        type_modifiers = {
            "hyperspace_relay": 0.1,  # Very fast communication
            "corporate": 0.3,  # Fast corporate networks
            "military": 0.4,  # Military communication networks
            "trade_route": 0.6,  # Standard trade routes
            "smuggling": 0.8,  # Slower, unofficial routes
            "independent": 1.0,  # Standard speed
        }
        
        modifier = type_modifiers.get(self.connection_type, 1.0)
        return base_delay * modifier
    
    def get_propagation_strength(self) -> float:
        """
        Calculate how strongly price effects propagate through this connection.
        
        Returns:
            Strength factor (0.0 to 1.0) for price propagation
        """
        if not self.is_active:
            return 0.0
        
        # Base strength from connection strength and trade volume
        base_strength = self.connection_strength * min(1.0, self.trade_volume / 100.0)
        
        # Distance decay - closer markets have stronger effects
        distance_factor = 1.0 / (1.0 + self.distance / 50.0)
        
        return base_strength * distance_factor


@dataclass
class MarketEvent:
    """
    Represents a market event that can propagate through the network.
    """
    event_id: str
    event_type: MarketEventType
    origin_market: str
    affected_items: List[str]
    magnitude: float  # Strength of the event (0.0 to 1.0)
    created_time: float
    duration: float  # How long the event lasts in seconds
    propagated_to: Set[str]  # Markets this event has already reached
    
    def is_expired(self) -> bool:
        """Check if the event has expired."""
        return time.time() > (self.created_time + self.duration)
    
    def get_current_strength(self) -> float:
        """Get the current strength of the event (decays over time)."""
        if self.is_expired():
            return 0.0
        
        elapsed = time.time() - self.created_time
        decay_factor = 1.0 - (elapsed / self.duration)
        return self.magnitude * decay_factor


class MarketNetwork:
    """
    Manages connections between station markets and handles price propagation.
    
    Creates a network of interconnected markets where price changes and events
    can propagate based on trade routes and communication networks.
    """
    
    def __init__(self):
        """Initialize the market network."""
        self.markets: Dict[str, StationMarket] = {}
        self.simulators: Dict[str, MarketSimulator] = {}
        self.connections: List[MarketConnection] = []
        self.active_events: List[MarketEvent] = []
        self.event_counter = 0
        self.last_network_update = time.time()
        
        # Network parameters
        self.propagation_damping = 0.8  # How much effects weaken as they propagate
        self.min_propagation_strength = 0.01  # Minimum strength to continue propagation
        self.max_propagation_hops = 5  # Maximum hops for event propagation
    
    def add_market(self, market: StationMarket) -> None:
        """
        Add a market to the network.
        
        Args:
            market: StationMarket to add to the network
        """
        self.markets[market.station_id] = market
        self.simulators[market.station_id] = MarketSimulator(market)
    
    def remove_market(self, station_id: str) -> None:
        """
        Remove a market from the network.
        
        Args:
            station_id: ID of the station market to remove
        """
        if station_id in self.markets:
            del self.markets[station_id]
            del self.simulators[station_id]
        
        # Remove connections involving this market
        self.connections = [
            conn for conn in self.connections
            if conn.from_market != station_id and conn.to_market != station_id
        ]
    
    def add_connection(
        self,
        from_market: str,
        to_market: str,
        connection_strength: float,
        distance: float,
        trade_volume: float = 50.0,
        connection_type: str = "trade_route",
    ) -> None:
        """
        Add a connection between two markets.
        
        Args:
            from_market: Source market station ID
            to_market: Destination market station ID
            connection_strength: Strength of connection (0.0 to 1.0)
            distance: Distance between markets in AU
            trade_volume: Average trade volume
            connection_type: Type of connection
        """
        # Check if markets exist
        if from_market not in self.markets or to_market not in self.markets:
            return
        
        # Check if connection already exists
        existing = self.get_connection(from_market, to_market)
        if existing:
            # Update existing connection
            existing.connection_strength = connection_strength
            existing.distance = distance
            existing.trade_volume = trade_volume
            existing.connection_type = connection_type
        else:
            # Create new connection
            connection = MarketConnection(
                from_market=from_market,
                to_market=to_market,
                connection_strength=connection_strength,
                distance=distance,
                trade_volume=trade_volume,
                connection_type=connection_type,
            )
            self.connections.append(connection)
        
        # Update market connection lists
        self.markets[from_market].add_connected_market(to_market)
        self.markets[to_market].add_connected_market(from_market)
    
    def get_connection(self, from_market: str, to_market: str) -> Optional[MarketConnection]:
        """
        Get connection between two markets.
        
        Args:
            from_market: Source market station ID
            to_market: Destination market station ID
            
        Returns:
            MarketConnection if found, None otherwise
        """
        for connection in self.connections:
            if (connection.from_market == from_market and connection.to_market == to_market) or \
               (connection.from_market == to_market and connection.to_market == from_market):
                return connection
        return None
    
    def update_network(self, time_elapsed: float) -> None:
        """
        Update the entire market network.
        
        Args:
            time_elapsed: Time elapsed since last update in seconds
        """
        current_time = time.time()
        
        # Update individual market simulators
        for simulator in self.simulators.values():
            simulator.update_prices(time_elapsed)
        
        # Process event propagation
        self._process_event_propagation()
        
        # Clean up expired events
        self._cleanup_expired_events()
        
        # Randomly generate new market events
        self._generate_random_events()
        
        self.last_network_update = current_time
    
    def create_market_event(
        self,
        event_type: MarketEventType,
        origin_market: str,
        affected_items: List[str],
        magnitude: float,
        duration: float = 86400.0,  # 24 hours default
    ) -> str:
        """
        Create a new market event.
        
        Args:
            event_type: Type of market event
            origin_market: Market where the event originates
            affected_items: List of item IDs affected by the event
            magnitude: Strength of the event (0.0 to 1.0)
            duration: How long the event lasts in seconds
            
        Returns:
            Event ID for tracking
        """
        self.event_counter += 1
        event_id = f"event_{self.event_counter}_{int(time.time())}"
        
        event = MarketEvent(
            event_id=event_id,
            event_type=event_type,
            origin_market=origin_market,
            affected_items=affected_items,
            magnitude=magnitude,
            created_time=time.time(),
            duration=duration,
            propagated_to={origin_market},
        )
        
        self.active_events.append(event)
        
        # Apply immediate effects to origin market
        self._apply_event_to_market(event, origin_market, magnitude)
        
        return event_id
    
    def _process_event_propagation(self) -> None:
        """Process propagation of active events through the network."""
        for event in self.active_events:
            if event.is_expired():
                continue
            
            current_strength = event.get_current_strength()
            if current_strength < self.min_propagation_strength:
                continue
            
            # Find markets to propagate to
            markets_to_propagate = []
            
            for propagated_market in event.propagated_to.copy():
                for connection in self.connections:
                    target_market = None
                    
                    if connection.from_market == propagated_market:
                        target_market = connection.to_market
                    elif connection.to_market == propagated_market:
                        target_market = connection.from_market
                    
                    if (target_market and 
                        target_market not in event.propagated_to and
                        connection.is_active):
                        
                        # Check if enough time has passed for propagation
                        delay = connection.get_propagation_delay()
                        if time.time() >= (event.created_time + delay):
                            propagation_strength = connection.get_propagation_strength()
                            effective_strength = current_strength * propagation_strength * self.propagation_damping
                            
                            if effective_strength >= self.min_propagation_strength:
                                markets_to_propagate.append((target_market, effective_strength))
            
            # Apply propagation effects
            for target_market, strength in markets_to_propagate:
                if len(event.propagated_to) < self.max_propagation_hops:
                    self._apply_event_to_market(event, target_market, strength)
                    event.propagated_to.add(target_market)
    
    def _apply_event_to_market(self, event: MarketEvent, market_id: str, strength: float) -> None:
        """
        Apply event effects to a specific market.
        
        Args:
            event: MarketEvent to apply
            market_id: ID of the market to affect
            strength: Strength of the effect to apply
        """
        market = self.markets.get(market_id)
        if not market:
            return
        
        for item_id in event.affected_items:
            market_data = market.get_market_data(item_id)
            if not market_data:
                continue
            
            # Apply effects based on event type
            if event.event_type == MarketEventType.PRICE_SHOCK:
                # Sudden price change
                price_change = random.uniform(-0.2, 0.2) * strength
                new_price = market_data.current_price * (1 + price_change)
                market_data.update_price(new_price)
                
            elif event.event_type == MarketEventType.SUPPLY_DISRUPTION:
                # Reduce supply, increase price
                supply_change = -0.3 * strength
                demand_change = 0.1 * strength
                market.update_supply_demand(item_id, supply_change, demand_change)
                
                price_increase = 1.0 + (0.2 * strength)
                new_price = market_data.current_price * price_increase
                market_data.update_price(new_price)
                
            elif event.event_type == MarketEventType.DEMAND_SURGE:
                # Increase demand, increase price
                supply_change = -0.1 * strength
                demand_change = 0.3 * strength
                market.update_supply_demand(item_id, supply_change, demand_change)
                
                price_increase = 1.0 + (0.15 * strength)
                new_price = market_data.current_price * price_increase
                market_data.update_price(new_price)
                
            elif event.event_type == MarketEventType.ECONOMIC_BOOM:
                # General positive effects
                supply_change = 0.1 * strength
                demand_change = 0.2 * strength
                market.update_supply_demand(item_id, supply_change, demand_change)
                
                price_increase = 1.0 + (0.1 * strength)
                new_price = market_data.current_price * price_increase
                market_data.update_price(new_price)
                
            elif event.event_type == MarketEventType.MARKET_CRASH:
                # General negative effects
                supply_change = 0.2 * strength
                demand_change = -0.3 * strength
                market.update_supply_demand(item_id, supply_change, demand_change)
                
                price_decrease = 1.0 - (0.25 * strength)
                new_price = market_data.current_price * price_decrease
                market_data.update_price(new_price)
    
    def _cleanup_expired_events(self) -> None:
        """Remove expired events from the active list."""
        self.active_events = [event for event in self.active_events if not event.is_expired()]
    
    def _generate_random_events(self) -> None:
        """Randomly generate new market events."""
        if not self.markets:
            return
        
        # Low chance of generating a random event
        if random.random() < 0.001:  # 0.1% chance per update
            event_types = list(MarketEventType)
            event_type = random.choice(event_types)
            
            origin_market = random.choice(list(self.markets.keys()))
            market = self.markets[origin_market]
            
            if market.market_items:
                # Select 1-3 random items to affect
                num_items = min(3, len(market.market_items))
                affected_items = random.sample(list(market.market_items.keys()), num_items)
                
                magnitude = random.uniform(0.1, 0.8)
                duration = random.uniform(3600, 86400)  # 1-24 hours
                
                self.create_market_event(
                    event_type, origin_market, affected_items, magnitude, duration
                )
    
    def get_market_path(self, from_market: str, to_market: str) -> Optional[List[str]]:
        """
        Find the shortest path between two markets.
        
        Args:
            from_market: Source market station ID
            to_market: Destination market station ID
            
        Returns:
            List of market IDs representing the path, or None if no path exists
        """
        if from_market == to_market:
            return [from_market]
        
        # Use breadth-first search to find shortest path
        queue = [(from_market, [from_market])]
        visited = {from_market}
        
        while queue:
            current_market, path = queue.pop(0)
            
            # Check all connections from current market
            for connection in self.connections:
                next_market = None
                
                if connection.from_market == current_market and connection.is_active:
                    next_market = connection.to_market
                elif connection.to_market == current_market and connection.is_active:
                    next_market = connection.from_market
                
                if next_market and next_market not in visited:
                    new_path = path + [next_market]
                    
                    if next_market == to_market:
                        return new_path
                    
                    queue.append((next_market, new_path))
                    visited.add(next_market)
        
        return None  # No path found
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the market network.
        
        Returns:
            Dictionary with network statistics
        """
        total_markets = len(self.markets)
        total_connections = len([conn for conn in self.connections if conn.is_active])
        active_events = len(self.active_events)
        
        # Calculate average connection strength
        if self.connections:
            avg_connection_strength = sum(
                conn.connection_strength for conn in self.connections if conn.is_active
            ) / max(1, total_connections)
        else:
            avg_connection_strength = 0.0
        
        # Calculate network connectivity (what percentage of market pairs are connected)
        if total_markets > 1:
            possible_connections = total_markets * (total_markets - 1) // 2
            connectivity = total_connections / possible_connections
        else:
            connectivity = 0.0
        
        return {
            "total_markets": total_markets,
            "total_connections": total_connections,
            "active_events": active_events,
            "average_connection_strength": avg_connection_strength,
            "network_connectivity": connectivity,
            "last_update": self.last_network_update,
        }
    
    def get_market_influence(self, market_id: str) -> Dict[str, Any]:
        """
        Get influence metrics for a specific market.
        
        Args:
            market_id: ID of the market to analyze
            
        Returns:
            Dictionary with influence metrics
        """
        if market_id not in self.markets:
            return {}
        
        # Count direct connections
        direct_connections = sum(
            1 for conn in self.connections
            if (conn.from_market == market_id or conn.to_market == market_id) and conn.is_active
        )
        
        # Calculate total connection strength
        total_strength = sum(
            conn.connection_strength for conn in self.connections
            if (conn.from_market == market_id or conn.to_market == market_id) and conn.is_active
        )
        
        # Count reachable markets
        reachable_markets = set()
        for other_market in self.markets:
            if other_market != market_id:
                path = self.get_market_path(market_id, other_market)
                if path:
                    reachable_markets.add(other_market)
        
        # Count events originated from this market
        originated_events = sum(
            1 for event in self.active_events if event.origin_market == market_id
        )
        
        return {
            "market_id": market_id,
            "direct_connections": direct_connections,
            "total_connection_strength": total_strength,
            "reachable_markets": len(reachable_markets),
            "originated_events": originated_events,
            "influence_score": direct_connections * total_strength + len(reachable_markets) * 0.1,
        }