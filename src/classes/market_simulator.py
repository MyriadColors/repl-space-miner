"""
Market simulation engine for dynamic pricing.

This module implements the MarketSimulator class that handles price adjustments
based on supply and demand, transaction processing, and time-based market evolution.
"""

import time
import random
from typing import Dict, List, Tuple, Any
from src.classes.market_data import StationMarket


class MarketSimulator:
    """
    Simulates market dynamics for a station or region.
    
    Handles price adjustments based on transactions, supply/demand changes,
    and time-based market evolution to create realistic economic behavior.
    """
    
    def __init__(self, market: StationMarket):
        """
        Initialize the market simulator.
        
        Args:
            market: StationMarket instance to simulate
        """
        self.market = market
        self.base_decay_rate = 0.01  # How quickly prices return to base
        self.transaction_impact_factor = 0.1  # How much transactions affect prices
        self.time_evolution_factor = 0.005  # How much time affects prices
        self.volatility_damping = 0.95  # Reduces extreme price swings
        
        # NPC trading simulation parameters
        self.npc_trade_frequency = 0.1  # Chance of NPC trade per update
        self.npc_trade_volume_range = (1, 50)  # Range of NPC trade volumes
        
        # Market event parameters
        self.event_chance = 0.01  # Chance of market event per update
        self.last_simulation_time = time.time()
    
    def update_prices(self, time_elapsed: float) -> None:
        """
        Update prices based on time elapsed and market conditions.
        
        Args:
            time_elapsed: Time elapsed since last update in seconds
        """
        current_time = time.time()
        
        # Simulate NPC trading activity
        self._simulate_npc_trading(time_elapsed)
        
        # Apply time-based price evolution
        self._apply_time_evolution(time_elapsed)
        
        # Check for random market events
        self._check_market_events()
        
        # Update market timestamp
        self.market.last_market_update = current_time
        self.last_simulation_time = current_time
    
    def process_transaction(self, item_id: str, quantity: float, is_buy: bool) -> float:
        """
        Process a buy or sell transaction and return the total price.
        
        Args:
            item_id: Identifier for the item being traded
            quantity: Amount being bought or sold
            is_buy: True if buying from market, False if selling to market
            
        Returns:
            Total price of the transaction
        """
        market_data = self.market.get_market_data(item_id)
        if not market_data:
            return 0.0
        
        # Calculate transaction price (may vary during large transactions)
        total_price = 0.0
        remaining_quantity = quantity
        current_price = market_data.current_price
        
        # Process transaction in chunks to simulate price impact
        chunk_size = max(1, quantity / 10)  # Process in 10% chunks
        
        while remaining_quantity > 0:
            current_chunk = min(chunk_size, remaining_quantity)
            
            # Calculate price for this chunk
            chunk_price = current_price * current_chunk
            total_price += chunk_price
            
            # Apply price impact based on transaction size and market size
            price_impact = self._calculate_price_impact(
                item_id, current_chunk, is_buy
            )
            
            # Update price for next chunk
            current_price *= (1 + price_impact)
            remaining_quantity -= current_chunk
        
        # Update market data with final price and transaction effects
        self._apply_transaction_effects(item_id, quantity, is_buy, current_price)
        
        return total_price
    
    def _calculate_price_impact(self, item_id: str, quantity: float, is_buy: bool) -> float:
        """
        Calculate the price impact of a transaction.
        
        Args:
            item_id: Item being traded
            quantity: Quantity being traded
            is_buy: True if buying, False if selling
            
        Returns:
            Price impact factor (positive for price increase, negative for decrease)
        """
        market_data = self.market.get_market_data(item_id)
        if not market_data:
            return 0.0
        
        # Base impact based on quantity and market size
        base_impact = (quantity / (self.market.market_size * 100)) * self.transaction_impact_factor
        
        # Adjust based on supply/demand levels
        if is_buy:
            # Buying increases price more when supply is low
            supply_factor = 2.0 - market_data.supply_level
            demand_factor = 1.0 + market_data.demand_level
            impact = base_impact * supply_factor * demand_factor
        else:
            # Selling decreases price more when demand is low
            supply_factor = 1.0 + market_data.supply_level
            demand_factor = 2.0 - market_data.demand_level
            impact = -base_impact * supply_factor * demand_factor
        
        # Apply volatility damping to prevent extreme swings
        impact *= self.volatility_damping
        
        # Clamp impact to reasonable bounds
        return max(-0.5, min(0.5, impact))
    
    def _apply_transaction_effects(
        self, item_id: str, quantity: float, is_buy: bool, final_price: float
    ) -> None:
        """
        Apply the effects of a transaction to market data.
        
        Args:
            item_id: Item that was traded
            quantity: Quantity that was traded
            is_buy: True if buying, False if selling
            final_price: Final price after transaction
        """
        market_data = self.market.get_market_data(item_id)
        if not market_data:
            return
        
        # Update current price
        market_data.update_price(final_price)
        
        # Update transaction volume
        market_data.transaction_volume += quantity
        
        # Update supply and demand based on transaction
        volume_factor = quantity / (self.market.market_size * 100)
        
        if is_buy:
            # Buying reduces supply, increases demand
            supply_change = -volume_factor * 0.1
            demand_change = volume_factor * 0.05
        else:
            # Selling increases supply, reduces demand
            supply_change = volume_factor * 0.1
            demand_change = -volume_factor * 0.05
        
        self.market.update_supply_demand(item_id, supply_change, demand_change)
    
    def _simulate_npc_trading(self, time_elapsed: float) -> None:
        """
        Simulate NPC trading activity to create market dynamics.
        
        Args:
            time_elapsed: Time elapsed since last simulation
        """
        # Calculate number of potential NPC trades based on time elapsed
        trade_opportunities = int(time_elapsed * self.npc_trade_frequency)
        
        for _ in range(trade_opportunities):
            if random.random() < self.npc_trade_frequency:
                self._execute_npc_trade()
    
    def _execute_npc_trade(self) -> None:
        """Execute a single NPC trade."""
        if not self.market.market_items:
            return
        
        # Select random item to trade
        item_id = random.choice(list(self.market.market_items.keys()))
        market_data = self.market.get_market_data(item_id)
        if not market_data:
            return
        
        # Determine trade type based on supply/demand
        # Higher supply = more likely to buy, higher demand = more likely to sell
        buy_probability = (market_data.supply_level + (1.0 - market_data.demand_level)) / 2.0
        is_buy = random.random() < buy_probability
        
        # Generate trade volume
        volume = random.uniform(*self.npc_trade_volume_range)
        
        # Execute the trade (but don't return the price since NPCs don't pay)
        self.process_transaction(item_id, volume, is_buy)
    
    def _apply_time_evolution(self, time_elapsed: float) -> None:
        """
        Apply time-based evolution to market prices.
        
        Args:
            time_elapsed: Time elapsed since last update
        """
        evolution_factor = time_elapsed * self.time_evolution_factor
        
        for item_id, market_data in self.market.market_items.items():
            # Prices gradually return to base price
            price_deviation = market_data.current_price - market_data.base_price
            decay_amount = price_deviation * self.base_decay_rate * evolution_factor
            
            # Apply random market fluctuations
            random_factor = random.uniform(-0.02, 0.02) * evolution_factor
            
            # Calculate new price
            new_price = market_data.current_price - decay_amount + (market_data.base_price * random_factor)
            
            # Ensure price doesn't go below a minimum threshold
            min_price = market_data.base_price * 0.1
            new_price = max(min_price, new_price)
            
            # Update price if it changed significantly
            if abs(new_price - market_data.current_price) > 0.01:
                market_data.update_price(new_price)
            
            # Gradually normalize supply and demand levels
            supply_normalization = (0.5 - market_data.supply_level) * 0.01 * evolution_factor
            demand_normalization = (0.5 - market_data.demand_level) * 0.01 * evolution_factor
            
            self.market.update_supply_demand(
                item_id, supply_normalization, demand_normalization
            )
    
    def _check_market_events(self) -> None:
        """Check for and potentially trigger random market events."""
        if random.random() < self.event_chance:
            self._trigger_market_event()
    
    def _trigger_market_event(self) -> None:
        """Trigger a random market event that affects prices."""
        if not self.market.market_items:
            return
        
        event_types = [
            "supply_shortage",
            "demand_surge",
            "price_crash",
            "market_boom",
            "trade_disruption",
        ]
        
        event_type = random.choice(event_types)
        affected_items = random.sample(
            list(self.market.market_items.keys()),
            min(3, len(self.market.market_items))
        )
        
        for item_id in affected_items:
            market_data = self.market.get_market_data(item_id)
            if not market_data:
                continue
            
            if event_type == "supply_shortage":
                # Reduce supply, increase price
                self.market.update_supply_demand(item_id, -0.3, 0.1)
                new_price = market_data.current_price * random.uniform(1.1, 1.3)
                market_data.update_price(new_price)
                
            elif event_type == "demand_surge":
                # Increase demand, increase price
                self.market.update_supply_demand(item_id, -0.1, 0.3)
                new_price = market_data.current_price * random.uniform(1.05, 1.2)
                market_data.update_price(new_price)
                
            elif event_type == "price_crash":
                # Sudden price drop
                new_price = market_data.current_price * random.uniform(0.6, 0.8)
                market_data.update_price(new_price)
                self.market.update_supply_demand(item_id, 0.2, -0.2)
                
            elif event_type == "market_boom":
                # General price increase
                new_price = market_data.current_price * random.uniform(1.1, 1.25)
                market_data.update_price(new_price)
                self.market.update_supply_demand(item_id, -0.1, 0.1)
                
            elif event_type == "trade_disruption":
                # Increased volatility
                price_change = random.uniform(-0.15, 0.15)
                new_price = market_data.current_price * (1 + price_change)
                market_data.update_price(new_price)
    
    def get_price_data(self, item_id: str) -> Dict[str, Any]:
        """
        Get detailed price information for an item.
        
        Args:
            item_id: Identifier for the item
            
        Returns:
            Dictionary with price, trend, supply/demand status
        """
        return self.market.get_price_data(item_id)
    
    def simulate_future_price(self, item_id: str, days: int = 7) -> List[Tuple[float, float]]:
        """
        Simulate future price movements for analysis.
        
        Args:
            item_id: Item to simulate
            days: Number of days to simulate
            
        Returns:
            List of (day, predicted_price) tuples
        """
        market_data = self.market.get_market_data(item_id)
        if not market_data:
            return []
        
        predictions = []
        current_price = market_data.current_price
        
        for day in range(1, days + 1):
            # Simple prediction based on current trend and random variation
            trend_factor = market_data.price_trend * 0.1
            random_factor = random.uniform(-0.05, 0.05)
            
            # Apply supply/demand influence
            supply_demand_factor = (market_data.demand_level - market_data.supply_level) * 0.02
            
            price_change = trend_factor + random_factor + supply_demand_factor
            current_price *= (1 + price_change)
            
            # Ensure price doesn't go too extreme
            min_price = market_data.base_price * 0.2
            max_price = market_data.base_price * 3.0
            current_price = max(min_price, min(max_price, current_price))
            
            predictions.append((float(day), current_price))
        
        return predictions
    
    def get_market_health(self) -> Dict[str, Any]:
        """
        Get overall market health indicators.
        
        Returns:
            Dictionary with market health metrics
        """
        if not self.market.market_items:
            return {"health": "No Data", "score": 0.0}
        
        total_volatility = 0.0
        extreme_prices = 0
        stable_prices = 0
        
        for market_data in self.market.market_items.values():
            volatility = market_data.calculate_price_volatility()
            total_volatility += volatility
            
            price_ratio = market_data.current_price / market_data.base_price
            if price_ratio < 0.5 or price_ratio > 2.0:
                extreme_prices += 1
            elif 0.8 <= price_ratio <= 1.2:
                stable_prices += 1
        
        avg_volatility = total_volatility / len(self.market.market_items)
        stability_ratio = stable_prices / len(self.market.market_items)
        extreme_ratio = extreme_prices / len(self.market.market_items)
        
        # Calculate health score (0-100)
        health_score = (
            (1.0 - min(1.0, avg_volatility)) * 40 +  # Low volatility is good
            stability_ratio * 40 +  # Stable prices are good
            (1.0 - extreme_ratio) * 20  # Fewer extreme prices is good
        )
        
        if health_score >= 80:
            health_desc = "Excellent"
        elif health_score >= 60:
            health_desc = "Good"
        elif health_score >= 40:
            health_desc = "Fair"
        elif health_score >= 20:
            health_desc = "Poor"
        else:
            health_desc = "Critical"
        
        return {
            "health": health_desc,
            "score": health_score,
            "average_volatility": avg_volatility,
            "stability_ratio": stability_ratio,
            "extreme_prices": extreme_prices,
            "total_items": len(self.market.market_items),
        }