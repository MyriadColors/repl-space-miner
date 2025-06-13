from pygame import Vector2
from colorama import Fore, Style
from src.classes.game import Game
from .registry import Argument
from .base import register_command

# Type annotations for methods dynamically added to Ship class
# mypy: ignore-errors


def refuel_antimatter_command(game_state: Game, amount: float) -> None:
    """Handle refueling the ship with antimatter at a station."""
    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message(
            "Must be docked at a station to refuel with antimatter."
        )
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("Not docked at any station.")
        return

    # Calculate how much antimatter can be added
    max_antimatter = player_ship.max_antimatter - player_ship.antimatter
    if max_antimatter <= 0:
        game_state.ui.error_message(
            "Ship's antimatter containment is already at capacity."
        )
        return

    # Limit amount to what can be added
    amount = min(amount, max_antimatter)

    # Calculate cost (antimatter is much more expensive than regular fuel)
    antimatter_price = station.fuel_price * 10  # 10x regular fuel price
    total_cost = round(amount * antimatter_price, 2)
    player_character = game_state.get_player_character()
    if player_character is None:
        game_state.ui.error_message("Player character not found.")
        return

    if player_character.credits < total_cost:
        game_state.ui.error_message(f"Not enough credits. Cost: {total_cost} credits")
        return

    # Confirm purchase
    game_state.ui.info_message(
        f"Refueling {amount} g of antimatter will cost {total_cost} credits."
    )
    game_state.ui.warn_message(
        "WARNING: Antimatter requires constant power to maintain containment."
    )
    confirm = input("Confirm purchase? (y/n): ").lower()
    if confirm != "y":
        game_state.ui.info_message("Antimatter refueling cancelled.")
        return

    # Process refueling with proper credit management
    player_character.remove_credits(total_cost)
    player_ship.antimatter += amount

    game_state.ui.success_message(f"Successfully loaded {amount} g of antimatter.")
    game_state.ui.info_message(
        f"New antimatter level: {player_ship.antimatter}/{player_ship.max_antimatter} g"
    )
    game_state.ui.info_message(f"Remaining credits: {player_character.credits}")


def repair_containment_command(game_state: Game) -> None:
    """Repair the antimatter containment system."""
    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message(
            "Must be docked at a station to repair containment systems."
        )
        return

    station = player_ship.get_station_docked_at()
    if not station:
        game_state.ui.error_message("Not docked at any station.")
        return

    # Check if repairs are needed
    if player_ship.containment_integrity >= 99.0:
        game_state.ui.info_message(
            "Containment system is already at optimal integrity."
        )
        return

    # Calculate repair cost based on how much repair is needed
    repair_needed = 100.0 - player_ship.containment_integrity
    repair_cost = int(repair_needed * 1000)  # 1000 credits per 1% repair

    player_character = game_state.get_player_character()
    if player_character is None:
        game_state.ui.error_message("Player character not found.")
        return

    if player_character.credits < repair_cost:
        game_state.ui.error_message(
            f"Not enough credits. Repair cost: {repair_cost} credits"
        )
        return

    # Confirm repair
    game_state.ui.info_message(
        f"Repairing containment system to 100% will cost {repair_cost} credits."
    )
    game_state.ui.info_message(
        f"Current integrity: {player_ship.containment_integrity:.1f}%"
    )
    confirm = input("Confirm repair? (y/n): ").lower()

    if confirm != "y":
        game_state.ui.info_message("Containment repair cancelled.")
        return

    # Process repair
    player_character.remove_credits(repair_cost)
    player_ship.repair_containment(100.0 - player_ship.containment_integrity)

    game_state.ui.success_message("Containment system repaired to 100% integrity.")
    game_state.ui.info_message(f"Remaining credits: {player_character.credits}")


