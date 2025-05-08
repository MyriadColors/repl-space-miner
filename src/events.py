from time import sleep
from colorama import init, Fore

from src.classes.game import background_choices, Game
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

# Background skill bonuses
BACKGROUND_BONUSES = {
    "Ex-Miner": {"mining_speed": 2, "engineering": 2, "belters": 15, "technical_aptitude": 1, "resilience": 1},
    "Corp Dropout": {"education": 2, "charisma": 2, "corporations": -15, "traders": 10, "intellect": 1, "presence": 1},
    "Lunar Drifter": {"piloting": 2, "combat": 1, "pirates": 10, "adaptability": 1, "perception": 1},
    "Void Runner": {"piloting": 3, "explorers": 20, "perception": 2, "adaptability": 1},
    "Xeno-Biologist": {"education": 3, "scientists": 25, "intellect": 2},
    "Discharged Trooper": {"combat": 3, "military": -10, "pirates": 10, "resilience": 2},
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

    # Different interactions based on first choice
    if approach_choice == 1:
        print(
            Fore.CYAN
            + "\nThe mercenary looks up. 'Either you're brave or stupid. Which is it?'"
        )
        print("Her prosthetic arm whirs quietly as she gestures to the empty seat.")
        print(
            "'Name's Vex. Used to captain a blockade runner before... complications.'"
        )
        print("She eyes you with professional interest. 'You look desperate. Good.'")
        contact_name = "Vex"
        bonus_trait = "Combat"
        skill_bonus = {"combat": 2, "piloting": 1}
    elif approach_choice == 2:
        print(
            Fore.CYAN
            + "\nThe engineer's hood shifts, revealing circuitry embedded in their temple."
        )
        print(
            "'Interesting neural patterns,' they murmur. 'You're different from the usual rabble.'"
        )
        print(
            "Mechanical fingers disassemble complex tech without looking. 'I'm Nexus.'"
        )
        print("'Those in need of... alternative solutions find me useful.'")
        contact_name = "Nexus"
        bonus_trait = "Technical"
        skill_bonus = {"engineering": 2, "education": 1}
    else:
        print(Fore.CYAN + "\nThe bartender's synthetic eyes whir as they focus on you.")
        print("'Debt profile: significant. Survival odds: minimal,' she states flatly.")
        print(
            "She slides a drink across the counter. 'On the house. Last courtesy before collection.'"
        )
        print(
            "'I'm Madam Siren. This establishment offers opportunities to the desperate.'"
        )
        contact_name = "Madam Siren"
        bonus_trait = "Trading"
        skill_bonus = {"charisma": 2, "education": 1}

    # More immersive scene continuation
    sleep(1.5)
    print(Fore.CYAN + f"\n{contact_name} slides a datapad across the table.")
    print("'I run jobs for those who can't afford to ask questions. You interested?'")

    response = 0
    while response not in [1, 2]:
        try:
            response = int(input(Fore.YELLOW + "\nTake the job? (1. Yes, 2. No): "))
            if response not in [1, 2]:
                print(Fore.RED + "Please enter 1 or 2.")
        except ValueError:
            print(Fore.RED + "Invalid input. Enter a number.")

    if response == 2:
        print(
            Fore.CYAN
            + f"\n{contact_name}'s expression darkens. 'Nobody walks away from me.'"
        )
        print("The room falls silent. Three enforcers materialize from the shadows.")
        second_chance = input(Fore.YELLOW + "Change your mind? (yes/no): ")
        if second_chance.lower() not in ["yes", "y"]:
            print(Fore.RED + "\nYou stand your ground. Admirable, but foolish.")
            print("The last thing you see is a neural disruptor activating.")
            print(Fore.RED + "\n----- GAME OVER -----")
            exit()
        print(
            Fore.CYAN + "\nA wise decision. The enforcers melt back into the darkness."
        )

    # Character creation with more depth
    print(
        Fore.CYAN
        + f"\n{contact_name} nods approvingly. 'Now, what's the name they'll whisper in fear?'"
    )

    # Player name input validation
    while True:
        player_name = input(Fore.YELLOW + "\nYour name (choose wisely): ")
        if player_name and len(player_name) <= 20:
            break
        print(Fore.RED + "Invalid name. Please enter a name with 1-20 characters.")

    print(
        Fore.CYAN
        + f"\n'Ah, {player_name},' {contact_name} says, testing the weight of your name."
    )
    print("'Everyone in the Outer Rim has a story. What's yours?'")

    # Enhanced background selection with descriptions and skill implications
    print(Fore.YELLOW + "\n--- SELECT YOUR PAST ---")
    enhanced_backgrounds = []

    for i, bg in enumerate(background_choices):
        enhanced_bg = bg
        bg_name = bg.name

        # Define specialized skill bonuses and lore for each background
        if bg_name == "Ex-Miner":
            desc = "Years in asteroid belts taught you resource extraction and survival. Mining expertise, engineering knowledge."
            spec_skills = "Mining +40%, Engineering +2, Belter Reputation +15"
        elif bg_name == "Corp Dropout":
            desc = "Former executive who refused to compromise ethics. Business acumen but corporate enemies."
            spec_skills = "Education +2, Charisma +2, Corporate Reputation -15, Trader Reputation +10"
        elif bg_name == "Lunar Drifter":
            desc = "Raised in the lawless lunar settlements. Street-smart and resourceful, with questionable connections."
            spec_skills = "Piloting +2, Combat +1, Pirate Reputation +10"
        elif bg_name == "Void Runner":
            desc = "Born on long-haul transport ships. Navigation is second nature, space is your true home."
            spec_skills = "Piloting +3, Explorer Reputation +20"
        elif bg_name == "Xeno-Biologist":
            desc = "Studied alien ecosystems until funding was cut. Scientific knowledge but academic debt."
            spec_skills = "Education +3, Scientist Reputation +25"
        elif bg_name == "Discharged Trooper":
            desc = "Elite soldier who questioned orders. Combat training but military blacklisting."
            spec_skills = "Combat +3, Military Reputation -10, Pirate Reputation +10"
        else:
            desc = "A mysterious past with advantages and disadvantages."
            spec_skills = "Balanced skills"

        enhanced_backgrounds.append((enhanced_bg, desc, spec_skills))
        print(Fore.GREEN + f"{i+1}. {enhanced_bg.name}: {desc}")
        print(Fore.BLUE + f"   {spec_skills}")
        print(f"   Starting Credits: {enhanced_bg.credits}, Debt: {enhanced_bg.debt}\n")

    while True:
        try:
            chosen_background_index = int(
                input(
                    Fore.YELLOW
                    + "Choose your background (1-"
                    + str(len(background_choices))
                    + "): "
                )
            )
            if 1 <= chosen_background_index <= len(background_choices):
                break
            else:
                print(
                    Fore.RED
                    + f"Invalid choice. Please choose between 1 and {len(background_choices)}."
                )
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")

    chosen_background = background_choices[chosen_background_index - 1]
    background_skill_bonuses = BACKGROUND_BONUSES.get(chosen_background.name, {})

    # More personalized character details
    print(
        Fore.CYAN
        + f"\n{contact_name} nods knowingly. 'A {chosen_background.name}. That explains a lot.'"
    )

    # Enhanced age and sex selection with implications
    print(Fore.YELLOW + "\nDifferent ages bring different advantages:")
    print(
        Fore.GREEN
        + "- Younger (18-30): Better reflexes (+1 Piloting), less reputation (-5 all factions)"
    )
    print(
        Fore.GREEN
        + "- Middle-aged (31-45): Balanced abilities, established contacts (+5 all factions)"
    )
    print(
        Fore.GREEN
        + "- Older (46-60): Slower reflexes (-1 Piloting), unparalleled experience (+1 Education) and reputation (+10 all factions)"
    )

    while True:
        age_input = input(Fore.YELLOW + "\nYour age (18-60): ")
        if is_valid_int(age_input):
            age = int(age_input)
            if 18 <= age <= 60:
                if 18 <= age <= 30:
                    age_category = "young"
                    age_bonuses = {"piloting": 1, "faction_modifier": -5}
                    print(
                        Fore.CYAN
                        + "You move with the confidence of youth. Speed bonus applied."
                    )
                elif 31 <= age <= 45:
                    age_category = "seasoned"
                    age_bonuses = {"faction_modifier": 5}
                    print(
                        Fore.CYAN
                        + "Your balanced experience serves you well. Reputation bonus applied."
                    )
                else:
                    age_category = "veteran"
                    age_bonuses = {
                        "piloting": -1,
                        "education": 1,
                        "faction_modifier": 10,
                    }
                    print(
                        Fore.CYAN
                        + "Your reputation precedes you. Respect and knowledge bonuses applied."
                    )
                break
            print(Fore.RED + "Invalid age. Please enter an age between 18 and 60.")
        else:
            print(Fore.RED + "Invalid input. Please enter a number.")

    while True:
        sex_input = (
            input(Fore.YELLOW + "\nBiological sex (Male/Female): ").strip().capitalize()
        )
        if sex_input in ["Male", "Female"]:
            sex = sex_input
            break
        print(Fore.RED + "Invalid input. Please enter 'Male' or 'Female'.")

    # Personality trait selection
    print(Fore.YELLOW + "\n--- PERSONALITY TRAITS ---")
    print("Your character's personality affects how you interact with the universe.")

    # Display positive traits
    print(Fore.GREEN + "\nPOSITIVE TRAITS (select one):")
    pos_traits = list(PERSONALITY_TRAITS["Positive"].items())
    for i, (trait, desc) in enumerate(pos_traits, 1):
        print(f"{i}. {trait}: {desc}")

    # Select positive trait
    while True:
        try:
            pos_choice = int(input(Fore.YELLOW + "Choose a positive trait (1-6): "))
            if 1 <= pos_choice <= 6:
                chosen_positive = pos_traits[pos_choice - 1][0]
                break
            else:
                print(
                    Fore.RED + "Invalid choice. Please enter a number between 1 and 6."
                )
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")

    # Display negative traits
    print(Fore.RED + "\nNEGATIVE TRAITS (select one):")
    neg_traits = list(PERSONALITY_TRAITS["Negative"].items())
    for i, (trait, desc) in enumerate(neg_traits, 1):
        print(f"{i}. {trait}: {desc}")

    # Select negative trait
    while True:
        try:
            neg_choice = int(input(Fore.YELLOW + "Choose a negative trait (1-6): "))
            if 1 <= neg_choice <= 6:
                chosen_negative = neg_traits[neg_choice - 1][0]
                break
            else:
                print(
                    Fore.RED + "Invalid choice. Please enter a number between 1 and 6."
                )
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")

    print(
        Fore.CYAN
        + f"\n{contact_name} studies you thoughtfully. 'Yes, I see the {chosen_positive} in you... and"
    )
    print(f"that hint of {chosen_negative}. Makes you... interesting.'")
    
    # Stats point allocation
    base_stats = {
        "perception": 5,
        "resilience": 5, 
        "intellect": 5,
        "presence": 5,
        "adaptability": 5,
        "technical_aptitude": 5,
    }
    
    # Describe what each stat does
    stat_descriptions = {
        "perception": "Affects critical hit chance, hidden discovery chance, sensor range",
        "resilience": "Affects hull integrity, system recovery speed, damage resistance",
        "intellect": "Affects research speed, market analysis, trading efficiency",
        "presence": "Affects prices, reputation gains, faction relations",
        "adaptability": "Affects cross-cultural interactions, skill synergy, environmental adaptation",
        "technical_aptitude": "Affects repair efficiency, salvage success, mining yields"
    }
    
    # Apply background bonuses to stats
    for stat, bonus in background_skill_bonuses.items():
        if stat in base_stats:
            base_stats[stat] += bonus
            
    # Allow manual distribution of stat points
    remaining_stat_points = 5
    print(Fore.YELLOW + "\n--- STAT POINT DISTRIBUTION ---")
    print("Stats are core attributes that reflect your natural capabilities.")
    print(f"You have {remaining_stat_points} stat points to distribute.")
    print("Your current stats (including background bonuses):")
    
    for stat, value in base_stats.items():
        formatted_stat = stat.replace('_', ' ').title()
        print(f"{formatted_stat}: {value} - {stat_descriptions[stat]}")
    
    while remaining_stat_points > 0:
        print(Fore.YELLOW + f"\nRemaining stat points: {remaining_stat_points}")
        stat_to_improve = input(
            "Which stat would you like to improve? (perception/resilience/intellect/presence/adaptability/technical_aptitude): "
        ).lower()
        
        # Handle technical_aptitude with underscore or space
        if stat_to_improve == "technical aptitude":
            stat_to_improve = "technical_aptitude"
        
        if stat_to_improve not in base_stats:
            print(Fore.RED + "Invalid stat. Please choose from the available stats.")
            print("Available stats: perception, resilience, intellect, presence, adaptability, technical_aptitude")
            continue
        
        try:
            points = int(
                input(
                    f"How many points to add to {stat_to_improve.replace('_', ' ')}? (1-{remaining_stat_points}): "
                )
            )
            if 1 <= points <= remaining_stat_points:
                base_stats[stat_to_improve] += points
                remaining_stat_points -= points
                formatted_stat = stat_to_improve.replace('_', ' ').title()
                print(
                    Fore.GREEN
                    + f"{formatted_stat} is now {base_stats[stat_to_improve]}"
                )
            else:
                print(
                    Fore.RED
                    + f"Please enter a number between 1 and {remaining_stat_points}."
                )
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")
    
    # Skill point allocation
    base_skills = {
        "piloting": 5,
        "engineering": 5,
        "combat": 5,
        "education": 5,
        "charisma": 5,
    }

    # Apply background bonuses
    for skill, bonus in background_skill_bonuses.items():
        if skill in base_skills:
            base_skills[skill] += bonus

    # Apply age bonuses
    for skill, bonus in age_bonuses.items():
        if skill in base_skills:
            base_skills[skill] += bonus

    # Apply contact bonus
    for skill, bonus in skill_bonus.items():
        base_skills[skill] += bonus

    # Allow manual distribution of remaining skill points
    remaining_points = 5
    print(Fore.YELLOW + "\n--- SKILL POINT DISTRIBUTION ---")
    print(f"You have {remaining_points} skill points to distribute.")
    print("Your current skills (including background and age bonuses):")
    for skill, value in base_skills.items():
        print(f"{skill.capitalize()}: {value}")

    while remaining_points > 0:
        print(Fore.YELLOW + f"\nRemaining points: {remaining_points}")
        skill_to_improve = input(
            "Which skill would you like to improve? (piloting/engineering/combat/education/charisma): "
        ).lower()

        if skill_to_improve not in base_skills:
            print(Fore.RED + "Invalid skill. Please choose from the available skills.")
            continue

        try:
            points = int(
                input(
                    f"How many points to add to {skill_to_improve}? (1-{remaining_points}): "
                )
            )
            if 1 <= points <= remaining_points:
                base_skills[skill_to_improve] += points
                remaining_points -= points
                print(
                    Fore.GREEN
                    + f"{skill_to_improve.capitalize()} is now {base_skills[skill_to_improve]}"
                )
            else:
                print(
                    Fore.RED
                    + f"Please enter a number between 1 and {remaining_points}."
                )
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")

    # Create character with the enhanced traits and skills
    game_state.set_player_character(
        player_name,
        age,
        sex,
        chosen_background.name,
        chosen_background.credits,
        chosen_background.debt,
    )

    # Apply the skill values to the character
    character = game_state.get_player_character()
    character.piloting = base_skills["piloting"]
    character.engineering = base_skills["engineering"]
    character.combat = base_skills["combat"]
    character.education = base_skills["education"]
    character.charisma = base_skills["charisma"]
    
    # Apply stat values from user selection
    character.perception = base_stats["perception"]
    character.resilience = base_stats["resilience"]
    character.intellect = base_stats["intellect"]
    character.presence = base_stats["presence"]
    character.adaptability = base_stats["adaptability"]
    character.technical_aptitude = base_stats["technical_aptitude"]

    # Apply faction reputation modifiers from background
    for faction, bonus in background_skill_bonuses.items():
        if faction == "belters":
            character.reputation_belters += bonus
        elif faction == "corporations":
            character.reputation_corporations += bonus
        elif faction == "pirates":
            character.reputation_pirates += bonus
        elif faction == "explorers":
            character.reputation_explorers += bonus
        elif faction == "scientists":
            character.reputation_scientists += bonus
        elif faction == "military":
            character.reputation_military += bonus
        elif faction == "traders":
            character.reputation_traders += bonus

    # Apply age-based faction modifier
    faction_mod = age_bonuses.get("faction_modifier", 0)
    character.reputation_belters += faction_mod
    character.reputation_corporations += faction_mod
    character.reputation_pirates += faction_mod
    character.reputation_explorers += faction_mod
    character.reputation_scientists += faction_mod
    character.reputation_military += faction_mod
    character.reputation_traders += faction_mod

    # Store personality traits
    try:
        # Try to set the personality traits directly if possible
        character.positive_trait = chosen_positive
        character.negative_trait = chosen_negative
        # Also trigger any trait effect calculations if the method exists
        if hasattr(character, "apply_trait_effects"):
            character.apply_trait_effects()
    except AttributeError:
        # If the attributes don't exist, print a message instead of crashing
        print(
            Fore.YELLOW
            + "Note: Character traits recorded but will need game update to take effect."
        )

    # Enhanced ship selection with more details and customization
    print(
        Fore.YELLOW
        + f"\n{contact_name} leads you to the docking bay. 'Now for your chariot of fire...'"
    )

    ship_choices = {
        "The Scrapheap (Freighter)": {
            "description": "Slow but sturdy. Massive cargo hold. Fuel-hungry engines. Perfect for traders.",
            "speed": 0.00005,
            "max_fuel": 200,
            "fuel_consumption": 0.075,
            "cargo_capacity": 200,
            "value": 25000,
            "mining_speed": 0.005,
            "sensor_range": 0.1,
            "hull_integrity": 120,
            "shield_capacity": 0.1,
            "specialty": "Trading",
            "lore": "A repurposed bulk hauler from the Saturn colonies. Built to last, not impress.",
        },
        "The Stiletto (Scout)": {
            "description": "Fast and agile. Limited cargo. Efficient engines. Ideal for explorers and couriers.",
            "speed": 0.0005,
            "max_fuel": 75,
            "fuel_consumption": 0.05,
            "cargo_capacity": 25,
            "value": 35000,
            "mining_speed": 0.001,
            "sensor_range": 0.5,
            "hull_integrity": 80,
            "shield_capacity": 0.2,
            "specialty": "Exploration",
            "lore": "Originally designed for rapid response military scouts. Stripped of weapons but kept the speed.",
        },
        "The Borer (Mining Vessel)": {
            "description": "Average speed. Specialized mining equipment. Moderate cargo. The prospector's choice.",
            "speed": 0.00025,
            "max_fuel": 100,
            "fuel_consumption": 0.05,
            "cargo_capacity": 150,
            "value": 30000,
            "mining_speed": 0.05,
            "sensor_range": 0.25,
            "hull_integrity": 100,
            "shield_capacity": 0.05,
            "specialty": "Mining",
            "lore": "A retrofitted industrial excavator. The drill assembly has been converted to an ore processor.",
        },
    }

    print(Fore.YELLOW + "\n--- AVAILABLE VESSELS ---")
    for idx, choice in enumerate(ship_choices.keys(), 1):
        ship_data = ship_choices[choice]
        print(Fore.GREEN + f"\n{idx}. {choice}")
        print(f"   {ship_data['description']}")
        print(f"   {ship_data['lore']}")
        print(f"   Specialty: {ship_data['specialty']}")
        print(f"   Speed: {ship_data['speed']}, Fuel Capacity: {ship_data['max_fuel']}")
        print(
            f"   Cargo Space: {ship_data['cargo_capacity']}, Mining Rate: {ship_data['mining_speed']}"
        )
        print(
            f"   Hull Integrity: {ship_data['hull_integrity']}, Shield Capacity: {ship_data['shield_capacity']}"
        )
        print(f"   Market Value: {ship_data['value']} credits")
        print(f"   Sensor Range: {ship_data['sensor_range']} AU")

    while True:
        try:
            ship_choice = int(input(Fore.YELLOW + "\nSelect your vessel (1-3): "))
            if 1 <= ship_choice <= len(ship_choices):
                chosen_ship = list(ship_choices.keys())[ship_choice - 1]
                break
            else:
                print(
                    Fore.RED
                    + f"Invalid choice. Please choose between 1 and {len(ship_choices)}."
                )
        except ValueError:
            print(
                Fore.RED
                + f"Invalid input. Please enter a number between 1 and {len(ship_choices)}."
            )

    # Ship naming with personality
    print(Fore.YELLOW + "\nThe registration officer yawns. 'Name for this... vehicle?'")
    print(Fore.CYAN + f"{contact_name} smirks. 'Make it memorable.'")

    while True:
        ship_name = input(Fore.YELLOW + "Baptize your ship: ")
        if ship_name and len(ship_name) <= 30:
            break
        print(Fore.RED + "Invalid ship name. Please enter a name with 1-30 characters.")

    # Enhanced ship customization
    print(Fore.YELLOW + f"\nThe {ship_name} awaits. Do you want to add modifications?")
    print(
        Fore.GREEN
        + "Modifications will improve your ship but increase your starting debt."
    )
    print(
        Fore.GREEN
        + "You can choose to skip modifications for a harder start but lower debt."
    )

    mod_decision = ""
    while mod_decision.lower() not in ["y", "yes", "n", "no"]:
        mod_decision = input(Fore.YELLOW + "Add modifications? (yes/no): ")
        if mod_decision.lower() not in ["y", "yes", "n", "no"]:
            print(Fore.RED + "Please enter 'yes' or 'no'.")

    if mod_decision.lower() in ["y", "yes"]:
        print(Fore.YELLOW + f"\nSelect up to TWO modifications:")
        ship_mods = [
            {
                "name": "Enhanced Sensors",
                "desc": "Longer detection range (+0.25 AU)",
                "cost": 5000,
                "stat": "sensor_range",
                "value": 0.25,
            },
            {
                "name": "Hidden Cargo Compartments",
                "desc": "Extra 'unofficial' cargo space (+20 units)",
                "cost": 3000,
                "stat": "cargo_capacity",
                "value": 20.0,
            },
            {
                "name": "Reinforced Hull",
                "desc": "Better damage resistance (+20% hull)",
                "cost": 4000,
                "stat": "hull_integrity",
                "value": 20.0,
            },
            {
                "name": "Engine Tuning",
                "desc": "Improved speed (+10% speed)",
                "cost": 4500,
                "stat": "speed",
                "value": 0.1,
                "multiplier": True,
            },
            {
                "name": "Efficient Fuel System",
                "desc": "Reduced consumption (-10% fuel use)",
                "cost": 3500,
                "stat": "fuel_consumption",
                "value": -0.1,
                "multiplier": True,
            },
            {
                "name": "Mining Laser Upgrade",
                "desc": "Faster resource extraction (+15% mining)",
                "cost": 4000,
                "stat": "mining_speed",
                "value": 0.15,
                "multiplier": True,
            },
        ]

        for i, mod in enumerate(ship_mods, 1):
            print(
                Fore.GREEN
                + f"{i}. {mod['name']}: {mod['desc']} (+{mod['cost']} credits debt)"
            )

        selected_mods = []
        debt_increase = 0

        num_selections = 0
        while num_selections < 2:
            try:
                mod_choice = input(
                    Fore.YELLOW
                    + f"\nSelect modification #{num_selections+1} (1-6 or 'done' to finish): "
                )

                # Allow player to stop at one or zero mods
                if mod_choice.lower() == "done":
                    break

                mod_choice_num = int(mod_choice)
                if 1 <= mod_choice_num <= len(ship_mods):
                    selected_mod = ship_mods[mod_choice_num - 1]
                    if selected_mod in selected_mods:
                        print(
                            Fore.RED
                            + "You've already selected this modification. Choose another."
                        )
                        continue
                    selected_mods.append(selected_mod)
                    # Fixed type error by explicitly casting to int
                    mod_cost = selected_mod.get("cost", 0)
                    if isinstance(mod_cost, (int, float)):
                        debt_increase += int(mod_cost)
                    else:
                        debt_increase += 0
                    print(
                        Fore.CYAN
                        + f"{selected_mod['name']} installed. {selected_mod['desc']}"
                    )
                    num_selections += 1

                    # After first mod, ask if they want another or if they're done
                    if num_selections == 1:
                        print(
                            Fore.GREEN
                            + "You can select one more modification, or type 'done' to finish."
                        )
                else:
                    print(
                        Fore.RED
                        + f"Invalid choice. Please enter a number between 1 and {len(ship_mods)}."
                    )
            except ValueError:
                print(Fore.RED + "Invalid input. Enter a number or 'done'.")

        if not selected_mods:
            print(
                Fore.CYAN
                + "You chose not to add any modifications. The ship remains in its basic configuration."
            )
        elif len(selected_mods) == 1:
            print(
                Fore.CYAN
                + "You decided on a single modification. A wise, economical choice."
            )
    else:
        print(
            Fore.CYAN
            + "You decided to save your credits and avoid additional debt. The ship remains in its basic configuration."
        )
        selected_mods = []
        debt_increase = 0

    # Apply the modifications to the ship data
    ship_data = ship_choices[chosen_ship].copy()
    ship_data["name"] = ship_name

    for mod in selected_mods:
        stat_name = str(mod["stat"])  # Ensure the stat key is a string
        # Safely get the current value and ensure it can be converted to float
        current_value = ship_data.get(stat_name, 0)
        if isinstance(current_value, (int, float, str)):
            current_value = float(current_value)
        else:
            current_value = 0.0

        if mod.get("multiplier", False):
            # Handle percentage-based modifications
            # Safely convert the modifier to float
            mod_value = mod.get("value", 0.0)
            if isinstance(mod_value, (int, float)):
                mod_value = float(mod_value)
            elif isinstance(mod_value, str):
                try:
                    mod_value = float(mod_value)
                except ValueError:
                    mod_value = 0.0
            else:
                mod_value = 0.0

            # Apply multiplier modification (handles both increases and reductions)
            ship_data[stat_name] = current_value * (1.0 + mod_value)
        else:
            # Handle flat additions (convert both to float)
            mod_value = mod.get("value", 0.0)
            if isinstance(mod_value, (int, float)):
                mod_value = float(mod_value)
            elif isinstance(mod_value, str):
                try:
                    mod_value = float(mod_value)
                except ValueError:
                    mod_value = 0.0
            else:
                mod_value = 0.0
            ship_data[stat_name] = current_value + mod_value

    # Add the debt from modifications
    game_state.get_player_character().add_debt(debt_increase)
    print(
        Fore.YELLOW
        + f"Total debt increased by {debt_increase} credits for modifications."
    )

    # Create the enhanced ship
    game_state.player_ship = Ship(
        str(ship_data["name"]),
        game_state.rnd_station.space_object.get_position(),
        ship_data["speed"],
        ship_data["max_fuel"],
        ship_data["fuel_consumption"],
        ship_data["cargo_capacity"],
        ship_data["value"],
        ship_data["mining_speed"],
        ship_data["sensor_range"],
    )

    # Set hull and shield values if the Ship class supports them
    if hasattr(game_state.player_ship, "hull_integrity"):
        # Get the hull integrity value, ensure it's a number, and convert to float
        hull_val = ship_data.get("hull_integrity", 100)  # Default to 100 if missing
        if isinstance(hull_val, (int, float, str)):
            game_state.player_ship.hull_integrity = float(hull_val)
        else:
            game_state.player_ship.hull_integrity = 100.0  # Fallback default value

    if hasattr(game_state.player_ship, "shield_capacity"):
        # Get the shield capacity value, ensure it's a number, and convert to float
        shield_val = ship_data.get("shield_capacity", 0.1)  # Default to 0.1 if missing
        if isinstance(shield_val, (int, float, str)):
            game_state.player_ship.shield_capacity = float(shield_val)
        else:
            game_state.player_ship.shield_capacity = 0.1  # Fallback default value

    print(
        Fore.CYAN
        + f"\nThe {ship_name}'s engines roar to life, vibrating through the docking bay."
    )
    print(f"{contact_name} slaps the hull. 'She's ugly, but she'll fly. For now.'")
    sleep(1)

    # Interactive tutorial mission with more branching options
    print(Fore.YELLOW + "\n--- YOUR FIRST MISSION ---")
    print(Fore.CYAN + f"{contact_name} uploads coordinates to your nav computer.")

    # Customize mission based on background
    if chosen_background.name == "Ex-Miner":
        mission_type = "resource extraction"
        mission_desc = (
            "'I need certain rare minerals that only you'd know how to identify.'"
        )
    elif (
        chosen_background.name == "Corp Dropout"
        or chosen_background.name == "Void Runner"
    ):
        mission_type = "data courier"
        mission_desc = (
            "'Deliver this data cache. Corporate eyes are watching, so be discreet.'"
        )
    elif chosen_background.name == "Xeno-Biologist":
        mission_type = "specimen retrieval"
        mission_desc = (
            "'A biological sample needs collection. Your expertise will be crucial.'"
        )
    else:
        mission_type = "package delivery"
        mission_desc = (
            "'Transport this package to Outpost 7. Simple enough, even for you.'"
        )

    print(Fore.CYAN + f"{contact_name} explains: {mission_desc}")
    print("'Don't open it. Don't scan it. Don't lose it. Questions?'")

    questions = [
        "1. 'What's in the package?'",
        "2. 'How much does it pay?'",
        "3. 'Any dangers I should know about?'",
        "4. 'No questions. Let's do this.'",
    ]

    print("\n")
    for question in questions:
        print(Fore.GREEN + question)

    q_choice = 0
    while q_choice not in [1, 2, 3, 4]:
        try:
            q_choice = int(input(Fore.YELLOW + "Your question (1-4): "))
            if q_choice not in [1, 2, 3, 4]:
                print(Fore.RED + "Please enter a number between 1 and 4.")
        except ValueError:
            print(Fore.RED + "Invalid input. Enter a number.")

    if q_choice == 1:
        print(
            Fore.CYAN
            + f"\n{contact_name} narrows their eyes. 'Medical supplies. Nothing more you need to know.'"
        )
        print("The lie is obvious, but you know better than to press the issue.")
        character.reputation_traders += 5  # They appreciate discretion
    elif q_choice == 2:
        print(
            Fore.CYAN
            + f"\n{contact_name} laughs. '5000 credits and you keep breathing. Fair?'"
        )
        print("The deal isn't negotiable, but at least you know what's coming.")
        if character.charisma >= 8:
            print(
                Fore.CYAN
                + f"Your charisma impresses {contact_name}. 'Fine. 5500 credits.'"
            )
            bonus_pay = 500
        else:
            bonus_pay = 0
    elif q_choice == 3:
        print(
            Fore.CYAN
            + f"\n{contact_name} considers you. 'Smart question. Watch for patrols near the Kestrel Nebula.'"
        )
        print("'And don't trust any distress signals. That's all you get.'")
        character.education += 1  # You learned something valuable
        print(Fore.YELLOW + "Intelligence gained: Education +1")
    else:
        print(
            Fore.CYAN
            + f"\n{contact_name} grins. 'I like your style. No questions, no problems.'"
        )
        character.reputation_pirates += 10  # Pirates respect boldness
        print(Fore.YELLOW + "Reputation gained: Pirates +10")

    # Final send-off with game mechanic tips integrated into dialogue
    tutorial_text = [
        f"\n{contact_name} hands you a datapad with critical information:",
        f"'You're {game_state.get_player_character().debt} credits in debt. Every chip matters.'",
        "'Check your status anytime with 'status' or 'st' command.'",
        "'Fuel is life. Empty tank? You're space debris.'",
        "'Mine asteroids for ore. Sell high, buy low. Basic economics.'",
        "'Upgrade your ship when you can afford it. You'll need every advantage.'",
        "'Pirates and patrols are equally dangerous, just for different reasons.'",
        f"'Complete this {mission_type} job, and I might have more work for a {age_category} {chosen_background.name} like you.'",
        "'Now get moving. The void waits for no one.'",
    ]

    for line in tutorial_text:
        sleep(0.8)  # Slightly faster text for better pacing
        print(Fore.CYAN + line)    # Character summary before starting
    print(Fore.YELLOW + "\n=== CHARACTER SUMMARY ===")
    print(f"Name: {player_name}, Age: {age}, Background: {chosen_background.name}")
    print(
        f"Ship: {ship_name} ({ship_choices[chosen_ship]['specialty']} specialization)"
    )
    print(f"Positive Trait: {chosen_positive}")
    print(f"Negative Trait: {chosen_negative}")
    
    print("\nSTATS:")
    for stat, value in base_stats.items():
        formatted_stat = stat.replace('_', ' ').title()
        print(f"{formatted_stat}: {value}")
        
    print("\nSKILLS:")
    for skill, value in base_skills.items():
        print(f"{skill.capitalize()}: {value}")

    print(
        Fore.YELLOW + "\nYour journey begins. The stars await, {}.".format(player_name)
    )
    print("Type 'help' for available commands.")


def quick_start(game_state: "Game"):

    # Create a standard character
    standard_background = background_choices[0]
    game_state.set_player_character(
        "Test Pilot",
        30,
        "Male",
        standard_background.name,
        standard_background.credits,
        standard_background.debt,
    )

    # Create a standard ship
    standard_ship = {
        "name": "Quick Tester",
        "speed": 0.0005,
        "max_fuel": 100,
        "fuel_consumption": 0.05,
        "cargo_capacity": 100,
        "value": 30000,
        "mining_speed": 0.01,
        "sensor_range": 0.25,
    }

    game_state.player_ship = Ship(
        str(standard_ship["name"]),
        game_state.rnd_station.space_object.get_position(),
        standard_ship["speed"],
        standard_ship["max_fuel"],
        standard_ship["fuel_consumption"],
        standard_ship["cargo_capacity"],
        standard_ship["value"],
        standard_ship["mining_speed"],
        standard_ship["sensor_range"],
    )

    print("Quick start initiated. Standard character and ship created.")
    print(
        f"Character: Test Pilot, Age: 30, Sex: Male, Background: {standard_background.name}"
    )
    print(f"Ship: {standard_ship['name']}")
    print("Type 'status' or 'st' to check your ship and character details.")

    # Skip tutorial and first mission selection
    print("Tutorial and first mission selection skipped for quick start.")
    print("You're ready to explore the galaxy. Good luck, spacer!")

    return
