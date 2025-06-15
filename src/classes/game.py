import json
import os
from typing import List, Dict, Union, Optional
import pygame as pg
from datetime import datetime
from dataclasses import dataclass
import random
import time
from colorama import Fore, Back, Style, init

from src.classes.ship import Ship
from src.classes.solar_system import SolarSystem
from src.classes.region import Region
from src.classes.skill_system import SkillSystem


init(autoreset=True)


class UI:
    def __init__(self, default_fg=Fore.WHITE, default_bg=Back.BLACK):
        self.default_fg = default_fg
        self.default_bg = default_bg
        self.default_style = Style.NORMAL

    def apply_default_colors(self):
        """Reset colors to the default settings."""
        print(self.default_fg + self.default_bg + self.default_style, end="")

    def reset_colors(self):
        """Reset all colors to terminal defaults."""
        print(Style.RESET_ALL, end="")

    def info_message(self, message):
        """Display an informational message with cyan color."""
        print(Fore.CYAN + message + Style.RESET_ALL)

    def success_message(self, message):
        """Display a success message with green color."""
        print(Fore.GREEN + message + Style.RESET_ALL)

    def warn_message(self, message):
        """Display a warning message with yellow color."""
        print(Fore.YELLOW + message + Style.RESET_ALL)

    def error_message(self, message):
        """Display an error message with red color."""
        print(Fore.RED + message + Style.RESET_ALL)

    def highlight_message(self, message):
        """Display a highlighted message."""
        print(Fore.MAGENTA + Style.BRIGHT + message + Style.RESET_ALL)

    def format_text(self, message, fg=None, bg=None, style=None):
        """Format text with specified colors and style."""
        fg_color = fg if fg else self.default_fg
        bg_color = bg if bg else self.default_bg
        text_style = style if style else self.default_style
        return fg_color + bg_color + text_style + message + Style.RESET_ALL

    def set_default_colors(self, fg=None, bg=None):
        """Change the default colors."""
        if fg:
            self.default_fg = fg
        if bg:
            self.default_bg = bg

    def clear_screen(self):
        """Clear the terminal screen."""
        import os

        os.system("cls" if os.name == "nt" else "clear")


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
    Background("Discharged Trooper", 800.0, 8000.0),
]


