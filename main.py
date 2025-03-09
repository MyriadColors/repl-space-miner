import argparse
from typing import Optional, Sequence

from src.repl import start_repl

def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Space Trader CLI Game')
    return parser.parse_args(argv)

def main(args: argparse.Namespace) -> None:
    """Start the game with the given arguments."""
    start_repl()

if __name__ == "__main__":
    args = parse_arguments()
    main(args)