# filepath: c:\Users\pedro\Desktop\coding\repos\repl-space-miner\src\events\intro_events.py
from time import sleep
from typing import Dict, cast # Added for type hinting
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
BACKGROUND_BONUSES: Dict[str, Dict[str, int]] = {
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


def intro_event(game_state: Game):
    # Quick start option
    quick_start_choice = input(
        Fore.YELLOW + "Do you wish to quick start the game (yes/no)? "
    )    
    if quick_start_choice.lower() in ["yes", "y"]:
            return quick_start(game_state)

    # Introduction text with more atmosphere and player involvement
    intro_text = [
        "The airlock hisses open, a metallic sigh into the cacophony of the Terminus Bar.",
        "It's a name whispered in hushed tones across the star lanes – a wretched hive of scum and villainy, and occasionally, opportunity.",
        "You step inside, the stench of stale synth-ale, unwashed bodies, and ozone assaulting your senses.",
        "Gloomy, flickering neon signs cast long, dancing shadows, painting the grime-caked walls in shades of sickly green and lurid pink.",
        "Faces, hard-bitten and desperate, turn to observe your entrance. A ripple of curiosity, or perhaps predatory interest, passes through the assembled crowd.",
        "Across the smoke-filled room, three figures in particular seem to register your arrival:",
        "A hulking mercenary, scarred and battle-worn, nursing a glass of what looks suspiciously like engine coolant.",
        "A wiry figure hunched over a flickering datapad, tools scattered around them – an engineer, by the looks of it, lost in some complex schematic.",
        "And the bartender, a stoic cyborg whose optical implants whir as they scan you, undoubtedly cross-referencing your face with a dozen outstanding bounties."
    ]

    for line in intro_text:
        sleep(1.5)  # Slightly increased delay for more dramatic effect
        print(Fore.CYAN + line)

    print("\n")
    sleep(1.5) # Slightly increased delay

    # Handle approaching a character
    print(Fore.YELLOW + "The denizens of the Terminus watch your every move. Who do you approach first?\n")
    approach_options = [
        "The battle-scarred mercenary, whose eyes seem to hold a thousand untold war stories.",
        "The enigmatic engineer, seemingly oblivious to the chaos, their fingers dancing across the datapad.",
        "The cybernetic bartender, whose gaze seems to penetrate right through to your credit balance... or lack thereof."
    ]
    for i, option in enumerate(approach_options, 1):
        sleep(0.2)
        print(f"{Fore.GREEN}{i}. {option}")

    valid_approach_choice = False
    approach_choice_num = 0
    while not valid_approach_choice:
        choice_input = input(Fore.WHITE + "\nYour choice (1-3): ")
        if is_valid_int(choice_input):
            choice_num = int(choice_input)
            if 1 <= choice_num <= 3:
                valid_approach_choice = True
                approach_choice_num = choice_num
            else:
                print(Fore.RED + "Please enter a number between 1 and 3.")
        else:
            print(Fore.RED + "Please enter a valid number.")

    sleep(1.5) # Slightly increased delay
    if approach_choice_num == 1:
        print(Fore.CYAN + "\nYou weave through the throng, the mercenary's gaze following you like a targeting system. As you reach his table, he grunts, one scarred eyebrow raised. 'Spit it out, spacer. I ain't got all rotation.'")
    elif approach_choice_num == 2:
        print(Fore.CYAN + "\nYou navigate towards the engineer. As you approach, a faint hum emanates from their direction. Without looking up from the datapad, a synthesized voice cuts through the din: 'If it ain't critical, it can wait. If it is critical, make it quick.'")
    elif approach_choice_num == 3:
        print(Fore.CYAN + "\nYou slide up to the bar. The bartender's optical sensors focus on you with an audible click. 'The usual for newcomers is trouble, with a shot of desperation. What'll it be for you?'")
    
    sleep(2.5)  # Slightly increased pause after interaction
    print("\n")

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
        sex = input(Fore.WHITE + "Enter your sex (male/female): ").lower()
        if sex in ["male", "female"]:
            valid_sex = True
        else:
            print(Fore.RED + "Please enter 'male' or 'female'.")

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
    sleep(1) # Reduced sleep to make way for new questions

    additional_bonus_details = {} # To store what to buff from background specialization

    if background == "Ex-Miner":
        print(Fore.YELLOW + "\nYOUR MINING SPECIALIZATION:")
        miner_focus_options = {
            1: {"text": "Keen Eyes: You excelled at spotting valuable ore pockets. (+1 Perception)", "type": "stat", "name": "perception", "value": 1},
            2: {"text": "Expert Tinkerer: Your knack for keeping aging mining equipment running was legendary. (+1 Engineering)", "type": "skill", "name": "engineering", "value": 1},
            3: {"text": "Belt Navigator: You learned to guide even clumsy mining rigs through treacherous asteroid fields. (+1 Piloting)", "type": "skill", "name": "piloting", "value": 1},
            4: {"text": "Community Ties: You built a reputation for fairness and solidarity among Belter communities. (+5 Belters Standing)", "type": "faction", "name": "belters", "value": 5},
        }
        for i, option_data in miner_focus_options.items():
            sleep(0.2)
            print(f"{Fore.GREEN}{i}. {option_data['text']}")

        valid_focus_choice = False
        while not valid_focus_choice:
            focus_input = input(Fore.WHITE + "\nChoose your specialty (1-4): ")
            if is_valid_int(focus_input):
                focus_choice_num = int(focus_input)
                if focus_choice_num in miner_focus_options:
                    selected_bonus = miner_focus_options[focus_choice_num]
                    additional_bonus_details = {"type": selected_bonus["type"], "name": selected_bonus["name"], "value": selected_bonus["value"]}
                    print(Fore.CYAN + f"Your expertise in {selected_bonus['name']} will undoubtedly be an asset.")
                    valid_focus_choice = True
                else:
                    print(Fore.RED + "Please enter a number between 1 and 4.")
            else:
                print(Fore.RED + "Please enter a valid number.")
        sleep(1.5) # Pause after selection

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
    
    # Apply background bonuses
    bg_bonus: Dict[str, int] = BACKGROUND_BONUSES[background] # More specific type hint
    character = game_state.player_character # shorthand
    
    for loop_stat_key, bonus_val in bg_bonus.items():
        current_stat_key = cast(str, loop_stat_key) # Explicitly cast to str for clarity and type hinting
        
        # Check if it's a skill (now a direct attribute)
        if current_stat_key in ["piloting", "engineering", "combat", "education", "charisma"] and hasattr(character, current_stat_key):
            # Skills from BACKGROUND_BONUSES are the starting values.
            setattr(character, current_stat_key, bonus_val)
        elif current_stat_key in character.faction_standings:
            # Faction standings from BACKGROUND_BONUSES are additive.
            character.faction_standings[current_stat_key] = character.faction_standings.get(current_stat_key, 0) + bonus_val
        elif hasattr(character, current_stat_key): 
            # This handles base stats like 'technical_aptitude', 'resilience', 'perception', etc.
            # These are direct attributes of the Character class, initialized to a base value (e.g., 5).
            # The bonus_val from BACKGROUND_BONUSES should be ADDED to this base value.
            current_base_val = getattr(character, current_stat_key) 
            setattr(character, current_stat_key, current_base_val + cast(int, bonus_val))
        # If current_stat_key is not a skill, not a faction, and not an attribute, it's an undefined bonus.

    # Apply additional stored bonus from background specialization
    if additional_bonus_details:
        bonus_type = cast(str, additional_bonus_details["type"])
        bonus_name = cast(str, additional_bonus_details["name"]) 
        bonus_value = cast(int, additional_bonus_details["value"]) # Assuming value is int
        applied_bonus_message = ""

        if bonus_type == "skill":
            # Specialization bonuses for skills are additive to what background might have set.
            if bonus_name in ["piloting", "engineering", "combat", "education", "charisma"] and hasattr(character, bonus_name):
                current_skill_value = getattr(character, bonus_name)
                setattr(character, bonus_name, current_skill_value + bonus_value)
                applied_bonus_message = f"Your specialization grants an additional +{bonus_value} to {bonus_name} skill."
        elif bonus_type == "faction":
            # Specialization bonuses for factions are additive.
            if bonus_name in character.faction_standings:
                current_faction_value = character.faction_standings.get(bonus_name, 0)
                character.faction_standings[bonus_name] = current_faction_value + bonus_value
                applied_bonus_message = f"Your specialization grants an additional +{bonus_value} to {bonus_name} standing."
        elif bonus_type == "stat": # Handling for base stats like perception
            # Specialization bonuses for base stats are additive to the (base_value + background_bonus).
            if hasattr(character, bonus_name):
                current_stat_val = getattr(character, bonus_name)
                setattr(character, bonus_name, current_stat_val + bonus_value)
                applied_bonus_message = f"Your specialization grants an additional +{bonus_value} to your {bonus_name}."
        
        if applied_bonus_message:
            print(Fore.GREEN + applied_bonus_message)
            sleep(1)
    
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
        sex="female", # Changed default to female for quick_start
        background="Ex-Miner",
        starting_creds=CHARACTER_STARTING_CREDS,
        starting_debt=CHARACTER_STARTING_DEBT
    )
    # Set personality traits as attributes
    game_state.player_character.positive_trait = "Resilient"
    game_state.player_character.negative_trait = "Impatient"
    
    # Apply Ex-Miner background bonuses
    bg_bonus: Dict[str, int] = BACKGROUND_BONUSES["Ex-Miner"] # More specific type hint
    character = game_state.player_character # shorthand

    for loop_key, bonus in bg_bonus.items():
        key = cast(str, loop_key) # Ensure key is treated as a string for clarity and type hinting
        # Check if it's a skill (now a direct attribute)
        if key in ["piloting", "engineering", "combat", "education", "charisma"] and hasattr(character, key):
            setattr(character, key, bonus) # Set as base value
        elif key in character.faction_standings:
            character.faction_standings[key] = character.faction_standings.get(key, 0) + bonus # Add to existing
        elif hasattr(character, key): # It's a base stat
            current_base_val = getattr(character, key)
            setattr(character, key, current_base_val + cast(int, bonus)) # Add to existing base value
    
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
