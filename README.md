# Space Miner

## Overview

**Space Miner** is a text-based space exploration and resource mining game built using Pygame. You command a spaceship, navigating a procedurally generated solar system. Mine asteroids, trade ores at space stations, and manage your resources to succeed in the depths of space!

**Current State:** This project is in active development. Here's what's working:

- **Character Creation:** Create a unique character with different backgrounds and personality traits that affect gameplay mechanics.
- **RPG Elements:** Character stats (perception, resilience, intellect, etc.) and skills (piloting, engineering, combat, etc.) that influence gameplay.
- **Banking System:** Manage your finances with savings accounts, debt, and interest calculations.
- **FTL Travel:** Use antimatter fuel for faster-than-light travel between star systems with containment mechanics. (Still need to add more solar systems)
- **Ship Upgrades:** Enhance your vessel with various upgrades for mining, speed, cargo capacity, and more.
- **Basic Gameplay Loop:** Mine asteroids, travel to stations, dock, refuel, buy, and sell ores.
- **Command-Line Interface:** Interact with the game using a simulated terminal within Pygame.
- **Procedural Generation:** The solar system, asteroid fields, and stations are procedurally generated.

## Note

The lore is not yet defined, and the game is still in development. The current focus is on building a solid foundation for the gameplay mechanics, so the specifics of locations, people and important events are not yet defined and will be changed throughout the development process.

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

Space Miner is played through a command-line interface. Type commands to navigate, mine resources, trade goods, and manage your ship.

### Getting Started

1. Type `help` to see all available commands
2. Use `status` or `st` to check your ship's current condition, cargo, and credits
3. Type `scan` or `sc` to scan your surroundings for stations and asteroid fields
4. Begin by traveling to an asteroid field with `travel closest field`

### Basic Gameplay Loop

#### Navigation

- `travel closest field` or `tr closest field`: Travel to the nearest asteroid field
- `travel closest station` or `tr closest station`: Travel to the nearest space station
- `direct_travel x y` or `dtr x y`: Travel directly to specific coordinates
- `scan` or `sc`: View nearby objects in the system
- `scan_field` or `scf`: When in an asteroid field, show available ores

#### Mining

- `mine 60` or `m 60`: Mine for 60 seconds
- `mine 30 true`: Mine for 30 seconds or until cargo hold is full (whichever comes first)
- `mine 60 false Pyrogen`: Mine specifically for Pyrogen ore for 60 seconds

#### Station Interactions

- `dock` or `do`: Dock at a nearby station
- `undock` or `ud`: Undock from current station
- `buy Pyrogen 10` or `by Pyrogen 10`: Buy 10 units of Pyrogen ore (while docked)
- `sell` or `sl`: Sell ores to the station (while docked)
- `refuel 50` or `ref 50`: Refuel your ship with 50 units of fuel (while docked)

#### Financial Management

- `bank`: Access banking services (while docked)
- `character` or `char`: View your character sheet and skills

#### System Commands

- `status` or `st`: Display your ship's status, cargo, and current time
- `save filename`: Save your game
- `load filename`: Load a saved game
- `clear` or `cl`: Clear the terminal screen
- `exit`: Exit the game

### Tips for Success

- Keep an eye on your fuel levels - running out will strand your ship!
- Different asteroid fields contain different ores - scan before mining
- Station prices vary - look for the best deals before selling
- Manage your debt carefully - high interest can accumulate quickly
- Upgrade your ship when possible to increase mining efficiency and cargo space

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgements

- Pygame: [https://www.pygame.org/](Pygame)
- Ukaer for his useful comments and suggestions
- Music: "Decoherence" by Scott Buckley (CC-BY 4.0) [https://www.scottbuckley.com.au](https://www.scottbuckley.com.au)
