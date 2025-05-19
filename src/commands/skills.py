"""
Skill management commands for REPL Space Miner.

This module provides commands for viewing and managing character skills.
"""
from src.classes.game import Game
from src.commands.base import register_command
from src.commands.registry import Argument

def skills_command(game_state: Game, args=None) -> None:
    """
    Display detailed skill information and allow skill point spending.
    
    Args:
        game_state: The current game state
        args: Optional arguments list: [skill_name] to view specific skill, 
              or [spend, skill_name] to spend skill points
    """
    character = game_state.get_player_character()
    if not character:
        game_state.ui.error_message("Error: Player character not found.")
        return
    
    # Access skill system
    skill_system = character.skill_system
    
    # If no arguments, display all skills
    if not args or len(args) == 0:
        display_all_skills(game_state, skill_system)
        return
    
    # Handle specific commands
    if args[0].lower() == "spend":
        if len(args) < 2:
            game_state.ui.warn_message("Please specify a skill to spend points on.")
            game_state.ui.info_message("Usage: skills spend [skill_name]")
            return
            
        skill_name = args[1].lower()
        spend_skill_point(game_state, skill_system, skill_name)
    else:
        # View a specific skill
        skill_name = args[0].lower()
        display_skill_detail(game_state, skill_system, skill_name)

def display_all_skills(game_state: Game, skill_system) -> None:
    """Display all skills with their current levels."""
    game_state.ui.info_message("\n=== Character Skills ===")
    
    # Unspent skill points
    game_state.ui.info_message(f"Unspent Skill Points: {skill_system.unspent_skill_points}")
    
    # Display all skills
    for skill_name, skill in skill_system.skills.items():
        progress = skill.xp_progress_percentage()
        progress_bar = generate_progress_bar(progress)
        
        game_state.ui.info_message(
            f"{skill_name.capitalize()} (Level {skill.level}): {progress_bar} {progress:.1f}%"
        )
    
    # Command help
    game_state.ui.info_message("\nUse 'skills [skill_name]' to view details for a specific skill.")
    game_state.ui.info_message("Use 'skills spend [skill_name]' to spend skill points.")

def display_skill_detail(game_state: Game, skill_system, skill_name: str) -> None:
    """Display detailed information about a specific skill."""
    skill = skill_system.get_skill(skill_name)
    if not skill:
        game_state.ui.error_message(f"Skill '{skill_name}' not found.")
        return
    
    progress = skill.xp_progress_percentage()
    progress_bar = generate_progress_bar(progress)
    bonus = skill.get_bonus_percentage()
    
    game_state.ui.info_message(f"\n=== {skill_name.capitalize()} Skill ===")
    game_state.ui.info_message(f"Level: {skill.level}")
    game_state.ui.info_message(f"Description: {skill.description}")
    game_state.ui.info_message(f"XP: {skill.xp} / {skill.xp_for_previous_level() + skill.xp_for_next_level()}")
    game_state.ui.info_message(f"Progress: {progress_bar} {progress:.1f}%")
    game_state.ui.info_message(f"Current Bonus: +{bonus:.1f}%")
    
    # Help for spending points
    if skill_system.unspent_skill_points > 0:
        game_state.ui.info_message(f"\nYou have {skill_system.unspent_skill_points} unspent skill points.")
        game_state.ui.info_message(f"Type 'skills spend {skill_name}' to level up this skill.")

def spend_skill_point(game_state: Game, skill_system, skill_name: str) -> None:
    """Spend a skill point to level up a skill."""
    if skill_system.unspent_skill_points <= 0:
        game_state.ui.error_message("You don't have any skill points to spend.")
        return
        
    skill = skill_system.get_skill(skill_name)
    if not skill:
        game_state.ui.error_message(f"Skill '{skill_name}' not found.")
        return
    
    # Try to spend the point
    success = skill_system.spend_skill_point(skill_name)
    if success:
        game_state.ui.success_message(f"Successfully improved {skill_name.capitalize()} to level {skill.level}!")
        game_state.ui.info_message(f"Remaining skill points: {skill_system.unspent_skill_points}")
    else:
        if skill.level >= 20:  # MAX_SKILL_LEVEL from skill_system
            game_state.ui.error_message(f"{skill_name.capitalize()} is already at maximum level ({skill.level}).")
        else:
            game_state.ui.error_message(f"Failed to spend skill point on {skill_name}.")

def generate_progress_bar(percentage: float, width: int = 20) -> str:
    """Generate a text-based progress bar."""
    filled_width = int(width * percentage / 100)
    bar = "█" * filled_width + "░" * (width - filled_width)
    return f"[{bar}]"

# Register skill commands
def register_skill_commands():
    register_command(
        ["skills", "skill", "sk"],
        skills_command,
        [Argument("args", list, True)]
    )
