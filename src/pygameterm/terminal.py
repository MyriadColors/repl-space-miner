from dataclasses import dataclass, field
from math import floor
import re
from typing import Callable, Any

import pygame

from src.pygameterm import color_data

@dataclass
class TerminalLine:
    text: str
    fg_color: pygame.Color | None = None
    bg_color: pygame.Color | None = None

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
        required_args = [arg for arg in self.arguments if not arg.is_optional]
        if len(args) < len(required_args):
            return False, "Not enough arguments provided."
        if len(args) > len(self.arguments):
            return False, "Too many arguments provided."

        for i, (arg, value) in enumerate(zip(self.arguments, args), start=1):
            if arg.type == int:
                if not self._is_valid_int(value):
                    return False, f"Argument {i} ({arg.name}) must be an integer."
            elif arg.type == float:
                if not self._is_valid_float(value):
                    return False, f"Argument {i} ({arg.name}) must be a float."
            elif arg.type == bool:
                if not self._is_valid_bool(value):
                    return False, f"Argument {i} ({arg.name}) must be a boolean value (true/false or 1/0)."
            elif arg.type == str:
                pass
            else:
                if not value:
                    return False, f"Argument {i} ({arg.name}) cannot be empty."

        return True, ""

    @staticmethod
    def _is_valid_int(value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_valid_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_valid_bool(value):
        return value.lower() in ('true', 'false', '1', '0')

    def __call__(self, *args, terminal: 'PygameTerminal'):
        valid, message = self.validate_arguments(args)
        if not valid:
            raise ValueError(message)
        return self.function(*args, term=terminal)


def typeof(value):
    return type(value)


class PygameTerminal:
    def __init__(self, app_state, width: int = 1024, height: int = 600, font_size: int = 28,
                 initial_message: str = "", default_bg_color: pygame.Color = color_data.color['black'],
                 default_fg_color: pygame.Color = color_data.color['white']) -> None:
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
        self.width: int = width  # The width of the terminal emulator window
        self.height: int = height  # The height of the terminal emulator window
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.width, self.height))  # The screen surface of the terminal emulator window
        self.font: pygame.font.Font = pygame.font.Font(None, font_size)
        self.default_bg_color: pygame.color.Color = default_bg_color
        self.bg_color: pygame.color.Color = self.default_bg_color
        self.default_fg_color: pygame.color.Color = default_fg_color
        self.fg_color: pygame.color.Color = self.default_fg_color
        self.custom_line_color = None
        self.terminal_lines: list[TerminalLine] = [TerminalLine(initial_message)]
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
        self.font_size = font_size
        self.set_monospace_font()
        self.lines_on_screen = floor(self.height / (self.font.get_height() + self.line_margin_height)) - 2
        self.illustration_window = None
        self.custom_event_handlers = {}
        pygame.key.set_repeat(250, 25)

        # Command registry
        self.commands: dict[str, Command] = {}

    def set_monospace_font(self):
        try:
            # Try to use 'Courier' font, which is available on most systems
            self.font = pygame.font.SysFont('courier', self.font_size)
        except Exception as e:
            print(e)
            try:
                # If 'Courier' is not available, try 'monospace'
                self.font = pygame.font.SysFont('monospace', self.font_size)
            except Exception as e:
                print(e)
                # If both fail, fall back to the default font
                print("Warning: Monospace font not found. Using default font.")
                self.font = pygame.font.Font(None, self.font_size)

    def set_font_size(self, font_size: int) -> None:
        """Set the font size."""
        self.font_size = font_size
        self.set_monospace_font()

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
    
    def prompt_multiple_choice(self, prompt: str, options: list[str]) -> int:
        """
        Query the user for input and return the result.

        :param prompt: The prompt to display to the user
        :param options: The list of options to display to the user
        :return: The index of the option selected by the user
        """
        for i, option in enumerate(options):
            self.writeLn(f"{i + 1}. {option}")
        self.input_mode = True
        self.input_prompt = prompt
        self.current_line = ""
        self.cursor_pos = 0
        selected_index: int = 0
        
        while self.input_mode:
            self.handle_events()
            self.draw_terminal()
            self.clock.tick(self.clock_tick_rate)
            if self.current_line.isdigit():
                selected_index = int(self.current_line)
                if 0 <= selected_index < len(options):
                    self.input_mode = False
                else:
                    self.writeLn("Invalid selection. Please enter a number corresponding to the options.")
                    self.current_line = ""
                    self.cursor_pos = 0
            elif self.current_line:
                self.writeLn("Invalid input. Please enter a number.")
                self.current_line = ""
                self.cursor_pos = 0

        return selected_index
        
        
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
            elif event.type == pygame.KEYUP:
                if self.input_mode:
                    self.handle_input_keyup()  # Handle key releases
                else:
                    self.handle_keyup()  # Handle key releases
            # Handle custom events
            elif event.type >= pygame.USEREVENT:
                event_name = pygame.event.event_name(event.type)
                if event_name in self.custom_event_handlers:
                    self.custom_event_handlers[event_name](event)  # Pass the event object

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
        """Handles characters with autocompletion."""
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

    @staticmethod
    def handle_input_keyup():
        """Handle key releases during input mode."""
        pygame.key.set_repeat()  # Disable key repeat on key release

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
        elif event_param.key == pygame.K_TAB:
            self.handle_tab()
        else:
            self.writeLn(f"Key {event_param.key} not recognized")

    @staticmethod
    def handle_keyup():
        """Handle key releases."""
        pygame.key.set_repeat()  # Disable key repeat on key release

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
            self.writeLn(message)
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
                                self.writeLn("Operation interrupted by user.")
                                return
                            else:
                                self.writeLn("Cannot interrupt.")

                # Control the frame rate
                pygame.time.Clock().tick(self.clock_tick_rate)

            current_value = round(current_value - step, 1)  # Round to avoid floating point errors
        on_complete()

    def draw_terminal(self):
        """Renders the terminal interface on the screen."""
        self.screen.fill(self.bg_color)

        # Draw previous terminal lines
        line_y = self.terminal_margin_top
        for line in self.terminal_lines[-self.lines_on_screen:]:
            line_fg_color = line.fg_color or self.fg_color
            line_bg_color = line.bg_color or self.bg_color
            line_surface = self.font.render(line.text, True, line_fg_color, line_bg_color)
            self.screen.blit(line_surface, (self.terminal_margin_left, line_y))
            line_y += self.font.get_height() + self.line_margin_height

        # Draw current input line
        input_prompt = self.input_prompt if self.input_mode else "> "
        input_line = input_prompt + self.current_line
        input_surface = self.font.render(input_line, True, self.fg_color)
        input_y = self.height - self.terminal_margin_bottom
        self.screen.blit(input_surface, (self.terminal_margin_left, input_y))

        # Draw cursor
        cursor_x = self.terminal_margin_left + self.font.size(input_prompt + self.current_line[:self.cursor_pos])[0]
        cursor_top = input_y
        cursor_bottom = self.height - self.terminal_margin_top
        pygame.draw.line(self.screen, self.fg_color, (cursor_x, cursor_top), (cursor_x, cursor_bottom), self.line_width)

        pygame.display.flip()

    def process_command(self, command: str):
        parts = command.strip().split()
        if not parts:
            return

        command_name: str = parts[0].lower()
        input_args = parts[1:]

        if command_name in self.commands:
            command_struct: Command = self.commands[command_name]

            try:
                for i, arg in enumerate(command_struct.arguments):
                    if i < len(input_args):
                        pass
                    elif not arg.is_optional:
                        raise ValueError(f"Missing required argument: {arg.name}")

                # Execute the command with the original string arguments and pass the terminal
                result = command_struct(*input_args, terminal=self)
                if result is not None:
                    self.writeLn(str(result))
            except ValueError as e:
                self.writeLn(str(e))
        else:
            self.writeLn(f"Command '{command_name}' not found")

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

    def writeLn(self, text: str, debug_flag: bool = False):
        """Write text to the terminal, interpreting '\n' as a newline."""
        lines = text.split('\n')
        for line in lines:
            self.terminal_lines.append(TerminalLine(line, self.fg_color, self.bg_color))
        if debug_flag:
            print(f"DEBUG: {text}")
            
    def write_colored_text(self, text: str, fg_color: pygame.Color | None = None, bg_color: pygame.Color | None = None):
        """Write text to the terminal with specified colors."""
        lines = text.split('\n')
        for line in lines:
            self.terminal_lines.append(TerminalLine(line, fg_color=fg_color, bg_color=bg_color))
    
    @staticmethod
    def args_length(args):
        if args:
            return len(args[0])
        else:
            return 0

    def create_illustration_window(self, width, height):
        self.illustration_window = pygame.display.set_mode((width, height))

    def close_illustration_window(self):
        if self.illustration_window:
            pygame.display.set_mode((self.width, self.height))  # Restore original window
            self.illustration_window = None

    def show_illustration(self, image_path):
        if self.illustration_window:
            try:
                image = pygame.image.load(image_path)
                self.illustration_window.blit(image, (0, 0))
                pygame.display.flip()  # Update illustration window
            except Exception as e:
                self.writeLn(f"Error loading illustration: {e}")

    def register_event_handler(self, event_name, handler):
        # Generate a unique event type id
        event_type = pygame.USEREVENT + len(self.custom_event_handlers)
        pygame.event.EventType(event_type, {'event_name': event_name})  # Register the event type
        self.custom_event_handlers[event_name] = handler

    def trigger_event(self, event_name, *args, **kwargs):
        # Find the event type id associated with the event name
        for event_type in range(pygame.USEREVENT, pygame.NUMEVENTS):
            if pygame.event.event_name(event_type) == event_name:
                event = pygame.event.Event(event_type, *args, **kwargs)
                pygame.event.post(event)
                return

        self.writeLn(f"Error: Event '{event_name}' not registered.")

    def draw_table(self, data, headers, x=None, y=None, column_widths=None, cell_padding=5, border_width=1,
                   border_color=pygame.Color('white'), header_bg_color=pygame.Color('gray')):

        # Calculate positions if not provided
        if x is None:
            x = self.terminal_margin_left
        if y is None:
            y = self.terminal_margin_top

        num_columns = len(headers)
        num_rows = len(data) + 1  # +1 for header row

        # Calculate column widths automatically if not provided
        if column_widths is None:
            column_widths = [
                self.font.size(str(max([row[i] for row in data + [headers]], key=lambda x: len(str(x)))))[0] +
                2 * cell_padding for i in range(num_columns)]

        # Calculate total table width and height
        table_width = sum(column_widths) + (num_columns + 1) * border_width
        table_height = num_rows * (self.font.get_height() + 2 * cell_padding) + (num_rows + 1) * border_width

        # Draw border
        pygame.draw.rect(self.screen, border_color, (x, y, table_width, table_height), border_width)

        # Draw header row
        current_x = x + border_width
        for i, header in enumerate(headers):
            header_rect = pygame.Rect(current_x, y + border_width, column_widths[i],
                                      self.font.get_height() + 2 * cell_padding)
            pygame.draw.rect(self.screen, header_bg_color, header_rect)

            header_surface = self.font.render(str(header), True, self.fg_color)
            header_rect.x += cell_padding  # Adjust for cell padding
            header_rect.y += cell_padding
            self.screen.blit(header_surface, header_rect)
            current_x += column_widths[i] + border_width

        # Draw data rows
        current_y = y + self.font.get_height() + 2 * cell_padding + 2 * border_width
        for row in data:
            current_x = x + border_width
            for i, cell in enumerate(row):
                cell_rect = pygame.Rect(current_x, current_y, column_widths[i],
                                        self.font.get_height() + 2 * cell_padding)
                cell_surface = self.font.render(str(cell), True, self.fg_color)
                cell_rect.x += cell_padding
                cell_rect.y += cell_padding
                self.screen.blit(cell_surface, cell_rect)
                current_x += column_widths[i] + border_width
            current_y += self.font.get_height() + 2 * cell_padding + border_width

        pygame.display.flip()

    def draw_menu(self, menu_options, x=None, y=None, selected_index=0, item_padding=5,
                  border_width=1, border_color=pygame.Color('white'),
                  selected_bg_color=pygame.Color('gray')):
        """
        Draws a menu with the given options on the screen.

        Args:
            menu_options (list): A list of strings representing the menu options.
            x (int, optional): The x-coordinate of the top-left corner of the menu. Defaults to None.
            y (int, optional): The y-coordinate of the top-left corner of the menu. Defaults to None.
            selected_index (int, optional): The index of the currently selected menu option. Defaults to 0.
            item_padding (int, optional): The padding around each menu item. Defaults to 5.
            border_width (int, optional): The width of the menu border. Defaults to 1.
            border_color (pygame.Color, optional): The color of the menu border. Defaults to white.
            selected_bg_color (pygame.Color, optional): The background color of the selected menu item. Defaults to gray.
        """
        x = x if x is not None else self.terminal_margin_left
        y = y if y is not None else self.terminal_margin_top

        # Calculate dimensions of the menu
        menu_width = max(self.font.size(option)[0] for option in menu_options) + 2 * item_padding
        menu_height = len(menu_options) * (self.font.get_height() + 2 * item_padding) + 2 * border_width

        # Draw the menu border
        pygame.draw.rect(self.screen, border_color, (x, y, menu_width, menu_height), border_width)

        # Position for the first menu item
        current_y = y + border_width + item_padding

        # Render each menu option
        for index, option in enumerate(menu_options):
            # Highlight the selected menu item
            if index == selected_index:
                pygame.draw.rect(self.screen, selected_bg_color,
                                 (x + border_width, current_y - item_padding, menu_width - 2 * border_width,
                                  self.font.get_height() + 2 * item_padding))

            # Render the menu option text
            option_surface = self.font.render(option, True, self.fg_color)
            self.screen.blit(option_surface, (x + border_width + item_padding, current_y))
            current_y += self.font.get_height() + 2 * item_padding

        # Update the display to show the menu
        pygame.display.flip()

    @staticmethod
    def handle_menu_input(event, menu_options, selected_index):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(menu_options)
            elif event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(menu_options)
            elif event.key == pygame.K_RETURN:
                # Return the selected option
                return selected_index, menu_options[selected_index]

        return selected_index, None

    def draw_progress_bar(self, current, total, x=None, y=None, width=200, height=20,
                          bg_color=pygame.Color('gray'), fg_color=pygame.Color('green')):
        if x is None:
            x = self.terminal_margin_left
        if y is None:
            y = self.terminal_margin_top

        progress = current / total
        progress_width = int(width * progress)

        # Draw background
        pygame.draw.rect(self.screen, bg_color, (x, y, width, height))

        # Draw progress
        pygame.draw.rect(self.screen, fg_color, (x, y, progress_width, height))

        # Display percentage (optional)
        percentage_text = self.font.render(f"{int(progress * 100)}%", True, self.fg_color)
        text_rect = percentage_text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(percentage_text, text_rect)

        pygame.display.flip()

    def update_progress_bar(self, current, total, x=None, y=None, width=200, height=20,
                            bg_color=pygame.Color('gray'), fg_color=pygame.Color('green')):
        self.draw_progress_bar(current, total, x, y, width, height, bg_color, fg_color)

    def handle_tab(self):
        """Handle tab key for command completion."""
        if not self.current_line:
            return

        parts = self.current_line.split()
        # Complete command
        possible_commands = [cmd for cmd in self.commands if cmd.startswith(parts[0])]
        if len(possible_commands) == 1:
            self.current_line = possible_commands[0] + " "
            self.cursor_pos = len(self.current_line)
        elif len(possible_commands) > 1:
            self.writeLn(" ".join(possible_commands))
