"""
Production stage system for the economy expansion.

This module implements the base production stage interface and utility methods
for calculating yields and quality in the resource production chain.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Tuple, Any


class ProductionResult(Enum):
    """Represents the result of a production process."""
    SUCCESS = auto()
    PARTIAL_SUCCESS = auto()
    FAILURE = auto()
    INSUFFICIENT_RESOURCES = auto()
    EQUIPMENT_FAILURE = auto()


@dataclass
class ProductionOutput:
    """
    Represents the output of a production process.
    
    Contains both the main products and waste products generated,
    along with metadata about the production process.
    """
    products: Dict[int, float]  # Resource ID to quantity mapping
    waste_products: Dict[int, float]  # Waste product ID to quantity mapping
    result: ProductionResult
    efficiency: float  # Actual efficiency achieved (0.0-1.0)
    quality_modifier: float  # Quality modifier applied to products (0.0-2.0)
    message: str = ""  # Optional message about the production process


class ProductionStage(ABC):
    """
    Base class for all production stages in the resource production chain.
    
    This abstract class defines the interface that all production stages must implement,
    providing common functionality for processing resources through the production chain.
    """
    
    def __init__(self, stage_name: str, base_efficiency: float = 1.0):
        """
        Initialize the production stage.
        
        Args:
            stage_name: Name of this production stage
            base_efficiency: Base efficiency of this stage (0.0-1.0)
        """
        self.stage_name = stage_name
        self.base_efficiency = max(0.0, min(base_efficiency, 1.0))
    
    @abstractmethod
    def process(
        self, 
        input_resources: Dict[int, float], 
        equipment_quality: float, 
        skills: Dict[str, float],
        batch_size: float = 1.0
    ) -> ProductionOutput:
        """
        Process input resources into output products and waste.
        
        Args:
            input_resources: Dictionary of resource IDs to quantities
            equipment_quality: Quality factor of the equipment (0.0-1.0)
            skills: Dictionary of relevant skill names to skill levels (0.0-1.0)
            batch_size: Size of the production batch (multiplier)
            
        Returns:
            ProductionOutput containing products, waste, and metadata
        """
        pass
    
    @abstractmethod
    def get_required_resources(self, output_quantity: float) -> Dict[int, float]:
        """
        Calculate the required input resources for a given output quantity.
        
        Args:
            output_quantity: Desired quantity of output
            
        Returns:
            Dictionary of resource IDs to required quantities
        """
        pass
    
    @abstractmethod
    def get_expected_output(self, input_resources: Dict[int, float]) -> Dict[int, float]:
        """
        Calculate the expected output for given input resources.
        
        Args:
            input_resources: Dictionary of resource IDs to quantities
            
        Returns:
            Dictionary of expected output resource IDs to quantities
        """
        pass
    
    def calculate_efficiency(
        self, 
        equipment_quality: float, 
        skills: Dict[str, float],
        batch_size: float = 1.0
    ) -> float:
        """
        Calculate the actual efficiency for this production process.
        
        Args:
            equipment_quality: Quality factor of the equipment (0.0-1.0)
            skills: Dictionary of relevant skill names to skill levels (0.0-1.0)
            batch_size: Size of the production batch
            
        Returns:
            Actual efficiency factor (0.0-1.0)
        """
        # Start with base efficiency
        efficiency = self.base_efficiency
        
        # Apply equipment quality modifier
        equipment_modifier = 0.5 + (equipment_quality * 0.5)  # 0.5 to 1.0 range
        efficiency *= equipment_modifier
        
        # Apply skill modifiers
        skill_modifier = self._calculate_skill_modifier(skills)
        efficiency *= skill_modifier
        
        # Apply batch size efficiency (larger batches are more efficient, up to a point)
        batch_modifier = self._calculate_batch_modifier(batch_size)
        efficiency *= batch_modifier
        
        # Ensure efficiency stays within bounds
        return max(0.0, min(efficiency, 1.0))
    
    def calculate_quality_modifier(
        self, 
        equipment_quality: float, 
        skills: Dict[str, float],
        input_quality: float = 1.0
    ) -> float:
        """
        Calculate the quality modifier for output products.
        
        Args:
            equipment_quality: Quality factor of the equipment (0.0-1.0)
            skills: Dictionary of relevant skill names to skill levels (0.0-1.0)
            input_quality: Quality of input materials (0.0-2.0)
            
        Returns:
            Quality modifier for output products (0.0-2.0)
        """
        # Base quality starts with input quality
        quality = input_quality
        
        # Equipment quality affects output quality
        equipment_factor = 0.8 + (equipment_quality * 0.4)  # 0.8 to 1.2 range
        quality *= equipment_factor
        
        # Skill affects quality
        skill_factor = self._calculate_skill_quality_factor(skills)
        quality *= skill_factor
        
        # Ensure quality stays within reasonable bounds
        return max(0.1, min(quality, 2.0))
    
    def calculate_waste_generation(
        self, 
        input_quantity: float, 
        efficiency: float,
        process_complexity: float = 1.0
    ) -> Dict[int, float]:
        """
        Calculate the waste products generated during production.
        
        Args:
            input_quantity: Total quantity of input materials
            efficiency: Actual efficiency of the process (0.0-1.0)
            process_complexity: Complexity of the process (affects waste generation)
            
        Returns:
            Dictionary of waste product IDs to quantities
        """
        # Base waste rate depends on efficiency - lower efficiency means more waste
        base_waste_rate = 0.1 + (0.2 * (1.0 - efficiency))  # 10% to 30% waste
        
        # Process complexity affects waste generation
        complexity_factor = 1.0 + (process_complexity - 1.0) * 0.1
        
        # Calculate total waste
        total_waste = input_quantity * base_waste_rate * complexity_factor
        
        # For now, return generic waste (ID 0)
        # This will be expanded in the waste management system
        return {0: round(total_waste, 3)} if total_waste > 0 else {}
    
    def _calculate_skill_modifier(self, skills: Dict[str, float]) -> float:
        """
        Calculate the skill modifier for efficiency.
        
        Args:
            skills: Dictionary of skill names to levels (0.0-1.0)
            
        Returns:
            Skill modifier for efficiency (0.5-1.2)
        """
        # Get relevant skills for this production stage
        relevant_skills = self._get_relevant_skills()
        
        if not relevant_skills:
            return 1.0
        
        # Calculate average skill level for relevant skills
        total_skill = 0.0
        skill_count = 0
        
        for skill_name in relevant_skills:
            if skill_name in skills:
                total_skill += skills[skill_name]
                skill_count += 1
        
        if skill_count == 0:
            return 0.8  # Penalty for no relevant skills
        
        average_skill = total_skill / skill_count
        
        # Convert skill level to modifier (0.5 to 1.2 range)
        return 0.5 + (average_skill * 0.7)
    
    def _calculate_skill_quality_factor(self, skills: Dict[str, float]) -> float:
        """
        Calculate the skill factor for quality.
        
        Args:
            skills: Dictionary of skill names to levels (0.0-1.0)
            
        Returns:
            Skill factor for quality (0.7-1.3)
        """
        # Get relevant skills for this production stage
        relevant_skills = self._get_relevant_skills()
        
        if not relevant_skills:
            return 1.0
        
        # Calculate average skill level for relevant skills
        total_skill = 0.0
        skill_count = 0
        
        for skill_name in relevant_skills:
            if skill_name in skills:
                total_skill += skills[skill_name]
                skill_count += 1
        
        if skill_count == 0:
            return 0.9  # Small penalty for no relevant skills
        
        average_skill = total_skill / skill_count
        
        # Convert skill level to quality factor (0.7 to 1.3 range)
        return 0.7 + (average_skill * 0.6)
    
    def _calculate_batch_modifier(self, batch_size: float) -> float:
        """
        Calculate the batch size modifier for efficiency.
        
        Args:
            batch_size: Size of the production batch
            
        Returns:
            Batch modifier for efficiency (0.8-1.1)
        """
        if batch_size <= 0:
            return 0.0
        
        # Optimal batch size is around 10 units
        optimal_size = 10.0
        
        if batch_size <= optimal_size:
            # Smaller batches are less efficient
            return 0.8 + (batch_size / optimal_size) * 0.2
        else:
            # Larger batches have diminishing returns
            excess = batch_size - optimal_size
            penalty = min(excess / optimal_size * 0.1, 0.1)  # Max 10% penalty
            return 1.1 - penalty
    
    def _get_relevant_skills(self) -> List[str]:
        """
        Get the list of skills relevant to this production stage.
        
        Returns:
            List of skill names that affect this production stage
        """
        # Base implementation returns common skills
        # Subclasses should override this to specify their relevant skills
        return ["engineering", "manufacturing"]
    
    def get_stage_info(self) -> Dict[str, Any]:
        """
        Get information about this production stage.
        
        Returns:
            Dictionary with stage information
        """
        return {
            "name": self.stage_name,
            "base_efficiency": self.base_efficiency,
            "relevant_skills": self._get_relevant_skills(),
            "description": self.__doc__ or "No description available"
        }
    
    def validate_input_resources(self, input_resources: Dict[int, float]) -> Tuple[bool, str]:
        """
        Validate that the input resources are valid for this production stage.
        
        Args:
            input_resources: Dictionary of resource IDs to quantities
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not input_resources:
            return False, "No input resources provided"
        
        for resource_id, quantity in input_resources.items():
            if not isinstance(resource_id, int):
                return False, f"Invalid resource ID type: {type(resource_id)}"
            
            if not isinstance(quantity, (int, float)):
                return False, f"Invalid quantity type for resource {resource_id}: {type(quantity)}"
            
            if quantity <= 0:
                return False, f"Invalid quantity for resource {resource_id}: {quantity}"
        
        return True, ""
    
    def estimate_production_time(
        self, 
        input_resources: Dict[int, float], 
        equipment_quality: float,
        skills: Dict[str, float]
    ) -> float:
        """
        Estimate the time required for production.
        
        Args:
            input_resources: Dictionary of resource IDs to quantities
            equipment_quality: Quality factor of the equipment (0.0-1.0)
            skills: Dictionary of skill names to levels (0.0-1.0)
            
        Returns:
            Estimated production time in hours
        """
        # Base time calculation (can be overridden by subclasses)
        total_input = sum(input_resources.values())
        base_time = total_input * 0.5  # 30 minutes per unit base time
        
        # Better equipment and skills reduce production time
        efficiency = self.calculate_efficiency(equipment_quality, skills)
        time_modifier = 2.0 - efficiency  # 1.0 to 2.0 range (inverted)
        
        return base_time * time_modifier