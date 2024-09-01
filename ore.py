class Ore:
    def __init__(self, name, value, volume, mineral_yield):
        self.name = name
        self.base_value = value  # in credits
        self.volume = volume  # in m³ per unit
        self.mineral_yield = mineral_yield  # Minerals per unit

    def to_string(self):
        return f"{self.name}: {self.base_value} credits, {self.volume} m³ per unit"

    def get_info(self):
        return f"{self.name} {self.base_value} {self.volume}"


class PyrogenOre(Ore):
    def __init__(self):
        super().__init__("Pyrogen", 29.0, 0.3, [])


class AscorbonOre(Ore):
    def __init__(self):
        super().__init__("Ascorbon", 16.0, 0.15, [])


class AngionOre(Ore):
    def __init__(self):
        super().__init__("Angion", 55.0, 0.35, [])


class VariteOre(Ore):
    def __init__(self):
        super().__init__("Varite", 18.0, 0.1, [])


class OxyniteOre(Ore):
    def __init__(self):
        super().__init__("Oxynite", 3500.0, 16, [])


class CyclonOre(Ore):
    def __init__(self):
        super().__init__("Cyclon", 600.0, 2, [])


class HeronOre(Ore):
    def __init__(self):
        super().__init__("Heron", 1200.0, 3, [])


class JonniteOre(Ore):
    def __init__(self):
        super().__init__("Jonnite", 7250.0, 16, [])


class MagnetonOre(Ore):
    def __init__(self):
        super().__init__("Magneton", 580.0, 1.2, [])
