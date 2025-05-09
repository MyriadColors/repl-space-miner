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


def ftl_jump_command(game_state: Game, destination: str, distance: float) -> None:
    """Perform an FTL jump to another system."""
    player_ship = game_state.get_player_ship()

    # Check if ship is docked
    if player_ship.is_docked:
        game_state.ui.error_message("Cannot initiate FTL jump while docked.")
        return

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
        f"Preparing FTL jump to {destination}, distance: {distance} light-years."
    )
    game_state.ui.info_message(
        f"This will consume {required_antimatter:.2f}g of antimatter."
    )
    confirm = input("Confirm FTL jump? (y/n): ").lower()

    if confirm != "y":
        game_state.ui.info_message("FTL jump cancelled.")
        return

    # Execute jump
    success, message = player_ship.ftl_jump(game_state, destination, distance)

    if success:
        game_state.ui.success_message(message)
        game_state.ui.info_message(
            f"Remaining antimatter: {player_ship.antimatter:.2f}g"
        )
    else:
        game_state.ui.error_message(f"FTL jump failed: {message}")


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
    ["ftl_jump", "ftl"],
    ftl_jump_command,
    [
        Argument("destination", str, False),
        Argument("distance", float, False),
    ],
)
