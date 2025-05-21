from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, List, Tuple


class PurityLevel(Enum):
    """Represents the purity level of an ore."""

    RAW = auto()  # Unrefined, as mined
    LOW = auto()  # Low purity, basic refinement
    MEDIUM = auto()  # Medium purity, standard refinement
    HIGH = auto()  # High purity, advanced refinement
    ULTRA = auto()  # Ultra pure, highest quality


@dataclass
class Ore:
    name: str
    base_value: float  # in credits
    volume: float  # in m³ per unit
    mineral_yield: List[Tuple[int, float]]  # List of tuples (mineral_id, yield_ratio)
    id: int
    purity: PurityLevel = PurityLevel.RAW  # Default purity is RAW
    refining_difficulty: float = (
        1.0  # Higher values mean harder to refine, affects refining time and cost
    )

    def to_string(self):
        purity_str = self.purity.name.capitalize()
        return f"{purity_str} {self.name}: {self.get_value()} credits, {self.volume} m³ per unit"

    def get_info(self):
        purity_str = self.purity.name.capitalize()
        return f"{purity_str} {self.name} {self.get_value()} {self.volume}"

    def get_name(self) -> str:
        return self.name.lower()

    def get_value(self) -> float:
        """Calculate the actual value based on purity level."""
        purity_modifiers = {
            PurityLevel.RAW: 1.0,
            PurityLevel.LOW: 1.5,
            PurityLevel.MEDIUM: 2.0,
            PurityLevel.HIGH: 3.0,
            PurityLevel.ULTRA: 5.0,
        }
        return round(self.base_value * purity_modifiers.get(self.purity, 1.0), 2)

    def can_refine(self) -> bool:
        """Check if the ore can be refined further."""
        if self.purity == PurityLevel.ULTRA:
            return False
        return True

    def get_next_purity_level(self) -> Optional[PurityLevel]:
        """Get the next purity level for refining."""
        purity_order = [
            PurityLevel.RAW,
            PurityLevel.LOW,
            PurityLevel.MEDIUM,
            PurityLevel.HIGH,
            PurityLevel.ULTRA,
        ]
        current_index = purity_order.index(self.purity)
        if current_index >= len(purity_order) - 1:
            return None
        return purity_order[current_index + 1]

    def create_refined_version(self) -> Optional["Ore"]:
        """Create a new ore object with the next purity level."""
        next_purity = self.get_next_purity_level()
        if not next_purity:
            return None

        # Create a new ore with the same properties but higher purity
        return Ore(
            name=self.name,
            base_value=self.base_value,
            volume=self.volume * 0.9,  # Refined ore has slightly less volume
            mineral_yield=self.mineral_yield.copy() if self.mineral_yield else [],
            id=self.id,
            purity=next_purity,
            refining_difficulty=self.refining_difficulty,
        )

    def __hash__(self):
        # Use the ID and purity for hashing since they together form a unique identifier
        return hash((self.id, self.purity))

    def __eq__(self, other):
        if not isinstance(other, Ore):
            return False
        return self.id == other.id and self.purity == other.purity

    def get_mineral_yield(self) -> Dict[int, float]:
        """
        Calculate the mineral yield from this ore based on purity.

        Returns:
            Dictionary mapping mineral_id to the amount of that mineral produced per ore unit.
        """
        # Apply purity modifier to yields
        purity_yield_modifiers = {
            PurityLevel.RAW: 0.5,  # Lower yield from raw ore
            PurityLevel.LOW: 0.60,
            PurityLevel.MEDIUM: 0.75,
            PurityLevel.HIGH: 0.85,
            PurityLevel.ULTRA: 0.95,  # Maximum yield
        }

        purity_modifier = purity_yield_modifiers.get(self.purity, 0.6)

        # Calculate yield for each mineral
        yields = {}
        for mineral_id, base_yield in self.mineral_yield:
            yields[mineral_id] = round(base_yield * purity_modifier, 2)

        return yields


# Define ores in a dictionary
ORES = {
    0: Ore(
        "Pyrogen", 29.0, 0.3, [(0, 0.7), (1, 0.2)], 0, refining_difficulty=1.0
    ),  # Iron, Carbon
    1: Ore("Ascorbon", 16.0, 0.15, [(1, 0.8)], 1, refining_difficulty=1.2),  # Carbon
    2: Ore(
        "Angion", 55.0, 0.35, [(3, 0.6), (4, 0.3)], 2, refining_difficulty=1.5
    ),  # Copper, Zinc
    3: Ore(
        "Varite", 18.0, 0.1, [(10, 0.5)], 3, refining_difficulty=0.8
    ),  # Rare Earth Elements
    4: Ore(
        "Oxynite", 3500.0, 16, [(11, 0.3)], 4, refining_difficulty=2.5
    ),  # Exotic Materials
    5: Ore(
        "Cyclon", 600.0, 2, [(2, 0.7), (5, 0.2)], 5, refining_difficulty=1.8
    ),  # Silicon, Aluminum
    6: Ore(
        "Heron", 1200.0, 3, [(6, 0.5), (7, 0.4)], 6, refining_difficulty=2.0
    ),  # Titanium, Nickel
    7: Ore(
        "Jonnite", 7250.0, 16, [(9, 0.2), (10, 0.1)], 7, refining_difficulty=3.0
    ),  # Gold, Rare Earth Elements
    8: Ore(
        "Magneton", 580.0, 1.2, [(0, 0.4), (8, 0.5)], 8, refining_difficulty=2.2
    ),  # Iron, Neodymium
}


def get_ore_by_name(name: str) -> Ore | None:
    for ore in ORES.values():
        if ore.name.lower() == name.lower():
            return ore
    return None
