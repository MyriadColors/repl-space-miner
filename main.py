from game import Game
from helpers import take_input
from repl import start_repl
from command_handlers import display_welcome_message
from pygame import mixer


def main():
    mixer.init()
    mixer.music.load("Decoherence.mp3")
    mixer.music.play(-1)
    display_welcome_message()
    ship_name = take_input("Enter your ship name: ").strip()
    game = Game(ship_name)
    start_repl(game)

if __name__ == "__main__":
    main()
