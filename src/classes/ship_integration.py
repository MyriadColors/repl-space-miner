"""
This module provides functions to integrate the dual fuel system with the main Ship class.
It applies the methods from ship_ftl.py to the Ship class to implement the dual fuel system.
"""

from src.classes.ship import Ship
from src.classes.ship_ftl import DualFuelSystem


def integrate_dual_fuel_system():
    """
    Apply the dual fuel system methods to the Ship class.
    This must be called during application startup before any Ship objects are created.
    """
    # Add all methods from DualFuelSystem to the Ship class
    Ship.add_antimatter = DualFuelSystem.add_antimatter
    Ship.check_containment_status = DualFuelSystem.check_containment_status
    Ship.repair_containment = DualFuelSystem.repair_containment
    Ship.emergency_antimatter_ejection = DualFuelSystem.emergency_antimatter_ejection
    Ship.ftl_jump = DualFuelSystem.ftl_jump

    # Log successful integration
    print("Dual fuel system integrated successfully")


# Functions to update the ship's to_dict and from_dict methods to include antimatter data


def update_ship_serialization():
    """
    Patch the Ship class's serialization methods to include antimatter data.
    """
    # Store original to_dict method
    original_to_dict = Ship.to_dict

    # Define extended to_dict that includes antimatter fields
    def extended_to_dict(self):
        data = original_to_dict(self)
        # Add antimatter data
        data.update(
            {
                "antimatter": self.antimatter,
                "max_antimatter": self.max_antimatter,
                "antimatter_consumption": self.antimatter_consumption,
                "containment_integrity": self.containment_integrity,
                "containment_power_draw": self.containment_power_draw,
                "containment_failure_risk": self.containment_failure_risk,
                "last_containment_check": self.last_containment_check,
            }
        )
        return data

    # Store original from_dict method
    original_from_dict = Ship.from_dict

    # Define extended from_dict that loads antimatter fields
    @classmethod
    def extended_from_dict(cls, data, game_state):
        ship = original_from_dict(data, game_state)

        # Load antimatter data if present
        if "antimatter" in data:
            ship.antimatter = data["antimatter"]
            ship.max_antimatter = data.get("max_antimatter", 5.0)
            ship.antimatter_consumption = data.get("antimatter_consumption", 0.5)
            ship.containment_integrity = data.get("containment_integrity", 100.0)
            ship.containment_power_draw = data.get("containment_power_draw", 0.001)
            ship.containment_failure_risk = data.get("containment_failure_risk", 0.0)
            ship.last_containment_check = data.get(
                "last_containment_check", game_state.global_time
            )

        return ship

    # Replace methods
    Ship.to_dict = extended_to_dict
    Ship.from_dict = extended_from_dict
