import argparse
from typing import Optional, Sequence

from src.repl import start_repl


def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Space Trader CLI Game")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    parser.add_argument("--mute", action="store_true", help="Mute game sounds")
    parser.add_argument(
        "--skipc", action="store_true", help="Skip character customization"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for procedural generation (uses current time if not provided)",
    )
    return parser.parse_args(argv)


def main(args: argparse.Namespace) -> None:
    """Start the game with the given arguments."""
    start_repl(args)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
