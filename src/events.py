from src.classes.game import Character, Game
from src.classes.ship import Ship
from src.pygameterm.terminal import PygameTerminal


def intro_event(terminal: PygameTerminal):
    game: Game = terminal.app_state

    terminal.writeLn(
        "You find yourself inside a small, dimly lit office, seated across from a stern-faced bank manager (press enter to continue...)."
    )
    terminal.writeLn(
        "The manager, a tall, thin man with a clipboard, regards you with a mixture of boredom and disdain."
    )
    terminal.writeLn(
        "'It seems you have found yourself in a bit of financial trouble,' he says, his voice dripping with condescension."
    )
    terminal.writeLn(
        "He glances down at the file in front of him, which no doubt contains the details of your registered ship and mounting debt."
    )
    terminal.writeLn(
        "The bank manager taps on the tablet on his desk. 'Before we proceed, I need to update your profile in our system.'"
    )
    terminal.writeLn("He looks up at you expectantly. 'Let's start with your name.'")
    char_name = terminal.prompt_user("Enter your character's name: ")

    terminal.writeLn(f"'Alright {char_name}, and your age?'")
    char_age = int(terminal.prompt_user("Enter your character's age: "))

    terminal.writeLn("He raises an eyebrow. 'And your biological sex?'")
    char_sex = terminal.prompt_multiple_choice("Select your character's sex:", ["Male", "Female"])
    char_sex_assigned = "male" if char_sex == 1 else "female"

    terminal.writeLn(
        "'Lastly, your background. It says here you have a significant debt with us. How did that come about?'"
    )
    char_background = ""
    while True:
        char_background_number = terminal.prompt_multiple_choice(
            "Select your character's background:", ["Belter", "Corpo", "Agent", "Jovian"]
        )
        if char_background_number == 1:
            char_background = "Belter"
            terminal.writeLn(
                "'Ah, a Belter. Let me guess, you took out a loan for a mining operation that didn't pan out?'"
            )
            break
        elif char_background_number == 2:
            char_background = "Corpo"
            terminal.writeLn("'A Corpo in debt? Did a business deal go south on you?'")
            break
        elif char_background_number == 3:
            char_background = "Agent"
            terminal.writeLn("'An Agent with a debt? I suppose even the law has its vices.'")
            break
        elif char_background_number == 4:
            char_background = "Jovian"
            terminal.writeLn("'A Jovian! I'm surprised to see one of your kind out here, let alone in debt.'")
        else:
            terminal.writeLn("Invalid input. Please enter a number corresponding to the options.")
            continue

    game.player_character = Character(char_name, char_age, char_sex_assigned, char_background)
    terminal.writeLn(
        f"The manager nods, inputting the information into his tablet. 'Well, {game.player_character.name}, a debt is a debt. Let's discuss your options.'"
    )
    terminal.writeLn("He sets the tablet aside and leans forward, his elbows on the desk. 'Now, about that debt...'")

    if game.player_character.sex == "male":
        terminal.writeLn(
            f"Mr. {game.player_character.name}, it seems you have accrued a significant debt to the Terminus Bank of Jove."
        )
    else:
        terminal.writeLn(
            f"Ms. {game.player_character.name}, it seems you have accrued a significant debt to the Terminus Bank of Jove."
        )

    if game.player_character.background == "Belter":
        terminal.writeLn(
            "'I see here you took out a loan for a mining operation that didn't quite work out. Tough break, but the debt remains.'"
        )
        terminal.writeLn(
            "He looks at you with a mix of pity and disdain. 'I don't envy your position, Belter. But a contract is a contract.'"
        )
        terminal.writeLn("'Now, let's get down to the matter at hand. Your debt is 50,000 credits.'")
        terminal.writeLn(
            "'Every day that you don't pay back the debt, a compound interest of 2.5% is added to the debt.'"
        )
        terminal.writeLn(
            "'After 6 months, we will send our repossession team to collect whatever items you own. If that isn't enough...'"
        )
        terminal.writeLn(
            "He shakes his head again in mock pity. 'Well, let's just say a long sentence of hard labor awaits you.'"
        )
        terminal.writeLn(
            "He hands you the papers to sign, and you can see the numbers on the paper are indeed 50,000 credits, just as he said."
        )
        terminal.writeLn(
            "With a heavy heart, you sign the papers, unsure of how you'll manage to pay back such a staggering sum."
        )
        terminal.writeLn(
            "Feeling desperate and overwhelmed, you leave the bank and head to the nearest bar, hoping to drown your sorrows."
        )
        terminal.writeLn(
            "As you enter the dimly lit establishment, you make your way to a table in the corner and order a stiff drink."
        )
        terminal.writeLn(
            "You sit there, nursing your drink and contemplating your bleak future, when a voice interrupts your thoughts."
        )
        terminal.writeLn(
            "'You look like you could use a friend,' a woman says as she slides into the seat across from you."
        )
        terminal.writeLn(
            "You look up to see a fellow Belter, a woman in her late 30s with a kind smile. 'Name's Jane,' she says, extending her hand."
        )
        terminal.writeLn(
            "Jane listens intently as you share your story, nodding in understanding. 'I've been in a similar spot myself,' she confides."
        )
        terminal.writeLn(
            "'It's a tough life out here for us Belters, but we're survivors. We look out for each other.'"
        )
        terminal.writeLn(
            "You find yourself opening up to Jane, sharing details about your past and the hardships you've faced."
        )
        terminal.writeLn(
            "Jane leans back in her seat. 'You know, I might be able to help you out. I have an old ship I'm not using anymore.'"
        )
        ship_name = terminal.prompt_user("Enter a name for the ship: ")
        game.player_ship = Ship(game.rnd_station.position, 0.0001, 100, 0.05, 100, 100, 0.01, ship_name)
        terminal.writeLn(f"You christen the ship '{ship_name}'.")
        terminal.writeLn(
            "'I'll send you the details of some lucrative contracts,' Jane says as you prepare to board your new ship."
        )
        terminal.writeLn(
            "'Just remember, in this business, discretion is key. I'm counting on you to handle these deals with the utmost professionalism.'"
        )
        terminal.writeLn(
            "You nod, understanding the implications. With the ship under your command, you're ready to navigate the shadowy world of corporate espionage and high-stakes deals."
        )
        terminal.writeLn(
            "As you settle into the pilot's seat, you can't help but feel a mix of excitement and trepidation. The future is uncertain, but one thing is clear: failure is not an option."
        )