class Character:
    def __init__(
        self,
        name: str,
        age: int,
        sex: str,
        background: str,
        starting_creds: float,
        starting_debt: float,
    ):
        self.name = name
        self.age = age
        self.sex = sex
        self.background = background

        self.perception = 5
        self.resilience = 5
        self.intellect = 5
        self.presence = 5
        self.adaptability = 5
        self.technical_aptitude = 5

        self.skill_system = SkillSystem()

        self.reputation_states = 0
        self.reputation_corporations = 0
        self.reputation_pirates = 0
        self.reputation_belters = 0
        self.reputation_traders = 0
        self.reputation_scientists = 0
        self.reputation_military = 0
        self.reputation_explorers = 0
        self.credits: float = self.round_credits(starting_creds)
        self.debt: float = self.round_credits(starting_debt)

        self.last_interest_time = 0

        self.savings: float = 0.0
        self.savings_interest_rate: float = 0.02

        self.bank_transactions: list = []

        self.initialize_faction_standings()

        self.positive_trait = ""
        self.negative_trait = ""

        self.damage_resist_mod = 1.0
        self.mining_yield_mod = 1.0
        self.buy_price_mod = 1.0
        self.sell_price_mod = 1.0
        self.sensor_range_mod = 1.0
        self.evasion_mod = 1.0
        self.fuel_consumption_mod = 1.0
        self.debt_interest_mod = 1.0

    def initialize_faction_standings(self):
        """Initialize the faction standings dictionary with default values."""
        self.faction_standings = {
            "states": 0,
            "corporations": 0,
            "pirates": 0,
            "belters": 0,
            "traders": 0,
            "scientists": 0,
            "military": 0,
            "explorers": 0,
        }

    @property
    def piloting(self) -> int:
        """Get piloting skill level from skill system"""
        skill = self.skill_system.get_skill("piloting")
        return skill.level if skill else 0

    @piloting.setter
    def piloting(self, value: int) -> None:
        """Set piloting skill level"""
        skill = self.skill_system.get_skill("piloting")
        if skill:
            skill._level = value

    @property
    def engineering(self) -> int:
        """Get engineering skill level from skill system"""
        skill = self.skill_system.get_skill("engineering")
        return skill.level if skill else 0

    @engineering.setter
    def engineering(self, value: int) -> None:
        """Set engineering skill level"""
        skill = self.skill_system.get_skill("engineering")
        if skill:
            skill._level = value

    @property
    def combat(self) -> int:
        """Get combat skill level from skill system"""
        skill = self.skill_system.get_skill("combat")
        return skill.level if skill else 0

    @combat.setter
    def combat(self, value: int) -> None:
        """Set combat skill level"""
        skill = self.skill_system.get_skill("combat")
        if skill:
            skill._level = value

    @property
    def education(self) -> int:
        """Get education skill level from skill system"""
        skill = self.skill_system.get_skill("education")
        return skill.level if skill else 0

    @education.setter
    def education(self, value: int) -> None:
        """Set education skill level"""
        skill = self.skill_system.get_skill("education")
        if skill:
            skill._level = value

    @property
    def charisma(self) -> int:
        """Get charisma skill level from skill system"""
        skill = self.skill_system.get_skill("charisma")
        return skill.level if skill else 0

    @charisma.setter
    def charisma(self, value: int) -> None:
        """Set charisma skill level"""
        skill = self.skill_system.get_skill("charisma")
        if skill:
            skill._level = value

    def apply_stat_effects(self):
        """Apply effects from all character stats"""
        self.apply_perception_effects()
        self.apply_resilience_effects()
        self.apply_intellect_effects()
        self.apply_presence_effects()
        self.apply_adaptability_effects()
        self.apply_technical_aptitude_effects()

    def apply_perception_effects(self):
        """Apply effects from the Perception stat"""

        self.critical_hit_chance_mod = 1.0
        self.hidden_discovery_chance_mod = 1.0

        if self.perception > 5:
            bonus_multiplier = 1 + ((self.perception - 5) * 0.05)
            self.critical_hit_chance_mod = bonus_multiplier
            self.hidden_discovery_chance_mod = bonus_multiplier

            self.sensor_range_mod *= 1 + ((self.perception - 5) * 0.03)

    def apply_resilience_effects(self):
        """Apply effects from the Resilience stat"""

        self.hull_integrity_mod = 1.0
        self.system_recovery_mod = 1.0

        if self.resilience > 5:
            self.hull_integrity_mod = 1 + ((self.resilience - 5) * 0.04)
            self.system_recovery_mod = 1 + ((self.resilience - 5) * 0.04)

            self.damage_resist_mod *= 1 - ((self.resilience - 5) * 0.02)

    def apply_intellect_effects(self):
        """Apply effects from the Intellect stat"""

        self.research_speed_mod = 1.0
        self.market_analysis_mod = 1.0

        if self.intellect > 5:
            self.research_speed_mod = 1 + ((self.intellect - 5) * 0.05)
            self.market_analysis_mod = 1 + ((self.intellect - 5) * 0.03)

    def apply_presence_effects(self):
        """Apply effects from the Presence stat"""

        self.faction_relation_mod = 1.0

        if self.presence > 5:
            price_bonus = (self.presence - 5) * 0.05
            self.buy_price_mod *= 1 - price_bonus
            self.sell_price_mod *= 1 + price_bonus
            self.faction_relation_mod = 1 + ((self.presence - 5) * 0.03)

    def apply_adaptability_effects(self):
        """Apply effects from the Adaptability stat"""

        self.cross_cultural_mod = 1.0

        if self.adaptability > 5:
            self.cross_cultural_mod = 1 + ((self.adaptability - 5) * 0.04)

    def apply_technical_aptitude_effects(self):
        """Apply effects from the Technical Aptitude stat"""

        self.repair_efficiency_mod = 1.0
        self.salvage_success_mod = 1.0

        if self.technical_aptitude > 5:
            self.repair_efficiency_mod = 1 + ((self.technical_aptitude - 5) * 0.05)
            self.salvage_success_mod = 1 + ((self.technical_aptitude - 5) * 0.05)

    def get_mining_bonus(self):
        """Calculate mining bonus based on stats and skills"""

        mining_bonus = self.mining_yield_mod

        if self.perception > 5:
            mining_bonus *= 1 + ((self.perception - 5) * 0.02)

        if self.technical_aptitude > 5:
            mining_bonus *= 1 + ((self.technical_aptitude - 5) * 0.01)

        return mining_bonus

    def get_trading_bonus(self):
        """Calculate trading bonuses based on stats and skills"""

        buy_mod = self.buy_price_mod
        sell_mod = self.sell_price_mod

        if self.intellect > 5:
            market_bonus = (self.intellect - 5) * 0.01
            buy_mod *= 1 - market_bonus
            sell_mod *= 1 + market_bonus

        if self.charisma > 5:
            charisma_bonus = (self.charisma - 5) * 0.02
            buy_mod *= 1 - charisma_bonus
            sell_mod *= 1 + charisma_bonus

        return (buy_mod, sell_mod)

    def round_credits(self, value: float) -> float:
        """
        Round credit values to two decimal places.
        If exact halfway case occurs, it rounds up as per requirement.
        """
        return round(value * 100) / 100

    def add_credits(self, amount: float) -> float:
        """Add credits and return the new balance"""
        self.credits = self.round_credits(self.credits + amount)
        return self.credits

    def remove_credits(self, amount: float) -> float:
        """Remove credits and return the new balance"""
        self.credits = self.round_credits(self.credits - amount)
        return self.credits

    def add_debt(self, amount: float) -> float:
        """Add debt and return the new balance"""
        self.debt = self.round_credits(self.debt + amount)
        return self.debt

    def remove_debt(self, amount: float) -> float:
        """Remove debt and return the new balance"""
        self.debt = self.round_credits(self.debt - amount)
        return self.debt

    def apply_trait_effects(self):
        """Apply effects from personality traits"""

        self.damage_resist_mod = 1.0
        self.mining_yield_mod = 1.0
        self.buy_price_mod = 1.0
        self.sell_price_mod = 1.0
        self.sensor_range_mod = 1.0
        self.evasion_mod = 1.0
        self.fuel_consumption_mod = 1.0
        self.debt_interest_mod = 1.0

        if self.positive_trait == "Resilient":
            self.damage_resist_mod = 0.9
        elif self.positive_trait == "Resourceful":
            self.mining_yield_mod = 1.05
        elif self.positive_trait == "Charismatic":
            self.buy_price_mod = 0.95
            self.sell_price_mod = 1.05
        elif self.positive_trait == "Perceptive":
            self.sensor_range_mod = 1.15
        elif self.positive_trait == "Quick":
            self.evasion_mod = 1.1
        elif self.positive_trait == "Methodical":
            self.fuel_consumption_mod = 0.92

        if self.negative_trait == "Reckless":
            self.damage_resist_mod *= 1.1
        elif self.negative_trait == "Paranoid":
            self.buy_price_mod *= 1.05
            self.sell_price_mod *= 0.95
        elif self.negative_trait == "Forgetful":
            pass
        elif self.negative_trait == "Impatient":
            self.mining_yield_mod *= 0.9

            pass
        elif self.negative_trait == "Indebted":
            self.debt_interest_mod = 1.1

        self.apply_stat_effects()

    def calculate_debt_interest(self, current_time: int):
        """
        Calculate and apply interest on the debt
        Returns a tuple of (interest_amount, new_debt) if interest was applied, None otherwise
        """

        DAILY_INTEREST_RATE = 0.007

        PERIOD_LENGTH = 24

        if self.last_interest_time == 0:
            days_passed = int(current_time // PERIOD_LENGTH)
            total_interest = 0.0
            current_debt = self.debt
            if days_passed >= 1 and self.debt > 0:
                for _ in range(days_passed):
                    adjusted_rate = DAILY_INTEREST_RATE * self.debt_interest_mod
                    interest = current_debt * adjusted_rate
                    current_debt += interest
                    total_interest += interest
                self.debt = self.round_credits(current_debt)
                self.last_interest_time = days_passed * PERIOD_LENGTH
                return (self.round_credits(total_interest), self.debt)
            else:
                self.last_interest_time = max(0, current_time - PERIOD_LENGTH + 6)
                return None

        time_diff = current_time - self.last_interest_time
        days_passed = int(time_diff // PERIOD_LENGTH)

        if days_passed >= 1 and self.debt > 0:
            total_interest = 0.0
            current_debt = self.debt
            for _ in range(days_passed):
                adjusted_rate = DAILY_INTEREST_RATE * self.debt_interest_mod
                interest = current_debt * adjusted_rate
                current_debt += interest
                total_interest += interest
            self.debt = self.round_credits(current_debt)
            self.last_interest_time += days_passed * PERIOD_LENGTH
            return (self.round_credits(total_interest), self.debt)
        return None

    def to_string(self) -> list[str]:
        trait_info = ""
        if self.positive_trait or self.negative_trait:
            trait_info = f"\nPositive Trait: {self.positive_trait}\nNegative Trait: {self.negative_trait}"

        stats_info = (
            "\nSTATS:"
            + f"\nPerception: {self.perception}"
            + f"\nResilience: {self.resilience}"
            + f"\nIntellect: {self.intellect}"
            + f"\nPresence: {self.presence}"
            + f"\nAdaptability: {self.adaptability}"
            + f"\nTechnical Aptitude: {self.technical_aptitude}"
        )

        skill_info = (
            "\nSKILLS:"
            + f"\nPiloting: {self.piloting}\nEngineering: {self.engineering}\nCombat: {self.combat}"
            + f"\nEducation: {self.education}\nCharisma: {self.charisma}"
            + f"\nUnspent Skill Points: {self.skill_system.unspent_skill_points}"
        )

        return [
            f"Name: {self.name}"
            + f"\nAge: {self.age}"
            + f"\nSex: {self.sex}"
            + f"\nBackground: {self.background}"
            + f"\nCredits: {self.credits}"
            + f"\nDebt: {self.debt}"
            + trait_info
            + stats_info
            + skill_info
            + f"\nReputation States: {self.reputation_states}"
            + f"\nReputation Corporations: {self.reputation_corporations}"
            + f"\nReputation Pirates: {self.reputation_pirates}"
            + f"\nReputation Belters: {self.reputation_belters}"
            + f"\nReputation Traders: {self.reputation_traders}"
            + f"\nReputation Scientists: {self.reputation_scientists}"
            + f"\nReputation Military: {self.reputation_military}"
            + f"\nReputation Explorers: {self.reputation_explorers}"
        ]

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "sex": self.sex,
            "background": self.background,
            "perception": self.perception,
            "resilience": self.resilience,
            "intellect": self.intellect,
            "presence": self.presence,
            "adaptability": self.adaptability,
            "technical_aptitude": self.technical_aptitude,
            "piloting": self.piloting,
            "engineering": self.engineering,
            "combat": self.combat,
            "education": self.education,
            "charisma": self.charisma,
            "skill_system": (
                self.skill_system.to_dict() if hasattr(self, "skill_system") else None
            ),
            "reputation_states": self.reputation_states,
            "reputation_corporations": self.reputation_corporations,
            "reputation_pirates": self.reputation_pirates,
            "reputation_belters": self.reputation_belters,
            "reputation_traders": self.reputation_traders,
            "reputation_scientists": self.reputation_scientists,
            "reputation_military": self.reputation_military,
            "reputation_explorers": self.reputation_explorers,
            "credits": self.credits,
            "debt": self.debt,
            "positive_trait": self.positive_trait,
            "negative_trait": self.negative_trait,
        }

    @classmethod
    def from_dict(cls, data):
        character = cls(
            name=data["name"],
            age=data["age"],
            sex=data["sex"],
            background=data["background"],
            starting_creds=data["credits"],
            starting_debt=data["debt"],
        )

        character.perception = data.get("perception", 5)
        character.resilience = data.get("resilience", 5)
        character.intellect = data.get("intellect", 5)
        character.presence = data.get("presence", 5)
        character.adaptability = data.get("adaptability", 5)
        character.technical_aptitude = data.get("technical_aptitude", 5)

        character.piloting = data.get("piloting", 5)
        character.engineering = data.get("engineering", 5)
        character.combat = data.get("combat", 5)
        character.education = data.get("education", 5)
        character.charisma = data.get("charisma", 5)

        character.reputation_states = data.get("reputation_states", 0)
        character.reputation_corporations = data.get("reputation_corporations", 0)
        character.reputation_pirates = data.get("reputation_pirates", 0)
        character.reputation_belters = data.get("reputation_belters", 0)
        character.reputation_traders = data.get("reputation_traders", 0)
        character.reputation_scientists = data.get("reputation_scientists", 0)
        character.reputation_military = data.get("reputation_military", 0)
        character.reputation_explorers = data.get("reputation_explorers", 0)
        character.positive_trait = data.get("positive_trait", "")
        character.negative_trait = data.get("negative_trait", "")

        character.apply_trait_effects()

        return character


class Contact(Character):
    """A specialized character class representing NPCs the player can interact with."""

    def __init__(
        self,
        name: str,
        description: str,
        location: str,
        specialty: str,
        faction: str,
        age: int = 30,
        sex: str = "unknown",
    ):
        super().__init__(
            name=name,
            age=age,
            sex=sex,
            background="NPC",
            starting_creds=0,
            starting_debt=0,
        )

        self.description = description
        self.location = location
        self.specialty = specialty

        self.primary_faction = faction

        self.available_missions: List = []
        self.dialogue_options: Dict[str, Union[str, int]] = {}

        self.player_standing = 10

        self.last_interaction = "Initial meeting"
        self.met_during = "character_creation"

    def get_info(self) -> Dict[str, Union[str, int]]:
        """Return basic information about the contact."""
        return {
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "specialty": self.specialty,
            "faction": self.primary_faction,
            "standing": self.player_standing,
            "last_interaction": self.last_interaction,
        }

    def update_standing(self, change: int) -> int:
        """Update the contact's standing with the player."""
        self.player_standing = max(0, min(100, self.player_standing + change))
        return self.player_standing

    def record_interaction(self, interaction_type: str) -> None:
        """Record an interaction with this contact."""
        self.last_interaction = interaction_type


class Game:
    """
    Represents the main game state, including the player character, ship,
    current location, and other game-related information.
    """

    def __init__(
        self,
        debug_flag: bool = False,
        mute_flag: bool = False,
        skip_customization: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        if seed is None:
            seed = int(time.time())
        self.seed = seed
        random.seed(self.seed)

        self.global_time = 0
        self.region = Region.generate_random_region("Local Sector", 50)
        self.solar_systems = self.region.solar_systems
        self.current_solar_system_index = 0
        current_system = self.solar_systems[self.current_solar_system_index]
        all_stations = current_system.get_all_stations()
        self.rnd_station = random.choice(all_stations) if all_stations else None
        self.player_character: Character
        self.player_ship: Ship
        self.debug_flag = debug_flag
        self.mute_flag = mute_flag
        self.skipc = skip_customization
        self.sound_init = True if not mute_flag else False
        self.ui = UI()
        self.sound_enabled = not mute_flag

        if self.sound_enabled:
            pg.mixer.init()
            pg.mixer.music.load("Decoherence.mp3")
            pg.mixer.music.play(-1)

    def set_player_character(
        self,
        name: str,
        age: int,
        sex: str,
        background: str,
        starting_creds: float,
        starting_debt: float,
    ):
        self.player_character = Character(
            name, age, sex, background, starting_creds, starting_debt
        )

    def get_player_ship(self) -> Ship:
        assert self.player_ship is not None, (
            "ERROR: There is no player_ship, this should not ever happen so something went very wrong. "
            "Please tell me at github if this happens to you."
        )
        return self.player_ship

    def get_credits(self) -> float:
        """Get player character credits."""
        return round(self.player_character.credits, 2)

    def get_ship(self):
        return self.player_ship

    def get_player_character(self) -> Character:
        assert self.player_character is not None, (
            "ERROR: There is no player_character, this should not ever happen so something went very wrong. "
            "Please tell me at the github page if this happens to you."
        )
        return self.player_character

    def get_current_solar_system(self) -> SolarSystem:
        """Returns the current solar system the player is in."""
        return self.solar_systems[self.current_solar_system_index]

    def add_solar_system(self, solar_system: SolarSystem) -> None:
        """Adds a new solar system to the game."""
        self.solar_systems.append(solar_system)

    def get_solar_system(self):
        return self.get_current_solar_system()

    def advance_time(self, time_delta):
        """
        Advance the game time by the specified timedelta

        Args:
            time_delta (timedelta): The amount of time to advance
        """
        self.global_time += time_delta.total_seconds()

    def get_region(self) -> Region:
        return self.region

    def to_dict(self):
        return {
            "global_time": self.global_time,
            "seed": self.seed,
            "solar_systems": [ss.to_dict() for ss in self.solar_systems],
            "current_solar_system_index": self.current_solar_system_index,
            "player_character": (
                self.player_character.to_dict() if self.player_character else None
            ),
            "player_ship": self.player_ship.to_dict() if self.player_ship else None,
            "debug_flag": self.debug_flag,
            "mute_flag": self.mute_flag,
            "skip_customization": self.skipc,
        }

    @classmethod
    def from_dict(cls, data, ui_instance):
        game = cls(
            debug_flag=data.get("debug_flag", False),
            mute_flag=data.get("mute_flag", False),
            skip_customization=data.get("skip_customization", False),
            seed=data.get("seed", None),
        )
        game.global_time = data["global_time"]

        game.solar_systems = [
            SolarSystem.from_dict(ss_data) for ss_data in data["solar_systems"]
        ]
        game.current_solar_system_index = data.get("current_solar_system_index", 0)
        if not game.solar_systems:
            game.solar_systems = [
                SolarSystem(
                    name="Default Gen",
                    x=0.0,
                    y=0.0,
                )
            ]
            game.current_solar_system_index = 0

        if data["player_character"]:
            game.player_character = Character.from_dict(data["player_character"])
        if data["player_ship"]:
            game.player_ship = Ship.from_dict(data["player_ship"], game)
        game.ui = ui_instance
        return game

    def save_game(self, filename: str = "", human_readable: bool = False):
        """
        Save the current game to a file.

        Args:
            filename: Optional file name for the save
            human_readable: If True, save in human-readable JSON format instead of compressed
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"RSM_SAVE_{timestamp}.json"

        save_path = os.path.join("save", filename)
        os.makedirs("save", exist_ok=True)

        game_data = self.to_dict()

        if not hasattr(self, "save_preference"):
            while True:
                choice = input(
                    "Save as [c]ompressed or [h]uman-readable format? (c/h): "
                ).lower()
                if choice in ["c", "h"]:
                    human_readable = choice == "h"

                    self.save_preference = human_readable
                    break
                else:
                    self.ui.warn_message("Invalid choice. Please enter 'c' or 'h'.")
        else:
            human_readable = self.save_preference

        if human_readable:
            try:
                with open(save_path, "w") as f:
                    json.dump(game_data, f, indent=4)
                self.ui.success_message(
                    f"Game saved to {save_path} (Human-readable format)"
                )
            except IOError as e:
                self.ui.error_message(f"Error saving game: {e}")
        else:
            try:
                from src.utils.compression import compress_save_data

                compressed_data = compress_save_data(game_data)

                original_size = len(json.dumps(game_data))
                compressed_size = len(compressed_data)
                compression_rate = (1 - (compressed_size / original_size)) * 100

                with open(save_path, "w") as f:
                    f.write(compressed_data)

                self.ui.success_message(
                    f"Game saved to {save_path} (Compressed {compression_rate:.1f}%)"
                )
            except IOError as e:
                self.ui.error_message(f"Error saving game: {e}")
            except Exception as e:
                self.ui.error_message(f"Error during save compression: {e}")

                try:
                    with open(save_path, "w") as f:
                        json.dump(game_data, f, indent=4)
                    self.ui.warn_message(f"Saved uncompressed backup to {save_path}")
                except IOError as e:
                    self.ui.error_message(f"Error saving backup: {e}")

    @classmethod
    def load_game(cls, ui_instance, filename: str = ""):
        save_dir = "save"
        if not os.path.exists(save_dir):
            ui_instance.error_message("No save directory found.")
            return None

        if not filename:
            save_files = [
                f
                for f in os.listdir(save_dir)
                if f.startswith("RSM_SAVE_") and f.endswith(".json")
            ]
            if not save_files:
                ui_instance.error_message("No save files found.")
                return None

            save_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(save_dir, f)), reverse=True
            )

            ui_instance.info_message("Available save files:")
            for i, sf in enumerate(save_files):
                mod_time = datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(save_dir, sf))
                )
                formatted_time = mod_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"  {i + 1}. {sf} (Saved: {formatted_time})")

            while True:
                try:
                    choice_str = input("Enter the number of the save file to load: ")
                    choice_idx = int(choice_str) - 1
                    if 0 <= choice_idx < len(save_files):
                        filename = save_files[choice_idx]
                        break
                    else:
                        ui_instance.warn_message("Invalid selection. Please try again.")
                except ValueError:
                    ui_instance.warn_message("Invalid input. Please enter a number.")

        load_path = os.path.join(save_dir, filename)
        if not os.path.exists(load_path):
            ui_instance.error_message(f"Save file {load_path} not found.")
            return None

        try:
            from src.utils.compression import decompress_save_data

            with open(load_path, "r") as f:
                file_content = f.read()

            try:
                if file_content.startswith("RSM_COMPRESSED_V1:"):
                    game_data = decompress_save_data(file_content)
                    ui_instance.info_message("Loaded compressed save file.")
                else:
                    ui_instance.info_message("Loading uncompressed save file...")
                    game_data = json.loads(file_content)
            except json.JSONDecodeError:
                with open(load_path, "r") as f:
                    game_data = json.load(f)
                ui_instance.warn_message("Loaded using fallback method.")

            game_instance = cls.from_dict(game_data, ui_instance)
            ui_instance.success_message(f"Game loaded from {load_path}")
            return game_instance
        except (IOError, json.JSONDecodeError, ValueError) as e:
            ui_instance.error_message(f"Error loading game: {e}")
            return None
