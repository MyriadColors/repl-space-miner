"""
Skill system implementation for REPL Space Miner.

This module provides classes for tracking and managing character skills,
including experience points, skill levels, and skill-based bonuses.
"""
from typing import Dict, List, Optional, Tuple
import math

# Constants for skill system
MAX_SKILL_LEVEL = 20  # Maximum level a skill can reach
BASE_XP_REQUIREMENT = 100  # Base XP needed for level 2
XP_SCALING_FACTOR = 1.5  # How much XP requirements increase per level


class Skill:
    """
    Represents a character skill with levels, experience points, and benefits.
    """
    
    def __init__(self, name: str, description: str, level: int = 1, xp: int = 0):
        """
        Initialize a skill with name, description, and optional starting level/XP.
        
        Args:
            name: The name of the skill (e.g., "Piloting", "Engineering")
            description: A short description of the skill and its benefits
            level: The starting level of the skill (default: 1)
            xp: The starting experience points (default: 0)
        """
        self.name = name
        self.description = description
        self._level = max(1, min(level, MAX_SKILL_LEVEL))  # Ensure level is between 1 and MAX_SKILL_LEVEL
        self._xp = xp
        
    @property
    def level(self) -> int:
        """Get the current skill level."""
        return self._level
        
    @property
    def xp(self) -> int:
        """Get the current experience points."""
        return self._xp
    
    def xp_for_next_level(self) -> int:
        """
        Calculate experience points required for the next level.
        
        Returns:
            int: XP required to reach the next level
        """
        if self._level >= MAX_SKILL_LEVEL:
            return 0  # Already at max level
        
        # Calculate XP requirement using a progressive scaling formula
        return int(BASE_XP_REQUIREMENT * (XP_SCALING_FACTOR ** (self._level - 1)))
    
    def xp_progress_percentage(self) -> float:
        """
        Calculate percentage progress to the next level.
        
        Returns:
            float: Percentage (0-100) progress towards next level
        """
        if self._level >= MAX_SKILL_LEVEL:
            return 100.0
            
        xp_for_current = self.xp_for_previous_level()
        xp_for_next = self.xp_for_next_level()
        xp_needed = xp_for_next - xp_for_current
        current_progress = self._xp - xp_for_current
        
        if xp_needed <= 0:  # Avoid division by zero
            return 100.0
            
        return min(100.0, (current_progress / xp_needed) * 100)
    
    def xp_for_previous_level(self) -> int:
        """
        Calculate experience points required for the current level.
        
        Returns:
            int: XP required to reach the current level
        """
        if self._level <= 1:
            return 0
            
        return int(BASE_XP_REQUIREMENT * (XP_SCALING_FACTOR ** (self._level - 2)))
    
    def add_xp(self, amount: int) -> Tuple[int, bool]:
        """
        Add experience points to the skill and check for level ups.
        
        Args:
            amount: Amount of XP to add
            
        Returns:
            Tuple[int, bool]: (new level, whether level up occurred)
        """
        if self._level >= MAX_SKILL_LEVEL:
            return self._level, False
            
        old_level = self._level
        self._xp += amount
        
        # Check for level ups
        while self._level < MAX_SKILL_LEVEL:
            xp_needed = self.xp_for_next_level()
            if self._xp >= self.xp_for_previous_level() + xp_needed:
                self._level += 1
            else:
                break
                
        return self._level, self._level > old_level
    
    def get_bonus_percentage(self) -> float:
        """
        Calculate the bonus percentage provided by this skill.
        
        Returns:
            float: Bonus percentage (e.g., 15.0 for 15% bonus)
        """
        # Level 1: 0% bonus (baseline)
        # Each level adds 3% bonus, so level 10 would be 27% bonus
        return (self._level - 1) * 3.0
    
    def to_dict(self) -> Dict:
        """
        Convert skill to dictionary for serialization.
        
        Returns:
            Dict: Dictionary representation of the skill
        """
        return {
            "name": self.name,
            "description": self.description,
            "level": self._level,
            "xp": self._xp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Skill':
        """
        Create skill from dictionary representation.
        
        Args:
            data: Dictionary containing skill data
            
        Returns:
            Skill: New skill instance
        """
        return cls(
            name=data.get("name", "Unknown"),
            description=data.get("description", ""),
            level=data.get("level", 1),
            xp=data.get("xp", 0)
        )


class SkillSystem:
    """
    System for managing multiple skills, skill points, and progression.
    """
    
    # Skill definitions with descriptions
    SKILL_DEFINITIONS = {
        "piloting": "Spacecraft handling and navigation. Improves fuel efficiency and travel speed.",
        "engineering": "Technical expertise. Boosts mining yield, repair effectiveness, and module efficiency.",
        "combat": "Combat proficiency. Enhances damage output, evasion, and tactical options.",
        "education": "Knowledge and research ability. Improves analysis, unlocks advanced templates, and enhances information gathering.",
        "charisma": "Social influence. Boosts trading prices, faction relationship gains, and negotiation outcomes."
    }
    
    def __init__(self):
        """Initialize the skill system with default skills."""
        self.skills: Dict[str, Skill] = {}
        self.unspent_skill_points = 0
        
        # Initialize standard skills at level 1
        for skill_name, description in self.SKILL_DEFINITIONS.items():
            self.skills[skill_name] = Skill(skill_name, description)
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        Get a skill by name.
        
        Args:
            skill_name: Name of the skill to retrieve
            
        Returns:
            Optional[Skill]: The skill object if found, None otherwise
        """
        return self.skills.get(skill_name.lower())
    
    def add_xp(self, skill_name: str, amount: int) -> Tuple[int, bool]:
        """
        Add experience to a specific skill.
        
        Args:
            skill_name: Name of the skill to add XP to
            amount: Amount of XP to add
            
        Returns:
            Tuple[int, bool]: (new level, whether level up occurred)
        """
        skill = self.get_skill(skill_name.lower())
        if not skill:
            return 0, False
            
        return skill.add_xp(amount)
    
    def add_skill_points(self, points: int) -> int:
        """
        Add unspent skill points to the character.
        
        Args:
            points: Number of skill points to add
            
        Returns:
            int: New total of unspent skill points
        """
        self.unspent_skill_points += points
        return self.unspent_skill_points
    
    def spend_skill_point(self, skill_name: str) -> bool:
        """
        Spend a skill point to level up a skill directly.
        
        Args:
            skill_name: Name of the skill to level up
            
        Returns:
            bool: True if successful, False if not enough points or invalid skill
        """
        if self.unspent_skill_points <= 0:
            return False
            
        skill = self.get_skill(skill_name.lower())
        if not skill:
            return False
            
        if skill.level >= MAX_SKILL_LEVEL:
            return False
            
        # Level up and deduct a skill point
        old_level = skill.level
        # Directly modify the private attribute to avoid XP requirements
        skill._level += 1
        self.unspent_skill_points -= 1
        
        return skill.level > old_level
    
    def to_dict(self) -> Dict:
        """
        Convert skill system to dictionary for serialization.
        
        Returns:
            Dict: Dictionary representation of the skill system
        """
        return {
            "skills": {name: skill.to_dict() for name, skill in self.skills.items()},
            "unspent_skill_points": self.unspent_skill_points
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SkillSystem':
        """
        Create skill system from dictionary representation.
        
        Args:
            data: Dictionary containing skill system data
            
        Returns:
            SkillSystem: New skill system instance
        """
        system = cls()
        
        # Load unspent skill points
        system.unspent_skill_points = data.get("unspent_skill_points", 0)
        
        # Load skills
        skills_data = data.get("skills", {})
        for skill_name, skill_data in skills_data.items():
            system.skills[skill_name] = Skill.from_dict(skill_data)
            
        return system
