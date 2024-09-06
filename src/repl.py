from src.command_handlers import handle_refuel_command, handle_sell_command, handle_buy_command, handle_travel_command, \
    handle_mine_command, display_help, handle_scan_command, handle_docking_command, handle_undocking_command, \
    handle_add_creds_command, handle_upgrade_command
from src.classes.game import Game
from src.helpers import format_seconds, take_input

def command_interpreter(game: Game, cmd: str, args: list[str]) -> bool:
    """Interprets the command and executes it."""
    match cmd:
        case 'q' | 'quit':
            return False
        case 'refuel' | 'r':
            handle_refuel_command(game.player_ship, game, args)
            return True
        case 'sell' | 's':
            handle_sell_command(game)
            return True
        case 'buy' | 'b':
            handle_buy_command(game, args)
            return True
        case 'move' | 'travel' | 'mo' | 't':
            game.global_time = handle_travel_command(game.player_ship,
                                                     game.solar_system, args,
                                                     game.global_time)
            return True
        case 'mine' | 'mi':
            game.global_time = handle_mine_command(game.player_ship,
                                                   game.solar_system, args,
                                                   game.global_time)
            return True
        case 's' | 'scan':
            handle_scan_command(game.player_ship, game, args)
            return True
        case 'st' | 'status':
            print(game.player_ship.status_to_string())
            print(f"Credits: {game.player_credits}")
            print(f"Time: {format_seconds(game.global_time)}s")
            return True
        case 'do' | 'dock':
            handle_docking_command(game.player_ship, game)
            return True
        case 'ud' | 'undock':
            handle_undocking_command(game.player_ship)
            return True
        case 'up' | 'upgrade':
            handle_upgrade_command(game, args)
            return True
        case 'ao' | 'add_ore':
            print("Sorry, this command is broken, try again next update.")
            # handle_add_ore_command(game.player_ship, args)
            return True
        case 'ac' | 'add_creds':
            handle_add_creds_command(game, args)
            return True
        case "reset_name" | 'rn':
            new_name = take_input("Enter new name").strip()
            if len(new_name) == 0:
                print("Invalid name. Please enter a valid name.")
            game.player_ship.set_ship_name(new_name)
            return True
        case 'help':
            display_help()
            return True
        case _:
            print("Invalid command. Please enter a valid command.")
            return True

def command_parser(input_cmd: list[str]) -> (bool, str, list[str]):
    """Parses the input string into a command and a list of arguments."""
    if len(input_cmd) == 0:
        return False, "", []
    cmd = input_cmd[0]
    args = input_cmd[1:]
    return True, cmd, args

def start_repl(game):
    display_help()
    while True:

        input_cmd = take_input(">> ").strip().lower().split(" ")
        result, cmd, args = command_parser(input_cmd)

        loop_command = command_interpreter(game, cmd, args)
        if loop_command:
            continue
        else:
            break
