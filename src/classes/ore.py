class Ore:
    def __init__(self, name, value, volume, mineral_yield, id: int):
        self.name: str = name
        self.base_value: float = value  # in credits
        self.volume: float = volume  # in m³ per unit
        self.id: int = id

    def to_string(self):
        return f"{self.name}: {self.base_value} credits, {self.volume} m³ per unit"

    def get_info(self):
        return f"{self.name} {self.base_value} {self.volume}"

    def get_name(self) -> str:
        return self.name.lower()


class PyrogenOre(Ore):
    def __init__(self):
        super().__init__("Pyrogen", 29.0, 0.3, [], 0)


class AscorbonOre(Ore):
    def __init__(self):
        super().__init__("Ascorbon", 16.0, 0.15, [], 1)


class AngionOre(Ore):
    def __init__(self):
        super().__init__("Angion", 55.0, 0.35, [], 2)


class VariteOre(Ore):
    def __init__(self):
        super().__init__("Varite", 18.0, 0.1, [], 3)


class OxyniteOre(Ore):
    def __init__(self):
        super().__init__("Oxynite", 3500.0, 16, [], 4)

class CyclonOre(Ore):
    def __init__(self):
        super().__init__("Cyclon", 600.0, 2, [], 5)


class HeronOre(Ore):
    def __init__(self):
        super().__init__("Heron", 1200.0, 3, [], 6)


class JonniteOre(Ore):
    def __init__(self):
        super().__init__("Jonnite", 7250.0, 16, [], 7)


class MagnetonOre(Ore):
    def __init__(self):
        super().__init__("Magneton", 580.0, 1.2, [], 8)