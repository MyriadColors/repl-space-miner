from random import choice

from src.classes.ship import Ship
from src.classes.solar_system import SolarSystem

class Character:
    def __init__(self, name: str, age: int, sex: str, background: str):
        self.name = name
        self.age = age
        self.sex = sex
        self.background = background
        self.piloting = 5
        self.engineering = 5
        self.combat = 5
        self.education = 5
        self.charisma = 5
        self.reputation_states = 0
        self.reputation_corporations = 0
        self.reputation_pirates = 0
        self.reputation_belters = 0
        self.reputation_traders = 0
        self.reputation_scientists = 0
        self.reputation_military = 0
        self.reputation_explorers = 0
        self.credits: float = 1000
        
    def to_string(self) -> list[str]:
        return [f"Name: {self.name}" + \
                f"\nAge: {self.age}" + \
                f"\nSex: {self.sex}" + \
                f"\nBackground: {self.background}" + \
                f"\nCredits: {self.credits}" + \
                f"\nReputation States: {self.reputation_states}" + \
                f"\nReputation Corporations: {self.reputation_corporations}" + \
                f"\nReputation Pirates: {self.reputation_pirates}" + \
                f"\nReputation Belters: {self.reputation_belters}" + \
                f"\nReputation Traders: {self.reputation_traders}" + \
                f"\nReputation Scientists: {self.reputation_scientists}" + \
                f"\nReputation Military: {self.reputation_military}" + \
                f"\nReputation Explorers: {self.reputation_explorers}"]

class Game:

    def __init__(self, debug_flag=False, mute_flag=False, skip_customization=False):
        self.global_time: int = 0
        self.solar_system: SolarSystem = SolarSystem(200, 100)
        self.rnd_station = choice(self.solar_system.stations)
        self.player_character: Character | None = None
        self.player_ship: Ship | None = None
        self.debug_flag = debug_flag
        self.mute_flag = mute_flag
        self.skipc = skip_customization
        self.sound_init = True if not mute_flag else False  # If the mute flag is false, then sound_init is true

    def get_credits(self):
        return round(self.player_character.credits, 2)

    def get_ship(self):
        return self.player_ship
    
    def get_character(self):
        return self.player_character
    
    def get_solar_system(self):
        return self.solar_system
    
    
        