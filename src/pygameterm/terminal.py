from dataclasses import dataclass, field
from math import floor
from typing import Callable, Any
import pygame
from pygame import Color

@dataclass
class Argument:
    name: str
    type: type
    is_optional: bool
    positional_index: int | None = None
    custom_validator: Callable[[Any], bool] | None = None


@dataclass
class Command:
    function: Callable
    arguments: list[Argument] = field(default_factory=list)
    number_of_arguments: int = field(init=False)

    def get_required_arguments(self):
        return [arg for arg in self.arguments if not arg.is_optional]

    def get_optional_arguments(self):
        return [arg for arg in self.arguments if arg.is_optional]

    def __post_init__(self):
        self.number_of_arguments = len(self.arguments)

    def validate_arguments(self, args):
        if len(args) < len([arg for arg in self.arguments if not arg.is_optional]):
            return False, "Not enough arguments provided."

        if len(args) > len(self.arguments):
            return False, "Too many arguments provided."

        for i, (arg, value) in enumerate(zip(self.arguments, args)):
            try:
                if arg.type == int:
                    int(value)
                elif arg.type == float:
                    float(value)
                elif arg.type == bool:
                    value = value.lower()
                    if value not in ('true', 'false', '1', '0'):
                        return False, f"Argument {i + 1} ({arg.name}) must be a boolean value (true/false or 1/0)."
                elif arg.type == str:
                    pass
                else:
                    # For any other types, we'll just check if it's not empty
                    if not value:
                        return False, f"Argument {i + 1} ({arg.name}) cannot be empty."
            except ValueError:
                return False, f"Argument {i + 1} ({arg.name}) must be of type {arg.type.__name__}."

        return True, ""

    def __call__(self, *args, terminal: 'PygameTerminal'):
        valid, message = self.validate_arguments(args)
        if not valid:
            raise ValueError(message)
        return self.function(*args, term=terminal)

def typeof(value):
    return type(value)


