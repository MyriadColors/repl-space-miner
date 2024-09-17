from src.classes.game import Character, Game
from src.classes.ship import Ship
from src.command_handlers import refuel_command, scan_field_command, sell_command, travel_command, scan_command, display_help, command_dock, \
    command_undock, display_time_and_status, mine_command, buy_command, add_creds_debug_command, \
    command_exit, command_color, command_reset, clear, add_ore_debug_command, direct_travel_command, debug_mode_command, \
    toggle_sound_command, init_music, create_character, create_ship
from src.pygameterm import color_data
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
        ["color", "co"],
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
        argument_list=[
            Argument(
                name="command_name",
                type=str,
                is_optional=True
            )
        ]
    )

    terminal.register_command(
        ['direct_travel', 'dtr'],
        direct_travel_command,
        argument_list=[
            Argument(
                name="destination_x",
                type=float,
                is_optional=False
            ),
            Argument(
                name="destination_y",
                type=float,
                is_optional=False
            )
        ]
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
        argument_list=[
            Argument(
                name="selection_flag",
                type=str,
                is_optional=True
            )
        ]
    )

    terminal.register_command(
        ["mine", "mi"],
        mine_command,
        argument_list=[
            Argument(
                name="time", # Time to mine
                type=int,
                is_optional=True
            ),

            Argument(
                name="uf", # Mine until full
                type=str,
                is_optional=True
            ),
            Argument(
                name="ores", # Ores to mine
                type=str,
                is_optional=True
            )
        ]
    )
    
    # COmmand to scan the asteroid field,r eturning the ores available
    terminal.register_command(
        ["scan_field", "scf"],
        scan_field_command,
    )
    
    terminal.register_command(
        ['clear', 'cl'],
        clear
    )

    terminal.register_command(
        ['debug', 'dm'],
        debug_mode_command
    )

    terminal.register_command(
        ['add_ore', 'ao'],
        add_ore_debug_command,
        argument_list=[
            Argument(
                name="amount",
                type=int,
                is_optional=False
            ),
            Argument(
                name="ore_name",
                type=str,
                is_optional=False
            )
        ],
    )
    
    terminal.register_command(
    ["add_creds", "ac"],
    add_creds_debug_command,
    argument_list=[
        Argument(
            name="amount",
            type=int,
            is_optional=False
            )
        ]
    )

    terminal.register_command(
        ["toggle_sound", "ts"],
        toggle_sound_command,
    )

def IntroScreen(terminal: PygameTerminal):
    terminal.write("Welcome to the Space Trader CLI game!")
    terminal.write("This is the placeholder intro screen.")
    terminal.write("In the future there will be background story and lore here.")
    
    game: Game = terminal.app_state
    
    if not game.skipc:
        terminal.write("Now the character and ship customization will begin.")
        create_character(terminal)
        create_ship(terminal)
    else:
        terminal.write("Skipping character and ship customization.")
        game.player_character = Character(name="Player", age=25, sex="male", background="Belter")
        game.player_ship = Ship(game.rnd_station.position, 0.0001, 100, 0.05, 100,
                                    100, 0.01, "Player's Ship")

def start_repl(args_input):
    game = Game(
        debug_flag=True if args_input.debug else False,
        mute_flag=True if args_input.mute else False,
        skip_customization=True if args_input.skipc else False
    )

    terminal = PygameTerminal(
        game,
        1400,
        950,
        18,
        "Welcome to the Space Trader CLI game!",
        default_bg_color=color_data.color["gray64"],
        default_fg_color=color_data.color["green144"],
    )

    init_music(terminal) if not game.mute_flag else None
    register_commands(terminal)
    IntroScreen(terminal)
    terminal.run()
