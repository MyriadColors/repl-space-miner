from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, List, Tuple

from src.classes.commodity import Commodity, Category


class PurityLevel(Enum):
    """Represents the purity level of an ore."""

    RAW = auto()  # Unrefined, as mined
    LOW = auto()  # Low purity, basic refinement
    MEDIUM = auto()  # Medium purity, standard refinement
    HIGH = auto()  # High purity, advanced refinement
    ULTRA = auto()  # Ultra pure, highest quality


@dataclass
class Ore:
    commodity: Commodity
    mineral_yield: List[Tuple[int, float]]
    purity: PurityLevel = PurityLevel.RAW  # Default purity is RAW
    refining_difficulty: float = 1.0

    @property
    def id(self) -> int:
        """Get the ore ID from the commodity."""
        return self.commodity.commodity_id

    @property
    def name(self) -> str:
        """Get the ore name from the commodity."""
        return self.commodity.name

    @property
    def base_value(self) -> float:
        """Get the base value from the commodity."""
        return self.commodity.base_price

    @property
    def volume(self) -> float:
        """Get the volume per unit from the commodity."""
        return self.commodity.volume_per_unit

    def to_string(self):
        purity_str = self.purity.name.capitalize()
        return f"{purity_str} {self.commodity.name}: {self.get_value()} credits, {self.commodity.volume_per_unit} m³ per unit"

    def get_info(self):
        purity_str = self.purity.name.capitalize()
        return f"{purity_str} {self.commodity.name} {self.get_value()} {self.commodity.volume_per_unit}"

    def get_name(self) -> str:
        return self.commodity.name.lower()

    def get_value(self) -> float:
        """Calculate the actual value based on purity level."""
        purity_modifiers = {
            PurityLevel.RAW: 1.0,
            PurityLevel.LOW: 1.5,
            PurityLevel.MEDIUM: 2.0,
            PurityLevel.HIGH: 3.0,
            PurityLevel.ULTRA: 5.0,
        }
        return round(
            self.commodity.base_price * purity_modifiers.get(self.purity, 1.0), 2
        )

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
            commodity=Commodity(
                commodity_id=self.commodity.commodity_id,
                name=self.commodity.name,
                category=self.commodity.category,
                base_price=self.commodity.base_price,
                price_volatility=self.commodity.price_volatility,
                volatility_range=self.commodity.volatility_range,
                description=self.commodity.description,
                volume_per_unit=self.commodity.volume_per_unit
                * 0.9,  # Refined ore has slightly less volume
                mass_per_unit=self.commodity.mass_per_unit,
            ),
            mineral_yield=self.mineral_yield.copy() if self.mineral_yield else [],
            purity=next_purity,
            refining_difficulty=self.refining_difficulty,
        )

    def __hash__(self):
        # Use the ID and purity for hashing since they together form a unique identifier
        return hash((self.commodity.commodity_id, self.purity))

    def __eq__(self, other):
        if not isinstance(other, Ore):
            return False
        return (
            self.commodity.commodity_id == other.commodity.commodity_id
            and self.purity == other.purity
        )
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
        commodity=Commodity(
            commodity_id=0,
            name="Pyrogen",
            category=Category.RAW_MATERIAL,
            base_price=29.0,
            price_volatility=0.3,
            volatility_range=(0.0, 0.0),
            volume_per_unit=1.0,
            mass_per_unit=0.8,
            description="A common mineral with moderate energy potential",
        ),
        mineral_yield=[(0, 0.7), (1, 0.2)],
        purity=PurityLevel.RAW,
        refining_difficulty=1.0,
    ),
    1: Ore(
        commodity=Commodity(
            commodity_id=1,
            name="Ascorbon",
            category=Category.RAW_MATERIAL,
            base_price=16.0,
            price_volatility=0.15,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.8,
            mass_per_unit=0.7,
            description="A lightweight ore with good structural properties",
        ),
        mineral_yield=[(1, 0.8)],
        purity=PurityLevel.LOW,
        refining_difficulty=1.2,
    ),
    2: Ore(
        commodity=Commodity(
            commodity_id=2,
            name="Angion",
            category=Category.RAW_MATERIAL,
            base_price=55.0,
            price_volatility=0.35,
            volatility_range=(0.0, 0.0),
            volume_per_unit=1.2,
            mass_per_unit=1.1,
            description="A dense ore with high mineral content",
        ),
        mineral_yield=[(3, 0.6), (4, 0.3)],
        purity=PurityLevel.MEDIUM,
        refining_difficulty=1.5,
    ),
    3: Ore(
        commodity=Commodity(
            commodity_id=3,
            name="Varite",
            category=Category.RAW_MATERIAL,
            base_price=18.0,
            price_volatility=0.1,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.9,
            mass_per_unit=0.6,
            description="A stable ore with consistent properties",
        ),
        mineral_yield=[(10, 0.5)],
        purity=PurityLevel.HIGH,
        refining_difficulty=0.8,
    ),
    4: Ore(
        commodity=Commodity(
            commodity_id=4,
            name="Oxynite",
            category=Category.RAW_MATERIAL,
            base_price=3500.0,
            price_volatility=16.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.3,
            mass_per_unit=2.5,
            description="An extremely valuable and dense rare ore",
        ),
        mineral_yield=[(11, 0.3)],
        purity=PurityLevel.ULTRA,
        refining_difficulty=2.5,
    ),
    5: Ore(
        commodity=Commodity(
            commodity_id=5,
            name="Cyclon",
            category=Category.RAW_MATERIAL,
            base_price=600.0,
            price_volatility=2.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.7,
            mass_per_unit=1.3,
            description="A valuable ore with unique crystalline structure",
        ),
        mineral_yield=[(2, 0.7), (5, 0.2)],
        purity=PurityLevel.RAW,
        refining_difficulty=1.8,
    ),
    6: Ore(
        commodity=Commodity(
            commodity_id=6,
            name="Heron",
            category=Category.RAW_MATERIAL,
            base_price=1200.0,
            price_volatility=3.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.5,
            mass_per_unit=1.8,
            description="A premium ore with excellent conductivity properties",
        ),
        mineral_yield=[(6, 0.5), (7, 0.4)],
        purity=PurityLevel.LOW,
        refining_difficulty=2.0,
    ),
    7: Ore(
        commodity=Commodity(
            commodity_id=7,
            name="Jonnite",
            category=Category.RAW_MATERIAL,
            base_price=7250.0,
            price_volatility=16.0,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.2,
            mass_per_unit=3.0,
            description="An extremely rare and valuable exotic ore",
        ),
        mineral_yield=[(9, 0.2), (10, 0.1)],
        purity=PurityLevel.MEDIUM,
        refining_difficulty=3.0,
    ),
    8: Ore(
        commodity=Commodity(
            commodity_id=8,
            name="Magneton",
            category=Category.RAW_MATERIAL,
            base_price=580.0,
            price_volatility=1.2,
            volatility_range=(0.0, 0.0),
            volume_per_unit=0.6,
            mass_per_unit=1.5,
            description="A magnetic ore with industrial applications",
        ),
        mineral_yield=[(0, 0.4), (8, 0.5)],
        purity=PurityLevel.HIGH,
        refining_difficulty=2.2,
    ),
}


def get_ore_by_name(name: str) -> Ore | None:
    for ore in ORES.values():
        if ore.commodity.name.lower() == name.lower():
            return ore
    return None
