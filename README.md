# Space Miner

## Overview

**Space Miner** is a text-based space exploration and resource mining game built using Pygame. You command a spaceship, navigating a procedurally generated solar system. Mine asteroids, trade ores at space stations, and manage your resources to succeed in the depths of space!

**Current State:** This project is in its **early stages**.  Here's what's working:

- **Basic Gameplay Loop:** You can mine, travel to stations, dock, refuel, buy, and sell ores.
- **Command-Line Interface:** Interact with the game using a simulated terminal within Pygame.
- **Procedural Generation:** The solar system, asteroid fields, and stations are procedurally generated.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MyriadColors/space-miner.git && cd repl-space-miner
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game:**
   ```bash
   python main.py
   ```

## How to Play

Use the command prompt to interact with the game. Type `help` to see a list of available commands.

**Example Commands:**

- `travel closest field`: Travel to the nearest asteroid field.
- `mine 60`: Mine for 60 seconds at your current location.
- `dock`: Dock at the nearest station (if in range).
- `buy Pyrogen 10`: Buy 10 units of Pyrogen ore from the station.
- `status`: View your ship's status, credits, and time.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgements

- Pygame: https://www.pygame.org/
- Ukaer for his useful comments and suggestions
- Music: "Decoherence" by Scott Buckley (CC-BY 4.0) - www.scottbuckley.com.au 