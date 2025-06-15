from dataclasses import dataclass
from enum import Enum, auto


class Category(Enum):
    RAW_MATERIAL = auto()  # Raw materials like ores, gases, and organics
    REFINED_GOOD = auto()  # Refined goods like metals, chemicals, and alloys
    MANUFACTURED_GOOD = (
        auto()
    )  # Manufactured goods like components, machinery, and electronics
    COMPONENT = auto()  # Components like circuit boards, engines, and structural parts
    FUEL = auto()  # Fuel sources like coal, gas, and nuclear material
    CONSUMABLE = auto()  # Consumables like food, water, and medical supplies


@dataclass
class Commodity:
    commodity_id: int
    name: str
    category: Category
    base_price: float
    price_volatility: float
    volatility_range: tuple[float, float]
    description: str
    volume_per_unit: float
    mass_per_unit: float
