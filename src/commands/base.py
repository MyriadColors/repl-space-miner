from typing import Callable

from .registry import Command, Argument, command_registry


def register_command(
    command_names: list[str],
    command_function: Callable,
    argument_list: list[Argument] | None = None,
):
    """
    Register a command with the global command registry.

    Args:
        command_names: List of names that can be used to invoke this command
        command_function: The function to execute when the command is called
        argument_list: List of arguments the command accepts
    """
    for name in command_names:
        argument_struct_list_with_index = []
        if argument_list:
            for i, arg in enumerate(argument_list):
                if arg.positional_index is None:
                    # If positional_index is not set, create a new Argument with the index
                    new_arg = Argument(
                        name=arg.name,
                        type=arg.type,
                        is_optional=arg.is_optional,
                        positional_index=i,
                        custom_validator=arg.custom_validator,
                    )
                    argument_struct_list_with_index.append(new_arg)
                else:
                    # If positional_index is already set, use the original Argument
                    argument_struct_list_with_index.append(arg)

        command = Command(command_function, argument_struct_list_with_index)
        command_registry.register(name, command)
