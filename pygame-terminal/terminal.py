import pygame


class PygameTerminal:
    def __init__(self, width: int = 800, height: int = 600) -> None:
        """
        Initialize the Pygame Terminal Emulator.

        :param width: The width of the terminal emulator window.
        :param height: The height of the terminal emulator window.
        """
        self.command_callback: callable = None
        pygame.init()
        pygame.display.set_caption("Pygame Terminal Emulator")
        self.width: int = width
        self.height: int = height
        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height))
        self.font: pygame.font = pygame.font.Font(None, 32)
        self.default_bg_color: pygame.color = (0, 0, 0)
        self.bg_color: pygame.color = self.default_bg_color
        self.default_fg_color: pygame.color = (255, 255, 255)
        self.fg_color: pygame.color = self.default_fg_color
        self.terminal_lines: list[str] = ["Welcome to Pygame Terminal Emulator"]
        self.current_line: str = ""
        self.cursor_pos: int = 0
        self.command_history: list[str] = []
        self.history_index: int = -1
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True

        # Command registry
        self.commands = {}

    def run(self):
        """The main loop to run the terminal emulator."""
        while self.running:
            self.handle_events()
            self.draw_terminal()
            self.clock.tick(30)

    def clear(self):
        """Clear the terminal screen."""
        self.terminal_lines.clear()

    def handle_events(self):
        """Handle events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

    def handle_return(self):
        """Handle the return key."""
        if self.current_line.strip():
            self.command_history.append(self.current_line)
        self.process_command(self.current_line)
        self.current_line = ""
        self.cursor_pos = 0
        self.history_index = -1

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

    def draw_terminal(self):
        """Renders the terminal interface on the screen."""
        self.screen.fill(self.bg_color)
        y = 10
        for line in self.terminal_lines[-18:]:
            text = self.font.render(line, True, self.fg_color)
            self.screen.blit(text, (10, y))
            y += 30

        # Draw the current input line
        prompt = "> " + self.current_line
        text = self.font.render(prompt, True, self.fg_color)
        self.screen.blit(text, (10, self.height - 40))

        # Draw the cursor
        cursor_x = 10 + self.font.size("> " + self.current_line[:self.cursor_pos])[0]
        pygame.draw.line(self.screen, self.fg_color, (cursor_x, self.height - 40), (cursor_x, self.height - 10), 2)

        pygame.display.flip()

    def process_command(self, command: str):
        """
        Process the entered command by splitting the input and calling the corresponding function.
        """
        # Split the command into the command name and arguments
        parts = command.strip().split()
        if not parts:
            return

        command_name = parts[0].lower()  # Extract command name
        args = parts[1:]  # The rest are arguments

        # Check if the command is registered
        if command_name in self.commands:
            # Call the registered command function and pass arguments
            self.commands[command_name](self, args)
        else:
            self.terminal_lines.append(f"Unknown command: {command_name}")

    def register_command(self, command_name: str, command_function: callable):
        """
        Register a command that maps a command name to a function.

        :param command_name: The name of the command (e.g., 'help', 'exit')
        :param command_function: A callable function that will be executed when the command is entered
        """
        self.commands[command_name] = command_function

    def write(self, text):
        """Write text to the terminal."""
        self.terminal_lines.append(text)

    @staticmethod
    def args_length(args):
        if args:
            return len(args[0])
        else:
            return 0
