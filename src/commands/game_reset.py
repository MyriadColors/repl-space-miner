"""Game reset command for restarting the game with a new or specified seed."""

import time
from typing import Optional
from src.classes.game import Game
from src.commands.registry import Argument
from src.commands.base import register_command


def game_reset_command(game_state: Game, seed: Optional[int] = None) -> None:
    """
    Reset the game with a new or specified seed.

    Args:
        game_state: Current game state
        seed: Optional seed for procedural generation. If None, uses current time.
    """
    # Use current time as seed if not provided
    if seed is None:
        seed = int(time.time())
    # Confirm with user before resetting
    confirm = input(
        f"Are you sure you want to reset the game with seed {seed}? This will delete all progress. (y/N): "
    ).lower()
    if confirm not in ["y", "yes"]:
        game_state.ui.info_message("Game reset cancelled.")
        return

    # Store current settings
    ui_instance = game_state.ui
    debug_flag = game_state.debug_flag
    mute_flag = game_state.mute_flag
    skip_customization = game_state.skipc

    # Create a new game instance with the new seed
    new_game = Game(
        debug_flag=debug_flag,
        mute_flag=mute_flag,
        skip_customization=skip_customization,
        seed=seed,
    )

    # Replace the current game state's attributes with the new ones
    game_state.__dict__.update(new_game.__dict__)

    # Restore the UI instance
    game_state.ui = ui_instance

    # Inform the user about the reset
    game_state.ui.success_message(f"Game reset successfully with seed: {seed}")
    game_state.ui.info_message(
        "You will need to recreate your character and ship.")
    game_state.ui.info_message("Use 'help' command to see available commands.")


# Register the game reset command
register_command(
    ["game_reset", "reset_game", "newgame"],
    game_reset_command,
    [Argument("seed", int, True, 0, None)],
)
