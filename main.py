import argparse
from src.repl import start_repl
from pygame import mixer

def main(args_input):
    mixer.init()
    mixer.music.load("Decoherence.mp3")
    if not args_input.mute:
        mixer.music.play(-1)
    start_repl()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Space Trader CLI Game')
    parser.add_argument('--mute', action='store_true', help='Mute the music')
    args = parser.parse_args()
    main(args)
