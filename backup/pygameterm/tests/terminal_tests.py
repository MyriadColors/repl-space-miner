import unittest
from io import StringIO
from unittest.mock import patch

import pygame

from backup.pygameterm.terminal import PygameTerminal, Argument


class TestPygameTerminal(unittest.TestCase):
    def setUp(self):
        """Setup method to create a PygameTerminal instance for each test."""
        self.app_state = {"test_var": "initial value"}
        self.terminal = PygameTerminal(app_state=self.app_state)

    # Test 1
    def test_init(self):
        """Test if the terminal initializes correctly."""
        self.assertEqual(self.terminal.width, 1024)
        self.assertEqual(self.terminal.height, 600)
        self.assertEqual(self.terminal.terminal_lines, [""])
        self.assertEqual(self.terminal.current_line, "")
        self.assertEqual(self.terminal.cursor_pos, 0)
        self.assertEqual(self.terminal.app_state['test_var'],  "initial value")

    # Test 2
    def test_write(self):
        """Test if the write method adds text to the terminal lines."""
        self.terminal.writeLn("Test Line 1")
        self.terminal.writeLn("Test Line 2")
        self.assertEqual(len(self.terminal.terminal_lines), 3)  # Including initial empty line
        self.assertEqual(self.terminal.terminal_lines[-2], "Test Line 1")
        self.assertEqual(self.terminal.terminal_lines[-1], "Test Line 2")

    # Test 3
    def test_handle_printable(self):
        """Test handling of printable characters."""
        self.terminal.handle_printable("a")
        self.terminal.handle_printable("b")
        self.terminal.handle_printable("c")
        self.assertEqual(self.terminal.current_line, "abc")
        self.assertEqual(self.terminal.cursor_pos, 3)

    # Test 4
    def test_handle_backspace(self):
        """Test handling of backspace."""
        self.terminal.handle_printable("a")
        self.terminal.handle_printable("b")
        self.terminal.handle_printable("c")
        self.terminal.handle_backspace()
        self.assertEqual(self.terminal.current_line, "ab")
        self.assertEqual(self.terminal.cursor_pos, 2)

    # Test 5
    def test_handle_left_arrow(self):
        """Test handling of left arrow key."""
        self.terminal.handle_printable("a")
        self.terminal.handle_printable("b")
        self.terminal.handle_left_arrow()
        self.assertEqual(self.terminal.cursor_pos, 1)

    # Test 6
    def test_handle_right_arrow(self):
        """Test handling of right arrow key."""
        self.terminal.handle_printable("a")
        self.terminal.handle_printable("b")
        self.terminal.handle_left_arrow()
        self.terminal.handle_right_arrow()
        self.assertEqual(self.terminal.cursor_pos, 2)

    # Test 7
    def test_handle_return(self):
        """Test handling of the return key, adding commands to history."""
        self.terminal.handle_printable("t")
        self.terminal.handle_printable("e")
        self.terminal.handle_printable("s")
        self.terminal.handle_printable("t")
        self.terminal.handle_return()
        self.assertEqual(self.terminal.command_history, ['test'])
        self.assertEqual(self.terminal.current_line, '')

    # Test 8
    @patch('sys.stdout', new_callable=StringIO)
    def test_set_font_size(self, mock_stdout):
        """Test setting the font size."""
        self.terminal.set_font_size(32)
        self.assertEqual(self.terminal.font_size, 32)

    # Test 9
    def test_register_command(self):
        """Test registering a command."""
        def test_command(term: PygameTerminal):
            term.writeLn("Command executed")

        self.terminal.register_command(
            command_names=['test', 't'],
            command_function=test_command,
            argument_list=[Argument(name="arg1", type=str, is_optional=False)]
        )
        self.assertIn('test', self.terminal.commands)
        self.assertIn('t', self.terminal.commands)
        self.assertEqual(self.terminal.commands['test'].function, test_command)

    # Test 10
    def test_process_command(self):
        """Test processing a registered command."""

        def test_command(arg1: str, term: PygameTerminal):
            term.writeLn(f"Command executed with argument: {arg1}")

        self.terminal.register_command(
            command_names=['test', 't'],
            command_function=test_command,
            argument_list=[Argument(name="arg1", type=str, is_optional=False)]
        )

        self.terminal.process_command("test argument")
        self.assertEqual(self.terminal.terminal_lines[-1], "Command executed with argument: argument")

    def test_process_command_success(self):
        """Test processing a valid command."""

        def test_command(arg1: str, arg2: int, term: PygameTerminal):
            return f"Command executed with {arg1} and {arg2}"

        self.terminal.register_command(
            command_names=['test', 't'],
            command_function=test_command,
            argument_list=[
                Argument(name="arg1", type=str, is_optional=False),
                Argument(name="arg2", type=int, is_optional=False)
            ]
        )

        self.terminal.process_command("test hello 123")
        self.assertEqual(self.terminal.terminal_lines[-1], "Command executed with hello and 123")

    def test_process_command_not_found(self):
        """Test processing an unknown command."""
        self.terminal.process_command("unknowncommand")
        self.assertEqual(self.terminal.terminal_lines[-1], "Command 'unknowncommand' not found")

    def test_process_command_invalid_type(self):
        """Test processing a command with an invalid argument type."""

        def test_command(arg1: int, term: PygameTerminal):
            return f"Command executed with {arg1}"

        self.terminal.register_command(
            command_names=['test', 't'],
            command_function=test_command,
            argument_list=[
                Argument(name="arg1", type=int, is_optional=False)
            ]
        )

        self.terminal.process_command("test hello")  # "hello" is not an int
        self.assertIn("Invalid type for argument arg1", self.terminal.terminal_lines[-1])

    def test_process_command_not_enough_arguments(self):
        """Test processing a command with missing required arguments."""

        def test_command(arg1: str, arg2: int, term: PygameTerminal):
            return f"Command executed with {arg1} and {arg2}"

        self.terminal.register_command(
            command_names=['test', 't'],
            command_function=test_command,
            argument_list=[
                Argument(name="arg1", type=str, is_optional=False),
                Argument(name="arg2", type=int, is_optional=False)
            ]
        )

        self.terminal.process_command("test hello")  # Missing arg2
        self.assertIn("Missing required argument: arg2", self.terminal.terminal_lines[-1])

    def test_process_command_too_many_arguments(self):
        """Test processing a command with too many arguments."""

        def test_command(arg1: str, term: PygameTerminal):
            return f"Command executed with {arg1}"

        self.terminal.register_command(
            command_names=['test', 't'],
            command_function=test_command,
            argument_list=[
                Argument(name="arg1", type=str, is_optional=False)
            ]
        )

        self.terminal.process_command("test hello extra argument")
        self.assertIn("Too many arguments provided", self.terminal.terminal_lines[-1])

if __name__ == '__main__':
    pygame.init()  # Initialize Pygame for font loading
    unittest.main()