"""
Events to handle skill experience and progression.

This module provides functions for handling skill XP gain during gameplay events.
"""
from src.classes.game import Game
import random
from typing import Dict, Tuple, List

def process_skill_xp_from_activity(
    game_state: Game, activity: str, difficulty: float = 1.0
) -> Dict[str, Tuple[int, int, bool]]:
    """
    Process skill experience gain from a game activity.
    
    Args:
        game_state: The current game state
        activity: The type of activity ("mining", "trading", "combat", "navigation", etc.)
        difficulty: Multiplier for XP based on difficulty (default: 1.0)
        
    Returns:
        Dict mapping skill names to tuples of (xp_gained, new_level, leveled_up)
    """
    if not game_state.player_character:
        return {}
    
    character = game_state.player_character
    skill_system = character.skill_system
    results = {}
    
    # Base XP values for different activities
    xp_values = {
        "mining": {"engineering": 10, "education": 5},
        "trading": {"charisma": 10, "education": 5},
        "combat": {"combat": 15, "piloting": 5},
        "navigation": {"piloting": 10},
        "research": {"education": 15},
        "negotiation": {"charisma": 15},
        "repair": {"engineering": 15},
        "scan": {"education": 7, "engineering": 3},
        "dock": {"piloting": 5},
        "refuel": {"engineering": 3},
        "ftl_jump": {"piloting": 15, "engineering": 10},
    }
    
    # Get relevant XP values for this activity
    activity_xp = xp_values.get(activity, {})
    
    if not activity_xp:
        # If activity not recognized, give small random XP to a random skill
        skill_names = list(skill_system.skills.keys())
        random_skill = random.choice(skill_names)
        activity_xp = {random_skill: random.randint(1, 5)}
    
    # Calculate actual XP based on difficulty
    for skill_name, base_xp in activity_xp.items():
        # Add some randomness to XP gain
        variation = random.uniform(0.8, 1.2)
        xp_to_add = max(1, int(base_xp * difficulty * variation))
        
        # Add XP to the skill
        new_level, leveled_up = skill_system.add_xp(skill_name, xp_to_add)
        
        # Record results
        results[skill_name] = (xp_to_add, new_level, leveled_up)
        
        # If character leveled up, award a skill point
        if leveled_up:
            skill_system.add_skill_points(1)
    
    return results

def notify_skill_progress(game_state: Game, skill_results: Dict[str, Tuple[int, int, bool]]) -> None:
    """
    Notify the player about skill progress.
    
    Args:
        game_state: The current game state
        skill_results: Results from process_skill_xp_from_activity
    """
    if not skill_results:
        return
        
    # Show notifications for XP gains and level ups
    for skill_name, (xp_gained, new_level, leveled_up) in skill_results.items():
        skill_display_name = skill_name.capitalize()
        
        if leveled_up:
            # Level up notification (more prominent)
            game_state.ui.success_message(
                f"Level Up! {skill_display_name} skill increased to level {new_level}!"
            )
            game_state.ui.info_message("You gained 1 skill point!")
        elif xp_gained > 0:
            # Regular XP gain (less prominent)
            game_state.ui.info_message(
                f"Gained {xp_gained} XP in {skill_display_name} skill."
            )
