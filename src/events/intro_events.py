# filepath: c:\Users\pedro\Desktop\coding\repos\repl-space-miner\src\events\intro_events.py
from time import sleep
from colorama import init, Fore
import pygame as pg

from src.classes.game import background_choices, Game, Character
from src.classes.ship import Ship
from src.helpers import is_valid_int

init(autoreset=True)

# Personality traits with gameplay effects
PERSONALITY_TRAITS = {
    "Positive": {
        "Resilient": "Recover from setbacks faster. +10% damage resistance.",
        "Resourceful": "Find more resources when mining. +5% ore yield.",
        "Charismatic": "Better prices when trading. -5% on purchases, +5% on sales.",
        "Perceptive": "Better chance to detect valuable items. +15% sensor range.",
        "Quick": "Faster reaction times. +10% evasion chance in combat.",
        "Methodical": "More efficient with resources. -8% fuel consumption.",
    },
    "Negative": {
        "Reckless": "Higher chance of accidents. +10% damage taken.",
        "Paranoid": "Overreact to threats. -5% trading prices due to rush decisions.",
        "Forgetful": "Miss details. 5% chance to lose small amounts of cargo.",
        "Impatient": "Rush through tasks. -10% mining efficiency.",
        "Superstitious": "Avoid 'unlucky' opportunities. Miss occasional deals.",
        "Indebted": "Poor money management. +10% interest on debt.",
    },
}

