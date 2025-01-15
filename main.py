import argparse

from src.repl import start_repl


def main(args_input):
    start_repl(args_input)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Space Trader CLI Game')
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument('--skipc', action='store_true', help='Skip the character and ship customization')
    args = parser.parse_args()
    main(args)
