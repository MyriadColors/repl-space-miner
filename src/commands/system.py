import os
from typing import Optional
from colorama import Fore, Style
from src.classes.game import Game
from src.helpers import format_seconds
from .registry import Argument, command_registry
from .base import register_command


def display_status(game_state: Game) -> None:
    """Display current ship and game status."""
    player_ship = game_state.get_player_ship()
    if player_ship is None:
        game_state.ui.error_message("Error: Player ship not found.")
        return

    status_lines = player_ship.status_to_string()

    game_state.ui.info_message("Ship Status:")
    for line in status_lines:
        game_state.ui.info_message(line)

    if game_state.player_character:
        # Check for debt interest first
        interest_result = game_state.player_character.calculate_debt_interest(
            game_state.global_time
        )
        if interest_result:
            interest_amount, new_debt = interest_result
            game_state.ui.warn_message(
                f"DEBT ALERT: {interest_amount:.2f} credits of interest has been applied to your debt!"
            )

        # Display financial status with emphasis on debt
        game_state.ui.info_message(f"\nFinancial Status:")
        game_state.ui.info_message(
            f"Credits: {game_state.player_character.credits:.2f}"
        )

        # Highlight debt with color based on amount
        debt = game_state.player_character.debt
        if debt > 10000:
            # Red for high debt
            game_state.ui.error_message(f"DEBT: {debt:.2f} credits")
            game_state.ui.warn_message(
                f"Warning: High debt levels! Banks may send debt collectors."
            )
        elif debt > 5000:
            # Yellow for medium debt
            game_state.ui.warn_message(f"DEBT: {debt:.2f} credits")
        else:
            # Normal for low debt
            game_state.ui.info_message(f"Debt: {debt:.2f} credits")

        if game_state.player_character.debt_interest_mod > 1.0:
            game_state.ui.warn_message(
                f"Your 'Indebted' trait increases interest by {(game_state.player_character.debt_interest_mod - 1.0) * 100:.0f}%"
            )

        # Show weekly interest rate
        weekly_rate = 0.05 * game_state.player_character.debt_interest_mod
        game_state.ui.info_message(f"Weekly Interest Rate: {weekly_rate:.1%}")
        next_interest = game_state.player_character.last_interest_time + 168
        time_to_next = next_interest - game_state.global_time
        game_state.ui.info_message(f"Next interest in: {format_seconds(time_to_next)}")

    game_state.ui.info_message(f"\nGame Time: {format_seconds(game_state.global_time)}")


def display_time_and_status(game_state: Game) -> None:
    """Display current time and status."""
    game_state.ui.info_message(
        f"Current game time: {format_seconds(game_state.global_time)}"
    )
    display_status(game_state)


def command_exit(game_state: Game) -> bool:
    """
    Handle game exit command.
    
    Returns:
        bool: True if exit confirmed, False otherwise
    """
    confirm = input("Are you sure you want to exit? (y/n): ")
    if confirm.lower() in ["y", "yes"]:
        game_state.ui.info_message("Thanks for playing!")
        return True
    else:
        game_state.ui.info_message("Exit canceled.")
        return False


def clear(game_state: Game) -> None:
    """Clear the screen."""
    os.system("cls" if os.name == "nt" else "clear")


def debug_mode_command(game_state: Game) -> None:
    """Toggle debug mode."""
    game_state.debug_flag = not game_state.debug_flag
    status = "enabled" if game_state.debug_flag else "disabled"
    game_state.ui.info_message(f"Debug mode {status}")


def save_game_command(
    game_state: Game, filename: str = "", human_readable: Optional[bool] = None
) -> None:
    """
    Save the current game state.

    Args:
        game_state: The current game state
        filename: Optional file name for the save
        human_readable: If True, save in human-readable format; if None, user will be prompted
    """
    if not filename:
        filename = input("Enter save filename (leave empty for auto-generated name): ")

    try:
        # Handle None case by using a default value (False) or prompting user
        if human_readable is None:
            prompt = input("Save in human-readable format? (y/n): ")
            human_readable = prompt.lower() == "y"

        game_state.save_game(filename, human_readable)
    except Exception as e:
        game_state.ui.error_message(f"Failed to save game: {str(e)}")


def load_game_command(game_state: Game, filename: str = "") -> None:
    """Load a saved game state."""
    try:
        # Call Game.load_game directly - it has the necessary UI to show file list
        loaded_game = Game.load_game(game_state.ui, filename)
        if loaded_game:
            # Replace current game state with loaded game
            game_state.__dict__.update(loaded_game.__dict__)
            game_state.ui.success_message("Game loaded successfully!")
        else:
            game_state.ui.error_message("Failed to load game.")
    except Exception as e:
        game_state.ui.error_message(f"Failed to load game: {str(e)}")


