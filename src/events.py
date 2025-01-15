from time import sleep

from src.classes.game import Background, background_choices, Game
from src.classes.ship import Ship


def intro_event(game_state: 'Game'):
    # Quick start option
    quick_start_choice = input("Do you wish to quick start the game (yes/no)? ")
    if quick_start_choice.lower() in ["yes", "y"]:
        return quick_start(game_state)

    # Introduction text
    intro_text = [
        "The Terminus Bar. A name that sends shivers down the spines of hardened spacers.",
        "You push through the hissing airlock, hit by a wall of sound and stench.",
        "Neon bathes grimy walls in sickly green, casting long shadows across desperate faces.",
        "The air? A toxic cocktail of synth-ale, cigar smoke, and raw fear.",
        "You claim a stool, order a drink that tastes like engine coolant. It fits your mood.",
        "Each sip is bitter, like the creditors' breath on your neck. Their patience? Gone.",
        "A figure materializes beside you. You catch a whiff of ozone and danger.",
        "Metal glints beneath a worn leather hat. Weapon? Tool? Both, probably.",
        "'Heard you're desperate for work,' a voice like gravel in a turbine rasps.",
        "The ancient speakers crackle, as if agreeing. You turn, meet eyes hard as vacuum.",
        "A woman in a black suit that's seen better days - and worse nights - sizes you up.",
        "'I run this lovely establishment. Got a job that needs doing. You game?'",
    ]

    for line in intro_text:
        sleep(1)
        print(line)
    response = int(input("Take the plunge? (1. Yes, 2. No): "))
    if response == 2:
        print(
            "You mumble an excuse, turn back to your drink. The woman's laugh is cold."
        )
        print(
            "'Your funeral, spacer. Debt collectors ain't known for mercy.'"
        )
        print(
            "She vanishes into the smoke. You're left alone with your bleak future."
        )
        print("GAME OVER")
        exit()

    print(
        "A razor-thin smile cuts across her face. 'Smart move, spacer.'"
    )
    print(
        "She leans in close. Scars crisscross her cheek like asteroid belts."
    )
    print(
        "'Now, what name should I put on your makeshift tombstone?'"
    )

    # Player name input validation
    while True:
        player_name = input("Your name (choose wisely): ")
        if player_name and len(player_name) <= 20:
            break
        print(
            "Invalid name. Please enter a name with 1-20 characters."
        )

    print(
        f"'Well then, {player_name}. What sorry tale landed you in my fine establishment?'"
    )

    background_choices_names: list[str] = [choice.name for choice in background_choices]
    for background_index, background_name in enumerate(background_choices_names):
        print(f"{background_index + 1}. {background_name}")
    while True:
        try:
            chosen_background_index: int = int(input("Choose your background: "))
            if 1 <= chosen_background_index <= len(background_choices):
                break
            else:
                print(
                    f"Invalid choice. Please choose a number between 1 and {len(background_choices)}."
                )
        except ValueError:
            print("Invalid input. Please enter a number.")
    chosen_background: Background = background_choices[chosen_background_index - 1]

    while True:
        sex_input = input("Biological sex (Male/Female): ").strip().capitalize()
        if sex_input in ["Male", "Female"]:
            sex = sex_input
            break
        print("Invalid input. Please enter 'Male' or 'Female'.")

    # Age input validation
    while True:
        age_input = input("Your age (18 - 60): ")
        try:
            age = int(age_input)
            if 18 <= age <= 60:
                break
            print(
                "Invalid age. Please enter an age between 18 and 60."
            )
        except ValueError:
            print("Invalid input. Please enter a number.")
    # Create character
    game_state.set_player_character(
        player_name,
        age,
        sex,
        chosen_background.name,
        chosen_background.credits,
        chosen_background.debt,
    )

    # Ship selection
    print(
        "The woman's eyes narrow. 'Now, about your ride...'"
    )
    ship_choices = {
        "The Scrapheap (Freighter)": {
            "speed": 0.00005,
            "max_fuel": 200,
            "fuel_consumption": 0.075,
            "cargo_capacity": 200,
            "value": 25000,
            "mining_speed": 0.005,
        },
        "The Stiletto (Scout)": {
            "speed": 0.0005,
            "max_fuel": 75,
            "fuel_consumption": 0.05,
            "cargo_capacity": 25,
            "value": 35000,
            "mining_speed": 0.001,
        },
        "The Borer (Mining Vessel)": {
            "speed": 0.00025,
            "max_fuel": 100,
            "fuel_consumption": 0.05,
            "cargo_capacity": 150,
            "value": 30000,
            "mining_speed": 0.05,
        },
    }

    for idx, choice in enumerate(ship_choices.keys(), 1):
        print(f"{idx}. {choice}")
    while True:
        try:
            ship_choice = int(input("Your deathtrap of choice: "))
            if 1 <= ship_choice <= len(ship_choices):
                chosen_ship = list(ship_choices.keys())[ship_choice - 1]
                break
            else:
                print(f"Invalid choice. Please choose a number between 1 and {len(ship_choices)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(ship_choices)}.")

    # Ship name input validation
    while True:
        ship_name: str = input("Baptize your bird: ")
        if ship_name and len(ship_name) <= 30:
            break
        print(
            "Invalid ship name. Please enter a name with 1-30 characters."
        )
    ship_data: dict = ship_choices[chosen_ship]
    ship_data["name"] = ship_name

    game_state.player_ship = Ship(
        ship_data["name"],
        game_state.rnd_station.space_object.get_position(),
        ship_data["speed"],
        ship_data["max_fuel"],
        ship_data["fuel_consumption"],
        ship_data["cargo_capacity"],
        ship_data["value"],
        ship_data["mining_speed"],
    )

    print(
        f"The {ship_name}'s name echoes through the bar. A declaration of defiance."
    )
    print(
        "It's a rustbucket, sure, but it's *your* rustbucket. Your ticket to freedom."
    )
    print("Or a floating coffin. Time will tell.")

    # Tutorial
    tutorial_text = [
        "'Listen up, rookie. Here's Survival 101:'",
        f"'You're {game_state.get_player_character().debt} credits in the hole. Every chip matters.'",
        "'Creditors? They're sharks. And your blood's in the water.'",
        "'Fuel is life out there. Empty tank? You're space debris.'",
        "'Stations are oases. Fuel, repairs, upgrades. If you've got the creds.'",
        "'Asteroids are floating goldmines. Learn to crack 'em or stay broke.'",
        "'Oh, and pirates? They're the least of your worries.'",
        "Type 'status' or 'st' to check your ship, creds, and impending doom.",
    ]

    for line in tutorial_text:
        print(line)


def quick_start(game_state: 'Game'):

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
    )

    print(
        "Quick start initiated. Standard character and ship created."
    )
    print(
        f"Character: Test Pilot, Age: 30, Sex: Male, Background: {standard_background.name}"
    )
    print(f"Ship: {standard_ship['name']}")
    print("Type 'status' or 'st' to check your ship and character details.")

    # Skip tutorial and mission selection
    print(
        "Tutorial and first mission selection skipped for quick start."
    )
    print("You're ready to explore the galaxy. Good luck, spacer!")

    return
