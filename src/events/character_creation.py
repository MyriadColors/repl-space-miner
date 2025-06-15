from typing import Dict, cast, Any
from colorama import init, Fore
import pygame as pg

from src.classes.game import Game
from src.classes.contacts import get_contact
from src.helpers import is_valid_int
from src.data import SHIP_TEMPLATES, BACKGROUND_BONUSES

init(autoreset=True)


def character_creation_event(
    game_state: Game,
):  # Default initializations for variables that might not be set in all paths
    ship_name: str = "The Void Jumper"  # Default ship name
    ship_appearance: str = "Stock Model"  # Default ship appearance
    positive_trait: str = "Adaptable"  # Default positive trait
    negative_trait: str = "Wary"  # Default negative trait
    dialogue_trait_hint: str = ""  # Initialize this as it's used to set positive_trait
    ship_template_id: str = "balanced_cruiser"  # Default ship template ID
    ship_idx: int = 3  # Default to balanced cruiser (index 3)

    # Initialize variables for trait selection to avoid "possibly unbound" errors
    trait_idx: int = 1  # Default value for positive trait index
    neg_trait_idx: int = 1  # Default value for negative trait index
    app_idx: int = 1  # Default value for all branches
    background: str = "Unknown"  # Default value for all branches
    # Initialize additional_bonus_details
    additional_bonus_details: Dict[str, Any] = {}

    # Introduction text with more atmosphere and player involvement
    intro_text = [
        "The airlock hisses open, a metallic sigh into the cacophony of the Terminus Bar.",
        "It's a name whispered in hushed tones across the star lanes – a wretched hive of scum and villainy, and occasionally, opportunity.",
        "You step inside, the stench of stale synth-ale, unwashed bodies, and ozone assaulting your senses.",
        "Gloomy, flickering neon signs cast long, dancing shadows, painting the grime-caked walls in shades of sickly green and lurid pink.",
        "Faces, hard-bitten and desperate, turn to observe your entrance. A ripple of curiosity, or perhaps predatory interest, passes through the assembled crowd.",
        "Across the smoke-filled room, four figures in particular seem to register your arrival:",
        "A hulking mercenary, scarred and battle-worn, nursing a glass of what looks suspiciously like engine coolant.",
        "A striking woman in form-fitting combat gear, weapons holstered at her hips, who studies you with cool calculation from a corner booth.",
        "A wiry figure hunched over a flickering datapad, tools scattered around them – an engineer, by the looks of it, lost in some complex schematic.",
        "And the bartender, a stoic cyborg whose optical implants whir as they scan you, undoubtedly cross-referencing your face with a dozen outstanding bounties.",
    ]

    for line in intro_text:
        # sleep(1.5)
        game_state.ui.info_message(Fore.CYAN + line)

    game_state.ui.info_message("\n")
    # sleep(
    #    1.5
    # )  # Slightly increased delay
    # Get basic character info with input validation before approaching anyone
    game_state.ui.info_message(
        Fore.CYAN
        + "\nThe station's customs terminal had required your basic information before granting access..."
    )
    # sleep(1.5)

    name = ""
    while not name:
        name = input(Fore.WHITE + "Enter your name: ")
        if not name:
            game_state.ui.info_message(Fore.RED + "You must enter a name.")

    valid_age = False
    age = 0
    while not valid_age:
        age_input = input(Fore.WHITE + "Enter your age: ")
        if is_valid_int(age_input):
            age = int(age_input)
            if 18 <= age <= 90:
                valid_age = True
            else:
                game_state.ui.info_message(
                    Fore.RED + "Age must be between 18 and 90.")
        else:
            game_state.ui.info_message(
                Fore.RED + "Please enter a valid number.")

    valid_sex = False
    sex = ""
    while not valid_sex:
        sex = input(Fore.WHITE + "Enter your sex (male/female): ").lower()
        if sex in ["male", "female"]:
            valid_sex = True
        else:
            game_state.ui.info_message(
                Fore.RED + "Please enter 'male' or 'female'.")

    # sleep(1.5)
    game_state.ui.info_message(
        Fore.CYAN
        + f"\nYou, {name}, take a deep breath as you look around the bar. The data pad in your pocket contains your remaining credits and the reminder of your substantial debt."
    )
    # sleep(1)  # Handle approaching a character
    game_state.ui.info_message(
        Fore.YELLOW
        + "The denizens of the Terminus watch your every move. Who do you approach first?\n"
    )
    approach_options = [
        "The battle-scarred mercenary, whose eyes seem to hold a thousand untold war stories.",
        "The alluring bounty hunter, whose deadly reputation seems at odds with the subtle smile she gives you.",
        "The enigmatic engineer, seemingly oblivious to the chaos, their fingers dancing across the datapad.",
        "The cybernetic bartender, whose gaze seems to penetrate right through to your credit balance... or lack thereof.",
    ]
    for i, option in enumerate(approach_options, 1):
        # sleep(0.2)
        game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

    valid_approach_choice = False
    approach_choice_num = 0
    while not valid_approach_choice:
        choice_input = input(Fore.WHITE + "\nYour choice (1-4): ")
        if is_valid_int(choice_input):
            choice_num = int(choice_input)
            if 1 <= choice_num <= 4:
                valid_approach_choice = True
                approach_choice_num = choice_num
            else:
                game_state.ui.info_message(
                    Fore.RED + "Please enter a number between 1 and 4."
                )
        else:
            game_state.ui.info_message(
                Fore.RED + "Please enter a valid number.")

    # sleep(1.5)  # Slightly increased delay

    # Variables to store dialogue choices and their effects
    dialogue_bonus = {"stat": "", "value": 0}
    faction_influenced = ""
    dialogue_trait_hint = ""
    if approach_choice_num == 1:
        game_state.ui.info_message(
            Fore.CYAN
            + "\nYou weave through the throng, the mercenary's gaze following you like a targeting system. As you reach his table, he grunts, one scarred eyebrow raised. 'Spit it out, spacer. I ain't got all rotation.'"
        )

        # sleep(2)
        game_state.ui.info_message(
            Fore.YELLOW + "\nHow do you respond to the intimidating mercenary?\n"
        )
        merc_dialogue = [
            "Straightforward: 'Looking for work. Heard you might know where the credits flow.'",
            "Confident: 'That's a nasty scar. Bet there's a better story behind it than the one you tell.'",
            "Cautious: 'Just looking for information. I can pay for your time.'",
        ]

        for i, option in enumerate(merc_dialogue, 1):
            # sleep(0.2)
            game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

        valid_dialogue = False
        merc_choice_num = 1  # Default value
        while not valid_dialogue:
            merc_choice = input(Fore.WHITE + "\nYour response (1-3): ")
            if is_valid_int(merc_choice) and 1 <= int(merc_choice) <= 3:
                valid_dialogue = True
                merc_choice_num = int(merc_choice)
            else:
                game_state.ui.info_message(
                    Fore.RED + "Please enter a number between 1 and 3."
                )

        if merc_choice_num == 1:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe mercenary sizes you up with a practiced eye. 'Straight to business. I respect that.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "He leans forward. 'Mining's where the real money is these days. Corps pay premium for rare finds, no questions asked. Just watch your back out there.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "He taps his scarred knuckles on the table. 'And if you need muscle, my rates are steep but worth it.'"
            )
            dialogue_bonus = {"stat": "resilience", "value": 1}
            dialogue_trait_hint = "Resilient"
            faction_influenced = "military"
            # Ask about background in a more natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe mercenary studies you for a moment. 'Haven't seen you around before. What's your story?'"
            )
            # Update Kell Voss's background options to include all standard backgrounds plus his unique "Battle-Scarred Mercenary" background.
            background_options = {
                1: "Ex-Miner: 'Spent years breaking rocks in the belt. Got tired of making other people rich.'",
                2: "Discharged Trooper: 'Military background. Let's just say my exit wasn't exactly ceremonial.'",
                3: "Lunar Drifter: 'Been making deals in the shadows of lunar cities. Learned to survive by any means.'",
                4: "Void Runner: 'Born in the deep black. Never known a planet's gravity for more than a few months.'",
                5: "Corp Dropout: 'Used to wear a suit, push data, make others rich. Decided I'd rather make myself rich.'",
                6: "Xeno-Biologist: 'Scientific expeditions. Started with research, then found I preferred the independence.'",
                # Mercenary's special background
                7: "Battle-Scarred Mercenary: 'Lot like you, I imagine. Fought in the border conflicts, got tired of others calling the shots.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx: int = 1  # Default value and type annotation
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-7): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 7:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 7."
                    )

            # Set background based on choice
            if bg_idx == 1:
                background = "Ex-Miner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe nods with newfound respect. 'Belters are tough folk. You've got the hands of someone who's seen real work.'"
                )
            elif bg_idx == 2:
                background = "Discharged Trooper"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nA flicker of recognition crosses his face. 'Figures. I can spot military a mile away. What unit?'"
                )
                game_state.ui.info_message(
                    Fore.CYAN + "You give a vague answer that seems to satisfy him."
                )
            elif bg_idx == 3:
                background = "Lunar Drifter"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe gives a knowing smirk. 'Luna's a good training ground. If you survived there, you might just make it out here.'"
                )
            elif bg_idx == 4:
                background = "Void Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Space-born,' he says with respect. 'You've probably seen more of the system than half the mercs I know.'"
                )
            elif bg_idx == 5:
                background = "Corp Dropout"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Corporate, huh?' He looks skeptical. 'Well, everyone's got a past they're running from. Just don't expect that soft life out here.'"
                )
            elif bg_idx == 6:
                background = "Xeno-Biologist"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe raises an eyebrow. 'A scientist? Unusual company for me. Though I've protected research teams before - good pay, but strange work.'"
                )
            else:
                background = "Battle-Scarred Mercenary"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe studies you with new interest. 'Takes one to know one. Those border conflicts were hell. Not many of us came back intact.' He taps his scar. 'Physically or otherwise.'"
                )
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'You'll find work easily enough with that background. Good fighters who can think are rare these days.'"
                )

        elif merc_choice_num == 2:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe mercenary's face hardens momentarily, then cracks into a twisted smile. 'Got spine. Unusual in fresh meat.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "He traces the jagged scar across his face. 'Ceresian border dispute. Took a plasma cutter meant for someone more important.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "He narrows his eyes. 'Combat skills keep you breathing out here. Remember that.'"
            )
            dialogue_bonus = {"stat": "combat", "value": 1}
            dialogue_trait_hint = "Quick"
            faction_influenced = "pirates"

            # Ask about background in a more natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'You don't flinch easy,' he remarks. 'Where'd you pick that up?'"
            )

            game_state.ui.info_message(
                Fore.YELLOW + "\nHow do you explain your courage?"
            )
            background_options = {
                1: "Void Runner: 'Been in space my whole life. When you're born on freighters, fear's a luxury.'",
                2: "Discharged Trooper: 'Military training. They drill the fear right out of you.'",
                3: "Lunar Drifter: 'When you've faced down Luna's gangs, not much else scares you.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx = 1
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 3:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set background based on choice
            if bg_idx == 1:
                background = "Void Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe gives an approving nod. 'Space-born, eh? You've probably got better instincts than half these station rats.'"
                )
            elif bg_idx == 2:
                background = "Discharged Trooper"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Military,' he muses. 'That explains it. Though you don't have that regulation stiffness anymore.'"
                )
            else:
                background = "Lunar Drifter"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Luna's tough,' he acknowledges. 'Different kind of battlefield, but just as deadly.'"
                )

        elif merc_choice_num == 3:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe mercenary's expression doesn't change, but some tension leaves his shoulders. 'Smart approach.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "He glances around before leaning closer. 'Information? Costs more than credits sometimes. But since you asked nice...'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "He gives you some insights on navigating local faction territories and dealing with aggressive miners."
            )
            dialogue_bonus = {"stat": "perception", "value": 1}
            dialogue_trait_hint = "Perceptive"
            faction_influenced = "belters"

            # Ask about background in a more natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nAfter sharing some valuable intel, he eyes you curiously. 'You seem to know what questions to ask. What's your angle?'"
            )

            game_state.ui.info_message(
                Fore.YELLOW + "\nHow do you explain your approach?"
            )
            background_options = {
                1: "Corp Dropout: 'Let's just say corporate life taught me the value of good intelligence.'",
                2: "Xeno-Biologist: 'Scientific curiosity. I evaluate all variables before forming conclusions.'",
                3: "Void Runner: 'When you navigate the void, information is as valuable as fuel.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx = 1  # Default value and type annotation
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 3:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set background based on choice
            if bg_idx == 1:
                background = "Corp Dropout"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe smirks. 'Corporate, huh? Don't worry, your secret's safe. We've all got pasts we're running from.'"
                )
            elif bg_idx == 2:
                background = "Xeno-Biologist"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe looks intrigued. 'A scientist in a place like this? Interesting. You might want to talk to that engineer over there.'"
                )
            else:
                background = "Void Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe nods in understanding. 'The void doesn't forgive mistakes. Good pilots know to map the dangerous spots before flying in.'"
                )
                # Store the background selected through dialogue
        game_state.ui.info_message(
            Fore.YELLOW + f"\nYou reflect on your past as a {background}..."
        )
        # sleep(1.5)
        game_state.ui.info_message(
            Fore.CYAN + "Your experiences have shaped your skills and connections."
        )

        # Assign positive_trait based on dialogue_trait_hint
        if dialogue_trait_hint:
            positive_trait = dialogue_trait_hint

        # Assign a default negative trait if one hasn't been set in this dialogue path
        if "negative_trait" not in locals():
            if positive_trait == "Perceptive":
                negative_trait = "Paranoid"
            elif positive_trait == "Charismatic":
                negative_trait = "Reckless"
            elif positive_trait == "Quick":
                negative_trait = "Impatient"
            elif positive_trait == "Resilient":
                negative_trait = "Impatient"
            else:
                # default fallback        #sleep(1)
                negative_trait = "Superstitious"

        # Prompt for ship name before type selection
        # sleep(2)
        ship_name = ""
        while not ship_name:
            ship_name = input(Fore.WHITE + "What do you call your ship? ")
            if not ship_name:
                game_state.ui.info_message(
                    Fore.RED + "You need to give your ship a name."
                )

        # Update ship options to provide real gameplay differences
        game_state.ui.info_message(
            Fore.YELLOW
            + f"\n'The {ship_name}, huh?' the mercenary grunts. 'Now, what kind of vessel is she?'"
        )
        ship_options = {
            1: "Armored Behemoth: 'Thick plating, heavy weapon mounts. Slower but durable with extra cargo space.'",
            2: "Agile Interceptor: 'Streamlined and fast. Prioritizes speed and sensors over cargo capacity.'",
            3: "Balanced Cruiser: 'A versatile design. Decent armor, speed, and cargo capacity for most situations.'",
            4: "Mining Vessel: 'Specialized for asteroid mining with enhanced ore extraction and large cargo hold.'",
        }

        # Special character-specific ship option based on background
        if background == "Battle-Scarred Mercenary":
            ship_options[5] = (
                "Mercenary Veteran: 'A battle-hardened vessel with custom combat modifications and stealth capabilities.'"
            )
        elif background == "Xeno-Biologist":
            ship_options[5] = (
                "Scientific Explorer: 'A research vessel equipped with advanced sensors and analytical equipment.'"
            )
        elif background == "Lunar Drifter":
            ship_options[5] = (
                "Smuggler's Edge: 'A customized freighter with hidden compartments and stealth modifications.'"
            )
        elif background == "Discharged Trooper":
            ship_options[5] = (
                "Military Surplus: 'A decommissioned patrol craft with reinforced systems and combat readiness.'"
            )

        for i, option in ship_options.items():
            # sleep(0.2)
            game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

        valid_ship_choice = False
        while not valid_ship_choice:
            ship_choice = input(
                Fore.WHITE + f"\nYour response (1-{len(ship_options)}): "
            )
            if is_valid_int(ship_choice) and 1 <= int(ship_choice) <= len(ship_options):
                valid_ship_choice = True
                ship_idx = int(ship_choice)
            else:
                game_state.ui.info_message(
                    Fore.RED
                    + f"Please enter a number between 1 and {len(ship_options)}."
                )

        # Map choice to ship template ID
        ship_template_map = {
            1: "armored_behemoth",
            2: "agile_interceptor",
            3: "balanced_cruiser",
            4: "mining_vessel",
            5: {
                "Battle-Scarred Mercenary": "merc_veteran",
                "Xeno-Biologist": "research_vessel",
                "Lunar Drifter": "smuggler_ship",
                "Discharged Trooper": "merc_veteran",
            },
        }

        # Get the template ID based on choice
        if ship_idx == 5:
            assert isinstance(ship_template_map[5], dict), (
                "Expected ship_template_map[5] to be a dictionary."
            )
            # Cast the result of get() to str to satisfy mypy
            ship_template_id = cast(
                str, ship_template_map[5].get(background, "balanced_cruiser")
            )
        else:
            assert isinstance(ship_template_map[ship_idx], str), (
                "Expected ship_template_map[ship_idx] to be a string."
            )
            # Cast the map access to str after assertion to satisfy mypy
            ship_template_id = cast(str, ship_template_map[ship_idx])

        # Store the ship appearance for later reference
        assert ship_template_id in SHIP_TEMPLATES, (
            f"Ship template ID {ship_template_id} not found in SHIP_TEMPLATES."
        )
        # Explicitly cast dict access for mypy
        ship_appearance = cast(str, SHIP_TEMPLATES[ship_template_id]["name"])

        # Display feedback based on ship choice
        if ship_idx == 1:  # Armored Behemoth
            game_state.ui.info_message(
                Fore.CYAN
                + "\nHe nods approvingly. 'A tank in space. Hull integrity at 150%. You'll be hard to take down, but don't expect to win any races.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "Ship Specs: Speed -20%, Hull +50%, Cargo +20%, Fuel +20%"
            )
        elif ship_idx == 2:  # Agile Interceptor
            game_state.ui.info_message(
                Fore.CYAN
                + "\nHe smirks. 'Speed kills, but only if you know how to use it. This one's fast - 40% faster than standard. Stay sharp out there.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW
                + "Ship Specs: Speed +40%, Sensors +20%, Hull -20%, Cargo -30%"
            )
        elif ship_idx == 3:  # Balanced Cruiser
            game_state.ui.info_message(
                Fore.CYAN
                + "\nHe gives a satisfied nod. 'Balanced stats across the board. Versatility is key in the void.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "Ship Specs: Standard baseline values for all systems"
            )
        elif ship_idx == 4:  # Mining Vessel
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'That's a serious mining setup,' he notes with appreciation. 'The extraction rate is 50% higher than standard, and that cargo bay can haul a lot of ore.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW
                + "Ship Specs: Mining speed +50%, Cargo +40%, Sensors +40%, Speed -10%"
            )
        elif ship_idx == 5:  # Special ship based on background
            if background == "Battle-Scarred Mercenary":
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Now that's a proper combat vessel,' he says with genuine respect. 'Reinforced hull, stealth capabilities, and enough speed to get you out of trouble.'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW
                    + "Ship Specs: Hull +20%, Stealth engine, Sensors +30%, Speed +10%"
                )
            elif background == "Xeno-Biologist":
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A science vessel? Interesting choice,' he remarks. 'Those sensor arrays are top-notch. You'll detect mineral deposits the average miner would miss completely.'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW
                    + "Ship Specs: Sensors +70%, Fuel efficiency +30%, Antimatter +40%"
                )
            elif background == "Lunar Drifter":
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe grins knowingly. 'I recognize those modified engine housings. That's a smuggler's setup if I ever saw one. Your sensor signature is practically non-existent.'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW
                    + "Ship Specs: Stealth engine, Signature -50%, Speed +20%, Cargo +10%"
                )
            elif background == "Discharged Trooper":
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Military surplus,' he notes with approval. 'Those patrol crafts are built to last. Good armor, decent speed, and combat-ready systems.'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW
                    + "Ship Specs: Hull +20%, Shields +25%, Speed +10%, Sensors +30%"
                )
    elif approach_choice_num == 2:
        game_state.ui.info_message(
            Fore.CYAN
            + "\nAs you approach, the bounty hunter's keen eyes track your movement. She gestures to the empty seat across from her with a slight smirk. 'Either you're brave or desperate to approach me directly. Which is it, spacer?'"
        )

        # sleep(2)
        game_state.ui.info_message(
            Fore.YELLOW
            + "\nHow do you respond to the dangerous-looking bounty hunter?\n"
        )
        hunter_dialogue = [
            "Honest: 'A bit of both. I'm new here and could use some guidance from someone who knows the ropes.'",
            "Flirtatious: 'Maybe I just wanted to meet the most intriguing person in this dump.'",
            "Professional: 'Your reputation precedes you. I'm looking to establish some connections in this sector.'",
        ]

        for i, option in enumerate(hunter_dialogue, 1):
            # sleep(0.2)
            game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

        valid_dialogue = False
        hunter_choice_num = 1  # Default value
        while not valid_dialogue:
            hunter_choice = input(Fore.WHITE + "\nYour response (1-3): ")
            if is_valid_int(hunter_choice) and 1 <= int(hunter_choice) <= 3:
                valid_dialogue = True
                hunter_choice_num = int(hunter_choice)
            else:
                game_state.ui.info_message(
                    Fore.RED + "Please enter a number between 1 and 3."
                )

        if hunter_choice_num == 1:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nNova Valen's expression softens almost imperceptibly. 'Honesty. Rare in these parts.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "She leans forward. 'The ropes are simple - trust no one completely, watch your back, and never underprice your worth. The void is full of predators.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "She taps her finger thoughtfully on the table. 'That said, everyone needs allies. Even loners like us.'"
            )
            dialogue_bonus = {"stat": "perception", "value": 1}
            dialogue_trait_hint = "Perceptive"
            faction_influenced = "explorers"
            # Ask about background in a more natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'So what drives you out here to the edge of civilization?' Nova asks. 'Most people have a story.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "\nWhat do you share about your background?"
            )
            background_options = {
                1: "Lunar Drifter: 'Grew up in Luna's shadow districts. Learned to survive by any means necessary.'",
                2: "Void Runner: 'Born in the deep black. Never known a planet's gravity for more than a few months.'",
                3: "Corp Dropout: 'Used to be corporate. Found out what they were really doing and couldn't stay.'",
                4: "Ex-Miner: 'Spent years breaking rocks in the belt. Looking for something more profitable now.'",
                5: "Discharged Trooper: 'Military training. Let's just say there was a disagreement about orders.'",
                6: "Xeno-Biologist: 'Research expeditions. Now I'm pursuing independent studies with fewer restrictions.'",
                # Bounty Hunter's special background
                7: "Shadow Operative: 'Similar to you. Extraction specialist. Recently decided to be my own contractor.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx = 1  # Default value and type annotation
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-7): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 7:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 7."
                    )

            # Set background based on choice
            if bg_idx == 1:
                background = "Lunar Drifter"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nShe nods with understanding. 'The Moon breeds survivors. You've got street smarts - that'll serve you well out here.'"
                )
            elif bg_idx == 2:
                background = "Void Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Space-born,' she says with respect. 'You've got the void in your blood. That gives you an edge most don't have.'"
                )
            elif bg_idx == 3:
                background = "Corp Dropout"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Corporate life,' she smirks. 'I've hunted my share of whistleblowers... and helped a few disappear. Depends who's paying.'"
                )
            elif bg_idx == 4:
                background = "Ex-Miner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Honest work,' she says with a nod. 'Miners see the real frontier before anyone else. You know how to spot value in the rough.'"
                )
            elif bg_idx == 5:
                background = "Discharged Trooper"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Military types.' She studies you with renewed interest. 'Good training. Better instincts, if you survived long enough to make it here.'"
                )
            elif bg_idx == 6:
                background = "Xeno-Biologist"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A scientist?' She raises an eyebrow. 'Interesting career change. Though I've met researchers who could handle themselves better than some mercs.'"
                )
            else:
                background = "Shadow Operative"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nNova's demeanor changes subtly. 'Extraction specialist.' Her voice drops. 'Now I'm curious which outfit you ran with. Not many in that line make it to retirement.'"
                )
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'We should compare notes sometime. There are corners of this sector where someone with your skills could make a small fortune.'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW
                    + "\nYou've chosen the bounty hunter's special background. This will provide unique advantages in stealth situations and interactions with intelligence networks."
                )

        elif hunter_choice_num == 2:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nNova's eyebrow arches slightly as she gives you a measured look, then her lips curl into a dangerous smile."
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'Smooth talker, hmm? That'll get you places... sometimes even where you want to go,' she says with a hint of amusement."
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "She leans back, studying you. 'Just remember - out here, flirtation is a currency. Spend it wisely, and know its value.'"
            )
            dialogue_bonus = {"stat": "charisma", "value": 1}
            dialogue_trait_hint = "Charismatic"
            faction_influenced = "traders"

            # Ask about background in a more natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nAs the conversation continues, Nova gives you an appraising look. 'You've got confidence. What's your story?'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "\nHow do you explain your background?"
            )
            background_options = {
                1: "Ex-Miner: 'Started in the asteroid fields. Found I prefer hunting people to hunting minerals.'",
                2: "Corp Dropout: 'Used to work corporate security. Got tired of protecting the wrong people.'",
                3: "Lunar Drifter: 'Grew up in Luna's underworld. Tracking targets came naturally.'",
                4: "Void Runner: 'My family's been traveling the black for generations. It's all I've ever known.'",
                5: "Xeno-Biologist: 'Used to study alien species. Academia got too political - and dangerous.'",
                6: "Discharged Trooper: 'Military background. Let's just say there was a disagreement about orders.'",
                # Bounty Hunter's special background
                7: "Shadow Operative: 'Similar to your line of work. Extraction specialist looking to be my own boss.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx = 1  # Default value and type annotation
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-7): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 7:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 7."
                    )

            # Set background based on choice
            if bg_idx == 1:
                background = "Ex-Miner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nShe nods with newfound respect. 'Belters are tough folk. You've got the hands of someone who's seen real work.'"
                )
            elif bg_idx == 2:
                background = "Discharged Trooper"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nA flicker of recognition crosses her face. 'Figures. I can spot military a mile away. What unit?'"
                )
                game_state.ui.info_message(
                    Fore.CYAN + "You give a vague answer that seems to satisfy her."
                )
            elif bg_idx == 3:
                background = "Lunar Drifter"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nShe gives a knowing smirk. 'Luna's a good training ground. If you survived there, you might just make it out here.'"
                )
            elif bg_idx == 4:
                background = "Void Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Space-born,' she says with respect. 'You've probably seen more of the system than half the mercs I know.'"
                )
            elif bg_idx == 5:
                background = "Corp Dropout"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Corporate, huh?' She looks skeptical. 'Well, everyone's got a past they're running from. Just don't expect that soft life out here.'"
                )
            elif bg_idx == 6:
                background = "Xeno-Biologist"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nShe raises an eyebrow. 'A scientist? Unusual company for me. Though I've protected research teams before - good pay, but strange work.'"
                )
            else:
                background = "Shadow Operative"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nNova's demeanor changes subtly. 'Extraction specialist.' Her voice drops. 'Now I'm curious which outfit you ran with. Not many in that line make it to retirement.'"
                )
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'We should compare notes sometime. There are corners of this sector where someone with your skills could make a small fortune.'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW
                    + "\nYou've chosen the bounty hunter's special background. This will provide unique advantages in stealth situations and interactions with intelligence networks."
                )

        elif hunter_choice_num == 3:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nNova's demeanor shifts slightly. 'Professional. I can work with that.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'Connections are currency out here,' she says quietly. 'More valuable than credits sometimes. Everyone needs someone who can find things... or people.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "She slides a small data chip across the table. 'My contact frequency. Never know when you might need someone found - or need to disappear yourself.'"
            )
            dialogue_bonus = {"stat": "resilience", "value": 1}
            dialogue_trait_hint = "Resilient"
            faction_influenced = "military"

            # Ask about background in a more natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'So what's your specialty?' Nova asks directly. 'Everyone's got an angle out here.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "\nHow do you describe your expertise?"
            )
            background_options = {
                1: "Ex-Miner: 'I know asteroids. Where to find the valuable ones and how to crack them open.'",
                2: "Corp Dropout: 'Corporate intelligence. I understand how the big players think and move.'",
                3: "Lunar Drifter: 'Urban survival. I know how to find what others want to keep hidden.'",
                4: "Void Runner: 'Navigation and piloting. I can get to places others can't reach.'",
                5: "Xeno-Biologist: 'Scientific analysis. I can understand and predict behavior patterns.'",
                6: "Discharged Trooper: 'Tactical operations. I can handle myself in a fight and plan an approach.'",
                # Bounty Hunter's special background
                7: "Shadow Operative: 'Asset acquisition and extraction. Similar to your line of work, but more specialized.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx = 1  # Default value and type annotation
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-7): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 7:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 7."
                    )

            # Set background based on choice
            if bg_idx == 1:
                background = "Ex-Miner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe nods with newfound respect. 'Belters are tough folk. You've got the hands of someone who's seen real work.'"
                )
            elif bg_idx == 2:
                background = "Discharged Trooper"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nA flicker of recognition crosses his face. 'Figures. I can spot military a mile away. What unit?'"
                )
                game_state.ui.info_message(
                    Fore.CYAN + "You give a vague answer that seems to satisfy him."
                )
            elif bg_idx == 3:
                background = "Lunar Drifter"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe gives a knowing smirk. 'Luna's a good training ground. If you survived there, you might just make it out here.'"
                )
            elif bg_idx == 4:
                background = "Void Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Space-born,' he says with respect. 'You've probably seen more of the system than half the mercs I know.'"
                )
            elif bg_idx == 5:
                background = "Corp Dropout"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Corporate, huh?' He looks skeptical. 'Well, everyone's got a past they're running from. Just don't expect that soft life out here.'"
                )
            elif bg_idx == 6:
                background = "Xeno-Biologist"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nHe raises an eyebrow. 'A scientist? Unusual company for me. Though I've protected research teams before - good pay, but strange work.'"
                )
            else:
                background = "Shadow Operative"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nNova's demeanor changes subtly. 'Extraction specialist.' Her voice drops. 'Now I'm curious which outfit you ran with. Not many in that line make it to retirement.'"
                )
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'We should compare notes sometime. There are corners of this sector where someone with your skills could make a small fortune.'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW
                    + "\nYou've chosen the bounty hunter's special background. This will provide unique advantages in stealth situations and interactions with intelligence networks."
                )

        # Store the background selected through dialogue
        game_state.ui.info_message(
            Fore.YELLOW + f"\nYou reflect on your past as a {background}..."
        )
        # sleep(1.5)
        game_state.ui.info_message(
            Fore.CYAN
            + "Nova seems to appreciate your background, and you sense there might be future opportunities for collaboration."
        )
        # sleep(1)

        # Ask about ship preferences
        # sleep(2)
        game_state.ui.info_message(
            Fore.CYAN
            + "\n'What are you flying?' Nova asks, changing the subject. 'In this business, your ship is your lifeline.'"
        )

        # First ask for ship name
        ship_name = ""
        while not ship_name:
            ship_name = input(Fore.WHITE + "What's your ship called? ")
            if not ship_name:
                game_state.ui.info_message(
                    Fore.RED + "You need to give your ship a name."
                )

        game_state.ui.info_message(
            Fore.CYAN
            + f"\n'The {ship_name},' Nova repeats. 'And what kind of vessel is she?'"
        )  # Then ask for ship type with actual gameplay differences
        ship_options = {
            1: "Hunter's Edge: 'Stealth profile with advanced sensor array. Low signature and high tracking capability.'",
            2: "Combat Bulwark: 'Heavy armor plating, reinforced hull. Not fast, but can withstand serious damage.'",
            3: "Swift Pursuit: 'Sleek design built for speed. Light on armor but can outrun most trouble.'",
            4: "Balanced Venture: 'Standard all-around vessel with decent capabilities in all areas.'",
        }

        # Special ship option based on background
        if background == "Shadow Operative":
            ship_options[5] = (
                "Ghost Protocol: 'Military-grade stealth vessel with advanced signature masking. Top tier for covert operations.'"
            )

        for i, option in ship_options.items():
            # sleep(0.2)
            game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

        valid_ship_choice = False
        while not valid_ship_choice:
            ship_choice = input(
                Fore.WHITE + f"\nYour ship type (1-{len(ship_options)}): "
            )
            if is_valid_int(ship_choice) and 1 <= int(ship_choice) <= len(ship_options):
                valid_ship_choice = True
                ship_idx = int(ship_choice)
            else:
                game_state.ui.info_message(
                    Fore.RED
                    + f"Please enter a number between 1 and {len(ship_options)}."
                )

        # Map choice to ship template ID
        ship_template_map = {
            1: "hunter_ship",  # Hunter's Edge maps to the hunter_ship template
            2: "armored_behemoth",  # Combat Bulwark maps to armored_behemoth
            3: "agile_interceptor",  # Swift Pursuit maps to agile_interceptor
            4: "balanced_cruiser",  # Balanced Venture maps to balanced_cruiser
            5: "hunter_ship",  # Special Shadow Operative ship with enhanced stats
        }

        # Get the template ID based on choice
        # Cast map access to str to satisfy mypy
        ship_template_id = cast(str, ship_template_map[ship_idx])

        # Store the ship appearance for later reference
        # Explicitly cast dict access for mypy
        ship_appearance = cast(str, SHIP_TEMPLATES[ship_template_id]["name"])
        # Display feedback based on ship choice
        if ship_idx == 1:  # Hunter's Edge
            game_state.ui.info_message(
                Fore.CYAN
                + "\nNova nods approvingly. 'A hunter's vessel. Enhanced sensors, low signature. Perfect for tracking targets across the void.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "Ship Specs: Sensors +50%, Signature -10%, Speed +30%"
            )
        elif ship_idx == 2:  # Combat Bulwark
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'Built like a tank,' Nova observes. 'Smart if you're expecting trouble. That hull can take a beating.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "Ship Specs: Hull +50%, Cargo +20%, Speed -20%"
            )
        elif ship_idx == 3:  # Swift Pursuit
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'Speed over armor,' she notes. 'My preference too. Can't hit what you can't catch.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "Ship Specs: Speed +40%, Hull -20%, Cargo -30%"
            )
        elif ship_idx == 4:  # Balanced Venture
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'Jack of all trades,' she comments. 'Not a bad choice for a beginner. Gives you flexibility.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "Ship Specs: Standard baseline values for all systems"
            )
        elif ship_idx == 5:  # Special Shadow Operative ship
            game_state.ui.info_message(
                Fore.CYAN
                + "\nNova's eyes widen slightly. 'Military-grade stealth tech? Those aren't easy to come by,' she says with newfound respect. 'You've got some serious connections.'"
            )
            game_state.ui.info_message(
                Fore.YELLOW
                + "Ship Specs: Signature -50%, Sensors +70%, Stealth engine, Speed +20%"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'I can hook you up with a contact who specializes in signature-reducing hull modifications if you're interested. For a finder's fee, of course.'"
            )
        elif app_idx == 2:
            ship_appearance = "Combat Ready"
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'Making a statement, I see,' Nova says with a slight smile. 'Sometimes the best defense is looking too dangerous to bother.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'Just remember, those weapons are only useful if you know how to use them effectively. Amateur gunners are just target practice.'"
            )
        else:
            ship_appearance = "Fast Courier"
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'Speed,' Nova says with appreciation. 'My preferred strategy too. Can't hit what you can't catch.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'I've outrun more trouble than I've shot my way through. A wise approach in the void.'"
            )

        game_state.ui.info_message(
            Fore.YELLOW +
            f"\nYou've told Nova about your ship, the {ship_name}..."
        )
        # sleep(1)
        game_state.ui.info_message(
            Fore.CYAN
            + f"Its {ship_appearance} design seems to have made an impression on her."
        )
        # Assign positive_trait based on dialogue_trait_hint
        if dialogue_trait_hint:
            positive_trait = dialogue_trait_hint

        # Assign a default negative trait if one hasn't been set in this dialogue path
        if "negative_trait" not in locals():
            if positive_trait == "Perceptive":
                negative_trait = "Paranoid"
            elif positive_trait == "Charismatic":
                negative_trait = "Reckless"
            elif positive_trait == "Resilient":
                negative_trait = "Impatient"
            else:
                negative_trait = "Superstitious"  # default fallback

        # sleep(1)
    elif approach_choice_num == 3:
        game_state.ui.info_message(
            Fore.CYAN
            + "\nYou navigate towards the engineer. As you approach, a faint hum emanates from their direction. Without looking up from the datapad, a synthesized voice cuts through the din: 'If it ain't critical, it can wait. If it is critical, make it quick.'"
        )

        # sleep(2)
        game_state.ui.info_message(
            Fore.YELLOW + "\nHow do you engage with the busy engineer?\n"
        )
        eng_dialogue = [
            "Technical: 'That's a V7 modulator you're reconfiguring. The efficiency curve flattens if you tweak the harmonic resonance.'",
            "Curious: 'What are you working on? Looks advanced.'",
            "Respectful: 'Sorry to interrupt. I could use some technical expertise when you have a moment.'",
        ]

        for i, option in enumerate(eng_dialogue, 1):
            # sleep(0.2)
            game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

        valid_dialogue = False
        eng_choice_num = 1  # Default value
        while not valid_dialogue:
            eng_choice = input(Fore.WHITE + "\nYour approach (1-3): ")
            if is_valid_int(eng_choice) and 1 <= int(eng_choice) <= 3:
                valid_dialogue = True
                eng_choice_num = int(eng_choice)
            else:
                game_state.ui.info_message(
                    Fore.RED + "Please enter a number between 1 and 3."
                )

        if eng_choice_num == 1:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe engineer's head snaps up, eyes wide with surprise. The synthesized voice switches off as they speak in a natural, excited tone."
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'You know your tech! Everyone else here thinks I'm just fixing broken vidscreens.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "They launch into a detailed explanation of their work on improving deep-space scanner efficiency. 'Your ship has decent tech?'"
            )
            dialogue_bonus = {"stat": "engineering", "value": 1}
            dialogue_trait_hint = "Methodical"
            faction_influenced = "scientists"

            # Integrate ship customization into dialogue
            # sleep(2)
            game_state.ui.info_message(
                Fore.YELLOW + "\nHow do you describe your ship to the engineer?"
            )

            # First ask for ship name
            ship_name = ""
            while not ship_name:
                ship_name = input(Fore.WHITE + "What's your ship's name? ")
                if not ship_name:
                    game_state.ui.info_message(
                        Fore.RED + "You need to give your ship a name."
                    )

            game_state.ui.info_message(
                Fore.CYAN
                + f"\n'The {ship_name}, huh? What kind of vessel are we talking about?'"
            )

            # Then ask for appearance
            appearance_options = {
                1: "Rust Bucket: 'It's... well-loved. Patches of mismatched plating, but she's sturdy.'",
                2: "Sleek Runner: 'Modern lines, polished finish. Not the newest model, but I keep her looking good.'",
                3: "Industrial Hauler: 'Bulky, practical. Built for function over form, with visible reinforcements.'",
            }

            for i, option in appearance_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_appearance_choice = False
            app_idx = 1  # Default value and type annotation
            while not valid_appearance_choice:
                appearance_choice = input(
                    Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(appearance_choice) and 1 <= int(appearance_choice) <= 3:
                    valid_appearance_choice = True
                    app_idx = int(appearance_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set appearance based on choice
            if app_idx == 1:
                ship_appearance = "Rust Bucket"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nZeta-9 nods appreciatively. 'Those old models have character. More importantly, they have space for upgrades and modifications that the newer, sleeker vessels can't accommodate.'"
                )
                # sleep(1.5)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "'I could help you optimize her systems sometime. Those patch jobs actually make her more resilient to damage, if done right.'"
                )
            elif app_idx == 2:
                ship_appearance = "Sleek Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nThe engineer's eyes light up. 'Nice choice. Good aerodynamics for atmospheric entry, and the cooling systems on those models are exceptional.'"
                )
                # sleep(1.5)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "'Keep her well-maintained and she'll outrun most trouble you encounter.'"
                )
            else:
                ship_appearance = "Industrial Hauler"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Practical. I like it,' Zeta-9 approves. 'Those haulers can be modified to carry serious equipment. Cargo space is valuable out here.'"
                )
                # sleep(1.5)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "'With some reinforced bulkheads, you could even withstand minor asteroid impacts without catastrophic failure.'"
                )

            # Ask about background in a natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'You seem to know your tech,' Zeta-9 notes. 'Where'd you pick that up?'"
            )
            game_state.ui.info_message(Fore.YELLOW + "\nHow do you respond?")
            background_options = {
                1: "Ex-Miner: 'When your life depends on equipment working, you learn fast. Spent years maintaining mining rigs.'",
                2: "Corp Dropout: 'Corporate R&D division. Got sick of designing planned obsolescence into everything.'",
                3: "Xeno-Biologist: 'Scientific expeditions require technical self-sufficiency. I've had to repair delicate equipment in the field.'",
                4: "Void Runner: 'When you're millions of miles from the nearest repair dock, you learn to fix things yourself.'",
                5: "Lunar Drifter: 'In Luna's underground, we had to repurpose and hack everything just to survive.'",
                6: "Discharged Trooper: 'Military tech specialist. Learned to maintain equipment under harsh conditions.'",
                # Engineer's special background
                7: "Tech Savant: 'Always had a knack for technology. Can reverse-engineer almost any system given enough time.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx = 1  # Default value and type annotation
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-7): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 7:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 7."
                    )

            # Set background based on choice
            if bg_idx == 1:
                background = "Ex-Miner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A practical education,' Zeta-9 says with approval. 'No better teacher than necessity.'"
                )
            elif bg_idx == 2:
                background = "Corp Dropout"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nZeta-9 gives you a knowing look. 'Corporate experience has its uses. You understand systems thinking.'"
                )
            else:
                background = "Xeno-Biologist"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Scientific mind,' Zeta-9 nods. 'That explains your grasp of the modulator principles.'"
                )

        elif eng_choice_num == 2:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe engineer glances up briefly, evaluating whether you're worth the distraction."
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'Working on a way to boost mineral scanner range without frying the circuits. Corps pay well for proprietary tech.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "They gesture to the stool beside them. 'You a tech yourself? Market's good for innovation right now.'"
            )
            dialogue_bonus = {"stat": "technical_aptitude", "value": 1}
            dialogue_trait_hint = "Resourceful"
            faction_influenced = "corporations"

            # Integrate ship customization into dialogue
            # sleep(2)
            game_state.ui.info_message(
                Fore.YELLOW
                + "\nAs you discuss technology, the conversation turns to your vessel."
            )

            # First ask for ship name
            ship_name = ""
            while not ship_name:
                ship_name = input(Fore.WHITE + "What's your ship called? ")
                if not ship_name:
                    game_state.ui.info_message(
                        Fore.RED + "You need to give your ship a name."
                    )

            game_state.ui.info_message(
                Fore.CYAN
                + f"\n'The {ship_name}... what kind of system configuration are you running?'"
            )

            # Then ask for appearance
            appearance_options = {
                1: "Retrofitted Classic: 'An older model I've upgraded extensively. She's got character.'",
                2: "Stealth Profile: 'Dark coating, minimal external features. I prefer to fly under the radar.'",
                3: "Colorful Maverick: 'Custom paintjob, stands out anywhere. Why be subtle in a universe this vast?'",
            }

            for i, option in appearance_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_appearance_choice = False
            app_idx = 1  # Default value and type annotation
            while not valid_appearance_choice:
                appearance_choice = input(
                    Fore.WHITE + "\nYour description (1-3): ")
                if is_valid_int(appearance_choice) and 1 <= int(appearance_choice) <= 3:
                    valid_appearance_choice = True
                    app_idx = int(appearance_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set appearance based on choice
            if app_idx == 1:
                ship_appearance = "Retrofitted Classic"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nZeta-9 nods appreciatively. 'Classic models have sturdy frameworks. Built to last, not like the disposable junk they manufacture now.'"
                )
                # sleep(1.5)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "'I've got some custom firmware that might interest you. Makes those old navigation systems sing.'"
                )
            elif app_idx == 2:
                ship_appearance = "Stealth Profile"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Smart choice,' Zeta-9 says quietly. 'Low profile means fewer unwanted encounters. I can appreciate that approach.'"
                )
                # sleep(1.5)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "'I might have some sensor-dampening tech that would complement your setup.'"
                )
            else:
                ship_appearance = "Colorful Maverick"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nThe engineer laughs, a surprisingly human sound. 'Bold! I respect the confidence. Not my approach, but it takes all kinds.'"
                )
                # sleep(1.5)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "'Just make sure your defenses are as impressive as your aesthetics. You're not exactly blending in.'"
                )

            # Ask about background in a natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\n'So what's your story?' Zeta-9 asks. 'Most people in this bar are running to or from something.'"
            )

            game_state.ui.info_message(
                Fore.YELLOW + "\nWhat part of your past do you share?"
            )
            background_options = {
                1: "Void Runner: 'Born on freighters. Never knew a planet as home. The void's in my blood.'",
                2: "Corp Dropout: 'Left a cushy corporate position. The pay was good, but the soul-crushing monotony wasn't worth it.'",
                3: "Ex-Miner: 'Used to break rocks for a living until I realized the real money's in selling what comes out of them.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx = 1  # Default value and type annotation
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 3:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set background based on choice
            if bg_idx == 1:
                background = "Void Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Space-born,' Zeta-9 says with interest. 'That's getting rarer these days. You probably have natural instincts most pilots train years for.'"
                )
            elif bg_idx == 2:
                background = "Corp Dropout"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nZeta-9 gives you a knowing look. 'Corporate experience has its uses. You understand systems thinking.'"
                )
            else:
                background = "Xeno-Biologist"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Scientific mind,' Zeta-9 nods. 'That explains your grasp of the modulator principles.'"
                )

        elif eng_choice_num == 3:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe engineer continues working but nods slightly, acknowledging your patience."
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "After completing a complex sequence of inputs, they look up. 'Refreshing. Most people demand attention.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'Technical expertise? I've got plenty. What's your ship running? Might have some optimization tips.'"
            )
            dialogue_bonus = {"stat": "education", "value": 1}
            dialogue_trait_hint = "Resourceful"
            faction_influenced = "traders"

            # Integrate ship customization into dialogue
            # sleep(2)

            # First ask for ship name
            ship_name = ""
            while not ship_name:
                ship_name = input(
                    Fore.WHITE + "What do you call your vessel? ")
                if not ship_name:
                    game_state.ui.info_message(
                        Fore.RED + "Your ship needs a name.")

            game_state.ui.info_message(
                Fore.CYAN
                + f"\n'Ah, the {ship_name}. What class of ship are we talking about?'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "\nWhat type of vessel do you pilot?"
            )
            ship_options = {
                1: "Industrial Hauler: 'Modified cargo vessel with expanded holds. Slow but can haul massive loads.'",
                2: "Sleek Runner: 'Speed-optimized craft with enhanced propulsion and reduced mass.'",
                3: "Mining Platform: 'Specialized vessel with advanced ore extraction systems and cargo capacity.'",
                4: "Balanced Explorer: 'Standard vessel with reasonable performance across all systems.'",
            }

            # Special ship option based on background
            if background == "Void Engineering Adept":
                ship_options[5] = (
                    "Tech Maven: 'Experimental vessel with enhanced power systems and engineering interfaces.'"
                )

            for i, option in ship_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_ship_choice = False
            while not valid_ship_choice:
                ship_choice = input(
                    Fore.WHITE + f"\nYour ship type (1-{len(ship_options)}): "
                )
                if is_valid_int(ship_choice) and 1 <= int(ship_choice) <= len(
                    ship_options
                ):
                    valid_ship_choice = True
                    ship_idx = int(ship_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED
                        + f"Please enter a number between 1 and {len(ship_options)}."
                    )

            # Map choice to ship template ID
            ship_template_map = {
                1: "cargo_hauler",  # Industrial Hauler maps to cargo_hauler
                2: "agile_interceptor",  # Sleek Runner maps to agile_interceptor
                3: "mining_vessel",  # Mining Platform maps to mining_vessel
                4: "balanced_cruiser",  # Balanced Explorer maps to balanced_cruiser
                5: "research_vessel",  # Tech Maven maps to research_vessel with enhanced stats
            }

            # Get the template ID based on choice
            # Cast map access to str to satisfy mypy
            ship_template_id = cast(str, ship_template_map[ship_idx])

            # Store the ship appearance for later reference
            # Explicitly cast dict access for mypy
            ship_appearance = cast(
                str, SHIP_TEMPLATES[ship_template_id]["name"])
            # Removed redundant if app_idx block that was overriding ship_appearance and causing lint issues.

            # Ask about background in a natural way
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nZeta-9 gives you an appraising look. 'You're patient. Thoughtful. What brought you into space? Education?'"
            )
            game_state.ui.info_message(
                Fore.YELLOW + "\nHow do you explain your path?")
            background_options = {
                1: "Xeno-Biologist: 'Scientific curiosity. Started with research expeditions, then found I preferred the independence.'",
                2: "Lunar Drifter: 'Grew up in Luna's domes. Learned to survive by reading people and situations.'",
                3: "Void Runner: 'My family's been in space for generations. It's the only life I've known.'",
                4: "Ex-Miner: 'Got my start in the asteroid fields. Hard work teaches you to value what you find.'",
                5: "Corp Dropout: 'Had enough of corporate structure. Out here I make my own decisions.'",
                6: "Discharged Trooper: 'Military background. Know how to follow and when to question orders.'",
                # Engineer's special background
                7: "Tech Savant: 'Always had a gift for understanding systems. Technology speaks to me in ways people don't.'",
            }

            for i, option in background_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_bg_choice = False
            bg_idx = 1  # Default value and type annotation
            while not valid_bg_choice:
                bg_choice = input(Fore.WHITE + "\nYour response (1-7): ")
                if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 7:
                    valid_bg_choice = True
                    bg_idx = int(bg_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 7."
                    )  # Set background based on choice
            if bg_idx == 1:
                background = "Xeno-Biologist"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A scientist,' Zeta-9 says with interest. 'That explains your methodical approach. Knowledge is valuable currency.'"
                )
            elif bg_idx == 2:
                background = "Lunar Drifter"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Luna teaches harsh lessons,' Zeta-9 nods. 'But those who learn them well tend to survive out here.'"
                )
            elif bg_idx == 3:
                background = "Void Runner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Deep space is in your DNA then,' Zeta-9 observes. 'That's becoming increasingly rare and valuable.'"
                )
            elif bg_idx == 4:
                background = "Ex-Miner"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Mining gives you a practical understanding,' Zeta-9 says. 'You know how systems work because your life depends on it.'"
                )
            elif bg_idx == 5:
                background = "Corp Dropout"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Corporate experience,' Zeta-9 nods. 'You understand how the big players think. That's an advantage out here.'"
                )
            elif bg_idx == 6:
                background = "Discharged Trooper"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Military training has its benefits,' Zeta-9 acknowledges. 'Especially when things don't go according to plan.'"
                )
            else:
                background = "Tech Savant"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A kindred spirit,' Zeta-9's eyes light up. 'Few people truly understand technology as a language rather than just a tool.'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW
                    + "\nYou've chosen the engineer's special background. This will provide unique advantages with technology and engineering challenges."
                )
                # Store the ship details selected through dialogue
        game_state.ui.info_message(
            Fore.YELLOW
            + f"\nYou've revealed details about your ship, the {ship_name}..."
        )
        # sleep(1)
        game_state.ui.info_message(
            Fore.CYAN
            + f"Its {ship_appearance} design stands out in its own way among the vessels docked at the station."
        )
        # sleep(1)
        game_state.ui.info_message(
            Fore.YELLOW
            + f"\nYour past as a {background} has shaped your approach to technology and survival."
        )
        # sleep(1.5)

        # Assign positive_trait based on dialogue_trait_hint
        if dialogue_trait_hint:
            positive_trait = dialogue_trait_hint

        # Assign a default negative trait if one hasn't been set in this dialogue path
        if "negative_trait" not in locals():
            if positive_trait == "Perceptive":
                negative_trait = "Paranoid"
            elif positive_trait == "Charismatic":
                negative_trait = "Reckless"
            elif positive_trait == "Methodical":
                negative_trait = "Forgetful"
            elif positive_trait == "Resourceful":
                negative_trait = "Indebted"
            else:
                negative_trait = "Superstitious"  # default fallback
    elif approach_choice_num == 4:
        game_state.ui.info_message(
            Fore.CYAN
            + "\nYou slide up to the bar. The bartender's optical sensors focus on you with an audible click. 'The usual for newcomers is trouble, with a shot of desperation. What'll it be for you?'"
        )

        # sleep(2)
        game_state.ui.info_message(
            Fore.YELLOW + "\nHow do you interact with the cybernetic bartender?\n"
        )
        bar_dialogue = [
            "Sociable: 'Whatever's strong and doesn't cause blindness. And I'll take some local intel with it.'",
            "Direct: 'Information. On mining opportunities, security patterns, and who to avoid around here.'",
            "Generous: Place extra credits on the bar. 'Something premium. And one for yourself, if you're so inclined.'",
        ]

        for i, option in enumerate(bar_dialogue, 1):
            # sleep(0.2)
            game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

        valid_dialogue = False
        bar_choice_num = 1  # Default value
        while not valid_dialogue:
            bar_choice = input(Fore.WHITE + "\nYour approach (1-3): ")
            if is_valid_int(bar_choice) and 1 <= int(bar_choice) <= 3:
                valid_dialogue = True
                bar_choice_num = int(bar_choice)
            else:
                game_state.ui.info_message(
                    Fore.RED + "Please enter a number between 1 and 3."
                )

        if bar_choice_num == 1:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender's optical implants whir as they slide a glowing blue beverage your way. 'Centaurian Sunset. Won't blind you, might make you see more clearly though.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "They wipe down the bar with a mechanical precision. 'Local intel? Everyone's hunting for Ghost Asteroids these days. Mineral content so pure it's worth killing for.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "They tap the side of their cybernetic eye. 'Keep your sensors sharp and your friends closer than your weapons.'"
            )
            dialogue_bonus = {"stat": "adaptability", "value": 1}
            dialogue_trait_hint = "Perceptive"
            faction_influenced = "explorers"

            # Background information through dialogue
            if "background" not in locals():
                # sleep(2)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nThe bartender studies you with those mechanical eyes. 'You're new to the station. What brings you to our corner of space?'"
                )

                game_state.ui.info_message(
                    Fore.YELLOW + "\nHow do you explain your presence?"
                )
                background_options = {
                    1: "Void Runner: 'Just another port for me. Been traveling the lanes since I was born.'",
                    2: "Xeno-Biologist: 'Research, primarily. The academic circles have gotten too... restrictive.'",
                    3: "Lunar Drifter: 'Looking for opportunities away from Luna's politics and gangs.'",
                }

                for i, option in background_options.items():
                    # sleep(0.2)
                    game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

                valid_bg_choice = False
                bg_idx = 1  # Default value and type annotation
                while not valid_bg_choice:
                    bg_choice = input(Fore.WHITE + "\nYour response (1-3): ")
                    if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 3:
                        valid_bg_choice = True
                        bg_idx = int(bg_choice)
                    else:
                        game_state.ui.info_message(
                            Fore.RED + "Please enter a number between 1 and 3."
                        )

                # Set background based on choice
                if bg_idx == 1:
                    background = "Void Runner"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'A spacer through and through,' the bartender notes. 'You've probably seen more of the system than most of my customers combined.'"
                    )
                elif bg_idx == 2:
                    background = "Xeno-Biologist"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\nThe bartender's optical sensors recalibrate. 'Interesting. We don't get many scientific minds here. There's plenty to discover, if you know where to look.'"
                    )
                else:
                    background = "Lunar Drifter"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Luna's tough,' the bartender acknowledges. 'But it teaches valuable lessons. Watch your back out here too.'"
                    )

            # Ship details if not already established
            if "ship_name" not in locals():
                # sleep(2)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'What are you flying?' the bartender inquires. 'Always good to know what's docked at our station.'"
                )

                # Ask for ship name
                ship_name = ""
                while not ship_name:
                    ship_name = input(Fore.WHITE + "Your ship's name: ")
                    if not ship_name:
                        game_state.ui.info_message(
                            Fore.RED + "Your ship needs a name.")

                game_state.ui.info_message(
                    Fore.CYAN
                    + f"\n'The {ship_name},' Obsidian repeats. 'What kind of vessel?'"
                )

                appearance_options = {
                    1: "Retrofitted Classic: 'An older model with some personal modifications.'",
                    2: "Stealth Profile: 'Low profile. Dark coating, minimal emissions.'",
                    3: "Colorful Maverick: 'You can't miss it. Custom paint job that stands out in any dock.'",
                }

                for i, option in appearance_options.items():
                    # sleep(0.2)
                    game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

                valid_appearance_choice = False
                app_idx = 1  # Default value and type annotation
                while not valid_appearance_choice:
                    appearance_choice = input(
                        Fore.WHITE + "\nYour description (1-3): ")
                    if (
                        is_valid_int(appearance_choice)
                        and 1 <= int(appearance_choice) <= 3
                    ):
                        valid_appearance_choice = True
                        app_idx = int(appearance_choice)
                    else:
                        game_state.ui.info_message(
                            Fore.RED + "Please enter a number between 1 and 3."
                        )

                # Set appearance based on choice
                if app_idx == 1:
                    ship_appearance = "Retrofitted Classic"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Classic models have their charm,' Obsidian notes. 'And they don't broadcast your movements like the newer ones with their constant telemetry.'"
                    )
                elif app_idx == 2:
                    ship_appearance = "Stealth Profile"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Subtle. Smart in these parts. Too many curious eyes watching docking logs.'"
                    )
                else:
                    ship_appearance = "Colorful Maverick"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Bold choice,' Obsidian comments. 'Either very brave or very foolish. Time will tell which.'"
                    )

            # Personality trait selection
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender watches as you drink. 'I pride myself on reading customers. You strike me as someone who's...'"
            )  # Offer positive traits
            game_state.ui.info_message(
                Fore.YELLOW + "\nHow do you come across to others?"
            )
            pos_trait_options = {
                1: f"Perceptive: 'I notice things others miss. Details matter in this line of work.' ({dialogue_trait_hint} - Suggested)",
                2: "Resilient: 'I've been knocked down plenty. Always get back up stronger.'",
                3: "Charismatic: 'I have a way with people. Makes life easier in the long run.'",
            }

            trait_idx = 1  # Default to first option

            for i, option in pos_trait_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_trait_choice = False
            while not valid_trait_choice:
                trait_choice = input(Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(trait_choice) and 1 <= int(trait_choice) <= 3:
                    valid_trait_choice = True
                    trait_idx = int(trait_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set positive trait based on choice
            if trait_idx == 1:
                positive_trait = "Perceptive"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Observant. Good.' Obsidian nods. 'That will serve you well. The little details are often what keeps you alive out here.'"
                )
            elif trait_idx == 2:
                positive_trait = "Resilient"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Resilience is rare,' the bartender comments. 'Most folks break after their first real setback.'"
                )
            else:
                positive_trait = "Charismatic"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A people person,' Obsidian notes. 'That can open doors... or get you into trouble if you trust too easily.'"
                )

            # Add negative trait selection
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender tilts their head, optical sensors whirring. 'But everyone's got their flaws. You seem like you might be...'"
            )  # Offer negative traits
            game_state.ui.info_message(
                Fore.YELLOW + "\nWhat's your biggest weakness?")
            neg_trait_options = {
                1: "Impatient: 'I don't like waiting. Time is credits, and I've got places to be.'",
                2: "Reckless: 'I take chances. Playing it safe never made anyone rich or famous.'",
                3: "Superstitious: 'I trust my instincts, even when they don't make rational sense.'",
            }

            neg_trait_idx = 1  # Default to first option

            for i, option in neg_trait_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.RED}{i}. {option}")

            valid_neg_trait_choice = False
            while not valid_neg_trait_choice:
                neg_trait_choice = input(
                    Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(neg_trait_choice) and 1 <= int(neg_trait_choice) <= 3:
                    valid_neg_trait_choice = True
                    neg_trait_idx = int(neg_trait_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set negative trait based on choice
            if neg_trait_idx == 1:
                negative_trait = "Impatient"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Careful with that,' the bartender warns. 'The void doesn't reward haste. Sometimes the slow, careful approach is what keeps you breathing.'"
                )
            elif neg_trait_idx == 2:
                negative_trait = "Reckless"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nObsidian gives a mechanical sigh. 'Bold moves can pay off big... or end with your ship in pieces. Your call.'"
                )
            else:
                negative_trait = "Superstitious"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Interesting,' the bartender comments. 'Space has its mysteries. Some veterans swear by their rituals and omens.'"
                )

        elif bar_choice_num == 2:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender makes a sound that might be a chuckle. 'Direct. I can work with that.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'Mining's best in the outer rim right now, but pirates are heavy. Station security sweeps every six hours, on schedule you could set your chrono to.'"
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "They lean forward, voice lowering. 'Avoid anyone with a red scarf. Syndicate markers. They ask questions with their fists.'"
            )
            dialogue_bonus = {"stat": "intellect", "value": 1}
            dialogue_trait_hint = "Methodical"
            faction_influenced = "traders"

            # Background information through dialogue
            if "background" not in locals():
                # sleep(2)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'You seem to know what questions to ask,' the bartender observes. 'What's your background?'"
                )
                game_state.ui.info_message(
                    Fore.YELLOW + "\nHow do you respond?")
                background_options = {
                    1: "Corp Dropout: 'Corporate sector. Decided the pay wasn't worth the soul-crushing monotony.'",
                    2: "Discharged Trooper: 'Military. Let's say my discharge wasn't ceremonial.'",
                    3: "Ex-Miner: 'Independent mining operations. Tired of breaking my back for middlemen taking all the profit.'",
                    4: "Void Runner: 'Born in deep space. Never known a permanent home other than my ship.'",
                    5: "Lunar Drifter: 'Grew up in Luna's shadow districts. Learned to survive by any means necessary.'",
                    6: "Xeno-Biologist: 'Academic background. The limitations of institutional research became... problematic.'",
                    # Bartender's special background
                    7: "Station Fixer: 'Been a mediator between factions for years. Know how to grease the right gears.'",
                }

                for i, option in background_options.items():
                    # sleep(0.2)
                    game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

                valid_bg_choice = False
                bg_idx = 1  # Default value and type annotation
                while not valid_bg_choice:
                    bg_choice = input(Fore.WHITE + "\nYour response (1-7): ")
                    if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 7:
                        valid_bg_choice = True
                        bg_idx = int(bg_choice)
                    else:
                        game_state.ui.info_message(
                            Fore.RED + "Please enter a number between 1 and 7."
                        )  # Set background based on choice
                if bg_idx == 1:
                    background = "Corp Dropout"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'The corps have their uses,' Obsidian notes. 'Their training, their connections... just not their loyalty or ethics.'"
                    )
                elif bg_idx == 2:
                    background = "Discharged Trooper"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\nThe bartender's sensors whir. 'Military experience is valuable out here. Combat skills and discipline... even if you had a disagreement with command.'"
                    )
                elif bg_idx == 3:
                    background = "Ex-Miner"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Mining teaches patience and persistence,' the bartender comments. 'And you learn to spot real value beneath the surface.'"
                    )
                elif bg_idx == 4:
                    background = "Void Runner"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Space-born,' Obsidian acknowledges. 'You have the look. That natural ease in low-G that planet-born never quite master.'"
                    )
                elif bg_idx == 5:
                    background = "Lunar Drifter"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Luna's domes breed a certain type,' Obsidian observes. 'Quick wits, quicker reflexes. Survival skills that transfer well to the void.'"
                    )
                elif bg_idx == 6:
                    background = "Xeno-Biologist"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'A scholar in our midst,' Obsidian remarks. 'Interesting. Knowledge is currency out here, especially the rare kind.'"
                    )
                else:
                    background = "Station Fixer"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\nObsidian's optical sensors flicker in what might be recognition. 'A fellow mediator. Not many understand the delicate balance of station politics.'"
                    )
                    game_state.ui.info_message(
                        Fore.YELLOW
                        + "\nYou've chosen the bartender's special background. This will provide unique advantages in social situations and faction interactions."
                    )

            # Ship details if not already established
            if "ship_name" not in locals():
                # sleep(2)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'What vessel brought you here?' the bartender asks. 'I like to know what's in our docks.'"
                )

                # Ask for ship name
                ship_name = ""
                while not ship_name:
                    ship_name = input(Fore.WHITE + "Your ship's designation: ")
                    if not ship_name:
                        game_state.ui.info_message(
                            Fore.RED + "Your ship needs a name.")

                game_state.ui.info_message(
                    Fore.CYAN
                    + f"\n'The {ship_name},' Obsidian acknowledges. 'And what type of ship is she?'"
                )

                appearance_options = {
                    1: "Rust Bucket: 'Older model. Not pretty, but reliable enough with proper maintenance.'",
                    2: "Industrial Hauler: 'Cargo vessel. Reinforced hull, practical design.'",
                    3: "Sleek Runner: 'Fast, maneuverable. Not much cargo space, but she can outrun trouble.'",
                }

                for i, option in appearance_options.items():
                    # sleep(0.2)
                    game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

                valid_appearance_choice = False
                app_idx = 1  # Default value and type annotation
                while not valid_appearance_choice:
                    appearance_choice = input(
                        Fore.WHITE + "\nYour description (1-3): ")
                    if (
                        is_valid_int(appearance_choice)
                        and 1 <= int(appearance_choice) <= 3
                    ):
                        valid_appearance_choice = True
                        app_idx = int(appearance_choice)
                    else:
                        game_state.ui.info_message(
                            Fore.RED + "Please enter a number between 1 and 3."
                        )

                # Set appearance based on choice
                if app_idx == 1:
                    ship_appearance = "Rust Bucket"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Those old models are surprisingly resilient,' Obsidian observes. 'Often overlooked by pirates too - they assume there's nothing worth taking.'"
                    )
                elif app_idx == 2:
                    ship_appearance = "Industrial Hauler"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Practical,' the bartender notes. 'Cargo space is at a premium these days. You'll find plenty of transport opportunities.'"
                    )
                else:
                    ship_appearance = "Sleek Runner"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Speed has its advantages,' Obsidian remarks. 'Especially when you need to make a hasty exit.'"
                    )

            # Personality trait selection
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender swirls the amber liquid in their glass thoughtfully. 'In my line of work, you learn to read people quickly. You strike me as...'"
            )  # Offer positive traits
            game_state.ui.info_message(
                Fore.YELLOW + "\nHow would you describe your greatest strength?"
            )
            pos_trait_options = {
                1: f"Charismatic: 'I know how to talk to people, make connections. It opens doors.' ({dialogue_trait_hint} - Suggested)",
                2: "Resourceful: 'I'm adaptable. Can make something from nothing when needed.'",
                3: "Resilient: 'I bounce back from setbacks. Nothing keeps me down for long.'",
            }

            for i, option in pos_trait_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_trait_choice = False
            while not valid_trait_choice:
                trait_choice = input(Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(trait_choice) and 1 <= int(trait_choice) <= 3:
                    valid_trait_choice = True
                    trait_idx = int(trait_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set positive trait based on choice
            if trait_idx == 1:
                positive_trait = "Charismatic"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A valuable talent,' the bartender agrees. 'The right words at the right time can be more powerful than any weapon.'"
                )
            elif trait_idx == 2:
                positive_trait = "Resourceful"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Adaptability is survival,' Obsidian approves. 'The void is unforgiving to those who can't improvise.'"
                )
            else:
                positive_trait = "Resilient"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Resilience matters,' the bartender acknowledges. 'Everyone falls. The successful ones get back up.'"
                )

            # Add negative trait selection
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender's expression shifts subtly. 'Of course, we all have our... challenges. Yours seems to be...'"
            )

            # Offer negative traits
            game_state.ui.info_message(
                Fore.YELLOW + "\nWhat might get you into trouble?"
            )
            neg_trait_options = {
                1: "Superstitious: 'I trust my hunches and omens. Logic isn't everything.'",
                2: "Reckless: 'I take chances. Sometimes too many.'",
                3: "Forgetful: 'Details slip by me. I see the big picture, miss the fine game_state.ui.info_message.'",
            }

            for i, option in neg_trait_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.RED}{i}. {option}")

            valid_neg_trait_choice = False
            while not valid_neg_trait_choice:
                neg_trait_choice = input(
                    Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(neg_trait_choice) and 1 <= int(neg_trait_choice) <= 3:
                    valid_neg_trait_choice = True
                    neg_trait_idx = int(neg_trait_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set negative trait based on choice
            if neg_trait_idx == 1:
                negative_trait = "Superstitious"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nObsidian nods slowly. 'The void has its mysteries. Some of the oldest spacers have their rituals... though they don't always admit it.'"
                )
            elif neg_trait_idx == 2:
                negative_trait = "Reckless"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Bold moves can pay off,' the bartender concedes. 'They can also end with your ship scattered across an asteroid field.'"
                )
            else:
                negative_trait = "Forgetful"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A common failing,' Obsidian comments. 'But in space, overlooking a small detail can have... outsized consequences.'"
                )

        elif bar_choice_num == 3:
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender's metallic fingers deftly collect your credits. A compartment in their chest hums as they extract a dusty bottle from beneath the bar."
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'Earth whiskey. Real thing, not synthetic.' They pour two glasses, raising one in salutation."
            )
            # sleep(1.5)
            game_state.ui.info_message(
                Fore.CYAN
                + "'Generous types need friends in this sector. Station administrator owes me. Might be able to arrange a discount on docking fees.'"
            )
            dialogue_bonus = {"stat": "charisma", "value": 1}
            dialogue_trait_hint = "Charismatic"
            faction_influenced = "corporations"

            # Background information through dialogue
            if "background" not in locals():
                # sleep(2)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nObsidian regards you over the rim of the glass. 'You handle yourself well. What's your story?'"
                )

                game_state.ui.info_message(
                    Fore.YELLOW + "\nWhat do you share about your past?"
                )
                background_options = {
                    1: "Corp Dropout: 'Used to wear a suit, push data, make others rich. Decided I'd rather make myself rich.'",
                    2: "Void Runner: 'Born in the black. Third generation spacer. Never known a life planetside.'",
                    3: "Xeno-Biologist: 'Academic background. Found out there's more to learn outside university restrictions.'",
                }

                for i, option in background_options.items():
                    # sleep(0.2)
                    game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

                valid_bg_choice = False
                bg_idx = 1  # Default value and type annotation
                while not valid_bg_choice:
                    bg_choice = input(Fore.WHITE + "\nYour response (1-3): ")
                    if is_valid_int(bg_choice) and 1 <= int(bg_choice) <= 3:
                        valid_bg_choice = True
                        bg_idx = int(bg_choice)
                    else:
                        game_state.ui.info_message(
                            Fore.RED + "Please enter a number between 1 and 3."
                        )

                # Set background based on choice
                if bg_idx == 1:
                    background = "Corp Dropout"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Corporate experience has its uses,' Obsidian notes. 'You understand systems, how to work them... and exploit them.'"
                    )
                elif bg_idx == 2:
                    background = "Void Runner"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Deep space is in your blood then,' Obsidian observes. 'You're comfortable where others feel lost.'"
                    )
                else:
                    background = "Xeno-Biologist"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Knowledge is valuable currency,' Obsidian says. 'Especially out here where mysteries still lurk in the dark.'"
                    )
            # Ship details if not already established
            if "ship_name" not in locals():
                # sleep(2)
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Tell me about your vessel,' Obsidian says, refilling your glass. 'I like to know my customers' capabilities.'"
                )

                # Ask for ship name
                ship_name = ""
                while not ship_name:
                    ship_name = input(Fore.WHITE + "What's your ship called? ")
                    if not ship_name:
                        game_state.ui.info_message(
                            Fore.RED + "Your ship needs a name.")

                game_state.ui.info_message(
                    Fore.CYAN
                    + f"\n'The {ship_name},' the bartender repeats. 'And what manner of ship is she?'"
                )

                appearance_options = {
                    1: "Sleek Runner: 'Fast and maneuverable. She's got style and speed.'",
                    2: "Colorful Maverick: 'Custom paint job, modifications. As unique as her captain.'",
                    3: "Retrofitted Classic: 'Vintage model I've updated. They don't make them like that anymore.'",
                }

                for i, option in appearance_options.items():
                    # sleep(0.2)
                    game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

                valid_appearance_choice = False
                app_idx = 1  # Default value and type annotation
                while not valid_appearance_choice:
                    appearance_choice = input(
                        Fore.WHITE + "\nYour description (1-3): ")
                    if (
                        is_valid_int(appearance_choice)
                        and 1 <= int(appearance_choice) <= 3
                    ):
                        valid_appearance_choice = True
                        app_idx = int(appearance_choice)
                    else:
                        game_state.ui.info_message(
                            Fore.RED + "Please enter a number between 1 and 3."
                        )

                # Set appearance based on choice
                if app_idx == 1:
                    ship_appearance = "Sleek Runner"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'A quality vessel,' Obsidian approves. 'Speed can be more valuable than firepower when things get dicey.'"
                    )
                elif app_idx == 2:
                    ship_appearance = "Colorful Maverick"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\nThe bartender's optical sensors gleam with amusement. 'Making a statement. I can appreciate that. The void could use more color.'"
                    )
                else:
                    ship_appearance = "Retrofitted Classic"
                    game_state.ui.info_message(
                        Fore.CYAN
                        + "\n'Classic lines,' Obsidian nods appreciatively. 'They built those old models to last. With the right upgrades, they can outperform the showroom models.'"
                    )

            # Personality trait selection
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender swirls the amber liquid in their glass thoughtfully. 'In my line of work, you learn to read people quickly. You strike me as...'"
            )  # Offer positive traits
            game_state.ui.info_message(
                Fore.YELLOW + "\nHow would you describe your greatest strength?"
            )
            pos_trait_options = {
                1: f"Charismatic: 'I know how to talk to people, make connections. It opens doors.' ({dialogue_trait_hint} - Suggested)",
                2: "Resourceful: 'I'm adaptable. Can make something from nothing when needed.'",
                3: "Resilient: 'I bounce back from setbacks. Nothing keeps me down for long.'",
            }

            for i, option in pos_trait_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.GREEN}{i}. {option}")

            valid_trait_choice = False
            while not valid_trait_choice:
                trait_choice = input(Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(trait_choice) and 1 <= int(trait_choice) <= 3:
                    valid_trait_choice = True
                    trait_idx = int(trait_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set positive trait based on choice
            if trait_idx == 1:
                positive_trait = "Charismatic"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A valuable talent,' the bartender agrees. 'The right words at the right time can be more powerful than any weapon.'"
                )
            elif trait_idx == 2:
                positive_trait = "Resourceful"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Adaptability is survival,' Obsidian approves. 'The void is unforgiving to those who can't improvise.'"
                )
            else:
                positive_trait = "Resilient"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Resilience matters,' the bartender acknowledges. 'Everyone falls. The successful ones get back up.'"
                )

            # Add negative trait selection
            # sleep(2)
            game_state.ui.info_message(
                Fore.CYAN
                + "\nThe bartender's expression shifts subtly. 'Of course, we all have our... challenges. Yours seems to be...'"
            )

            # Offer negative traits
            game_state.ui.info_message(
                Fore.YELLOW + "\nWhat might get you into trouble?"
            )
            neg_trait_options = {
                1: "Superstitious: 'I trust my hunches and omens. Logic isn't everything.'",
                2: "Reckless: 'I take chances. Sometimes too many.'",
                3: "Forgetful: 'Details slip by me. I see the big picture, miss the fine game_state.ui.info_message.'",
            }

            for i, option in neg_trait_options.items():
                # sleep(0.2)
                game_state.ui.info_message(f"{Fore.RED}{i}. {option}")

            valid_neg_trait_choice = False
            while not valid_neg_trait_choice:
                neg_trait_choice = input(
                    Fore.WHITE + "\nYour response (1-3): ")
                if is_valid_int(neg_trait_choice) and 1 <= int(neg_trait_choice) <= 3:
                    valid_neg_trait_choice = True
                    neg_trait_idx = int(neg_trait_choice)
                else:
                    game_state.ui.info_message(
                        Fore.RED + "Please enter a number between 1 and 3."
                    )

            # Set negative trait based on choice
            if neg_trait_idx == 1:
                negative_trait = "Superstitious"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\nObsidian nods slowly. 'The void has its mysteries. Some of the oldest spacers have their rituals... though they don't always admit it.'"
                )
            elif neg_trait_idx == 2:
                negative_trait = "Reckless"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'Bold moves can pay off,' the bartender concedes. 'They can also end with your ship scattered across an asteroid field.'"
                )
            else:
                negative_trait = "Forgetful"
                game_state.ui.info_message(
                    Fore.CYAN
                    + "\n'A common failing,' Obsidian comments. 'But in space, overlooking a small detail can have... outsized consequences.'"
                )

        # Display character summary
        game_state.ui.info_message(
            Fore.YELLOW + "\nREPL SPACE MINER - CHARACTER SUMMARY\n"
        )
        # sleep(0.5)

        game_state.ui.info_message(Fore.CYAN + f"Name: {name}")
        game_state.ui.info_message(Fore.CYAN + f"Age: {age}")
        game_state.ui.info_message(Fore.CYAN + f"Background: {background}")
        game_state.ui.info_message(
            Fore.CYAN + f"Positive Trait: {positive_trait}")
        game_state.ui.info_message(
            Fore.CYAN + f"Negative Trait: {negative_trait}")
        game_state.ui.info_message(
            Fore.CYAN + f"Ship: The {ship_name} ({ship_appearance})"
        )

        # sleep(2)  # Background information for the selected background
        bg_descriptions = {
            "Ex-Miner": "You've spent years breaking rocks in the belt. Your technical skills are superior, and you know how to survive in harsh environments. You have connections with the Belters Union.",
            "Corp Dropout": "Former middle management at a mega-corp. You understand business and have education, but corporations might not view you favorably after your 'strategic exit'.",
            "Lunar Drifter": "You've lived in the shadows of lunar cities, making deals and sometimes working outside the law. Your street smarts are unmatched.",
            "Void Runner": "Born on long-haul freighters, you've spent more time in space than planetside. Your piloting skills are exceptional.",
            "Xeno-Biologist": "You've studied life across the solar system. Your scientific knowledge is valuable, particularly to research organizations.",
            "Discharged Trooper": "Former military with combat experience. Your tactical skills are sharp, but your discharge wasn't entirely honorable.",
        }

        game_state.ui.info_message(f"{Fore.CYAN}{bg_descriptions[background]}")
        # sleep(1)

        # Set background specialization based on background choices made during dialogue
        additional_bonus_details = {}

        # Add specializations based on background for more depth
        if background == "Ex-Miner":
            game_state.ui.info_message(
                Fore.YELLOW
                + "\nYour mining experience has given you a particular edge..."
            )
            # sleep(1.5)
            additional_bonus_details = {
                "type": "skill",
                "name": "engineering",
                "value": 1,
            }
            game_state.ui.info_message(
                Fore.CYAN
                + "Your knack for keeping aging mining equipment running was legendary. (+1 Engineering)"
            )
        elif background == "Corp Dropout":
            game_state.ui.info_message(
                Fore.YELLOW
                + "\nYour corporate training provided you with valuable business insights..."
            )
            # sleep(1.5)
            additional_bonus_details = {
                "type": "stat", "name": "intellect", "value": 1}
            game_state.ui.info_message(
                Fore.CYAN
                + "You developed a sharp analytical mind during your time in the corporate sector. (+1 Intellect)"
            )
        elif background == "Lunar Drifter":
            game_state.ui.info_message(
                Fore.YELLOW
                + "\nYour time navigating lunar politics gave you a particular advantage..."
            )
            # sleep(1.5)
            additional_bonus_details = {
                "type": "stat",
                "name": "perception",
                "value": 1,
            }
            game_state.ui.info_message(
                Fore.CYAN
                + "You learned to spot trouble before it finds you. (+1 Perception)"
            )
        elif background == "Void Runner":
            game_state.ui.info_message(
                Fore.YELLOW
                + "\nBeing born in space has given you a natural affinity..."
            )
            # sleep(1.5)
            additional_bonus_details = {
                "type": "skill", "name": "piloting", "value": 1}
            game_state.ui.info_message(
                Fore.CYAN
                + "You have an intuitive understanding of spacecraft handling. (+1 Piloting)"
            )
        elif background == "Xeno-Biologist":
            game_state.ui.info_message(
                Fore.YELLOW
                + "\nYour scientific training has given you specialized knowledge..."
            )
            # sleep(1.5)
            additional_bonus_details = {
                "type": "skill",
                "name": "education",
                "value": 1,
            }
            game_state.ui.info_message(
                Fore.CYAN
                + "Your research background has prepared you to analyze new situations methodically. (+1 Education)"
            )
        elif background == "Discharged Trooper":
            game_state.ui.info_message(
                Fore.YELLOW
                + "\nYour military background has honed your combat reflexes..."
            )
            # sleep(1.5)
            additional_bonus_details = {
                "type": "skill", "name": "combat", "value": 1}
            game_state.ui.info_message(
                Fore.CYAN
                + "Your training allows you to react quickly in dangerous situations. (+1 Combat)"
            )

    # sleep(1.5)  # Sound effects question - integrate into narrative
    game_state.ui.info_message(
        Fore.YELLOW
        + "\nAs you prepare to leave the bar, your communicator displays a message."
    )
    # sleep(1)
    game_state.ui.info_message(
        Fore.WHITE + "SYSTEM QUERY: Enable audio notification system? [yes/no]"
    )
    sound_choice = input(Fore.WHITE + "Your response: ")
    enable_sound = sound_choice.lower() in ["yes", "y"]

    if enable_sound:
        game_state.ui.info_message(Fore.GREEN + "Audio notifications enabled.")
        # Initialize pygame mixer
        pg.mixer.init()
        pg.mixer.music.set_volume(0.5)
    else:
        game_state.ui.info_message(
            Fore.GREEN + "Audio notifications disabled.")

    # Create character & ship objects with chosen attributes
    from src.classes.ship import Ship
    from src.classes.game import Character  # Character is defined in game.py

    # Default starting values
    CHARACTER_STARTING_CREDS = 1000
    CHARACTER_STARTING_DEBT = 5000

    game_state.ui.info_message(
        Fore.YELLOW + "\nYou check your account status as you leave the bar..."
    )
    # sleep(1)
    game_state.ui.info_message(
        Fore.GREEN + f"Available Credits: {CHARACTER_STARTING_CREDS}"
    )
    game_state.ui.info_message(
        Fore.RED + f"Outstanding Debt: {CHARACTER_STARTING_DEBT}"
    )
    # sleep(1.5)    # Create character instance with the information gathered through dialogue
    character = Character(
        name=name,
        age=age,
        sex=sex,
        background=background,
        starting_creds=CHARACTER_STARTING_CREDS,
        starting_debt=CHARACTER_STARTING_DEBT,
    )

    # Set personality traits directly on the character object
    character.positive_trait = positive_trait
    character.negative_trait = negative_trait

    # Assign the fully initialized character to game_state
    game_state.player_character = character

    # Apply background bonuses
    # More specific type hint
    bg_bonus: Dict[str, int] = BACKGROUND_BONUSES[background]

    for loop_stat_key, bonus_val in bg_bonus.items():
        current_stat_key = cast(
            str, loop_stat_key
        )  # Explicitly cast to str for clarity and type hinting

        # Check if it's a skill (now a direct attribute)
        if current_stat_key in [
            "piloting",
            "engineering",
            "combat",
            "education",
            "charisma",
        ] and hasattr(character, current_stat_key):
            # Skills from BACKGROUND_BONUSES are the starting values.
            setattr(character, current_stat_key, bonus_val)
        elif current_stat_key in character.faction_standings:
            # Faction standings from BACKGROUND_BONUSES are additive.
            character.faction_standings[current_stat_key] = (
                character.faction_standings.get(
                    current_stat_key, 0) + bonus_val
            )
        elif hasattr(character, current_stat_key):
            # This handles base stats like 'technical_aptitude', 'resilience', 'perception', etc.
            # These are direct attributes of the Character class, initialized to a base value (e.g., 5).
            # The bonus_val from BACKGROUND_BONUSES should be ADDED to this base value.
            current_base_val = getattr(character, current_stat_key)
            setattr(
                character, current_stat_key, current_base_val +
                cast(int, bonus_val)
            )
        # If current_stat_key is not a skill, not a faction, and not an attribute, it's an undefined bonus.

    # Apply additional stored bonus from background specialization
    if additional_bonus_details:
        bonus_type = cast(str, additional_bonus_details["type"])
        bonus_name = cast(str, additional_bonus_details["name"])
        bonus_value = cast(
            int, additional_bonus_details["value"]
        )  # Assuming value is int
        applied_bonus_message = ""

        if bonus_type == "skill":
            # Specialization bonuses for skills are additive to what background might have set.
            if bonus_name in [
                "piloting",
                "engineering",
                "combat",
                "education",
                "charisma",
            ] and hasattr(character, bonus_name):
                current_skill_value = getattr(character, bonus_name)
                setattr(character, bonus_name,
                        current_skill_value + bonus_value)
                applied_bonus_message = f"Your specialization grants an additional +{bonus_value} to {bonus_name} skill."
        elif bonus_type == "faction":
            # Specialization bonuses for factions are additive.
            if bonus_name in character.faction_standings:
                current_faction_value = character.faction_standings.get(
                    bonus_name, 0)
                character.faction_standings[bonus_name] = (
                    current_faction_value + bonus_value
                )
                applied_bonus_message = f"Your specialization grants an additional +{bonus_value} to {bonus_name} standing."
        elif bonus_type == "stat":  # Handling for base stats like perception
            # Specialization bonuses for base stats are additive to the (base_value + background_bonus).
            # Specialization bonuses for base stats are additive to the (base_value + background_bonus).
            if hasattr(character, bonus_name):
                current_stat_val = getattr(character, bonus_name)
                setattr(character, bonus_name, current_stat_val + bonus_value)
                applied_bonus_message = f"Your specialization grants an additional +{bonus_value} to your {bonus_name}."

        if applied_bonus_message:
            game_state.ui.info_message(Fore.GREEN + applied_bonus_message)
            # sleep(1)

    # Apply dialogue bonuses from character interaction
    if (
        dialogue_bonus
        and "stat" in dialogue_bonus
        and "value" in dialogue_bonus
        and dialogue_bonus["stat"]
        and dialogue_bonus["value"]
    ):
        bonus_stat = str(dialogue_bonus["stat"])
        bonus_val = cast(int, dialogue_bonus["value"])

        if bonus_val > 0:
            # Handle both skills and base stats
            if bonus_stat in [
                "piloting",
                "engineering",
                "combat",
                "education",
                "charisma",
            ] and hasattr(character, bonus_stat):
                # It's a skill
                current_val = getattr(character, bonus_stat)
                setattr(character, bonus_stat, current_val + bonus_val)
                game_state.ui.info_message(
                    Fore.GREEN
                    + f"Your conversation has improved your {bonus_stat} skill by +{bonus_val}."
                )
            elif hasattr(character, bonus_stat):
                # It's a base stat
                current_val = getattr(character, bonus_stat)
                setattr(character, bonus_stat, current_val + bonus_val)
                game_state.ui.info_message(
                    Fore.GREEN
                    + f"Your conversation has improved your {bonus_stat} by +{bonus_val}."
                )

    # Apply faction standing bonus from dialogue
    if (
        faction_influenced
        and hasattr(character, "faction_standings")
        and faction_influenced in character.faction_standings
    ):
        faction_bonus = 5  # Standard bonus for initial conversation
        current_standing = character.faction_standings.get(
            faction_influenced, 0)
        character.faction_standings[faction_influenced] = (
            current_standing + faction_bonus
        )
        game_state.ui.info_message(
            Fore.GREEN
            + f"Your interaction has improved your standing with the {faction_influenced} faction by +{faction_bonus}."
        )

    # Record the contact made during character creation
    if approach_choice_num == 1:
        contact_type = "mercenary"
    elif approach_choice_num == 2:
        contact_type = "bounty_hunter"
    elif approach_choice_num == 3:
        contact_type = "engineer"
    else:
        contact_type = "bartender"
        # Add the contact as a proper Contact object
    # Initialize contacts list if it doesn't exist
    if not hasattr(character, "contacts"):
        # Add contacts as a list attribute (as defined in the Character class)
        setattr(character, "contacts", [])

    # Get the contact object from our new system
    contact_obj = get_contact(contact_type)
    # Record that this was first interaction
    contact_obj.last_interaction = "Made first contact at Terminus Bar"
    contact_obj.met_during = "character_creation"

    # Add the contact to the player's contacts list
    contacts_list = getattr(character, "contacts")
    contacts_list.append(contact_obj)
    game_state.ui.info_message(
        Fore.CYAN
        + f"\nYou've made a connection with {contact_obj.name}, "
        + f"the {contact_type} at Terminus Bar. This connection may be valuable in the future."
    )  # sleep(1.5)

    # Create ship from the selected template and assign it to game_state
    ship = Ship.from_template(ship_template_id, ship_name)
    game_state.player_ship = ship