def display_help(game_state: Game, command_name: str = "") -> None:
    """Display help information for commands."""

    def write_command(
        command: str,
        description: str,
        allowed: bool = True,
        context_required: Optional[str] = None,
    ) -> None:
        # Color coding based on availability:
        # Green: Available in current context
        # Yellow: Available but in a different context
        # Red: Not available at all

        player_ship = game_state.get_player_ship()
        is_docked = player_ship.is_docked if player_ship else False
        is_in_field, _ = (
            player_ship.check_field_presence(game_state)
            if player_ship
            else (False, None)
        )

        # Determine if command is available in current context
        context_matches = True
        if context_required == "docked" and not is_docked:
            context_matches = False
        elif context_required == "field" and not is_in_field:
            context_matches = False
        elif context_required == "undocked" and is_docked:
            context_matches = False

        # Apply appropriate color based on availability
        if not allowed:
            color = Fore.RED  # Not available
        elif context_matches:
            color = Fore.GREEN  # Available in current context
        else:
            color = Fore.YELLOW  # Available but requires different context

        # Format the message
        if not allowed:
            status = "(Not available)"
        elif not context_matches:
            status = f"(Requires {context_required})" if context_required else ""
        else:
            status = ""

        game_state.ui.info_message(
            f"{color}{command}{Style.RESET_ALL}: {description} {color}{status}{Style.RESET_ALL}"
        )

    if command_name:
        # Display help for specific command
        command = command_registry.get_command(command_name)
        if command:
            game_state.ui.info_message(f"\nHelp for command: {command_name}")
            game_state.ui.info_message(
                f"Description: {command.function.__doc__ or 'No description available'}"
            )
            if command.arguments:
                game_state.ui.info_message("\nArguments:")
                for arg in command.arguments:
                    optional = "(optional)" if arg.is_optional else "(required)"
                    game_state.ui.info_message(
                        f"  {arg.name} ({arg.type.__name__}) {optional}"                    )
            return
        else:
            game_state.ui.error_message(f"Unknown command: {command_name}")
            return
            
    # Display general help
    game_state.ui.info_message("\nAVAILABLE COMMANDS:")
    game_state.ui.info_message("==================")

    # Show the player's current context
    player_ship = game_state.get_player_ship()
    if player_ship:
        is_docked = player_ship.is_docked
        is_in_field, _ = player_ship.check_field_presence(game_state)

        context_message = "Current context: "
        if is_docked:
            context_message += f"{Fore.GREEN}DOCKED AT STATION{Style.RESET_ALL}"
        elif is_in_field:
            context_message += f"{Fore.GREEN}IN ASTEROID FIELD{Style.RESET_ALL}"
        else:
            context_message += f"{Fore.GREEN}IN SPACE{Style.RESET_ALL}"

        game_state.ui.info_message(context_message)
        game_state.ui.info_message(
            "Commands are color-coded based on availability in your current context:"
        )
        game_state.ui.info_message(
            f"  {Fore.GREEN}Green{Style.RESET_ALL}: Available now"
        )
        game_state.ui.info_message(
            f"  {Fore.YELLOW}Yellow{Style.RESET_ALL}: Requires different context"
        )
        game_state.ui.info_message("")

        # NAVIGATION CATEGORY
        game_state.ui.info_message(f"{Fore.CYAN}=== NAVIGATION ==={Style.RESET_ALL}")
        write_command(
            "travel/t <x> <y>", "Travel to specific coordinates", True, "undocked"
        )
        write_command(
            "closest/c <field|station>",
            "Travel to closest field or station",
            True,
            "undocked",
        )
        write_command(
            "direct/d <x> <y>", "Direct travel to coordinates", True, "undocked"
        )        
        write_command("dock/do", "Dock with nearby station", True, "undocked")
        write_command("undock/ud", "Undock from current station", True, "docked")
        game_state.ui.info_message("")        # FTL TRAVEL CATEGORY
        game_state.ui.info_message(f"{Fore.CYAN}=== FTL TRAVEL ==={Style.RESET_ALL}")
        write_command("listsystems/lsys", "List all available solar systems", True)
        write_command(
            "ftl/ftl_jump <destination>",
            "Jump to a solar system by name or index",
            True,
            "undocked",
        )
        game_state.ui.info_message("")        # MINING CATEGORY
        game_state.ui.info_message(
            f"{Fore.CYAN}=== MINING & SCANNING ==={Style.RESET_ALL}"
        )
        write_command(
            "mine/m <time> [until_full] [ore]",
            "Mine asteroids for specified time",
            True,
            "field",
        )
        write_command("scan/sc", "Scan for objects in the system", True)
        write_command("scan_asteroids/scna", "Scan current asteroid field for ores", True, "field")
        game_state.ui.info_message("")

        # CARGO & RESOURCES CATEGORY
        game_state.ui.info_message(
            f"{Fore.CYAN}=== CARGO & RESOURCES ==={Style.RESET_ALL}"
        )
        write_command("cargo/inv/inventory", "Display ship cargo and inventory", True)
        write_command("refine [amount]", "Refine ore to higher purity", True, "docked")
        write_command(
            "purify [amount]", "Convert ore to minerals", True, "docked"
        )
        game_state.ui.info_message("")

        # TRADING CATEGORY
        game_state.ui.info_message(
            f"{Fore.CYAN}=== TRADING & COMMERCE ==={Style.RESET_ALL}"
        )
        write_command("buy/b <item> <amount>", "Buy items from station", True, "docked")
        write_command("sell/s", "Sell items to station", True, "docked")
        write_command(
            "upgrade/up [id]", "View or purchase ship upgrades", True, "docked"
        )
        game_state.ui.info_message("")

        # RESOURCES MANAGEMENT CATEGORY
        game_state.ui.info_message(
            f"{Fore.CYAN}=== SHIP RESOURCES ==={Style.RESET_ALL}"
        )
        write_command(
            "refuel <amount>", "Refuel your ship with standard fuel", True, "docked"
        )
        write_command(
            "refuel_antimatter/refa <amount>", "Refuel with antimatter", True, "docked"
        )
        write_command(
            "repair_containment/repc", "Repair antimatter containment", True, "docked"
        )
        write_command(
            "eject_antimatter/eject", "Emergency ejection of antimatter", True
        )
        game_state.ui.info_message("")

        # BANKING & FINANCE
        game_state.ui.info_message(
            f"{Fore.CYAN}=== BANKING & FINANCE ==={Style.RESET_ALL}"
        )
        write_command(
            "bank/banking",
            "Access banking services for loans, deposits and repaying debt",
            True,
            "docked",
        )
        game_state.ui.info_message("")

        # CHARACTER PROGRESSION
        game_state.ui.info_message(
            f"{Fore.CYAN}=== CHARACTER PROGRESSION ==={Style.RESET_ALL}"
        )
        write_command("character/char/c", "Display character sheet", True)
        write_command("skills/skill/sk [name]", "View or upgrade skills", True)
        game_state.ui.info_message("")

        # SYSTEM & UI COMMANDS
        game_state.ui.info_message(f"{Fore.CYAN}=== SYSTEM & UI ==={Style.RESET_ALL}")
        write_command("status", "Display ship and game status", True)
        write_command("time", "Display current game time", True)
        write_command("clear", "Clear the screen", True)
        write_command("save [filename]", "Save current game state", True)
        write_command("load [filename]", "Load saved game state", True)
        write_command("exit", "Exit the game", True)
        write_command("help [command]", "Display help information", True)
        game_state.ui.info_message("")

        # CUSTOMIZATION
        game_state.ui.info_message(f"{Fore.CYAN}=== CUSTOMIZATION ==={Style.RESET_ALL}")
        write_command("color <text|background> <color>", "Change terminal colors", True)
        write_command("reset", "Reset terminal colors to defaults", True)
        write_command("sound", "Toggle game sound effects", True)
        game_state.ui.info_message("")

        # DEBUG COMMANDS
        game_state.ui.info_message(f"{Fore.CYAN}=== DEBUG ==={Style.RESET_ALL}")
        write_command("debug", "Toggle debug mode", True)

        # Footer with tip
        game_state.ui.info_message(
            "\nTip: Use 'help <command>' for detailed information about a specific command."
        )


# Register system commands
register_command(
    ["status", "st"],
    display_status,
    [],
)

register_command(
    ["time", "t"],
    display_time_and_status,
    [],
)

register_command(
    ["exit", "quit", "q"],
    command_exit,
    [],
)

register_command(
    ["clear", "cls"],
    clear,
    [],
)

register_command(
    ["debug"],
    debug_mode_command,
    [],
)

register_command(
    ["save"],
    save_game_command,
    [Argument("filename", str, True)],
)

register_command(
    ["load"],
    load_game_command,
    [Argument("filename", str, True)],
)

register_command(
    ["help", "h", "?"],
    display_help,
    [Argument("command_name", str, True)],
)
