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
    setattr(Ship, "add_antimatter", DualFuelSystem.add_antimatter)
    setattr(Ship, "check_containment_status",
            DualFuelSystem.check_containment_status)
    setattr(Ship, "repair_containment", DualFuelSystem.repair_containment)
    setattr(
        Ship,
        "emergency_antimatter_ejection",
        DualFuelSystem.emergency_antimatter_ejection,
    )
    setattr(Ship, "ftl_jump", DualFuelSystem.ftl_jump)
    original_init = Ship.__init__

    def extended_init(self, *args, **kwargs):
        original_init(
            self, *args, **kwargs
        )  # The antimatter and FTL attributes are now handled in the Ship class __init__

    # Use setattr to avoid direct method assignment
    setattr(Ship, "__init__", extended_init)

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
                "antimatter": getattr(self, "antimatter", 0.0),
                "max_antimatter": getattr(self, "max_antimatter", 5.0),
                "antimatter_consumption": getattr(self, "antimatter_consumption", 0.05),
                "containment_integrity": getattr(self, "containment_integrity", 100.0),
                "containment_power_draw": getattr(
                    self, "containment_power_draw", 0.001
                ),
                "containment_failure_risk": getattr(
                    self, "containment_failure_risk", 0.0
                ),
                "last_containment_check": getattr(self, "last_containment_check", 0.0),
            }
        )
        return data

    # Store original from_dict method
    original_from_dict = Ship.from_dict

    # Define new from_dict function to handle antimatter fields
    def extended_from_dict(cls, data, game_state):
        ship = original_from_dict(data, game_state)

        # Load antimatter data if present
        if "antimatter" in data:
            ship.antimatter = float(data["antimatter"])
            ship.max_antimatter = float(data.get("max_antimatter", 5.0))
            ship.antimatter_consumption = float(
                data.get("antimatter_consumption", 0.05)
            )
            ship.containment_integrity = float(
                data.get("containment_integrity", 100.0))
            ship.containment_power_draw = float(
                data.get("containment_power_draw", 0.001)
            )
            ship.containment_failure_risk = float(
                data.get("containment_failure_risk", 0.0)
            )
            ship.last_containment_check = float(
                data.get("last_containment_check", game_state.global_time)
            )

        return ship

    # Replace methods using setattr to avoid direct method assignment issues
    setattr(Ship, "to_dict", extended_to_dict)

    # Create a proper classmethod for from_dict
    extended_from_dict_cm = classmethod(extended_from_dict)
    setattr(Ship, "from_dict", extended_from_dict_cm)