def emergency_ejection_command(game_state: Game) -> None:
    """Emergency procedure to eject all antimatter."""
    player_ship = game_state.get_player_ship()

    if player_ship.antimatter <= 0:
        game_state.ui.error_message("No antimatter to eject.")
        return

    # Warn about losing valuable antimatter
    game_state.ui.warn_message(
        "WARNING: Emergency ejection will discard all antimatter on board."
    )
    game_state.ui.warn_message(
        f"You will lose {player_ship.antimatter:.2f}g of antimatter worth approximately {int(player_ship.antimatter * 5000)} credits."
    )
    confirm = input("Confirm emergency ejection? (y/n): ").lower()

    if confirm != "y":
        game_state.ui.info_message("Ejection cancelled.")
        return

    # Second confirmation for safety
    confirm = input("ARE YOU SURE? This cannot be undone. (yes/no): ").lower()

    if confirm != "yes":
        game_state.ui.info_message("Ejection cancelled.")
        return

    # Process ejection
    if player_ship.emergency_antimatter_ejection():
        game_state.ui.success_message("Emergency antimatter ejection successful.")
        game_state.ui.success_message("Containment systems stabilized.")
    else:
        game_state.ui.error_message("Ejection failed. Contact system administrator.")


def ftl_jump_command(game_state: Game, destination: str) -> None:
    """Perform an FTL jump to another system using system name or index."""
    player_ship = game_state.get_player_ship()

    # Check if ship is docked
    if player_ship.is_docked:
        game_state.ui.error_message("Cannot initiate FTL jump while docked.")
        return

    # Try to parse the destination as an index first
    systems = game_state.solar_systems
    current_system_idx = game_state.current_solar_system_index
    current_system = game_state.get_current_solar_system()
    region = game_state.get_region()

    target_system = None
    target_idx = -1  # Initialize with invalid index

    # Check if destination is a system index
    try:
        idx = int(destination)
        if 0 <= idx < len(systems):
            target_system = systems[idx]
            target_idx = idx
        else:
            game_state.ui.error_message(f"Invalid system index: {destination}")
            return
    except ValueError:
        # If not an index, try to find system by name
        for idx, system in enumerate(systems):
            if system.name.lower() == destination.lower():
                target_system = system
                target_idx = idx
                break

        if target_system is None:
            game_state.ui.error_message(f"System '{destination}' not found.")
            return

    # Check if trying to jump to current system
    if target_idx == current_system_idx:
        game_state.ui.info_message("You are already in this system.")
        return

    # Calculate distance
    distance = region.calculate_distance(current_system.name, target_system.name)

    # Check antimatter levels
    required_antimatter = distance * player_ship.antimatter_consumption
    if player_ship.antimatter < required_antimatter:
        game_state.ui.error_message(
            f"Insufficient antimatter. Need {required_antimatter:.2f}g for this jump."
        )
        game_state.ui.info_message(
            f"Current antimatter level: {player_ship.antimatter:.2f}g"
        )
        return

    # Check containment integrity
    containment_ok, risk = player_ship.check_containment_status(game_state)
    if not containment_ok:
        game_state.ui.error_message(
            f"Antimatter containment unstable ({risk:.1f}% failure risk)."
        )
        game_state.ui.error_message("Repairs needed before FTL jump is safe.")
        return

    # Confirm jump
    game_state.ui.info_message(
        f"Preparing FTL jump to {target_system.name}, distance: {distance} light-years."
    )
    game_state.ui.info_message(
        f"This will consume {required_antimatter:.2f}g of antimatter."
    )
    confirm = input("Confirm FTL jump? (y/n): ").lower()

    if confirm != "y":
        game_state.ui.info_message("FTL jump cancelled.")
        return

    # Execute jump
    success, message = player_ship.ftl_jump(game_state, target_system.name, distance)

    game_state.ui.info_message(message)

    if success:
        # Update current system index and reset player position
        game_state.current_solar_system_index = target_idx
        player_ship.space_object.position = Vector2(0, 0)
        game_state.ui.success_message(
            f"Arrived in {target_system.name}. Ship position reset to system center."
        )
        current_system_name = game_state.get_current_solar_system().name
        game_state.ui.info_message(f"Current system: {current_system_name}")
        game_state.ui.info_message(
            f"Remaining antimatter: {player_ship.antimatter:.2f}g"
        )
    else:
        game_state.ui.error_message(f"FTL jump failed: {message}")