# Background skill bonuses - expanded to fully determine character skills
BACKGROUND_BONUSES = {
    "Ex-Miner": {
        # Stats
        "technical_aptitude": 2, "resilience": 2, 
        # Skills
        "piloting": 4, "engineering": 8, "combat": 4, "education": 3, "charisma": 3,
        # Factions
        "belters": 20
    },
    "Corp Dropout": {
        # Stats
        "intellect": 2, "presence": 2,
        # Skills
        "piloting": 3, "engineering": 4, "combat": 3, "education": 8, "charisma": 7, 
        # Factions
        "corporations": -20, "traders": 15
    },
    "Lunar Drifter": {
        # Stats
        "adaptability": 2, "perception": 2,
        # Skills
        "piloting": 6, "engineering": 3, "combat": 7, "education": 3, "charisma": 5,
        # Factions
        "pirates": 15
    },
    "Void Runner": {
        # Stats
        "perception": 3, "adaptability": 1,
        # Skills
        "piloting": 8, "engineering": 5, "combat": 4, "education": 4, "charisma": 3,
        # Factions
        "explorers": 25
    },
    "Xeno-Biologist": {
        # Stats
        "intellect": 3, "technical_aptitude": 1,
        # Skills
        "piloting": 3, "engineering": 5, "combat": 2, "education": 9, "charisma": 5,
        # Factions
        "scientists": 30
    },
    "Discharged Trooper": {
        # Stats
        "resilience": 3, "perception": 1,
        # Skills
        "piloting": 5, "engineering": 4, "combat": 9, "education": 4, "charisma": 2,
        # Factions
        "military": -10, "pirates": 15
    },
}


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

    print("\n")
    sleep(1)

    # Character creation sequence
    print(Fore.YELLOW + "REPL SPACE MINER - CHARACTER CREATION\n")
    sleep(0.5)

    # Get basic character info with input validation
    name = ""
    while not name:
        name = input(Fore.WHITE + "Enter your name: ")
        if not name:
            print(Fore.RED + "You must enter a name.")

    valid_age = False
    age = 0
    while not valid_age:
        age_input = input(Fore.WHITE + "Enter your age: ")
        if is_valid_int(age_input):
            age = int(age_input)
            if 18 <= age <= 90:
                valid_age = True
            else:
                print(Fore.RED + "Age must be between 18 and 90.")
        else:
            print(Fore.RED + "Please enter a valid number.")

    valid_sex = False
    sex = ""
    while not valid_sex:
        sex = input(Fore.WHITE + "Enter your sex (male/female/non-binary/other): ").lower()
        if sex in ["male", "female", "non-binary", "other"]:
            valid_sex = True
        else:
            print(Fore.RED + "Please enter 'male', 'female', 'non-binary', or 'other'.")

    # Select background with gameplay effects
    print(Fore.YELLOW + "\nCHOOSE YOUR BACKGROUND\n")
    sleep(0.5)
    for i, bg in enumerate(background_choices, 1):
        sleep(0.2)
        print(f"{Fore.GREEN}{i}. {bg}")

    valid_background = False
    background = ""
    while not valid_background:
        bg_choice = input(Fore.WHITE + "\nSelect background (1-6): ")
        if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 6:
            background = background_choices[int(bg_choice) - 1].name
            valid_background = True
        else:
            print(Fore.RED + "Please enter a number between 1 and 6.")

    # Display background description based on choice
    print(f"\n{Fore.YELLOW}BACKGROUND: {background}")
    bg_descriptions = {
        "Ex-Miner": "You've spent years breaking rocks in the belt. Your technical skills are superior, and you know how to survive in harsh environments. You have connections with the Belters Union.",
        "Corp Dropout": "Former middle management at a mega-corp. You understand business and have education, but corporations might not view you favorably after your 'strategic exit'.",
        "Lunar Drifter": "You've lived in the shadows of lunar cities, making deals and sometimes working outside the law. Your street smarts are unmatched.",
        "Void Runner": "Born on long-haul freighters, you've spent more time in space than planetside. Your piloting skills are exceptional.",
        "Xeno-Biologist": "You've studied life across the solar system. Your scientific knowledge is valuable, particularly to research organizations.",
        "Discharged Trooper": "Former military with combat experience. Your tactical skills are sharp, but your discharge wasn't entirely honorable."
    }

    print(f"{Fore.CYAN}{bg_descriptions[background]}")
    sleep(2)

    # Choose positive trait
    print(Fore.YELLOW + "\nCHOOSE A POSITIVE TRAIT\n")
    pos_traits = list(PERSONALITY_TRAITS["Positive"].keys())
    for i, trait in enumerate(pos_traits, 1):
        sleep(0.2)
        print(f"{Fore.GREEN}{i}. {trait}: {PERSONALITY_TRAITS['Positive'][trait]}")

    valid_pos_trait = False
    positive_trait = ""
    while not valid_pos_trait:
        trait_choice = input(Fore.WHITE + "\nSelect positive trait (1-6): ")
        if is_valid_int(trait_choice) and 1 <= int(trait_choice) <= 6:
            positive_trait = pos_traits[int(trait_choice) - 1]
            valid_pos_trait = True
        else:
            print(Fore.RED + "Please enter a number between 1 and 6.")

    # Choose negative trait
    print(Fore.YELLOW + "\nCHOOSE A NEGATIVE TRAIT\n")
    neg_traits = list(PERSONALITY_TRAITS["Negative"].keys())
    for i, trait in enumerate(neg_traits, 1):
        sleep(0.2)
        print(f"{Fore.RED}{i}. {trait}: {PERSONALITY_TRAITS['Negative'][trait]}")

    valid_neg_trait = False
    negative_trait = ""
    while not valid_neg_trait:
        trait_choice = input(Fore.WHITE + "\nSelect negative trait (1-6): ")
        if is_valid_int(trait_choice) and 1 <= int(trait_choice) <= 6:
            negative_trait = neg_traits[int(trait_choice) - 1]
            valid_neg_trait = True
        else:
            print(Fore.RED + "Please enter a number between 1 and 6.")

    # Ship customization
    print(Fore.YELLOW + "\nCUSTOMIZE YOUR SHIP\n")
    sleep(0.5)

    valid_ship_name = False
    ship_name = ""
    while not valid_ship_name:
        ship_name = input(Fore.WHITE + "Name your ship: ")
        if ship_name:
            valid_ship_name = True
        else:
            print(Fore.RED + "Your ship needs a name.")

    # Ship appearance customization
    print(Fore.YELLOW + "\nCHOOSE YOUR SHIP'S APPEARANCE\n")
    appearance_options = [
        "Rust Bucket: A well-worn vessel with patches of mismatched plating",
        "Sleek Runner: Modern lines with a polished, aerodynamic finish",
        "Industrial Hauler: Bulky and practical with visible reinforcements",
        "Retrofitted Classic: An older model with visible modifications",
        "Stealth Profile: Dark coating with minimal external features",
        "Colorful Maverick: Bright custom paintjob that stands out anywhere"
    ]

    for i, appearance in enumerate(appearance_options, 1):
        sleep(0.2)
        print(f"{Fore.GREEN}{i}. {appearance}")

    valid_appearance = False
    ship_appearance = ""
    while not valid_appearance:
        appearance_choice = input(Fore.WHITE + "\nSelect ship appearance (1-6): ")
        if is_valid_int(appearance_choice) and 1 <= int(appearance_choice) <= 6:
            ship_appearance = appearance_options[int(appearance_choice) - 1].split(":")[0]
            valid_appearance = True
        else:
            print(Fore.RED + "Please enter a number between 1 and 6.")

    # Sound effects question
    print(Fore.YELLOW + "\nGAME OPTIONS\n")
    sound_choice = input(Fore.WHITE + "Enable sound effects? (yes/no): ")
    enable_sound = sound_choice.lower() in ["yes", "y"]

    if enable_sound:
        # Initialize pygame mixer
        pg.mixer.init()
        pg.mixer.music.set_volume(0.5)

    # Create character & ship objects with chosen attributes
    from src.classes.ship import Ship
    from src.classes.game import Game, Character  # Character is defined in game.py
    
    # Default starting values
    CHARACTER_STARTING_CREDS = 1000
    CHARACTER_STARTING_DEBT = 5000
    
    # Create character instance
    game_state.player_character = Character(
        name=name, 
        age=age, 
        sex=sex,
        background=background,
        starting_creds=CHARACTER_STARTING_CREDS,
        starting_debt=CHARACTER_STARTING_DEBT
    )
    # Set personality traits as attributes
    game_state.player_character.positive_trait = positive_trait
    game_state.player_character.negative_trait = negative_trait
    
    # Initialize skills and faction standings if not already set
    # These are now initialized in the Character class constructor
    # if not hasattr(game_state.player_character, 'skills'):
    #     game_state.player_character.skills = {
    #         "piloting": 0, "engineering": 0, "combat": 0, 
    #         "education": 0, "charisma": 0
    #     }
    
    # if not hasattr(game_state.player_character, 'faction_standings'):
    #     game_state.player_character.faction_standings = {
    #         "belters": 0, "corporations": 0, "pirates": 0, 
    #         "explorers": 0, "scientists": 0, "military": 0, "traders": 0
    #     }
    
    # Apply background bonuses to skills
    bg_bonus = BACKGROUND_BONUSES[background] # Define bg_bonus
    for skill, bonus in bg_bonus.items():
        if skill in game_state.player_character.skills:
            game_state.player_character.skills[skill] = bonus
        elif skill in game_state.player_character.faction_standings:
            game_state.player_character.faction_standings[skill] += bonus
    
    # Create ship (removed appearance parameter if not supported)
    game_state.player_ship = Ship(name=ship_name, appearance=ship_appearance)
    # game_state.player_ship.appearance = ship_appearance  # Set appearance as attribute instead
    
