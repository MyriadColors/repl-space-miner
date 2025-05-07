from typing import Optional, Dict, List
from src.classes.game import Game
from src.data import UPGRADES, UpgradeCategory, Upgrade
from .registry import Argument
from .base import register_command


def upgrade_command(game_state: Game, args: Optional[List[str]] = None) -> None:
    """
    Allow purchasing upgrades for the player's ship when docked at a station.
    
    Args:
        game_state: The game state object
        args: Command arguments (optional)
            - list: Show list of available upgrades
            - <upgrade_id>: Purchase a specific upgrade
    """
    player_ship = game_state.get_player_ship()
    if not player_ship.is_docked:
        game_state.ui.error_message("You need to be docked at a station to purchase ship upgrades.")
        return
    
    # List all available upgrades
    if not args or args[0] == "list":
        available_upgrades = player_ship.get_available_upgrades()
        
        if not available_upgrades:
            game_state.ui.warn_message("No upgrades available for your ship at this time.")
            return
        
        game_state.ui.info_message("=== AVAILABLE SHIP UPGRADES ===")
        game_state.ui.info_message(f"Credits available: {game_state.get_credits():.2f}")
        game_state.ui.info_message("\n")
        
        # Group upgrades by category for better presentation
        by_category: Dict[str, List[Upgrade]] = {}
        for upgrade in available_upgrades:
            category = upgrade.category.name
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(upgrade)
        
        for category, upgrades in by_category.items():
            game_state.ui.info_message(f"--- {category} UPGRADES ---")
            for upgrade in upgrades:
                level_info = ""
                current_level = 1
                if upgrade.id in player_ship.applied_upgrades:
                    current_level = player_ship.applied_upgrades[upgrade.id].level
                    level_info = f" (Current: Level {current_level}/{upgrade.max_level})"
                
                price = upgrade.get_next_level_price() if current_level > 1 else upgrade.price
                game_state.ui.info_message(f"{upgrade.id}: {upgrade.name}{level_info} - {price:.2f} credits")
                game_state.ui.info_message(f"  {upgrade.description}")
                
                # Show preview of effects
                preview = player_ship.get_upgrade_effect_preview(upgrade)
                if preview["attribute"] == "fuel_consumption":
                    game_state.ui.info_message(f"  Effect: {preview['attribute']} {preview['before']:.5f} -> {preview['after']:.5f}")
                else:
                    game_state.ui.info_message(f"  Effect: {preview['attribute']} {preview['before']:.2f} -> {preview['after']:.2f}")
                game_state.ui.info_message("")
        
        game_state.ui.info_message("To purchase an upgrade, use: upgrade <upgrade_id>")
        return
    
    # Purchase a specific upgrade
    upgrade_id = args[0]
    if upgrade_id not in UPGRADES:
        game_state.ui.error_message(f"Unknown upgrade: {upgrade_id}")
        game_state.ui.info_message("Use 'upgrade list' to see available upgrades.")
        return
    
    # Check if upgrade can be applied
    if not player_ship.can_apply_upgrade(upgrade_id):
        # Check if it's due to max level
        if upgrade_id in player_ship.applied_upgrades:
            if player_ship.applied_upgrades[upgrade_id].level >= UPGRADES[upgrade_id].max_level:
                game_state.ui.error_message(f"You've already reached the maximum level for {UPGRADES[upgrade_id].name}.")
                return
        
        # Check for prerequisites
        upgrade = UPGRADES[upgrade_id]
        if upgrade.prerequisites is not None:
            missing = [prereq_id for prereq_id in upgrade.prerequisites 
                      if prereq_id not in player_ship.applied_upgrades]
            if missing:
                prereq_names = [UPGRADES[m].name for m in missing]
                game_state.ui.error_message(f"You need the following upgrades first: {', '.join(prereq_names)}")
                return
        
        game_state.ui.error_message("This upgrade cannot be applied to your ship right now.")
        return
    
    # Calculate price
    base_price = UPGRADES[upgrade_id].price
    current_level = 1
    if upgrade_id in player_ship.applied_upgrades:
        current_level = player_ship.applied_upgrades[upgrade_id].level
    
    price = base_price
    if current_level > 1:
        price = UPGRADES[upgrade_id].get_next_level_price()
    
    # Check if player can afford it
    player_credits = game_state.get_credits()
    if player_credits is None:
        game_state.ui.error_message("Error: Unable to get player credits.")
        return
        
    if player_credits < price:
        game_state.ui.error_message(f"You don't have enough credits. The upgrade costs {price:.2f} credits.")
        return
    
    # Confirm purchase
    upgrade = UPGRADES[upgrade_id]
    preview = player_ship.get_upgrade_effect_preview(upgrade)
    
    game_state.ui.info_message(f"Purchase {upgrade.name} for {price:.2f} credits?")
    game_state.ui.info_message(f"Effect: {preview['attribute']} {preview['before']:.5f} -> {preview['after']:.5f}")
    
    response = input("Confirm (y/n): ")
    if response.lower() != "y":
        game_state.ui.info_message("Purchase cancelled.")
        return
    
    # Apply upgrade and deduct credits
    result = player_ship.apply_upgrade(upgrade)
    if result:
        if game_state.player_character is None:
            game_state.ui.error_message("Error: Player character not found.")
            return
            
        game_state.player_character.credits -= price
        
        # Show success message
        level_str = ""
        if upgrade_id in player_ship.applied_upgrades:
            level = player_ship.applied_upgrades[upgrade_id].level
            if level > 1:
                level_str = f" (Level {level})"
        
        game_state.ui.success_message(f"Successfully installed {upgrade.name}{level_str}!")
        game_state.ui.info_message(f"Credits remaining: {game_state.get_credits():.2f}")
    else:
        game_state.ui.error_message("Failed to apply upgrade. Please report this as a bug.")


# Register upgrade command
register_command(
    ["upgrade", "upg"],
    upgrade_command,
    [Argument("args", list, True)],
) 