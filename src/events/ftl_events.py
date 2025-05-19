"""
FTL travel events that can occur during faster-than-light jumps.
These events add depth to the FTL travel experience beyond just a time skip.
"""

import random
from colorama import Fore, Style
from time import sleep
from typing import Dict, Optional, Union

# Define a type alias for our event result dictionaries
EventResultDict = Dict[str, Union[str, int, float]]

from src.classes.game import Game, background_choices


# Importing quick_start function to avoid circular imports
def quick_start(game_state: "Game"):
    """Quick start option for players who want to skip the detailed character creation."""
    print(Fore.CYAN + "Quick start selected. Creating a default character...")
    
    # Default character settings
    player_name = "Captain"
    age = 35
    sex = "Male"
    chosen_background_name = "Ex-Miner"
    chosen_positive = "Resourceful"
    chosen_negative = "Impatient"
    
    # Find the chosen background from the background_choices list
    chosen_background = None
    for bg in background_choices:
        if bg.name == chosen_background_name:
            chosen_background = bg
            break
    
    if not chosen_background:
        # Fallback in case the background isn't found
        print(Fore.RED + "Error: Background not found. Using default settings.")
        return
    # Create the character with default settings
    from src.classes.game import Character
    game_state.player_character = Character(
        name=player_name,
        age=age,
        sex=sex,
        background=chosen_background.name,
        starting_creds=5000.0,  # Add default starting credits
        starting_debt=10000.0,  # Add default starting debt
    )
    
    # Apply personality traits
    game_state.player_character.positive_trait = chosen_positive
    game_state.player_character.negative_trait = chosen_negative
    
    print(Fore.GREEN + f"Created character: {player_name}, {age} year old {sex}")
    print(Fore.GREEN + f"Background: {chosen_background.name}")
    print(Fore.GREEN + f"Positive trait: {chosen_positive}")
    print(Fore.GREEN + f"Negative trait: {chosen_negative}")
      # Create default ship
    from src.classes.ship import Ship
    # Use the balanced cruiser template as a default ship
    game_state.player_ship = Ship.from_template("balanced_cruiser", "Rusty Bucket")
    # Position it at the random station
    if game_state.rnd_station and game_state.player_ship is not None and hasattr(game_state.player_ship, "space_object"):
        game_state.player_ship.space_object.position = game_state.rnd_station.position.copy()
    else:
        print(Fore.RED + "Error: Random station or player ship not found for quick start. Ship position not set.")
        # Optionally, set a default position or handle this case as needed
        # if game_state.player_ship and hasattr(game_state.player_ship, "space_object"):
        #     game_state.player_ship.space_object.position = pg.math.Vector2(0, 0) # Example default

    print(Fore.GREEN + f"Ship: {game_state.player_ship.name}")
    print(Fore.CYAN + "Quick start complete. Good luck, Captain!")


# Moving the intro_event function here to avoid import issues
def intro_event(game_state: "Game"):
    # Quick start option
    quick_start_choice = input(
        Fore.YELLOW + "Do you wish to quick start the game (yes/no)? "
    )
    if quick_start_choice.lower() in ["yes", "y"]:
        return quick_start(game_state)

    # Introduction text with more atmosphere and player involvement
    intro_text = [
        "The Terminus Bar. A name that sends shivers down the spines of hardened spacers.",
        "You push through the hissing airlock, hit by a wall of sound and stench.",
        "Neon bathes grimy walls in sickly green, casting long shadows across desperate faces.",
        "Three sets of eyes track you across the room: a one-armed mercenary, a hooded engineer, and the bartender.",
    ]

    for line in intro_text:
        sleep(1.2)
        print(Fore.CYAN + line)

    # First meaningful choice
    print(Fore.YELLOW + "\nWho do you approach?")
    print(Fore.GREEN + "1. The scarred mercenary nursing a synthetic whiskey")
    print(Fore.GREEN + "2. The mysterious engineer tinkering with a neural implant")
    print(
        Fore.GREEN + "3. The bartender with cybernetic eyes that scan your debt profile"
    )

    approach_choice = 0
    while approach_choice not in [1, 2, 3]:
        try:
            approach_choice = int(input(Fore.YELLOW + "Your choice (1-3): "))
            if approach_choice not in [1, 2, 3]:
                print(Fore.RED + "Please enter 1, 2, or 3.")
        except ValueError:
            print(Fore.RED + "Invalid input. Enter a number.")


