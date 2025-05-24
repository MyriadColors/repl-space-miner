from colorama import Fore, Back, Style
from src.commands.registry import Argument
from src.commands.base import register_command

# Supported colors for colorama
COLOR_MAP = {
    "black": Fore.BLACK,
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
    "reset": Fore.RESET,
}
BG_COLOR_MAP = {
    "black": Back.BLACK,
    "red": Back.RED,
    "green": Back.GREEN,
    "yellow": Back.YELLOW,
    "blue": Back.BLUE,
    "magenta": Back.MAGENTA,
    "cyan": Back.CYAN,
    "white": Back.WHITE,
    "reset": Back.RESET,
}

# Store current color state (could be extended to game_state if needed)
current_fg = Fore.RESET
current_bg = Back.RESET


def color_command(game_state, target: str, color_name: str):
    """Change the terminal foreground or background color."""
    global current_fg, current_bg
    if target not in ("fg", "bg"):
        game_state.ui.error_message("Target must be 'fg' or 'bg'.")
        return
    color_name = color_name.lower()
    if target == "fg":
        if color_name in COLOR_MAP:
            current_fg = COLOR_MAP[color_name]
            print(current_fg + f"Foreground color set to {color_name}.")
        else:
            game_state.ui.error_message(
                f"Unknown foreground color: {color_name}")
    elif target == "bg":
        if color_name in BG_COLOR_MAP:
            current_bg = BG_COLOR_MAP[color_name]
            print(current_bg + f"Background color set to {color_name}.")
        else:
            game_state.ui.error_message(
                f"Unknown background color: {color_name}")


def reset_command(game_state, what: str):
    """Reset terminal settings."""
    global current_fg, current_bg
    what = what.lower()
    if what in ("color", "fg", "bg", "all"):
        current_fg = Fore.RESET
        current_bg = Back.RESET
        print(Style.RESET_ALL + "Colors reset.")
    elif what == "text":
        print(Style.RESET_ALL + "Text style reset.")
    elif what == "history":
        print("History reset (not implemented).")
    else:
        game_state.ui.error_message(f"Unknown reset target: {what}")


register_command(
    ["color", "co"],
    color_command,
    [
        Argument("target", str, False, 0, None),
        Argument("color_name", str, False, 1, None),
    ],
)

register_command(
    ["reset", "rs"],
    reset_command,
    [
        Argument("what", str, False, 0, None),
    ],
)
