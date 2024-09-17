from src.classes.game import Character, Game
from src.classes.ship import Ship
from src.pygameterm import color_data
from src.pygameterm.terminal import PygameTerminal


def IntroEvent(terminal: PygameTerminal):
    terminal.write("You find yourself inside a small, dimly lit office, seated across from a stern-faced bank manager (press enter to continue...).")
    terminal.wait_for_input()
    terminal.write("The manager, a tall, thin man with a clipboard, regards you with a mixture of boredom and disdain.")
    terminal.wait_for_input()
    terminal.write("'It seems you have found yourself in a bit of financial trouble,' he says, his voice dripping with condescension.")
    terminal.wait_for_input()
    terminal.write("He glances down at the file in front of him, which no doubt contains the details of your registered ship and mounting debt.")
    terminal.wait_for_input()
    game: Game = terminal.app_state
    terminal.write("The bank manager taps on the tablet on his desk. 'Before we proceed, I need to update your profile in our system.'")
    terminal.wait_for_input()
    terminal.write("He looks up at you expectantly. 'Let's start with your name.'")
    name = terminal.prompt_user("Enter your character's name: ")

    terminal.write(f"'Alright {name}, and your age?'")
    age = terminal.prompt_user("Enter your character's age: ")

    terminal.write("He raises an eyebrow. 'And your biological sex?'")
    sex = terminal.prompt_multiple_choice("Select your character's sex:", ["Male", "Female"])
    sex_assigned= "male" if sex == 1 else "female"

    terminal.write("'Lastly, your background. It says here you have a significant debt with us. How did that come about?'")
    while True:
        background_number = terminal.prompt_multiple_choice("Select your character's background:", ["Belter", "Corpo", "Agent", "Jovian"])
        if background_number == 1:
            background = "Belter"
            terminal.write("'Ah, a Belter. Let me guess, you took out a loan for a mining operation that didn't pan out?'")
            break
        elif background_number == 2:
            background = "Corpo"
            terminal.write("'A Corpo in debt? Did a business deal go south on you?'")
            break
        elif background_number == 3:
            background = "Agent"
            terminal.write("'An Agent with a debt? I suppose even the law has its vices.'")
            break
        elif background_number == 4:
            background = "Jovian"
            terminal.write("'A Jovian! I'm surprised to see one of your kind out here, let alone in debt.'")
        else:
            terminal.write("Invalid input. Please enter a number corresponding to the options.")
            continue

    game.player_character = Character(name=name, age=age, sex=sex_assigned, background=background)
    terminal.wait_for_input()
    terminal.write(f"The manager nods, inputting the information into his tablet. 'Well, {game.player_character.name}, a debt is a debt. Let's discuss your options.'", fg_color=color_data.get_color("blue"))
    terminal.wait_for_input()
    terminal.write("He sets the tablet aside and leans forward, his elbows on the desk. 'Now, about that debt...'")


    if game.player_character.sex == "male":
        terminal.write(f"Mr. {game.player_character.name}, it seems you have accrued a significant debt to the Terminus Bank of Jove.")
    else:
        terminal.write(f"Ms. {game.player_character.name}, it seems you have accrued a significant debt to the Terminus Bank of Jove.")

    if game.player_character.background == "Belter":
        terminal.write("'I see here you took out a loan for a mining operation that didn't quite work out. Tough break, but the debt remains.'")
        terminal.write("He looks at you with a mix of pity and disdain. 'I don't envy your position, Belter. But a contract is a contract.'")
        terminal.write("'Now, let's get down to the matter at hand. Your debt is 50,000 credits.'")
        terminal.write("'Every day that you don't pay back the debt, a compound interest of 2.5% is added to the debt.'")
        terminal.write("'After 6 months, we will send our repossession team to collect whatever items you own. If that isn't enough...'")
        terminal.write("He shakes his head again in mock pity. 'Well, let's just say a long sentence of hard labor awaits you.'")
        terminal.write("He hands you the papers to sign, and you can see the numbers on the paper are indeed 50,000 credits, just as he said.")
        terminal.write("With a heavy heart, you sign the papers, unsure of how you'll manage to pay back such a staggering sum.")
        terminal.write("Feeling desperate and overwhelmed, you leave the bank and head to the nearest bar, hoping to drown your sorrows.")
        terminal.write("As you enter the dimly lit establishment, you make your way to a table in the corner and order a stiff drink.")
        terminal.write("You sit there, nursing your drink and contemplating your bleak future, when a voice interrupts your thoughts.")
        terminal.write("'You look like you could use a friend,' a woman says as she slides into the seat across from you.")
        terminal.write("You look up to see a fellow Belter, a woman in her late 30s with a kind smile. 'Name's Jane,' she says, extending her hand.")
        terminal.write("Jane listens intently as you share your story, nodding in understanding. 'I've been in a similar spot myself,' she confides.")
        terminal.write("'It's a tough life out here for us Belters, but we're survivors. We look out for each other.'")
        terminal.write("You find yourself opening up to Jane, sharing details about your past and the hardships you've faced.")
        terminal.write("Jane leans back in her seat. 'You know, I might be able to help you out. I have an old ship I'm not using anymore.'")
        terminal.write("You look at her, surprised. 'But I'm penniless. How would I afford the fuel, the repairs?'")
        terminal.write("Jane waves off your concerns. 'We'll figure that out. The important thing is getting you back on your feet.'")
        terminal.write("She stands up, motioning for you to follow. 'Come on, let me show you the ship. It's not much, but it's a start.'")
        terminal.write("Jane leads you to a small, battered vessel in the hangar. 'Here she is. She's yours now, if you want her.'")
        ship_name = terminal.prompt_user("Enter a name for your ship: ")
        game.player_ship = Ship(game.rnd_station.position, 0.0001, 100, 0.05, 100, 100, 0.01, ship_name)
        terminal.write(f"You christen your ship '{ship_name}' and turn to Jane, gratitude welling up inside you.")
        terminal.write("'I don't know how to thank you,' you start, but she cuts you off with a smile.")
        terminal.write("'Just promise me you'll pay it forward someday. Help out another Belter in need.'")
        terminal.write("With a newfound sense of hope, you prepare to embark on your journey, determined to make the most of this second chance.")

    elif game.player_character.background == "Corpo":
        terminal.write("'Says here a business deal went sour on you. Invested in the wrong venture, eh? It happens to the best of us.'")
        terminal.write("The manager shrugs. 'But a debt is a debt, even for a Corpo. Your company won't be happy if this isn't settled.'")
        terminal.write("'Now, let's get down to the matter at hand. Your debt is 100,000 credits.'")
        terminal.write("'Every day that you don't pay back the debt, a compound interest of 2.5% is added.'")
        terminal.write("'After 3 months, we will inform your company and they will likely terminate your employment.'")
        terminal.write("He slides the papers across the desk. 'I'm sure you understand the gravity of the situation.'")
        terminal.write("You grit your teeth as you sign, knowing your career is on the line if you can't repay this quickly.")
        terminal.write("Leaving the bank, you head straight to the spaceport, your mind racing as you try to devise a plan.")
        terminal.write("As you're checking the ship listings, a man in a crisp suit approaches you, a friendly smile on his face.")
        terminal.write("'Vance,' he introduces himself, extending a hand. 'I couldn't help but notice you seem a bit troubled.'")
        terminal.write("You hesitate for a moment before shaking his hand, wondering what this stranger could possibly want.")
        terminal.write("'I specialize in helping Corpos like yourself,' Vance explains. 'I have a knack for finding solutions to tricky problems.'")
        terminal.write("He gestures for you to walk with him. 'I happened to overhear about your situation with the bank. I might be able to help.'")
        terminal.write("Vance leads you to a sleek, state-of-the-art ship. 'The Nighthawk. Fast, discreet, perfect for high-value cargo runs.'")
        terminal.write("'I can lease her to you,' he offers. 'With the right contracts, you could pay off that debt in no time. What do you say?'")
        ship_name = terminal.prompt_user("Enter a name for your ship: ")
        game.player_ship = Ship(game.rnd_station.position, 0.0001, 100, 0.05, 100, 100, 0.01, ship_name)
        terminal.write(f"You christen the ship '{ship_name}'. With Vance's contacts and this impressive vessel, you might just salvage your career.")
        terminal.write("'I'll send you the details of some lucrative contracts,' Vance says as you prepare to board your new ship.")
        terminal.write("'Just remember, in this business, discretion is key. I'm counting on you to handle these deals with the utmost professionalism.'")
        terminal.write("You nod, understanding the implications. With the Nighthawk under your command, you're ready to navigate the shadowy world of corporate espionage and high-stakes deals.")
        terminal.write("As you settle into the pilot's seat, you can't help but feel a mix of excitement and trepidation. The future is uncertain, but one thing is clear: failure is not an option.")

    elif game.player_character.background == "Agent":
        terminal.write("The manager eyes you cautiously. 'An Agent, huh? I don't want any trouble with the law.'")
        terminal.write("You assure him that you're here on personal business. Your work as an interstellar agent can be dangerous, and it's best to keep a low profile.")
        terminal.write("'Fair enough,' he says. 'Your debt is 75,000 credits. Hazard pay advance for a mission, it seems.'")
        terminal.write("'Daily interest is 2.5%. After 4 months, we'll have to inform your agency. I'm sure you know what that means for your career.'")
        terminal.write("You sign the papers, mind already racing with ways to come up with the credits.")
        terminal.write("At the spaceport bar, you nurse a drink, considering your limited options.")
        terminal.write("A woman slides into the booth across from you. 'You've got that look,' she says. 'The look of an Agent in trouble.'")
        terminal.write("She introduces herself as Zara, a fellow Agent. 'Word gets around,' she says with a wry smile.")
        terminal.write("'I might have a solution for you,' Zara says, leaning in conspiratorially. 'There's a ship. The Phantom. Off the books, but perfect for our line of work.'")
        terminal.write("She slides a data chip across the table. 'Take the ship. Do some side jobs. The agency doesn't need to know. You'll have that debt cleared in no time.'")
        ship_name = terminal.prompt_user("Enter a name for your ship: ")
        game.player_ship = Ship(game.rnd_station.position, 0.0001, 100, 0.05, 100, 100, 0.01, ship_name)
        terminal.write(f"The newly christened '{ship_name}' awaits you in the hangar, your key to resolving this debt without the agency knowing.")
        terminal.write("Zara walks with you to the hangar. 'I've loaded some potential contracts onto that chip. High-paying, but discreet.'")
        terminal.write("She places a hand on your shoulder. 'Be careful out there. Some of these jobs, they're not exactly legal. But they'll get you out of this mess.'")
        terminal.write("You nod, understanding the risks. In your line of work, sometimes you have to operate in the shadows.")
        terminal.write("As you board your new ship, you feel a mix of relief and apprehension. You're grateful for Zara's help, but you know you're heading into dangerous territory.")
        terminal.write("But you're an Agent. Danger is part of the job. With the Phantom at your command, you're ready to face whatever challenges come your way.")

    elif game.player_character.background == "Jovian":
        terminal.write("'A Jovian!' the manager exclaims. 'We don't see many of your kind out here.'")
        terminal.write("You shrug. Life on Jupiter is comfortable, but you've always longed for adventure beyond your home planet.")
        terminal.write("'Well, seems like you got more adventure than you bargained for,' he says, looking at your file.")
        terminal.write("'Gambling debts. 80,000 credits. 2.5% daily interest. After 5 months, we'll have to inform your family back on Jupiter.'")
        terminal.write("You wince at the thought. Disappointing your family would be worse than the debt itself.")
        terminal.write("The manager almost looks sympathetic. 'I know it's a lot. But you Jovians have resources. You'll figure something out.'")
        terminal.write("At the spaceport, you're deep in thought when a cheerful voice interrupts your brooding.")
        terminal.write("'Why the long face, my Jovian friend?' a jovial man asks. 'Lyle's the name. I know that look. You need a ship.'")
        terminal.write("Lyle throws an arm around your shoulders, guiding you to a hangar. 'The Odyssey. A fine ship. She'll take you places.'")
        terminal.write("He grins. 'You take this ship, you can see the galaxy. Find some opportunities. And maybe solve that little debt problem while you're at it.'")
        ship_name = terminal.prompt_user("Enter a name for your ship: ")
        game.player_ship = Ship(game.rnd_station.position, 0.0001, 100, 0.05, 100, 100, 0.01, ship_name)
        terminal.write(f"You board the '{ship_name}', ready to embark on an odyssey of your own, to explore the stars and escape this debt.")
        terminal.write("Lyle hands you a data pad. 'I've taken the liberty of loading some potential jobs for you. Should help you get on your feet.'")
        terminal.write("You raise an eyebrow as you scroll through the listings. Some of these 'jobs' seem a bit unorthodox for a Jovian.")
        terminal.write("Lyle chuckles at your expression. 'Hey, sometimes you gotta get your hands dirty to clean up a mess, you know what I mean?'")
        terminal.write("You nod slowly, realizing that your sheltered life on Jupiter hasn't quite prepared you for the realities of the wider galaxy.")
        terminal.write("But you're determined to adapt. With the Odyssey as your vessel, you're ready to leave your comfort zone far behind.")
        terminal.write("As you settle into the captain's chair, you feel a thrill of exhilaration. The unknown stretches out before you, full of danger and possibility.")
        terminal.write("You may be a Jovian out of your element, but you're ready to face whatever challenges the cosmos has in store.")

    terminal.write("With your ship ready and your character created, you are now ready to start your journey.")