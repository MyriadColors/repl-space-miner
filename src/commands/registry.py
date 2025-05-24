from dataclasses import dataclass, field
from typing import Callable, Any, Optional

from src.classes.game import Game
from src.helpers import is_valid_int, is_valid_float, is_valid_bool


@dataclass
class Argument:
    name: str
    type: type
    is_optional: bool
    positional_index: int | None = None
    custom_validator: Callable[[Any], bool] | None = None


@dataclass
class Command:
    """
    Represents a command that can be executed in the game.
    """

    function: Callable
    arguments: list[Argument] = field(default_factory=list)
    number_of_arguments: int = field(init=False)
    command_name: str = ""

    def __post_init__(self):
        self.number_of_arguments = len(self.arguments)

    def get_optional_arguments(self):
        return [arg for arg in self.arguments if not arg.is_optional]

    def validate_arguments(self, args):
        required_args = [arg for arg in self.arguments if not arg.is_optional]
        if len(args) < len(required_args):
            return False, "Not enough arguments provided."
        if len(args) > len(self.arguments):
            return False, "Too many arguments provided."

        for i, (arg, value) in enumerate(zip(self.arguments, args), start=1):
            if arg.type is int:
                if not self._is_valid_int(value):
                    return False, f"Argument {i} ({arg.name}) must be an integer."
            elif arg.type is float:
                if not self._is_valid_float(value):
                    return False, f"Argument {i} ({arg.name}) must be a float."
            elif arg.type is bool:
                if not self._is_valid_bool(value):
                    return (
                        False,
                        f"Argument {i} ({arg.name}) must be a boolean value (true/false or 1/0).",
                    )
            elif arg.type is str:
                pass
            else:
                if not value:
                    return False, f"Argument {i} ({arg.name}) cannot be empty."

        return True, ""

    @staticmethod
    def _is_valid_int(value):
        return is_valid_int(value)

    @staticmethod
    def _is_valid_float(value):
        return is_valid_float(value)

    @staticmethod
    def _is_valid_bool(value):
        return is_valid_bool(value)

    def __call__(self, *args: Any, game_state: Game) -> Any:
        valid, message = self.validate_arguments(args)
        if not valid:
            raise ValueError(message)
        return self.function(*args, game_state=game_state)


@dataclass
class CommandRegistry:
    commands: dict[str, Command] = field(default_factory=dict)

    def register(self, name: str, command: Command):
        self.commands[name] = command
        command.command_name = name

    def unregister(self, command_name: str):
        self.commands.pop(command_name, None)

    def get_command(self, command_name: str) -> Optional[Command]:
        return self.commands.get(command_name)

    @staticmethod
    def execute(command: Command, *args, **kwargs):
        command.function(*args, **kwargs)


# Create a global command registry instance
command_registry = CommandRegistry()
