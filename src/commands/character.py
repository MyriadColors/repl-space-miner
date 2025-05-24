from src.classes.game import Game


def display_character_sheet(game_state: Game) -> None:
    """Display detailed character information."""
    character = game_state.get_player_character()
    if not character:
        game_state.ui.error_message("Error: Player character not found.")
        return

    char_info = character.to_string()

    game_state.ui.info_message("\n=== Character Sheet ===")
    for line in char_info:
        game_state.ui.info_message(line)
