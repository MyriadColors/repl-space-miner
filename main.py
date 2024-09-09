from src.repl import start_repl
from pygame import mixer

def main():
    mixer.init()
    mixer.music.load("Decoherence.mp3")
    mixer.music.play(-1)
    start_repl()

if __name__ == "__main__":
    main()
