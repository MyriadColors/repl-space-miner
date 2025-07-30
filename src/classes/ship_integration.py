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