def list_systems_command(game_state: Game) -> None:
    """Lists all available solar systems with true distance and FTL cost."""
    systems = game_state.solar_systems
    current_system_idx = game_state.current_solar_system_index
    player_ship = game_state.get_player_ship()
    region = game_state.get_region()
    current_system = game_state.get_current_solar_system()

    if not systems:
        game_state.ui.warn_message("No solar systems found.")
        return

    # Pre-calculate all data for proper alignment
    system_data = []
    max_index_width = len(str(len(systems) - 1))
    max_name_width = 0
    max_cost_width = 0
    
    for idx, system in enumerate(systems):
        if idx == current_system_idx:
            marker = "(Current System)"
            ftl_cost_str = "N/A (Current)"
            distance_str = "-"
            cost_needed = 0.0
            can_reach = True  # Always can reach current system
            has_fuel = True
            distance_ly = 0.0  # Current system has 0 distance
        else:
            marker = ""
            distance_ly = region.calculate_distance(current_system.name, system.name)
            cost_needed = distance_ly * player_ship.antimatter_consumption
            distance_str = f"{distance_ly:.2f} LY"
            ftl_cost_str = f"{cost_needed:.2f}g (Distance: {distance_str})"
            
            # Determine reachability based on ship capabilities and fuel
            # Check if ship can theoretically reach (based on max antimatter capacity)
            max_possible_cost = distance_ly * player_ship.antimatter_consumption
            can_reach = max_possible_cost <= player_ship.max_antimatter
            
            # Check if ship has enough fuel currently
            has_fuel = cost_needed <= player_ship.antimatter
        
        # Calculate display name with marker
        display_name = f"{system.name} {marker}".strip()
        max_name_width = max(max_name_width, len(display_name))
        max_cost_width = max(max_cost_width, len(ftl_cost_str))
        system_data.append({
            'idx': idx,
            'name': display_name,
            'cost_str': ftl_cost_str,            'can_reach': can_reach,
            'has_fuel': has_fuel,
            'is_current': idx == current_system_idx,
            'distance_ly': distance_ly
        })

    # Sort systems by distance (current system first, then by proximity)
    system_data.sort(key=lambda x: (not x['is_current'], x['distance_ly']))

    game_state.ui.info_message("Available Solar Systems:")
    
    for data in system_data:
        # Format index with proper padding
        index_str = f"Index: {data['idx']:>{max_index_width}}"
        
        # Format name with proper padding
        name_str = f"Name: {data['name']:<{max_name_width}}"
        
        # Format cost with proper padding
        cost_str = f"FTL Cost: {data['cost_str']:<{max_cost_width}}"
        
        # Determine color for entire line based on reachability
        if data['is_current']:
            line_color = Fore.CYAN  # Current system - cyan
        elif not data['can_reach']:
            line_color = Fore.RED   # Cannot reach - red
        elif not data['has_fuel']:
            line_color = Fore.YELLOW  # Can reach but insufficient fuel - yellow
        else:
            line_color = Fore.GREEN  # Can reach with sufficient fuel - green
        
        # Create the formatted line with entire line colored
        line = f"{line_color}  {index_str} | {name_str} | {cost_str}{Style.RESET_ALL}"
        print(line)

    game_state.ui.info_message(
        "\nUse 'ftl <index>' or 'ftl <system_name>' to travel to another system."
    )


# Register commands
register_command(
    ["refuel_antimatter", "refa"],
    refuel_antimatter_command,
    [Argument("amount", float, False)],
)

register_command(
    ["repair_containment", "repc"],
    repair_containment_command,
    [],
)

register_command(
    ["eject_antimatter", "eject"],
    emergency_ejection_command,
    [],
)

register_command(
    ["ftl", "ftl_jump"],
    ftl_jump_command,
    [
        Argument("destination", str, False),
    ],
)

# Register system navigation commands
register_command(
    ["listsystems", "lsys"],
    list_systems_command,
    [],
)
