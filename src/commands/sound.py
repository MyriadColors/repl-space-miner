from src.commands.base import register_command


def toggle_sound_command(game_state):
    game_state.sound_enabled = not game_state.sound_enabled
    status = "enabled" if game_state.sound_enabled else "disabled"
    game_state.ui.info_message(f"Sound {status}.")


register_command(
    ["toggle_sound", "ts"],
    toggle_sound_command,
    [],
)
