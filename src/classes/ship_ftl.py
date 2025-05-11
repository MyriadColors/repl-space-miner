from datetime import timedelta
from typing import Optional, Tuple, Dict, Any, Union

import random
from pygame import Vector2

from src.helpers import format_seconds
from src.events.ftl_events import get_random_ftl_event
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
    
    def check_containment_status(self, game_state: Game) -> Tuple[bool, float]:
        """Check antimatter containment system status.

        This updates containment integrity based on time passed and performs power draws.
        Returns status and risk percentage.

        Args:
            game_state: The current game state

        Returns:
            Tuple[bool, float]: (containment_ok, risk_percentage)
        """
        # Skip if no antimatter to contain
        if self.antimatter <= 0:
            self.containment_failure_risk = 0.0
            return True, 0.0

        # Calculate time since last check
        time_delta = game_state.global_time - self.last_containment_check

        if time_delta > 0:
            hours_passed = time_delta / 3600  # Convert seconds to hours

            # Calculate power draw for containment
            power_needed = hours_passed * self.containment_power_draw * self.antimatter

            # Draw power from hydrogen fuel cells
            if self.fuel >= power_needed:
                self.fuel -= power_needed
            else:
                # Not enough fuel for containment
                power_shortage = power_needed - self.fuel
                self.fuel = 0

                # Increase failure risk based on power shortage
                risk_increase = (
                    power_shortage / power_needed
                ) * 5.0  # 5% per hour without full power
                self.containment_integrity -= (
                    risk_increase * 10
                )  # Integrity decreases faster than risk increases
                self.containment_failure_risk += risk_increase

            # Small random degradation of containment (0.01-0.05% per hour)
            random_degradation = random.uniform(0.01, 0.05) * hours_passed
            self.containment_integrity -= random_degradation

            # Cap integrity at 0-100%
            self.containment_integrity = max(
                0.0, min(100.0, self.containment_integrity)
            )

            # Update failure risk based on integrity
            if self.containment_integrity < 50:
                # Below 50% integrity, risk increases more rapidly
                risk_factor = (50.0 - self.containment_integrity) / 50.0
                self.containment_failure_risk += 0.1 * risk_factor * hours_passed

            # Cap failure risk
            self.containment_failure_risk = max(
                0.0, min(100.0, self.containment_failure_risk)
            )

        # Update last check time
        self.last_containment_check = game_state.global_time

        # Containment is OK if risk is below threshold and integrity above 20%
        containment_ok = (self.containment_failure_risk < 5.0) and (
            self.containment_integrity > 20.0
        )
        return containment_ok, self.containment_failure_risk

    def repair_containment(self, repair_amount: float = 20.0) -> float:
        """Repair antimatter containment system

        Args:
            repair_amount: Amount of containment integrity to restore (percentage)

        Returns:
            float: New containment integrity level
        """
        self.containment_integrity = min(
            100.0, self.containment_integrity + repair_amount
        )
        # Repairs also reduce failure risk
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
        self, game_state: Game, destination_system: str, distance_ly: float
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
                f"Antimatter containment unstable ({risk:.1f}% failure risk). Repairs needed before FTL jump.",
            )        # Calculate time for the jump
        jump_time = distance_ly * 3600  # Simplified: 1 light year = 1 hour of game time

        # Perform the jump
        self.antimatter -= required_antimatter
        
        # Check if an FTL event occurs
        ftl_event = get_random_ftl_event()
        
        # Process event if one occurred
        event_message = ""
        if ftl_event:
            ftl_event.display_intro()
            event_result = ftl_event.execute(game_state)
              # Apply event effects to ship or game state
            if "new_integrity" in event_result and "old_integrity" in event_result:
                # Calculate the damage based on difference between old and new integrity
                containment_damage = float(event_result["old_integrity"]) - float(event_result["new_integrity"])
                event_message = f"\nEncountered: {ftl_event.name} - Containment integrity reduced by {containment_damage:.1f}%."
            elif "antimatter_loss" in event_result:
                antimatter_lost = float(event_result["antimatter_loss"])
                if antimatter_lost > self.antimatter:
                    antimatter_lost = self.antimatter
                self.antimatter -= antimatter_lost
                event_message = f"\nEncountered: {ftl_event.name} - Lost {antimatter_lost:.2f}g of antimatter."
            elif "journey_time_modifier" in event_result:
                time_mod = float(event_result["journey_time_modifier"])
                jump_time *= time_mod
                if time_mod > 1.0:
                    event_message = f"\nEncountered: {ftl_event.name} - Journey took {time_mod:.1f}x longer than expected."
                else:
                    event_message = f"\nEncountered: {ftl_event.name} - Journey took {time_mod:.1f}x less time than expected."
            else:
                event_message = f"\nEncountered: {ftl_event.name}"
                
        # Update game time
        game_state.global_time += int(jump_time)

        # In 1.0, we don't actually change systems, just simulate time passing
        return (
            True,
            f"FTL jump complete. Arrived at {destination_system} after {format_seconds(jump_time)}.{event_message}",
        )