class FTLEvent:
    """Base class for FTL travel events"""

    def __init__(
        self,
        name: str,
        description: str,
        severity: int = 1,  # 1-5 scale: 1=minor, 5=critical
    ):
        self.name = name
        self.description = description
        self.severity = severity

    def display_intro(self):
        """Display the intro text for the event with appropriate coloring based on severity."""
        severity_colors = {
            1: Fore.CYAN,  # Minor event
            2: Fore.BLUE,  # Low risk
            3: Fore.YELLOW,  # Medium risk
            4: Fore.RED,  # Serious
            5: Fore.MAGENTA,  # Critical
        }
        color = severity_colors.get(self.severity, Fore.WHITE)

        print(f"\n{color}{'=' * 60}")
        print(f"{color}FTL EVENT: {self.name}")
        print(f"{color}{'-' * 60}")
        print(f"{color}{self.description}")
        print(f"{color}{'=' * 60}{Style.RESET_ALL}\n")

    def execute(self, game_state: Game) -> Dict[str, Union[str, int, float]]:
        """Execute the event and return results."""
        raise NotImplementedError("Subclasses must implement execute()")


class AntimatterFluctuation(FTLEvent):
    """Antimatter containment experiences fluctuations during the jump."""

    def __init__(self):
        super().__init__(
            name="Antimatter Containment Fluctuation",
            description="Your ship's antimatter containment field experiences unusual fluctuations during the jump.",
            severity=random.randint(2, 4),  # Varies from concerning to serious
        )

    def execute(self, game_state: Game) -> Dict[str, Union[str, int, float]]:
        player_ship = game_state.get_player_ship()

        # The drop in containment integrity depends on severity
        integrity_drop = self.severity * random.uniform(5.0, 10.0)

        # Apply the drop to containment integrity
        old_integrity = player_ship.containment_integrity
        player_ship.containment_integrity = max(5.0, old_integrity - integrity_drop)

        # Increase failure risk based on severity
        risk_increase = self.severity * random.uniform(1.0, 3.0)
        player_ship.containment_failure_risk += risk_increase
        player_ship.containment_failure_risk = min(
            95.0, player_ship.containment_failure_risk
        )

        # Create result messages
        if self.severity >= 4:
            message = (
                f"{Fore.RED}ALERT! Containment field dropped to {player_ship.containment_integrity:.1f}%!{Style.RESET_ALL}\n"
                f"{Fore.RED}Emergency protocols engaged. Failure risk now at {player_ship.containment_failure_risk:.1f}%.{Style.RESET_ALL}\n"
                f"{Fore.RED}Recommend immediate repairs at the next station.{Style.RESET_ALL}"
            )
        else:
            message = (
                f"{Fore.YELLOW}Containment field integrity reduced to {player_ship.containment_integrity:.1f}%.{Style.RESET_ALL}\n"
                f"{Fore.YELLOW}Current failure risk: {player_ship.containment_failure_risk:.1f}%.{Style.RESET_ALL}\n"
                f"Engineers recommend maintenance when convenient."
            )

        # Present player with options if severe enough
        if self.severity >= 3:
            print(message)
            print("\nOptions:")
            print("1. Apply emergency power to stabilize containment (uses extra fuel)")
            print("2. Recalibrate containment field (takes additional time)")
            print("3. Do nothing and hope for the best")

            choice = input("\nYour decision (1/2/3): ")

            if choice == "1":
                # Use extra fuel to stabilize
                fuel_needed = self.severity * 5.0
                if player_ship.fuel >= fuel_needed:
                    player_ship.fuel -= fuel_needed
                    player_ship.containment_integrity += integrity_drop / 2
                    player_ship.containment_failure_risk -= risk_increase / 2
                    print(
                        f"{Fore.GREEN}Emergency power applied. Containment stabilized at {player_ship.containment_integrity:.1f}%.{Style.RESET_ALL}"
                    )
                    print(f"Fuel reserves depleted by {fuel_needed:.1f} units.")
                else:
                    print(
                        f"{Fore.RED}Not enough fuel! Containment remains unstable!{Style.RESET_ALL}"
                    )

            elif choice == "2":
                # Take extra time but improve containment
                time_needed = self.severity * 300  # seconds
                game_state.global_time += time_needed
                player_ship.containment_integrity += integrity_drop * 0.75
                player_ship.containment_failure_risk -= risk_increase * 0.75
                print(
                    f"{Fore.GREEN}Containment field recalibrated to {player_ship.containment_integrity:.1f}%.{Style.RESET_ALL}"
                )
                print(f"The procedure took {time_needed/60:.1f} additional minutes.")

            else:  # choice 3 or invalid
                print(
                    f"{Fore.YELLOW}You decide to take no action. Containment remains at {player_ship.containment_integrity:.1f}%.{Style.RESET_ALL}"
                )
                # Small chance of further deterioration
                if self.severity == 3:
                    # Minor chance of a secondary effect
                    if random.random() < 0.25: # Already a probability, no need to round
                        further_drop = random.uniform(2.0, 5.0)
                        player_ship.containment_integrity -= further_drop
                        game_state.ui.info_message(f"Minor cascade failure: Containment integrity decreased by an additional {further_drop:.2f}.")
                elif self.severity == 4:
                    # Moderate chance of a secondary effect
                    if random.random() < 0.5: # Already a probability, no need to round
                        further_drop = random.uniform(5.0, 10.0)
                        player_ship.containment_integrity -= further_drop
                        game_state.ui.info_message(f"Warning: Containment integrity dropped by an additional {further_drop:.2f} due to fluctuations.")
                else:  # self.severity == 5
                    # High chance of a critical failure
                    if random.random() < 0.75: # Already a probability, no need to round
                        further_drop = random.uniform(10.0, 20.0)
                        player_ship.containment_integrity -= further_drop
                        game_state.ui.info_message(f"CRITICAL FAILURE: Containment integrity plummeted by {further_drop:.2f}!! Immediate action required!")

                # For minor events, just show the message
                print(message)

        return {
            "old_integrity": int(old_integrity),
            "new_integrity": int(player_ship.containment_integrity),
            "risk_increase": int(risk_increase),
            "current_risk": int(player_ship.containment_failure_risk),
        }


