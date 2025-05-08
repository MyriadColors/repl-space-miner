import json
import os
from datetime import datetime
from dataclasses import dataclass
from random import choice
from colorama import Fore, Back, Style, init

from src.classes.ship import Ship
from src.classes.solar_system import SolarSystem

# Initialize colorama
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
        self.credits: float = self.round_credits(starting_creds)
        self.debt: float = self.round_credits(starting_debt)
        self.last_interest_time = 0  # Store the last time interest was applied
        # New personality traits
        self.positive_trait = ""
        self.negative_trait = ""
        # Trait effect modifiers (default to 1.0 = no effect)
        self.damage_resist_mod = 1.0
        self.mining_yield_mod = 1.0
        self.buy_price_mod = 1.0
        self.sell_price_mod = 1.0
        self.sensor_range_mod = 1.0
        self.evasion_mod = 1.0
        self.fuel_consumption_mod = 1.0
        self.debt_interest_mod = 1.0
        # Banking system attributes
        self.bank_transactions: list[dict] = []
        self.savings = 0.0
        self.savings_interest_rate = 0.02  # 2% weekly interest rate
        self.last_savings_interest_time = (
            0  # Store the last time savings interest was applied
        )

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
        # Reset modifiers to default
        self.damage_resist_mod = 1.0
        self.mining_yield_mod = 1.0
        self.buy_price_mod = 1.0
        self.sell_price_mod = 1.0
        self.sensor_range_mod = 1.0
        self.evasion_mod = 1.0
        self.fuel_consumption_mod = 1.0
        self.debt_interest_mod = 1.0

        # Apply positive trait effects
        if self.positive_trait == "Resilient":
            self.damage_resist_mod = 0.9  # 10% less damage
        elif self.positive_trait == "Resourceful":
            self.mining_yield_mod = 1.05  # 5% more ore
        elif self.positive_trait == "Charismatic":
            self.buy_price_mod = 0.95  # 5% cheaper purchases
            self.sell_price_mod = 1.05  # 5% better sales
        elif self.positive_trait == "Perceptive":
            self.sensor_range_mod = 1.15  # 15% better sensors
        elif self.positive_trait == "Quick":
            self.evasion_mod = 1.1  # 10% better evasion
        elif self.positive_trait == "Methodical":
            self.fuel_consumption_mod = 0.92  # 8% less fuel use

        # Apply negative trait effects
        if self.negative_trait == "Reckless":
            self.damage_resist_mod *= 1.1  # 10% more damage
        elif self.negative_trait == "Paranoid":
            self.buy_price_mod *= 1.05  # 5% higher prices overall
            self.sell_price_mod *= 0.95  # 5% worse sales
        elif self.negative_trait == "Forgetful":
            # Forgetful has a random chance effect, handled in mining
            pass
        elif self.negative_trait == "Impatient":
            self.mining_yield_mod *= 0.9  # 10% less mining efficiency
        elif self.negative_trait == "Superstitious":
            # Superstitious has special event handling, no modifier needed
            pass
        elif self.negative_trait == "Indebted":
            self.debt_interest_mod = 1.1  # 10% higher interest

    def calculate_debt_interest(self, current_time: int):
        """
        Calculate and apply weekly interest on the debt
        Returns a tuple of (interest_amount, new_debt) if interest was applied, None otherwise
        """
        # Weekly interest rate (5% per week)
        WEEKLY_INTEREST_RATE = 0.05
        # Define a week as 168 hours (7 days * 24 hours)
        WEEK_LENGTH = 168

        # Check if a week has passed since last interest calculation
        if self.last_interest_time == 0:
            # First time tracking interest - just store current time
            self.last_interest_time = current_time
            return None

        weeks_passed = (current_time - self.last_interest_time) // WEEK_LENGTH

        if weeks_passed >= 1:
            # Apply interest for each week passed
            total_interest = 0.0
            current_debt = self.debt

            for _ in range(weeks_passed):
                # Apply the "Indebted" trait modifier if it exists
                adjusted_rate = WEEKLY_INTEREST_RATE * self.debt_interest_mod
                interest = current_debt * adjusted_rate
                current_debt += interest
                total_interest += interest

            # Update debt and last interest time
            self.debt = self.round_credits(current_debt)
            self.last_interest_time = current_time

            return (self.round_credits(total_interest), self.debt)

        return None

    def to_string(self) -> list[str]:
        trait_info = ""
        if self.positive_trait or self.negative_trait:
            trait_info = f"\nPositive Trait: {self.positive_trait}\nNegative Trait: {self.negative_trait}"

        skill_info = (
            f"\nPiloting: {self.piloting}\nEngineering: {self.engineering}\nCombat: {self.combat}"
            + f"\nEducation: {self.education}\nCharisma: {self.charisma}"
        )

        return [
            f"Name: {self.name}"
            + f"\nAge: {self.age}"
            + f"\nSex: {self.sex}"
            + f"\nBackground: {self.background}"
            + f"\nCredits: {self.credits}"
            + f"\nDebt: {self.debt}"
            + trait_info
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
            "piloting": self.piloting,
            "engineering": self.engineering,
            "combat": self.combat,
            "education": self.education,
            "charisma": self.charisma,
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

        # Set skill values
        character.piloting = data.get("piloting", 5)
        character.engineering = data.get("engineering", 5)
        character.combat = data.get("combat", 5)
        character.education = data.get("education", 5)
        character.charisma = data.get("charisma", 5)

        # Set reputation values
        character.reputation_states = data.get("reputation_states", 0)
        character.reputation_corporations = data.get("reputation_corporations", 0)
        character.reputation_pirates = data.get("reputation_pirates", 0)
        character.reputation_belters = data.get("reputation_belters", 0)
        character.reputation_traders = data.get("reputation_traders", 0)
        character.reputation_scientists = data.get("reputation_scientists", 0)
        character.reputation_military = data.get("reputation_military", 0)
        character.reputation_explorers = data.get("reputation_explorers", 0)

        # Set personality traits if available
        character.positive_trait = data.get("positive_trait", "")
        character.negative_trait = data.get("negative_trait", "")

        # Apply trait effects
        character.apply_trait_effects()

        return character


class Game:

    def __init__(
        self,
        debug_flag: bool = False,
        mute_flag: bool = False,
        skip_customization: bool = False,
    ) -> None:
        self.global_time: int = 0
        self.solar_system: SolarSystem = SolarSystem(200, 100)
        self.rnd_station = choice(self.solar_system.stations)
        self.player_character: Character | None = None
        self.player_ship: Ship | None = None
        self.debug_flag = debug_flag
        self.mute_flag = mute_flag
        self.skipc = skip_customization
        self.sound_init = True if not mute_flag else False
        self.ui = UI()

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

    def to_dict(self):
        return {
            "global_time": self.global_time,
            "solar_system": self.solar_system.to_dict(),
            "player_character": (
                self.player_character.to_dict() if self.player_character else None
            ),
            "player_ship": self.player_ship.to_dict() if self.player_ship else None,
            "debug_flag": self.debug_flag,
            "mute_flag": self.mute_flag,
            "skip_customization": self.skipc,  # Skip customization flag
        }

    @classmethod
    def from_dict(cls, data, ui_instance):
        game = cls(
            debug_flag=data.get("debug_flag", False),
            mute_flag=data.get("mute_flag", False),
            skip_customization=data.get("skip_customization", False),
        )
        game.global_time = data["global_time"]
        game.solar_system = SolarSystem.from_dict(data["solar_system"])
        if data["player_character"]:
            game.player_character = Character.from_dict(data["player_character"])
        if data["player_ship"]:
            game.player_ship = Ship.from_dict(
                data["player_ship"], game
            )  # Pass game instance
        game.ui = ui_instance  # Assign the passed UI instance
        return game

    def save_game(self, filename: str = ""):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"RSM_SAVE_{timestamp}.json"

        save_path = os.path.join("save", filename)
        os.makedirs("save", exist_ok=True)  # Ensure save directory exists

        game_data = self.to_dict()

        try:
            with open(save_path, "w") as f:
                json.dump(game_data, f, indent=4)
            self.ui.success_message(f"Game saved to {save_path}")
        except IOError as e:
            self.ui.error_message(f"Error saving game: {e}")

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

            # Sort files by modification time (newest first)
            save_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(save_dir, f)), reverse=True
            )

            ui_instance.info_message("Available save files:")
            for i, sf in enumerate(save_files):
                # Get modification time and format it
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
            with open(load_path, "r") as f:
                game_data = json.load(f)

            game_instance = cls.from_dict(game_data, ui_instance)
            ui_instance.success_message(f"Game loaded from {load_path}")
            return game_instance
        except (IOError, json.JSONDecodeError, ValueError) as e:
            ui_instance.error_message(f"Error loading game: {e}")
            return None