def quick_start(game_state: "Game"):
    """Create a character with default values for quick start."""
    from src.classes.game import Character
    from src.classes.ship import Ship
    
    # Default starting values
    CHARACTER_STARTING_CREDS = 1000
    CHARACTER_STARTING_DEBT = 5000
    # Create default character
    game_state.player_character = Character(
        name="Space Miner", 
        age=30, 
        sex="non-binary",
        background="Ex-Miner",
        starting_creds=CHARACTER_STARTING_CREDS,
        starting_debt=CHARACTER_STARTING_DEBT
    )
    # Set personality traits as attributes
    game_state.player_character.positive_trait = "Resilient"
    game_state.player_character.negative_trait = "Impatient"
    
    # Apply Ex-Miner background bonuses
    bg_bonus = BACKGROUND_BONUSES["Ex-Miner"]
    for skill, bonus in bg_bonus.items():
        if skill in game_state.player_character.skills:
            game_state.player_character.skills[skill] = bonus
        elif skill in game_state.player_character.faction_standings:
            game_state.player_character.faction_standings[skill] += bonus
    
    # Create ship
    game_state.player_ship = Ship(name="Rusty Bucket", appearance="Rust Bucket")
    
    # Default sound to off in quick start
    game_state.sound_enabled = False
    
    print(f"\n{Fore.GREEN}Quick start initiated! Welcome aboard the Rusty Bucket.")
    sleep(1)
    print(f"{Fore.YELLOW}Your starting credits: {CHARACTER_STARTING_CREDS}")
    print(f"{Fore.RED}Your starting debt: {CHARACTER_STARTING_DEBT}")
    print(f"{Fore.RED}However, being Impatient might present some challenges.")
    sleep(1)
    
    return game_state