class SpacetimeDisruption(FTLEvent):
    """Encounter unusual spacetime disruption during FTL travel."""

    def __init__(self):
        super().__init__(
            name="Spacetime Disruption",
            description="Your ship encounters a region of disrupted spacetime during FTL travel.",
            severity=random.randint(1, 3),
        )

    def execute(self, game_state: Game) -> Dict[str, Union[str, int, float]]:
        player_ship = game_state.get_player_ship()
        player_character = game_state.get_player_character()

        # Effects based on severity
        if self.severity == 1:
            # Minor - just a delay or time save
            time_effect = random.choice([-1800, -900, 900, 1800])  # +/- 15-30 minutes
            game_state.global_time += time_effect

            if time_effect < 0:
                print(
                    f"{Fore.GREEN}The disruption creates a shortcut through spacetime!{Style.RESET_ALL}"
                )
                print(
                    f"You arrive {abs(time_effect/60):.0f} minutes ahead of schedule."
                )
            else:
                print(
                    f"{Fore.YELLOW}The disruption slows your FTL transit.{Style.RESET_ALL}"
                )
                print(f"Your journey takes an additional {time_effect/60:.0f} minutes.")

            result_time: EventResultDict = {"time_effect": time_effect}
            return result_time

        elif self.severity == 2:
            # Moderate - affects ship systems
            system_affected = random.choice(["sensors", "hull", "antimatter"])
            result_system: Dict[str, Union[str, int, float]] = {}

            if system_affected == "sensors":
                player_ship.sensor_range *= 0.8
                print(
                    f"{Fore.YELLOW}The disruption temporarily reduces sensor efficiency.{Style.RESET_ALL}"
                )
                print(f"Sensor range decreased to {player_ship.sensor_range:.2f} AU.")
                result_system = {
                    "affected": "sensors",
                    "new_range": player_ship.sensor_range,
                }

            elif system_affected == "hull":
                damage = round(random.uniform(3.0, 8.0), 2)
                player_ship.hull_integrity -= damage
                print(
                    f"{Fore.YELLOW}Spacetime stress causes minor hull damage.{Style.RESET_ALL}"
                )
                print(f"Hull integrity reduced to {player_ship.hull_integrity:.1f}%")
                result_system = {"affected": "hull", "damage": damage}

            else:  # antimatter
                loss = round(random.uniform(0.1, 0.3), 2)  # 10-30% of a random resource
                if player_ship.antimatter > loss:
                    player_ship.antimatter -= loss
                    print(
                        f"{Fore.YELLOW}The disruption causes antimatter particles to decay at an accelerated rate.{Style.RESET_ALL}"
                    )
                    print(
                        f"You lost {loss:.2f}g of antimatter. Remaining: {player_ship.antimatter:.2f}g"
                    )
                    result_system = {"affected": "antimatter", "loss": loss}
                else:
                    print(
                        f"{Fore.YELLOW}The disruption could have affected your antimatter reserves, but levels were too low to matter.{Style.RESET_ALL}"
                    )
                    result_system = {"affected": "antimatter", "loss": 0}

            return result_system

        else:  # severity == 3
            # More significant - requires player action
            print(
                f"{Fore.RED}A significant spacetime disruption threatens to throw your ship off course!{Style.RESET_ALL}"
            )
            print("Your options:")
            print("1. Increase power to the engines to push through (uses extra fuel)")
            print("2. Plot a course around the disruption (adds travel time)")
            print("3. Try to ride out the disruption (unpredictable outcome)")

            choice = input("\nYour decision (1/2/3): ")

            if choice == "1":
                fuel_needed = round(random.uniform(10.0, 20.0), 2)
                if player_ship.fuel >= fuel_needed:
                    player_ship.fuel -= fuel_needed
                    print(
                        f"{Fore.GREEN}You push the engines hard and force your way through the disruption.{Style.RESET_ALL}"
                    )
                    print(f"The maneuver consumed {fuel_needed:.1f} units of fuel.")
                    return {
                        "choice": "force_through",
                        "fuel_used": fuel_needed,
                    }
                elif choice == "2":
                    added_time = round(random.uniform(3600, 7200), 2)  # 1-2 hours
                    game_state.global_time += int(added_time)
                    print(
                        f"{Fore.YELLOW}You plot a safer course around the disruption.{Style.RESET_ALL}"
                    )
                    print(
                        f"The detour adds {added_time/3600:.1f} hours to your journey."
                    )
                    result_choice2: EventResultDict = {
                        "choice": "go_around",
                        "added_time": float(added_time),
                    }
                else:
                    print(
                        f"{Fore.RED}Not enough fuel! You're forced to endure the disruption!{Style.RESET_ALL}"
                    )  # Apply random negative effect
                    player_ship.hull_integrity -= random.uniform(5.0, 15.0)
                    print(
                        f"Hull integrity reduced to {player_ship.hull_integrity:.1f}%"
                    )
                    result_choice1_fail: EventResultDict = {
                        "choice": "force_through_failed",
                        "new_hull": float(player_ship.hull_integrity),
                    }
                    return result_choice1_fail
                return result_choice2

            else:  # choice 3 or invalid
                # Roll the dice!
                luck = random.random()
                if luck < 0.4:  # Bad outcome
                    damage = round(random.uniform(10.0, 25.0), 2)
                    player_ship.hull_integrity -= damage
                    print(
                        f"{Fore.RED}The ship is violently tossed by the disruption!{Style.RESET_ALL}"
                    )
                    print(
                        f"Hull integrity reduced to {player_ship.hull_integrity:.1f}%"
                    )
                    result_choice3_bad: EventResultDict = {
                        "choice": "ride_out",
                        "outcome": "bad",
                        "damage": damage,
                    }
                    return result_choice3_bad
                elif luck < 0.8:  # Neutral outcome
                    time_effect = int(random.uniform(1800, 3600))  # 30-60 min delay
                    game_state.global_time += int(time_effect)
                    print(
                        f"{Fore.YELLOW}Your ship is buffeted by the disruption but survives intact.{Style.RESET_ALL}"
                    )
                    print(
                        f"The ordeal adds {time_effect/60:.0f} minutes to your journey."
                    )                    
                    result_choice3_neutral: EventResultDict = {
                        "choice": "ride_out",
                        "outcome": "neutral",
                        "delay": float(time_effect),
                    }
                    return result_choice3_neutral
                else:  # Good outcome - boost to skills from the experience
                    print(
                        f"{Fore.GREEN}You navigate the disruption brilliantly!{Style.RESET_ALL}"
                    )
                    print(f"The experience improves your piloting skills.")
                    if hasattr(player_character, "piloting"):
                        player_character.piloting += 1
                        print(
                            f"Piloting skill increased to {player_character.piloting}."
                        )
                    result_choice3_good: EventResultDict = {
                        "choice": "ride_out",
                        "outcome": "good",
                    }
                    return result_choice3_good


# List of available FTL events with their relative probabilities
FTL_EVENTS = [
    (AntimatterFluctuation, 60),  # 60% chance
    (SpacetimeDisruption, 40),  # 40% chance
]


def get_random_ftl_event() -> Optional[FTLEvent]:
    """
    Get a random FTL event based on weighted probabilities.
    May return None if no event should occur.
    """
    # First determine if an event happens at all (70% chance)
    if random.random() > 0.7:
        return None

    # Select an event based on weighted probabilities
    total_weight = sum(weight for _, weight in FTL_EVENTS)
    r = round(random.uniform(0, total_weight), 2)
    upto = 0
    for event_data in FTL_EVENTS:
        upto += event_data[1]
        if upto >= r:
            return event_data[0]()

    return None  # Fallback
