from src.classes.game import Game
from src.command_handlers import refuel_command, sell_command, travel_command, scan_command, display_help, command_dock, \
    command_undock, display_time_and_status, mine_command, buy_command, add_creds_command, \
    command_exit, command_color, command_reset
from src.pygameterm.terminal import PygameTerminal, Argument

def register_commands(terminal: PygameTerminal):
    terminal.register_command(
        ["refuel", "ref"],
        refuel_command,
        argument_list=[
            Argument(
                name="amount",
                type=float,
                is_optional=False,
                custom_validator=lambda x: isinstance(x, float) and x > 0,
            )
        ]
    )

    terminal.register_command(
        ["sell", "sl"],
        sell_command,
    )

    terminal.register_command(
        ["buy", "by"],
        buy_command,
        argument_list=[
            Argument(
                name="item_name",
                type=str,
                is_optional=False
            ),
            Argument(
                name="amount",
                type=int,
                is_optional=False,
                custom_validator=lambda x: int(x) > 0
            ),
        ]
    )

    terminal.register_command(
        ["travel", "tr"],  # Include "tr" as an abbreviation
        travel_command,
        argument_list=[
            Argument(
                name="sort_type",
                type=str,
                is_optional=False,
                custom_validator=lambda x: x in ["closest", "c"]
            ),
            Argument(
                name="object_type",
                type=str,
                is_optional=False,
                custom_validator=lambda x: x in ["field", "station", "f", "s"]
            ),
        ]
    )

    terminal.register_command(
        ["scan", "sc"],
        scan_command,
        argument_list=[
            Argument(
                name="quantity_of_objects",
                type=int,
                is_optional=False,
            ),
        ]
    )

    # command_reset
    terminal.register_command(
        ["reset", "rs"],
        command_reset,
        argument_list=[
            Argument(
                name="type_of_reset",
                type=str,
                is_optional=False
            )
        ]
    )

    terminal.register_command(
        ["quit", "exit", "q", "e"],
        command_exit
    )

    terminal.register_command(
        ["color", "crl"],
        command_color,
        argument_list=[
            Argument(
                name="color-type",
                type=str,
                is_optional=False
            ),
            Argument(
                name="color",
                type=str,
                is_optional=False
            )
        ]
    )

    terminal.register_command(
        ["help", "h"],
        display_help,
    )

    terminal.register_command(
        ["dock", "do"],
        command_dock,
    )

    terminal.register_command(
        ["undock", "ud"],
        command_undock,
    )

    terminal.register_command(
        ["status", "st"],
        display_time_and_status,
    )

    terminal.register_command(
        ["mine", "mi"],
        mine_command,
        argument_list=[
            Argument(
                name="time",
                type=int,
                is_optional=False
            )
        ]
    )

    terminal.register_command(
        ["add_creds", "ac"],
        add_creds_command,
        argument_list=[
            Argument(
                name="amount",
                type=int,
                is_optional=False
            )
        ]
    )


def start_repl():
    game: Game = Game()
    terminal = PygameTerminal(game, 1400, 1000, 28, "Welcome to the Space Trader CLI game!")
    register_commands(terminal)
    terminal.run()

