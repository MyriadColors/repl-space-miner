from time import sleep
from colorama import init, Fore, Style

from src.classes.game import Background, background_choices, Game
from src.classes.ship import Ship
from src.helpers import is_valid_int, is_valid_float, is_valid_bool

init(autoreset=True)

def intro_event(game_state: 'Game'):
    # Quick start option
    quick_start_choice = input(Fore.YELLOW + "Do you wish to quick start the game (yes/no)? ")
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
    print(Fore.GREEN + "3. The bartender with cybernetic eyes that scan your debt profile")
    
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
        print(Fore.CYAN + "\nThe mercenary looks up. 'Either you're brave or stupid. Which is it?'")
        print("Her prosthetic arm whirs quietly as she gestures to the empty seat.")
        print("'Name's Vex. Used to captain a blockade runner before... complications.'")
        print("She eyes you with professional interest. 'You look desperate. Good.'")
        contact_name = "Vex"
        bonus_trait = "Combat"
    elif approach_choice == 2:
        print(Fore.CYAN + "\nThe engineer's hood shifts, revealing circuitry embedded in their temple.")
        print("'Interesting neural patterns,' they murmur. 'You're different from the usual rabble.'")
        print("Mechanical fingers disassemble complex tech without looking. 'I'm Nexus.'")
        print("'Those in need of... alternative solutions find me useful.'")
        contact_name = "Nexus"
        bonus_trait = "Technical"
    else:
        print(Fore.CYAN + "\nThe bartender's synthetic eyes whir as they focus on you.")
        print("'Debt profile: significant. Survival odds: minimal,' she states flatly.")
        print("She slides a drink across the counter. 'On the house. Last courtesy before collection.'")
        print("'I'm Madam Siren. This establishment offers opportunities to the desperate.'")
        contact_name = "Madam Siren"
        bonus_trait = "Trading"

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
        print(Fore.CYAN + f"\n{contact_name}'s expression darkens. 'Nobody walks away from me.'")
        print("The room falls silent. Three enforcers materialize from the shadows.")
        second_chance = input(Fore.YELLOW + "Change your mind? (yes/no): ")
        if second_chance.lower() not in ["yes", "y"]:
            print(Fore.RED + "\nYou stand your ground. Admirable, but foolish.")
            print("The last thing you see is a neural disruptor activating.")
            print(Fore.RED + "\n----- GAME OVER -----")
            exit()
        print(Fore.CYAN + "\nA wise decision. The enforcers melt back into the darkness.")

    # Character creation with more depth
    print(Fore.CYAN + f"\n{contact_name} nods approvingly. 'Now, what's the name they'll whisper in fear?'")

    # Player name input validation
    while True:
        player_name = input(Fore.YELLOW + "\nYour name (choose wisely): ")
        if player_name and len(player_name) <= 20:
            break
        print(Fore.RED + "Invalid name. Please enter a name with 1-20 characters.")

    print(Fore.CYAN + f"\n'Ah, {player_name},' {contact_name} says, testing the weight of your name.")
    print("'Everyone in the Outer Rim has a story. What's yours?'")

    # Enhanced background selection with descriptions
    print(Fore.YELLOW + "\n--- SELECT YOUR PAST ---")
    enhanced_backgrounds = []
    
    for i, bg in enumerate(background_choices):
        enhanced_bg = bg
        if i == 0:  # Ex-Military
            desc = "Military training, but a dishonorable discharge. Combat skills but bureaucratic enemies."
        elif i == 1:  # Merchant
            desc = "Former trading empire, bankrupted by corporate sabotage. Contacts but enemies."
        elif i == 2:  # Engineer
            desc = "Brilliant innovations, stolen by your employer. Technical skills but industrial blacklisting."
        elif i == 3:  # Criminal
            desc = "Legendary heists, betrayed by your crew. Street smarts but bounty hunters on your trail."
        else:
            desc = "A mysterious past with advantages and disadvantages."
        
        enhanced_backgrounds.append((enhanced_bg, desc))
        print(Fore.GREEN + f"{i+1}. {enhanced_bg.name}: {desc}")
        print(f"   Starting Credits: {enhanced_bg.credits}, Debt: {enhanced_bg.debt}\n")
    
    while True:
        try:
            chosen_background_index = int(input(Fore.YELLOW + "Choose your background (1-" + str(len(background_choices)) + "): "))
            if 1 <= chosen_background_index <= len(background_choices):
                break
            else:
                print(Fore.RED + f"Invalid choice. Please choose between 1 and {len(background_choices)}.")
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")
    
    chosen_background = background_choices[chosen_background_index - 1]
    
    # More personalized character details
    print(Fore.CYAN + f"\n{contact_name} nods knowingly. 'A {chosen_background.name}. That explains a lot.'")
    
    # Enhanced age and sex selection with implications
    print(Fore.YELLOW + "\nDifferent ages bring different advantages:")
    print(Fore.GREEN + "- Younger (18-30): Better reflexes, less experience")
    print(Fore.GREEN + "- Middle-aged (31-45): Balanced abilities, established contacts")
    print(Fore.GREEN + "- Older (46-60): Slower reflexes, unparalleled experience and reputation")
    
    while True:
        age_input = input(Fore.YELLOW + "\nYour age (18-60): ")
        if is_valid_int(age_input):
            age = int(age_input)
            if 18 <= age <= 60:
                if 18 <= age <= 30:
                    age_category = "young"
                    print(Fore.CYAN + "You move with the confidence of youth. Speed bonus applied.")
                elif 31 <= age <= 45:
                    age_category = "seasoned"
                    print(Fore.CYAN + "Your balanced experience serves you well. No penalties or bonuses.")
                else:
                    age_category = "veteran"
                    print(Fore.CYAN + "Your reputation precedes you. Respect bonus applied.")
                break
            print(Fore.RED + "Invalid age. Please enter an age between 18 and 60.")
        else:
            print(Fore.RED + "Invalid input. Please enter a number.")

    while True:
        sex_input = input(Fore.YELLOW + "\nBiological sex (Male/Female): ").strip().capitalize()
        if sex_input in ["Male", "Female"]:
            sex = sex_input
            break
        print(Fore.RED + "Invalid input. Please enter 'Male' or 'Female'.")

    # Create character with the bonus trait from earlier choice
    game_state.set_player_character(
        player_name,
        age,
        sex,
        chosen_background.name,
        chosen_background.credits,
        chosen_background.debt,
    )
    
    # Add bonus trait based on who they approached
    print(Fore.CYAN + f"\nYour interaction with {contact_name} has granted you a {bonus_trait} specialization.")

    # Enhanced ship selection with more details and customization
    print(Fore.YELLOW + f"\n{contact_name} leads you to the docking bay. 'Now for your chariot of fire...'")
    
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
        },
    }

    print(Fore.YELLOW + "\n--- AVAILABLE VESSELS ---")
    for idx, choice in enumerate(ship_choices.keys(), 1):
        ship_data = ship_choices[choice]
        print(Fore.GREEN + f"\n{idx}. {choice}")
        print(f"   {ship_data['description']}")
        print(f"   Speed: {ship_data['speed']}, Fuel Capacity: {ship_data['max_fuel']}")
        print(f"   Cargo Space: {ship_data['cargo_capacity']}, Mining Rate: {ship_data['mining_speed']}")
        print(f"   Market Value: {ship_data['value']} credits")
        print(f"   Sensor Range: {ship_data['sensor_range']} AU")
    
    while True:
        try:
            ship_choice = int(input(Fore.YELLOW + "\nSelect your vessel (1-3): "))
            if 1 <= ship_choice <= len(ship_choices):
                chosen_ship = list(ship_choices.keys())[ship_choice - 1]
                break
            else:
                print(Fore.RED + f"Invalid choice. Please choose between 1 and {len(ship_choices)}.")
        except ValueError:
            print(Fore.RED + f"Invalid input. Please enter a number between 1 and {len(ship_choices)}.")

    # Ship naming with personality
    print(Fore.YELLOW + "\nThe registration officer yawns. 'Name for this... vehicle?'")
    print(Fore.CYAN + f"{contact_name} smirks. 'Make it memorable.'")
    
    while True:
        ship_name = input(Fore.YELLOW + "Baptize your ship: ")
        if ship_name and len(ship_name) <= 30:
            break
        print(Fore.RED + "Invalid ship name. Please enter a name with 1-30 characters.")
    
    # Optional ship customization
    print(Fore.YELLOW + f"\nThe {ship_name} awaits. Any last-minute modifications?")
    print(Fore.GREEN + "1. Enhanced sensors (+5000 credits debt)")
    print(Fore.GREEN + "2. Hidden cargo compartments (+3000 credits debt)")
    print(Fore.GREEN + "3. Reinforced hull plating (+4000 credits debt)")
    print(Fore.GREEN + "4. No modifications")
    
    mod_choice = 0
    while mod_choice not in [1, 2, 3, 4]:
        try:
            mod_choice = int(input(Fore.YELLOW + "Your choice (1-4): "))
            if mod_choice not in [1, 2, 3, 4]:
                print(Fore.RED + "Please enter a number between 1 and 4.")
        except ValueError:
            print(Fore.RED + "Invalid input. Enter a number.")
    
    ship_data = ship_choices[chosen_ship].copy()
    ship_data["name"] = ship_name
    
    if mod_choice == 1:
        print(Fore.CYAN + "Sensors upgraded. You'll detect minerals and threats from further away.")
        ship_data["sensor_range"] = 0.25 + 0.25  # Add 0.25 to the default sensor range
        game_state.get_player_character().debt += 5000
    elif mod_choice == 2:
        print(Fore.CYAN + "Hidden compartments installed. Extra 20 units of 'unofficial' cargo space.")
        ship_data["cargo_capacity"] = 20.0 + float(str(ship_data["cargo_capacity"]))
        game_state.get_player_character().debt += 3000
    elif mod_choice == 3:
        print(Fore.CYAN + "Hull reinforced. Your ship can take more damage before critical failure.")
        game_state.get_player_character().debt += 4000
    else:
        print(Fore.CYAN + "No modifications. Keeping it stock... and cheap.")

    # Create the ship
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

    print(Fore.CYAN + f"\nThe {ship_name}'s engines roar to life, vibrating through the docking bay.")
    print(f"{contact_name} slaps the hull. 'She's ugly, but she'll fly. For now.'")
    sleep(1)

    # Interactive tutorial mission
    print(Fore.YELLOW + "\n--- YOUR FIRST MISSION ---")
    print(Fore.CYAN + f"{contact_name} uploads coordinates to your nav computer.")
    print(f"'Simple job to start. Transport this package to Outpost 7.'")
    print("'Don't open it. Don't scan it. Don't lose it. Questions?'")
    
    questions = [
        "1. 'What's in the package?'",
        "2. 'How much does it pay?'", 
        "3. 'Any dangers I should know about?'",
        "4. 'No questions. Let's do this.'"
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
        print(Fore.CYAN + f"\n{contact_name} narrows their eyes. 'Medical supplies. Nothing more you need to know.'")
        print("The lie is obvious, but you know better than to press the issue.")
    elif q_choice == 2:
        print(Fore.CYAN + f"\n{contact_name} laughs. '5000 credits and you keep breathing. Fair?'")
        print("The deal isn't negotiable, but at least you know what's coming.")
    elif q_choice == 3:
        print(Fore.CYAN + f"\n{contact_name} considers you. 'Smart question. Watch for patrols near the Kestrel Nebula.'")
        print("'And don't trust any distress signals. That's all you get.'")
    else:
        print(Fore.CYAN + f"\n{contact_name} grins. 'I like your style. No questions, no problems.'")
    
    # Final send-off with game mechanic tips integrated into dialogue
    tutorial_text = [
        f"\n{contact_name} hands you a datapad with critical information:",
        f"'You're {game_state.get_player_character().debt} credits in debt. Every chip matters.'",
        "'Check your status anytime with 'status' or 'st' command.'",
        "'Fuel is life. Empty tank? You're space debris.'",
        "'Mine asteroids for ore. Sell high, buy low. Basic economics.'",
        "'Upgrade your ship when you can afford it. You'll need every advantage.'",
        "'Pirates and patrols are equally dangerous, just for different reasons.'",
        f"'Complete this job, and I might have more work for a {age_category} {chosen_background.name} like you.'",
        "'Now get moving. The void waits for no one.'"
    ]

    for line in tutorial_text:
        sleep(1)
        print(Fore.CYAN + line)
        
    print(Fore.YELLOW + "\nYour journey begins. The stars await, {}.".format(player_name))
    print("Type 'help' for available commands.")


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