class PygameTerminal:
    def __init__(self, app_state, width: int = 1024, height: int = 600, font_size: int = 32, initial_message: str = "") -> None:
        """
        Initialize the Pygame Terminal Emulator.

        :param width: The width of the terminal emulator window.
        :param height: The height of the terminal emulator window.
        :param font_size: The font size of the terminal emulator window.
        :param initial_message: The initial message to display in the terminal emulator.
        """
        self.terminal_margin_bottom = 40
        self.terminal_margin_left = 10
        self.terminal_margin_top = 10
        self.line_width = 2
        self.command_callback: Callable | None = None
        pygame.init()
        pygame.display.set_caption("Pygame Terminal Emulator")
        self.app_state = app_state  # This is the state of the application, this will be passed to commands by default
        self.width: int = width
        self.height: int = height
        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height))
        self.font: pygame.font.Font = pygame.font.Font(None, font_size)
        self.default_bg_color: pygame.color.Color = Color(0, 0, 0)
        self.bg_color: pygame.color.Color = self.default_bg_color
        self.default_fg_color: pygame.color.Color = Color(255, 255, 255)
        self.fg_color: pygame.color.Color = self.default_fg_color
        self.custom_line_color = None
        self.terminal_lines: list[str] = [initial_message]
        self.current_line: str = ""
        self.cursor_pos: int = 0
        self.command_history: list[str] = []
        self.history_index: int = -1
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.clock_tick_rate = 30
        self.running: bool = True
        self.input_mode: bool = False
        self.input_prompt: str = ""
        self.input_callback: Callable | None = None
        self.line_margin_height = 5
        self.lines_on_screen = floor(self.height / (self.font.get_height() + self.line_margin_height)) -2


        # Command registry
        # add some default commands
        self.commands: dict[str, Command] = {}

    def color_current_line(self):
        pass

    def quit(self):
        self.running = False

    def prompt_user(self, prompt: str) -> str:
        """
        Query the user for input and return the result.

        :param prompt: The prompt to display to the user
        :return: 's input as a string
        """
        self.input_mode = True
        self.input_prompt = prompt
        self.current_line = ""
        self.cursor_pos = 0

        while self.input_mode:
            self.handle_events()
            self.draw_terminal()
            self.clock.tick(self.clock_tick_rate)

        return self.current_line

    def set_font_size(self, font_size: int) -> None:
        """Set the font size."""
        self.font = pygame.font.Font(None, font_size)

    def set_font_name(self, font_name: str) -> None:
        """Set the font name."""
        self.font = pygame.font.Font(font_name, self.font.get_height())

    def set_font(self, font_name: str, font_size: int) -> None:
        """Set the font."""
        self.font = pygame.font.Font(font_name, font_size)

    def write_command_history(self, limit: int = -1) -> None:
        """Write the command history to the terminal."""
        for line in self.command_history[-limit:]:
            self.terminal_lines.append(line)

    def run(self):
        """The main loop to run the terminal emulator."""
        while self.running:
            self.handle_events()
            self.draw_terminal()
            self.clock.tick(self.clock_tick_rate)

    @staticmethod
    def clear(terminal):
        """Clear the terminal screen."""
        terminal.terminal_lines.clear()

    def handle_events(self):
        """Handle events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.input_mode:
                    self.handle_input_keydown(event)
                else:
                    self.handle_keydown(event)

    def handle_return(self):
        """Handle the return key."""
        if self.current_line.strip():
            self.command_history.append(self.current_line)
        self.process_command(self.current_line)
        self.current_line = ""
        self.cursor_pos = 0
        self.history_index = -1

    def new_line(self):
        """Handle the new line key."""
        self.handle_return()

    def handle_backspace(self):
        """Handle the backspace key."""
        if self.cursor_pos > 0:
            self.current_line = self.current_line[:self.cursor_pos - 1] + self.current_line[self.cursor_pos:]
            self.cursor_pos -= 1

    def handle_left_arrow(self):
        """ Handle the left arrow key. """
        if self.cursor_pos > 0:
            self.cursor_pos = max(0, self.cursor_pos - 1)

    def handle_right_arrow(self):
        """ Handle the right arrow key. """
        if self.cursor_pos < len(self.current_line):
            self.cursor_pos = min(len(self.current_line), self.cursor_pos + 1)

    def handle_up_arrow(self):
        """ Handle the up arrow key. """
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.current_line = self.command_history[-(self.history_index + 1)]
            self.cursor_pos = len(self.current_line)

    def handle_down_arrow(self):
        """ Handle the down arrow key. """
        if self.history_index > -1:
            self.history_index -= 1
            if self.history_index == -1:
                self.current_line = ""
            else:
                self.current_line = self.command_history[-(self.history_index + 1)]
            self.cursor_pos = len(self.current_line)

    def handle_printable(self, char):
        """Handle printable characters."""
        self.current_line = self.current_line[:self.cursor_pos] + char + self.current_line[self.cursor_pos:]
        self.cursor_pos += 1

    def handle_input_keydown(self, event):
        """Handle key presses during input mode."""
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self.input_mode = False
        elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
            self.handle_backspace()
        elif event.key == pygame.K_LEFT:
            self.handle_left_arrow()
        elif event.key == pygame.K_RIGHT:
            self.handle_right_arrow()
        elif event.unicode.isprintable():
            self.handle_printable(event.unicode)

    def handle_keydown(self, event_param):
        """Handle key presses."""
        if event_param.key == pygame.K_RETURN or event_param.key == pygame.K_KP_ENTER:
            self.handle_return()
        elif event_param.key == pygame.K_BACKSPACE or event_param.key == pygame.K_DELETE:
            self.handle_backspace()
        elif event_param.key == pygame.K_LEFT:
            self.handle_left_arrow()
        elif event_param.key == pygame.K_RIGHT:
            self.handle_right_arrow()
        elif event_param.key == pygame.K_UP:
            self.handle_up_arrow()
        elif event_param.key == pygame.K_DOWN:
            self.handle_down_arrow()
        elif event_param.unicode.isprintable():
            self.handle_printable(event_param.unicode)

    def write_in_place(self, text):
        """
        Write text to the terminal in-place (overwrite the last rendered line).
        Useful for dynamic updates like progress bars.
        """
        if self.terminal_lines:
            self.terminal_lines[-1] = text  # Replace the last line
        else:
            self.terminal_lines.append(text)  # In case it's the first line

        self.draw_terminal()

    def progress_bar(self, total, current, bar_length=30):
        """
        Display a progress bar that updates in-place.

        :param total: The total number of steps.
        :param current: The current step.
        :param bar_length: The length of the progress bar.
        """
        progress = current / total
        block = int(round(bar_length * progress))
        bar = "#" * block + "-" * (bar_length - block)
        percentage = progress * 100
        progress_message = f"Progress: [{bar}] {percentage:.2f}%"

        # Write the progress bar in place
        self.write_in_place(progress_message)

    def wait(self, duration_ms: int):
        """
        Wait for the specified duration while keeping the terminal responsive.

        :param duration_ms: Duration to wait in milliseconds
        """
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < duration_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Update and draw the terminal
            self.draw_terminal()
            pygame.display.flip()

            # Control the frame rate
            pygame.time.Clock().tick(self.clock_tick_rate)

    def countdown_with_message(self,
                               start_value: float,
                               end_value: float,
                               step: float,
                               message_template: str,
                               wait_time: float,
                               on_complete: Callable,
                               can_interrupt: bool = False):
        """
        Countdown from start_value to end_value, displaying a message at each step.

        :param start_value: The value to start counting down from
        :param end_value: The value to count down to (inclusive)
        :param step: The amount to decrease the value by each iteration
        :param message_template: A string template for the message (use {} for the countdown value)
        :param wait_time: Time to wait between each countdown step (in seconds)
        :param on_complete: Optional callback function to execute when countdown completes
        :param can_interrupt: Whether the countdown can be interrupted by the user
        """
        current_value = start_value
        while current_value >= end_value:
            message = message_template.format(current_value)
            self.write(message)
            self.draw_terminal()
            pygame.display.flip()

            wait_start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - wait_start < int(wait_time * 1000):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    # Handle other events if needed
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if can_interrupt:
                                self.write("Operation interrupted by user.")
                                return
                            else:
                                self.write("Cannot interrupt.")

                # Control the frame rate
                pygame.time.Clock().tick(self.clock_tick_rate)

            current_value = round(current_value - step, 1)  # Round to avoid floating point errors
        on_complete()

    def draw_terminal(self):
        """Renders the terminal interface on the screen."""
        self.screen.fill(self.bg_color)
        y = self.terminal_margin_top
        for line in self.terminal_lines[-self.lines_on_screen:]:
            text = self.font.render(line, True,
                                    self.fg_color if self.custom_line_color is None else self.custom_line_color)
            self.screen.blit(text, (self.terminal_margin_left, y))
            y += self.font.get_height() + self.line_margin_height

        # Draw the current input line
        if self.input_mode:
            prompt = self.input_prompt + " " + self.current_line
        else:
            prompt = "> " + self.current_line
        text = self.font.render(prompt, True, self.fg_color)
        self.screen.blit(text, (self.terminal_margin_left, self.height - self.terminal_margin_bottom))

        # Draw the cursor
        cursor_x = self.terminal_margin_left + \
                   self.font.size(prompt[:len(prompt) - len(self.current_line) + self.cursor_pos])[0]
        pygame.draw.line(self.screen, self.fg_color, (cursor_x, self.height - self.terminal_margin_bottom),
                         (cursor_x, self.height - self.terminal_margin_top), self.line_width)

        pygame.display.flip()

    def process_command(self, command: str):
        parts = command.strip().split()
        if not parts:
            return

        command_name: str = parts[0].lower()
        input_args = parts[1:]

        if command_name in self.commands:
            #print(f"Debug: {command_name} {input_args} found")
            command_struct: Command = self.commands[command_name]

            try:
                for i, arg in enumerate(command_struct.arguments):
                    if i < len(input_args):
                        value = input_args[i]
                        arg_type = arg.type

                        # Check if the value satisfies the expected type
                        if not self.check_type(value, arg_type):
                            raise ValueError(f"Invalid type for argument {arg.name}: {value} ({arg_type})")

                        # Apply custom validator if it exists
                        if arg.custom_validator and not arg.custom_validator(value):
                            raise ValueError(f"Custom validation failed for argument {arg.name}")
                    elif not arg.is_optional:
                        raise ValueError(f"Missing required argument: {arg.name}")

                # Execute the command with the original string arguments and pass the terminal
                result = command_struct(*input_args, terminal=self)
                if result is not None:
                    self.write(str(result))
            except ValueError as e:
                self.write(str(e))
        else:
            self.write(f"Command '{command_name}' not found")

    @staticmethod
    def check_type(value: str, expected_type: type) -> bool:
        """
        Check if a string value satisfies the expected type without conversion.
        """
        if expected_type == int:
            return value.isdigit() or (value[0] == '-' and value[1:].isdigit())
        elif expected_type == float:
            try:
                float(value)
                return True
            except ValueError:
                return False
        elif expected_type == str:
            return True  # All inputs are initially strings
        else:
            return False  # Unsupported type

    def register_command(self, command_names: list[str], command_function: Callable,
                         argument_list: list[Argument] | None = None):
        """
        Register a command that maps a command name to a function.

        :param command_names: The list of names of the command (e.g., ['help', 'h'], ['exit', 'h'])
        :param command_function: A callable function that will be executed when the command is entered
        :param argument_list: A list of Argument objects that describe the arguments of the command
        """
        for name in command_names:
            argument_struct_list_with_index = []
            for i, arg in enumerate(argument_list or []):
                if arg.positional_index is None:
                    # If positional_index is not set, create a new Argument with the index
                    new_arg = Argument(
                        name=arg.name,
                        type=arg.type,
                        is_optional=arg.is_optional,
                        positional_index=i,
                        custom_validator=arg.custom_validator if hasattr(arg, 'custom_validator') else None
                    )
                    argument_struct_list_with_index.append(new_arg)
                else:
                    # If positional_index is already set, use the original Argument
                    argument_struct_list_with_index.append(arg)

            self.commands[name] = Command(function=command_function, arguments=argument_struct_list_with_index)

    def write(self, text: str, debug_flag: bool = False):
        """Write text to the terminal."""
        self.terminal_lines.append(text)
        if debug_flag:
            print(f"Debug: {text}")

    @staticmethod
    def args_length(args):
        if args:
            return len(args[0])
        else:
            return 0
