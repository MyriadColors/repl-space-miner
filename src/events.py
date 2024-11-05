from src.classes.game import Game, Background, background_choices
from src.classes.ship import Ship
from src.pygameterm.terminal import PygameTerminal


def intro_event(terminal: PygameTerminal):
    game: Game = terminal.app_state

    # Quick start option
    quick_start_choice = terminal.prompt_user("Do you wish to quick start the game (yes/no)? ")
    if quick_start_choice.lower() in ["yes", "y"]:
        return quick_start(terminal)

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
        "<green192>'Heard you're desperate for work,'</green192> a voice like gravel in a turbine rasps.",
        "The ancient speakers crackle, as if agreeing. You turn, meet eyes hard as vacuum.",
        "A woman in a black suit that's seen better days - and worse nights - sizes you up.",
        "<green192>'I run this lovely establishment. Got a job that needs doing. You game?'</green192>",
    ]

    for line in intro_text:
        terminal.wait(100)
        terminal.writeLn(line)

    if (
        terminal.prompt_multiple_choice("Take the plunge?", ["Hell yes", "I'll pass"])
        == 2
    ):
        terminal.writeLn(
            "You mumble an excuse, turn back to your drink. The woman's laugh is cold."
        )
        terminal.writeLn(
            "<green192>'Your funeral, spacer. Debt collectors ain't known for mercy.'</green192>"
        )
        terminal.writeLn(
            "She vanishes into the smoke. You're left alone with your bleak future."
        )
        terminal.writeLn("GAME OVER")
        terminal.quit()
        return

    terminal.writeLn(
        "A razor-thin smile cuts across her face. <green192>'Smart move, spacer.'</green192>"
    )
    terminal.writeLn(
        "She leans in close. Scars crisscross her cheek like asteroid belts."
    )
    terminal.writeLn(
        "<green192>'Now, what name should I put on your makeshift tombstone?'</green192>"
    )

    # Player name input validation
    while True:
        player_name = terminal.prompt_user("Your name (choose wisely): ")
        if player_name and len(player_name) <= 20:
            break
        terminal.writeLn(
            "<red>Invalid name. Please enter a name with 1-20 characters.</red>"
        )

    terminal.writeLn(
        f"<green192>'Well then, {player_name}. What sorry tale landed you in my fine establishment?'</green192>"
    )

    background_choices_names: list[str] = [choice.name for choice in background_choices]
    chosen_background_index: int = terminal.prompt_multiple_choice(
        "Your checkered past:", background_choices_names
    )
    chosen_background: Background = background_choices[chosen_background_index - 1]

    sex: str = (
        "Male"
        if terminal.prompt_multiple_choice("Biological sex:", ["Male", "Female"]) == 1
        else "Female"
    )

    # Age input validation
    while True:
        age_input = terminal.prompt_user("Your age (18 - 60): ")
        try:
            age = int(age_input)
            if 18 <= age <= 60:
                break
            terminal.writeLn(
                "<red>Invalid age. Please enter an age between 18 and 60.</red>"
            )
        except ValueError:
            terminal.writeLn("<red>Invalid input. Please enter a number.</red>")
    # Create character
    game.set_player_character(
        player_name,
        age,
        sex,
        chosen_background.name,
        chosen_background.credits,
        chosen_background.debt,
    )

    # Ship selection
    terminal.writeLn(
        "The woman's eyes narrow. <green192>'Now, about your ride...'</green192>"
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

    ship_choice = terminal.prompt_multiple_choice(
        "Your deathtrap of choice:", list(ship_choices.keys())
    )
    chosen_ship = list(ship_choices.keys())[ship_choice - 1]

    # Ship name input validation
    while True:
        ship_name: str = terminal.prompt_user("Baptize your bird: ")
        if ship_name and len(ship_name) <= 30:
            break
        terminal.writeLn(
            "<red>Invalid ship name. Please enter a name with 1-30 characters.</red>"
        )
    ship_data: dict = ship_choices[chosen_ship]
    ship_data["name"] = ship_name

    game.player_ship = Ship(
        ship_data["name"],
        game.rnd_station.space_object.get_position(),
        ship_data["speed"],
        ship_data["max_fuel"],
        ship_data["fuel_consumption"],
        ship_data["cargo_capacity"],
        ship_data["value"],
        ship_data["mining_speed"],
    )

    terminal.writeLn(
        f"The {ship_name}'s name echoes through the bar. A declaration of defiance."
    )
    terminal.writeLn(
        "It's a rustbucket, sure, but it's *your* rustbucket. Your ticket to freedom."
    )
    terminal.writeLn("Or a floating coffin. Time will tell.")

    # Tutorial
    tutorial_text = [
        "<green192>'Listen up, rookie. Here's Survival 101:'</green192>",
        f"<green192>'You're {game.get_player_character().debt} credits in the hole. Every chip matters.'</green192>",
        "<green192>'Creditors? They're sharks. And your blood's in the water.'</green192>",
        "<green192>'Fuel is life out there. Empty tank? You're space debris.'</green192>",
        "<green192>'Stations are oases. Fuel, repairs, upgrades. If you've got the creds.'</green192>",
        "<green192>'Asteroids are floating goldmines. Learn to crack 'em or stay broke.'</green192>",
        "<green192>'Oh, and pirates? They're the least of your worries.'</green192>",
        "Type 'status' or 'st' to check your ship, creds, and impending doom.",
    ]

    for line in tutorial_text:
        terminal.writeLn(line)

    # First mission selection
    terminal.writeLn(
        "<green192>'Now, your first job. Three options. Choose your poison:'</green192>"
    )

    missions = {
        "The Delivery": {
            "name": "The Package",
            "description": "Simple delivery job. Don't ask, don't open, don't lose.",
            "risk_level": "Low",
            "reward": 1000,
            "location": "Terminus Station to Proxima Centauri",
            "estimated_duration": "2 days",
        },
        "The Bounty": {
            "name": "The Salvage",
            "description": "Recover a black box from a derelict ship in the Crimson Nebula. Watch out for... competitors.",
            "risk_level": "Medium",
            "reward": 2500,
            "location": "Crimson Nebula",
            "requirements": {"ship_type": "Mining Vessel", "min_cargo_space": 50},
            "special_conditions": ["Radiation hazard", "Possible pirate activity"],
            "estimated_duration": "1 week",
        },
        "The Heist": {
            "name": "The Heist",
            "description": "During an 'unfortunate accident' at a Novo-Gen Corp research station, certain valuable data might go missing.",
            "risk_level": "High",
            "reward": 5000,
            "location": "Novo-Gen Research Station",
            "requirements": {"min_stealth": 3, "hacking_skill": 2},
            "estimated_duration": "6 hours",
            "special_conditions": ["High security", "Limited time window"],
        },
    }

    for i, mission in enumerate(missions):
        terminal.writeLn(f"{i + 1}. {mission}")

    mission_choice = terminal.prompt_multiple_choice(
        "Choose your poison:", list(missions.keys())
    )

def quick_start(terminal: PygameTerminal):
    game: Game = terminal.app_state

    # Create a standard character
    standard_background = background_choices[0]
    game.set_player_character(
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

    game.player_ship = Ship(
        str(standard_ship["name"]),
        game.rnd_station.space_object.get_position(),
        standard_ship["speed"],
        standard_ship["max_fuel"],
        standard_ship["fuel_consumption"],
        standard_ship["cargo_capacity"],
        standard_ship["value"],
        standard_ship["mining_speed"],
    )

    terminal.writeLn(
        "<yellow128>Quick start initiated. Standard character and ship created.</yellow128>"
    )
    terminal.writeLn(
        f"Character: Test Pilot, Age: 30, Sex: Male, Background: {standard_background.name}"
    )
    terminal.writeLn(f"Ship: {standard_ship['name']}")
    terminal.writeLn("Type 'status' or 'st' to check your ship and character details.")

    # Skip tutorial and mission selection
    terminal.writeLn(
        "<yellow128>Tutorial and first mission selection skipped for quick start.</yellow128>"
    )
    terminal.writeLn("You're ready to explore the galaxy. Good luck, spacer!")

    return
