from dataclasses import dataclass


@dataclass
class Ore:
    name: str
    base_value: float  # in credits
    volume: float  # in m³ per unit
    mineral_yield: list  # Placeholder for future use
    id: int

    def to_string(self):
        return f"{self.name}: {self.base_value} credits, {self.volume} m³ per unit"

    def get_info(self):
        return f"{self.name} {self.base_value} {self.volume}"

    def get_name(self) -> str:
        return self.name.lower()
    
    def __hash__(self):
        # Use the ID for hashing since it's a unique identifier
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Ore):
            return False
        return self.id == other.id


# Define ores in a dictionary
ORES = {
    0: Ore("Pyrogen", 29.0, 0.3, [], 0),
    1: Ore("Ascorbon", 16.0, 0.15, [], 1),
    2: Ore("Angion", 55.0, 0.35, [], 2),
    3: Ore("Varite", 18.0, 0.1, [], 3),
    4: Ore("Oxynite", 3500.0, 16, [], 4),
    5: Ore("Cyclon", 600.0, 2, [], 5),
    6: Ore("Heron", 1200.0, 3, [], 6),
    7: Ore("Jonnite", 7250.0, 16, [], 7),
    8: Ore("Magneton", 580.0, 1.2, [], 8),
}


def get_ore_by_name(name: str) -> Ore | None:
    for ore in ORES.values():
        if ore.name.lower() == name.lower():
            return ore
    return None
