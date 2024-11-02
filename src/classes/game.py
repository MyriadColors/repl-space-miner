from random import choice
from dataclasses import dataclass
from result import Result, Ok, Err
from src.classes.ship import Ship
from src.classes.solar_system import SolarSystem

@dataclass
class Background:
    name: str
    credits: float
    debt: float

background_choices: list[Background] = [
    Background("Ex-Miner", 500.0, 5000.0),
    Background("Corp Dropout", 1000.0, 10000.0),
    Background("Lunar Drifter", 750.0, 7500.0),
    Background("Void Runner", 750.0, 7500.0),
    Background("Xeno-Biologist", 600.0, 6000.0),
    Background("Discharged Trooper", 800.0, 8000.0)
]

class Character:
    def __init__(self, name: str, age: int, sex: str, background: str, starting_creds: float, starting_debt: float):
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
        self.debt: float = 0

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

    def __init__(self, debug_flag: bool = False, mute_flag: bool = False, skip_customization: bool = False) -> None:
        self.global_time: int = 0
        self.solar_system: SolarSystem = SolarSystem(200, 100)
        self.rnd_station = choice(self.solar_system.stations)
        self.player_character: Character | None = None
        self.player_ship: Ship | None = None
        self.debug_flag = debug_flag
        self.mute_flag = mute_flag
        self.skipc = skip_customization
        self.sound_init = True if not mute_flag else False

    def set_player_character(self, 
                             name: str, 
                             age: int, 
                             sex: str, 
                             background: str, 
                             starting_creds: float, 
                             starting_debt: float):

        self.player_character = Character(name, age, sex, background, starting_creds, starting_debt)

    def get_player_ship(self) -> Ship:
        assert self.player_ship is not None, (
            "ERROR: There is no player_ship, this should not ever happen so something went very wrong. "
            "Please tell me at github if this happens to you."
        )
        return self.player_ship


    def get_credits(self) -> float | None:
        if self.player_character is not None:
            return round(self.player_character.credits, 2)
        return None

    def get_ship(self):
        return self.player_ship

    def get_player_character(self) -> Character:
        assert self.player_character is not None, (
            "ERROR: There is no player_character, this should not ever happen so something went very wrong. "
            "Please tell me at github if this happens to you."
        )
        return self.player_character

    def get_solar_system(self):
        return self.solar_system