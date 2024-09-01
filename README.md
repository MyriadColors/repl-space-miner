# Space Miner

# Overview

**Space Miner** is a text-based space exploration and resource mining game. You command a spaceship, navigating through a procedurally generated solar system, mining asteroids, trading ores, and managing your resources to thrive in the harsh environment of space. 

Please note that this project is in a **very early stage** of development. Many features are missing or incomplete, and there may be bugs or unoptimized code.

# Installation

1. **Clone the repository:**
   For Linux or MacOs:
   ```bash
   git clone https://github.com/yourusername/space-miner.git && cd space-miner
   ```
   
   For Windows:
   ```powershell
   git clone https://github.com/yourusername/space-miner.git && cd space-miner
   ```

2. **Install the dependencies:**

   Make sure you have Python 3.x installed. Install the required dependencies using:

   ```bash
   pip install -r requirements.txt
   ```
   
   
3. **Run the game:**

   ```bash
   python main.py
   ```

## How to Play

Once you start the game, you’ll be greeted with a welcome message and a command prompt where you can type various commands to interact with the game world.

### Available Commands

- **help**: Displays a list of available commands.
- **travel (or move) [x y] or ['closest']**: Travel to the specified coordinates in the solar system.
- **mine [time]**: Mine for ores in the asteroid field at your current location for the specified time.
- **refuel [amount]**: Refuel your spaceship at a station.
- **status (or st)**: Displays the current status of your ship, including position, fuel, cargo, and credits.
- **scan [amount]**: Scans for nearby objects (asteroid fields or stations) within your current range.
- **dock (or do)**: Dock at a station if your are close enough to it.
- **undock (or ud)**: Undock from the station you are currently docked at.
- **quit (or q)**: Exit the game.

### Game Features

- **Exploration**: Navigate through a procedurally generated solar system with multiple asteroid fields and space stations.
- **Mining**: Extract valuable ores from asteroids, which can be sold at stations for credits.
- **Resource Management**: Manage your fuel, cargo space, and credits carefully to survive and progress.

### Future Development

Given the current state of the game, the following features could realistically be added as development progresses:

- **Combat**: Introduce space battles with pirates or other factions.
- **Economy**: Implement a dynamic market system where ore prices fluctuate based on supply and demand, influencing trading strategies.
- **Missions and Quests**: Add story-driven missions or random quests that provide rewards, such as rare ores or unique ship upgrades.
- **Ship Customization**: Allow players to upgrade and customize their ships with better engines, weapons, and larger cargo holds.
- **Space Exploration**: Introduce new space exploration mechanics, such as interstellar travel, planet landing, finding hidden secrets and so on.
## Contribution

Contributions are welcome! Feel free to submit issues and pull requests. Please ensure that any contributions align with the project's direction and follow the coding style of the existing codebase.

## Acknowledgements

- [Pygame](https://www.pygame.org/) for the sound and game management.
- Ukaer for helpful tips, suggestions and bugtesting.
---

This is just the beginning of what could become a more complex and engaging space exploration game. The current focus is on building a solid foundation, with more features and improvements to come as the project evolves.
