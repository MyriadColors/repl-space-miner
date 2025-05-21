from datetime import timedelta
from typing import Optional, Tuple, Dict, Any, Union, TYPE_CHECKING

import random
from pygame import Vector2

from src.helpers import format_seconds
from src.events.ftl_events import get_random_ftl_event

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.classes.game import Game


class DualFuelSystem:
    """
    Extension methods for the Ship class to handle the dual fuel system.
    These methods will be added to the Ship class functionality.
    """

    # Define class attributes with type annotations
    antimatter: float
    max_antimatter: float
    antimatter_consumption: float
    containment_integrity: float
    containment_power_draw: float
    containment_failure_risk: float
    last_containment_check: float
    fuel: float
    previous_system: str
    current_system: str
    location: Vector2

    # These type annotations are just for mypy and will never be executed directly on this class
    # They will be added to the Ship class

    def add_antimatter(self, amount: float) -> float:
        """Add antimatter to the ship's containment system

        Args:
            amount: Amount of antimatter to add in grams

        Returns:
            float: New antimatter level
        """
        max_add = self.max_antimatter - self.antimatter
        actual_add = min(amount, max_add)
        self.antimatter += actual_add
        return self.antimatter

    def check_containment_status(self, game_state: "Game") -> Tuple[bool, float]:
        """Check antimatter containment system status.

        This updates containment integrity based on time passed and performs power draws.
        Returns status and risk percentage.

        Args:
            game_state: The current game state

        Returns:
            Tuple[bool, float]: (is_stable, risk_percentage)
        """
        # Calculate time passed since last check
        last_check = self.last_containment_check
        current_time = game_state.global_time
        time_delta = max(0, current_time - last_check)

        # Update last check time
        self.last_containment_check = current_time

        if self.antimatter <= 0 or time_delta <= 0:
            # No antimatter or no time passed, nothing to update
            return True, self.containment_failure_risk

        # Power draw based on time passed and containment amount
        power_draw = (
            (time_delta / 60) * self.containment_power_draw * (self.antimatter / 100)
        )
        # Apply power draw
        player_ship = game_state.player_ship
        if player_ship is not None and player_ship.power >= power_draw:
            player_ship.power -= power_draw
        else:
            # Not enough power, increase risk significantly
            if player_ship is not None:
                self.containment_failure_risk += (power_draw - player_ship.power) * 0.1
                player_ship.power = 0
            else:
                # No player ship reference, apply risk directly
                self.containment_failure_risk += power_draw * 0.2

        # Base decay rate (small chance of integrity loss over time)
        base_decay = 0.001 * (time_delta / 60)
        decay_modifier = (self.antimatter / self.max_antimatter) * 0.05

        # Apply decay proportional to antimatter amount
        integrity_loss = base_decay * (1 + decay_modifier)
        self.containment_integrity = max(0, self.containment_integrity - integrity_loss)

        # Calculate risk based on integrity
        risk_increase: float = 0

        if self.containment_integrity < 50:
            # Below 50% integrity, risk increases faster
            risk_increase = (50 - self.containment_integrity) * 0.02 * (time_delta / 60)

        self.containment_failure_risk = min(
            100, self.containment_failure_risk + risk_increase
        )

        # Random events for integrity loss
        # Chance of antimatter containment failure based on time and current antimatter levels
        # Higher antimatter and longer time increase risk
        if random.random() < 0.001 * (time_delta / 60) * (
            self.antimatter / self.max_antimatter
        ):
            random_loss = round(random.uniform(0.1, 0.5), 2)
            lost_antimatter = self.antimatter * random_loss
            self.antimatter -= lost_antimatter

        # Check if containment system is still stable
        is_stable = (
            self.containment_integrity > 0 and self.containment_failure_risk < 80
        )
        return is_stable, self.containment_failure_risk

    def repair_containment(self, repair_amount: float) -> float:
        """Repair the antimatter containment system

        Args:
            repair_amount: Amount of repair in percentage points

        Returns:
            float: New containment integrity level
        """
        self.containment_integrity = min(
            100, self.containment_integrity + repair_amount
        )
        self.containment_failure_risk = max(
            0.0, self.containment_failure_risk - (repair_amount / 2)
        )
        return self.containment_integrity

    def emergency_antimatter_ejection(self) -> bool:
        """Emergency procedure to eject antimatter in case of containment failure

        Returns:
            bool: True if ejection was successful
        """
        if self.antimatter > 0:
            self.antimatter = 0.0
            self.containment_failure_risk = 0.0
            return True
        return False

    def ftl_jump(
        self, game_state: "Game", destination_system: str, distance_ly: float
    ) -> Tuple[bool, str]:
        # Check if antimatter is available
        required_antimatter = distance_ly * self.antimatter_consumption

        if self.antimatter < required_antimatter:
            return (
                False,
                f"Insufficient antimatter. Need {required_antimatter:.2f}g, but only have {self.antimatter:.2f}g.",
            )

        # Check containment stability
        containment_ok, risk = self.check_containment_status(game_state)
        if not containment_ok:
            return (
                False,
                f"Antimatter containment system unstable. Current risk: {risk:.1f}%. Repairs needed before FTL jump.",
            )  # All checks passed, perform FTL jump
        self.antimatter -= required_antimatter  # Calculate travel time based on the desired speed of 1e-10 LY per day for fastest ships        # Use a more reasonable scale for FTL travel - 1 LY per day as base speed
        # This means a distance of 1 LY would take approximately 1 day to travel
        base_ftl_speed = 1.0  # LY per day
        
        # Adjust based on ship's antimatter consumption (as a proxy for FTL speed capability)
        # Standard consumption rate is 0.05g/LY, we'll use that as reference
        ftl_speed_modifier = (
            0.05 / self.antimatter_consumption
        )  # Faster ships have lower consumption
        
        # Calculate days to travel the distance
        effective_speed = base_ftl_speed * ftl_speed_modifier
        days_to_travel = distance_ly / effective_speed
        
        # Add some randomization (±10%)
        days_to_travel *= random.uniform(0.9, 1.1)
        
        # Convert to seconds
        travel_time_seconds = days_to_travel * 86400

        # Get a random event
        event = get_random_ftl_event()
        result = event.execute(game_state) if event is not None else None
        if result is None:
            result = {
                "description": "No significant events during the jump.",
                "success": True,
            }

        # Create travel summary
        # Ensure summary is used in the return statement
        summary = {
            "origin": getattr(game_state.player_ship, "current_system", "Unknown"),
            "destination": destination_system,
            "distance": distance_ly,
            "antimatter_used": required_antimatter,
            "travel_time": travel_time_seconds,
            "event": result,
        }
        
        if hasattr(game_state, "advance_time"):
            # Apply the full travel time without any cap
            game_state.advance_time(timedelta(seconds=travel_time_seconds))
        else:
            raise AttributeError("Game object is missing 'advance_time' method.")
        if game_state.player_ship is not None:
            game_state.player_ship.previous_system = getattr(game_state.player_ship, "current_system", "Unknown")  # type: ignore
            game_state.player_ship.current_system = destination_system  # type: ignore
            game_state.player_ship.location = Vector2(0, 0)  # type: ignore # Default to center of system
        else:
            raise AttributeError(
                "Game object is missing 'player_ship' attribute or it is None."
            )
        # Set new location
        assert game_state.player_ship is not None, "Player ship is None"
        game_state.player_ship.previous_system = game_state.player_ship.current_system  # type: ignore
        game_state.player_ship.current_system = destination_system  # type: ignore
        game_state.player_ship.location = Vector2(0, 0)  # type: ignore # Default to center of system

        # Apply a small degradation to containment integrity from the jump
        # Simulate the stress of the jump on the FTL drive components
        # This could be influenced by ship upgrades or current FTL drive health in a more complex system
        jump_stress = round(random.uniform(0.5, 1.5) * (distance_ly / 10), 2)

        # TODO: add a hull integrity system to the ship class
        # game_state.get_player_ship().hull_integrity -= jump_stress

        game_state.ui.info_message(
            f"The Jump Stress to the Hull Integrity was of {jump_stress:.2f}%."
        )

        # Format travel summary
        event_desc = (
            result["description"] if "description" in result else "Uneventful journey"
        )
        antimatter_left = self.antimatter

        summary_text = (
            f"FTL Jump complete. Arrival in {destination_system} system.\n"
            f"Distance traveled: {distance_ly:.2f} light years\n"
            f"Antimatter consumed: {required_antimatter:.2f}g (Remaining: {antimatter_left:.2f}g)\n"
            f"Journey time: {format_seconds(travel_time_seconds)}\n"
            f"\n--- Journey Report ---\n"
            f"{event_desc}"
        )

        return True, summary_text

    def to_dict(self) -> Dict[str, Any]:
        """Convert antimatter system status to dictionary for serialization"""
        return {
            "antimatter": self.antimatter,
            "max_antimatter": self.max_antimatter,
            "antimatter_consumption": self.antimatter_consumption,
            "containment_integrity": self.containment_integrity,
            "containment_power_draw": self.containment_power_draw,
            "containment_failure_risk": self.containment_failure_risk,
            "last_containment_check": self.last_containment_check,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Update antimatter system status from dictionary"""
        self.antimatter = data.get("antimatter", 0.0)
        self.max_antimatter = data.get("max_antimatter", 100.0)
        self.antimatter_consumption = data.get("antimatter_consumption", 1.0)
        self.containment_integrity = data.get("containment_integrity", 100.0)
        self.containment_power_draw = data.get("containment_power_draw", 1.0)
        self.containment_failure_risk = data.get("containment_failure_risk", 0.0)
        self.last_containment_check = data.get("last_containment_check", 0.0)
