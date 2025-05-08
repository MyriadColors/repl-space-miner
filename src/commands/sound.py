from src.commands.base import register_command

global_sound_enabled = True


def toggle_sound_command(game_state):
    global global_sound_enabled
    global_sound_enabled = not global_sound_enabled
    status = "enabled" if global_sound_enabled else "disabled"
    game_state.ui.info_message(f"Sound {status}.")


register_command(
    ["toggle_sound", "ts"],
    toggle_sound_command,
    [],
)
