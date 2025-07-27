"""
Refining stage implementation for the production chain system.

This module implements the RefiningStage class that converts raw ores into minerals,
taking into account ore purity, skill effects, and equipment quality.
"""

from typing import Any, Dict, List, Optional

from src.classes.production_stage import ProductionStage, ProductionOutput, ProductionResult
from src.classes.ore import Ore, PurityLevel, ORES
from src.classes.mineral import MINERALS


class RefiningStage(ProductionStage):
    """
    Production stage that converts raw ores into refined minerals.
    
    The refining process takes ore purity, equipment quality, and operator skills
    into account to determine yield, quality, and waste generation.
    """
    
    def __init__(self):
        """Initialize the refining stage."""
        super().__init__("Ore Refining", base_efficiency=0.75)
    
    def process(
        self, 
        input_resources: Dict[int, float], 
        equipment_quality: float, 
        skills: Dict[str, float],
        batch_size: float = 1.0
    ) -> ProductionOutput:
        """
        Process ores into minerals.
        
        Args:
            input_resources: Dictionary of ore IDs to quantities
            equipment_quality: Quality factor of the refining equipment (0.0-1.0)
            skills: Dictionary of skill names to levels (0.0-1.0)
            batch_size: Size of the production batch
            
        Returns:
            ProductionOutput containing refined minerals and waste products
        """
        # Validate input resources
        is_valid, error_msg = self.validate_input_resources(input_resources)
        if not is_valid:
            return ProductionOutput(
                products={},
                waste_products={},
                result=ProductionResult.INSUFFICIENT_RESOURCES,
                efficiency=0.0,
                quality_modifier=0.0,
                message=f"Invalid input: {error_msg}"
            )
        
        # Calculate process efficiency
        efficiency = self.calculate_efficiency(equipment_quality, skills, batch_size)
        
        # Calculate quality modifier for output minerals
        quality_modifier = self.calculate_quality_modifier(equipment_quality, skills)
        
        # Process each ore type
        total_products: Dict[int, float] = {}
        total_waste: Dict[int, float] = {}
        total_input_quantity = 0.0
        processed_ores = []
        
        for ore_id, quantity in input_resources.items():
            if ore_id not in ORES:
                continue  # Skip unknown ores
            
            ore = ORES[ore_id]
            total_input_quantity += quantity
            
            # Get mineral yields for this ore
            mineral_yields = ore.get_mineral_yield()
            
            # Apply purity effects to yields
            purity_modifier = self._get_purity_modifier(ore.purity)
            
            # Process each mineral yield
            for mineral_id, base_yield in mineral_yields.items():
                if mineral_id not in MINERALS:
                    continue  # Skip unknown minerals
                
                # Calculate actual yield
                actual_yield = base_yield * quantity * efficiency * purity_modifier
                
                if actual_yield > 0:
                    if mineral_id in total_products:
                        total_products[mineral_id] += actual_yield
                    else:
                        total_products[mineral_id] = actual_yield
            
            # Calculate waste products for this ore
            ore_waste = self._calculate_ore_waste(ore, quantity, efficiency)
            for waste_id, waste_quantity in ore_waste.items():
                if waste_id in total_waste:
                    total_waste[waste_id] += waste_quantity
                else:
                    total_waste[waste_id] = waste_quantity
            
            processed_ores.append(ore.name)
        
        # Round all quantities to reasonable precision
        total_products = {k: round(v, 3) for k, v in total_products.items()}
        total_waste = {k: round(v, 3) for k, v in total_waste.items()}
        
        # Determine result status
        if not total_products:
            result = ProductionResult.FAILURE
            message = "No minerals produced from input ores"
        elif efficiency < 0.5:
            result = ProductionResult.PARTIAL_SUCCESS
            message = f"Low efficiency refining of {', '.join(processed_ores)}"
        else:
            result = ProductionResult.SUCCESS
            message = f"Successfully refined {', '.join(processed_ores)}"
        
        return ProductionOutput(
            products=total_products,
            waste_products=total_waste,
            result=result,
            efficiency=efficiency,
            quality_modifier=quality_modifier,
            message=message
        )
    
    def get_required_resources(self, output_quantity: float) -> Dict[int, float]:
        """
        Calculate the required ore inputs for a given mineral output quantity.
        
        This is a simplified calculation that assumes average ore composition.
        
        Args:
            output_quantity: Desired quantity of mineral output
            
        Returns:
            Dictionary of ore IDs to required quantities
        """
        # This is a simplified implementation
        # In practice, you'd need to specify which minerals you want to produce
        
        # For now, return a basic ore requirement
        # Assuming average efficiency and yield
        average_efficiency = 0.6
        average_yield = 0.5
        
        required_ore_quantity = output_quantity / (average_efficiency * average_yield)
        
        # Return the most common ore (Pyrogen)
        return {0: round(required_ore_quantity, 3)}
    
    def get_expected_output(self, input_resources: Dict[int, float]) -> Dict[int, float]:
        """
        Calculate the expected mineral output for given ore inputs.
        
        Args:
            input_resources: Dictionary of ore IDs to quantities
            
        Returns:
            Dictionary of expected mineral IDs to quantities
        """
        expected_output: Dict[int, float] = {}
        
        # Use average efficiency for estimation
        average_efficiency = 0.6
        
        for ore_id, quantity in input_resources.items():
            if ore_id not in ORES:
                continue
            
            ore = ORES[ore_id]
            mineral_yields = ore.get_mineral_yield()
            purity_modifier = self._get_purity_modifier(ore.purity)
            
            for mineral_id, base_yield in mineral_yields.items():
                expected_yield = base_yield * quantity * average_efficiency * purity_modifier
                
                if mineral_id in expected_output:
                    expected_output[mineral_id] += expected_yield
                else:
                    expected_output[mineral_id] = expected_yield
        
        return {k: round(v, 3) for k, v in expected_output.items()}
    
    def _get_purity_modifier(self, purity: PurityLevel) -> float:
        """
        Get the yield modifier based on ore purity.
        
        Args:
            purity: Purity level of the ore
            
        Returns:
            Yield modifier (0.5-1.2)
        """
        purity_modifiers = {
            PurityLevel.RAW: 0.5,      # 50% yield
            PurityLevel.LOW: 0.65,     # 65% yield
            PurityLevel.MEDIUM: 0.8,   # 80% yield
            PurityLevel.HIGH: 1.0,     # 100% yield
            PurityLevel.ULTRA: 1.2,    # 120% yield (bonus for ultra-pure)
        }
        
        return purity_modifiers.get(purity, 0.6)
    
    def _calculate_ore_waste(self, ore: Ore, quantity: float, efficiency: float) -> Dict[int, float]:
        """
        Calculate waste products generated from refining a specific ore.
        
        Args:
            ore: The ore being refined
            quantity: Quantity of ore being processed
            efficiency: Process efficiency (0.0-1.0)
            
        Returns:
            Dictionary of waste product IDs to quantities
        """
        # Base waste generation from the ore
        ore_waste = ore.get_waste_products()
        
        # Apply quantity scaling
        scaled_waste = {}
        for waste_id, waste_rate in ore_waste.items():
            waste_quantity = waste_rate * quantity
            
            # Efficiency affects waste generation - lower efficiency means more waste
            efficiency_factor = 1.5 - (efficiency * 0.5)  # 1.0 to 1.5 range
            waste_quantity *= efficiency_factor
            
            # Ore refining difficulty affects waste generation
            difficulty_factor = 1.0 + (ore.refining_difficulty - 1.0) * 0.2
            waste_quantity *= difficulty_factor
            
            if waste_quantity > 0:
                scaled_waste[waste_id] = waste_quantity
        
        return scaled_waste
    
    def _get_relevant_skills(self) -> List[str]:
        """
        Get the list of skills relevant to ore refining.
        
        Returns:
            List of skill names that affect refining efficiency and quality
        """
        return ["engineering", "chemistry", "materials_science", "equipment_operation"]
    
    def get_refining_info(self, ore_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about refining a specific ore.
        
        Args:
            ore_id: ID of the ore to get refining info for
            
        Returns:
            Dictionary with refining information, or None if ore not found
        """
        if ore_id not in ORES:
            return None
        
        ore = ORES[ore_id]
        mineral_yields = ore.get_mineral_yield()
        
        # Get mineral names for the yields
        mineral_info = {}
        for mineral_id, yield_rate in mineral_yields.items():
            if mineral_id in MINERALS:
                mineral = MINERALS[mineral_id]
                mineral_info[mineral.name] = {
                    "yield_rate": yield_rate,
                    "base_value": mineral.base_value
                }
        
        return {
            "ore_name": ore.name,
            "purity": ore.purity.name,
            "refining_difficulty": ore.refining_difficulty,
            "mineral_yields": mineral_info,
            "waste_products": ore.get_waste_products(),
            "purity_modifier": self._get_purity_modifier(ore.purity)
        }
    
    def estimate_refining_cost(
        self, 
        input_resources: Dict[int, float], 
        equipment_quality: float,
        base_cost_per_hour: float = 100.0
    ) -> float:
        """
        Estimate the cost of refining the given ores.
        
        Args:
            input_resources: Dictionary of ore IDs to quantities
            equipment_quality: Quality of refining equipment (0.0-1.0)
            base_cost_per_hour: Base operational cost per hour
            
        Returns:
            Estimated total refining cost
        """
        total_input = sum(input_resources.values())
        
        # Calculate complexity factor based on ore types
        complexity_factor = 1.0
        for ore_id, quantity in input_resources.items():
            if ore_id in ORES:
                ore = ORES[ore_id]
                ore_complexity = ore.refining_difficulty
                weight = quantity / total_input
                complexity_factor += (ore_complexity - 1.0) * weight * 0.2
        
        # Estimate processing time
        base_time = total_input * 0.5  # 30 minutes per unit
        time_modifier = 2.0 - equipment_quality  # Better equipment is faster
        processing_time = base_time * time_modifier * complexity_factor
        
        # Calculate cost
        return processing_time * base_cost_per_hour
    
    def get_optimal_batch_size(self, ore_types: List[int]) -> float:
        """
        Get the optimal batch size for refining the given ore types.
        
        Args:
            ore_types: List of ore IDs to be refined together
            
        Returns:
            Optimal batch size for efficiency
        """
        if not ore_types:
            return 1.0
        
        # Base optimal size
        optimal_size = 10.0
        
        # Adjust based on ore complexity
        avg_complexity = 0.0
        valid_ores = 0
        
        for ore_id in ore_types:
            if ore_id in ORES:
                avg_complexity += ORES[ore_id].refining_difficulty
                valid_ores += 1
        
        if valid_ores > 0:
            avg_complexity /= valid_ores
            # More complex ores benefit from smaller batches
            optimal_size *= (2.0 - avg_complexity) / 2.0
        
        return max(1.0, optimal_size)