def quick_start(game_state: "Game"):
    """Create a character with default values for quick start."""
    from src.classes.game import Character
    from src.classes.ship import Ship

    game_state.ui.info_message(
        Fore.CYAN
        + "\nQuick Start mode activated via command line flag. Skipping customization..."
    )
    game_state.ui.info_message(
        Fore.CYAN
        + "\nThe station's customs terminal flashes with a quick entry protocol..."
    )
    # sleep(1)

    # Default values
    name = "Space Miner"
    age = 30
    sex = "male"
    background = "Ex-Miner"
    positive_trait = "Resilient"
    negative_trait = "Impatient"
    ship_name = "Rusty Bucket"
    ship_appearance = "Rust Bucket"

    # Default starting values
    CHARACTER_STARTING_CREDS = 1000
    CHARACTER_STARTING_DEBT = 5000  # Create default character
    character = Character(
        name=name,
        age=age,
        sex=sex,
        background=background,
        starting_creds=CHARACTER_STARTING_CREDS,
        starting_debt=CHARACTER_STARTING_DEBT,
    )
    # Set personality traits directly on the character object
    character.positive_trait = positive_trait
    character.negative_trait = negative_trait

    # Assign the character to game_state
    game_state.player_character = character

    # Apply Ex-Miner background bonuses
    # More specific type hint
    bg_bonus: Dict[str, int] = BACKGROUND_BONUSES["Ex-Miner"]

    for loop_key, bonus in bg_bonus.items():
        key = cast(
            str, loop_key
        )  # Ensure key is treated as a string for clarity and type hinting
        # Check if it's a skill (now a direct attribute)
        if key in [
            "piloting",
            "engineering",
            "combat",
            "education",
            "charisma",
        ] and hasattr(character, key):
            setattr(character, key, bonus)  # Set as base value
        elif key in character.faction_standings:
            character.faction_standings[key] = (
                character.faction_standings.get(key, 0) + bonus
            )  # Add to existing
        elif hasattr(character, key):  # It's a base stat
            current_base_val = getattr(character, key)
            setattr(
                character, key, current_base_val + cast(int, bonus)
            )  # Add to existing base value    # Create ship from the default balanced template
    ship = Ship.from_template("balanced_cruiser", ship_name)
    game_state.player_ship = ship
    # Default sound to off in quick start
    game_state.sound_enabled = False

    # Add a default contact for quick start as a proper Contact object
    # Initialize the contacts list attribute
    setattr(game_state.player_character, "contacts", [])

    # Get bartender contact and add it to the player's contact
    bartender = get_contact("bartender")
    bartender.met_during = "character_creation"
    bartender.last_interaction = "Quick start"

    # Display character summary
    game_state.ui.info_message(
        Fore.YELLOW + "\nREPL SPACE MINER - QUICK START CHARACTER\n"
    )
    game_state.ui.info_message(Fore.CYAN + f"Name: {name}")
    game_state.ui.info_message(Fore.CYAN + f"Age: {age}")
    game_state.ui.info_message(Fore.CYAN + f"Background: {background}")
    game_state.ui.info_message(Fore.CYAN + f"Positive Trait: {positive_trait}")
    game_state.ui.info_message(Fore.CYAN + f"Negative Trait: {negative_trait}")
    game_state.ui.info_message(
        Fore.CYAN + f"Ship: The {ship_name} ({ship_appearance})")
    game_state.ui.info_message(
        f"\n{Fore.GREEN}Quick start initiated! Welcome aboard the {ship_name}."
    )
    # sleep(1)
    game_state.ui.info_message(
        f"{Fore.YELLOW}Your starting credits: {CHARACTER_STARTING_CREDS}"
    )
    game_state.ui.info_message(
        f"{Fore.RED}Your starting debt: {CHARACTER_STARTING_DEBT}"
    )
    game_state.ui.info_message(
        f"{Fore.CYAN}You've established a connection with {bartender.name}, the bartender at Terminus Bar."
    )
    game_state.ui.info_message(
        f"{Fore.RED}However, being {negative_trait} might present some challenges."
    )
    game_state.ui.info_message(
        f"{Fore.CYAN}Note: You used the --skipc flag to skip customization. Next time, launch without this flag for full character creation."
    )
    # sleep(1)

    # Position the ship at a station or at a safe location
    if game_state.rnd_station:
        # Position ship at the random station and dock it
        game_state.player_ship.space_object.position = (
            game_state.rnd_station.position.copy()
        )
        game_state.player_ship.dock_into_station(game_state.rnd_station)
        game_state.ui.info_message(
            f"{Fore.GREEN}Ship positioned and docked at {game_state.rnd_station.name}."
        )
    else:
        # No station available, position ship at system center
        from pygame import Vector2

        game_state.player_ship.space_object.position = Vector2(0, 0)
        game_state.ui.info_message(
            f"{Fore.YELLOW}No docking station available. Ship positioned at system center (0,0)."
        )

    return game_state
