"""
Assembly stage implementation for the production chain system.

This module implements the AssemblyStage class that converts manufactured components
into finished goods, taking into account tech level requirements and quality calculations.
"""

from typing import Dict, List, Optional, Any

from src.classes.production_stage import ProductionStage, ProductionOutput, ProductionResult
from src.classes.component import ComponentQuality, COMPONENTS
from src.classes.finished_good import FinishedGood, FinishedGoodQuality, FinishedGoodType, FINISHED_GOODS


class AssemblyStage(ProductionStage):
    """
    Production stage that converts manufactured components into finished goods.
    
    The assembly process considers component quality, tech level requirements,
    equipment capabilities, and operator skills to determine output quality and yield.
    """
    
    def __init__(self):
        """Initialize the assembly stage."""
        super().__init__("Finished Goods Assembly", base_efficiency=0.8)
    
    def process(
        self, 
        input_resources: Dict[int, float], 
        equipment_quality: float, 
        skills: Dict[str, float],
        batch_size: float = 1.0,
        target_product_id: Optional[int] = None,
        tech_level: int = 1
    ) -> ProductionOutput:
        """
        Process components into finished goods.
        
        Args:
            input_resources: Dictionary of component IDs to quantities
            equipment_quality: Quality factor of the assembly equipment (0.0-1.0)
            skills: Dictionary of skill names to levels (0.0-1.0)
            batch_size: Size of the production batch
            target_product_id: Specific finished good to assemble (optional)
            tech_level: Available technology level for assembly
            
        Returns:
            ProductionOutput containing assembled finished goods and waste products
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
        
        # If target product specified, validate it can be made with available components
        if target_product_id is not None:
            if target_product_id not in FINISHED_GOODS:
                return ProductionOutput(
                    products={},
                    waste_products={},
                    result=ProductionResult.FAILURE,
                    efficiency=0.0,
                    quality_modifier=0.0,
                    message=f"Unknown finished good ID: {target_product_id}"
                )
            
            return self._assemble_specific_product(
                input_resources, equipment_quality, skills, batch_size, target_product_id, tech_level
            )
        
        # General assembly - determine what can be made with available components
        return self._assemble_available_products(
            input_resources, equipment_quality, skills, batch_size, tech_level
        )
    
    def _assemble_specific_product(
        self,
        input_resources: Dict[int, float],
        equipment_quality: float,
        skills: Dict[str, float],
        batch_size: float,
        product_id: int,
        tech_level: int
    ) -> ProductionOutput:
        """
        Assemble a specific finished good.
        
        Args:
            input_resources: Available component resources
            equipment_quality: Quality of assembly equipment
            skills: Operator skills
            batch_size: Production batch size
            product_id: ID of finished good to assemble
            tech_level: Available technology level
            
        Returns:
            ProductionOutput for the specific finished good
        """
        product = FINISHED_GOODS[product_id]
        
        # Check tech level requirement
        if tech_level < product.tech_level:
            return ProductionOutput(
                products={},
                waste_products={},
                result=ProductionResult.FAILURE,
                efficiency=0.0,
                quality_modifier=0.0,
                message=f"Insufficient tech level for {product.name} (requires {product.tech_level}, have {tech_level})"
            )
        
        # Check if we have the required components
        required_components = product.required_components
        if not required_components:
            return ProductionOutput(
                products={},
                waste_products={},
                result=ProductionResult.FAILURE,
                efficiency=0.0,
                quality_modifier=0.0,
                message=f"No component requirements defined for {product.name}"
            )
        
        # Calculate how many products we can make
        max_products = float('inf')
        for component_id, required_quantity in required_components.items():
            if component_id not in input_resources:
                component = COMPONENTS.get(component_id)
                component_name = component.name if component else str(component_id)
                return ProductionOutput(
                    products={},
                    waste_products={},
                    result=ProductionResult.INSUFFICIENT_RESOURCES,
                    efficiency=0.0,
                    quality_modifier=0.0,
                    message=f"Missing required component: {component_name}"
                )
            
            available = input_resources[component_id]
            possible = available / required_quantity
            max_products = min(max_products, possible)
        
        if max_products <= 0:
            return ProductionOutput(
                products={},
                waste_products={},
                result=ProductionResult.INSUFFICIENT_RESOURCES,
                efficiency=0.0,
                quality_modifier=0.0,
                message="Insufficient components for assembly"
            )
        
        # Apply batch size constraint
        actual_products = min(max_products, batch_size)
        
        # Calculate process efficiency
        complexity_factor = product.assembly_complexity
        efficiency = self.calculate_efficiency(equipment_quality, skills, batch_size)
        
        # Apply complexity penalty to efficiency
        complexity_penalty = 1.0 - ((complexity_factor - 1.0) * 0.15)
        efficiency *= max(0.4, complexity_penalty)
        
        # Apply tech level bonus (having higher tech than required improves efficiency)
        tech_bonus = 1.0 + ((tech_level - product.tech_level) * 0.05)
        efficiency *= min(tech_bonus, 1.2)  # Cap at 20% bonus
        
        # Calculate actual output considering efficiency
        final_products = actual_products * efficiency
        
        # Calculate quality modifier
        input_quality = self._calculate_input_quality(input_resources, required_components)
        quality_modifier = self.calculate_quality_modifier(equipment_quality, skills, input_quality)
        
        # Apply tech level bonus to quality
        tech_quality_bonus = 1.0 + ((tech_level - product.tech_level) * 0.03)
        quality_modifier *= min(tech_quality_bonus, 1.15)  # Cap at 15% bonus
        
        # Calculate waste products
        total_input_used = sum(
            required_components[component_id] * actual_products 
            for component_id in required_components
        )
        waste_products = self._calculate_assembly_waste(
            product, total_input_used, efficiency, complexity_factor
        )
        
        # Determine result status
        if final_products <= 0:
            result = ProductionResult.FAILURE
            message = f"Assembly failed for {product.name}"
        elif efficiency < 0.7:
            result = ProductionResult.PARTIAL_SUCCESS
            message = f"Low efficiency assembly of {product.name}"
        else:
            result = ProductionResult.SUCCESS
            message = f"Successfully assembled {product.name}"
        
        return ProductionOutput(
            products={product_id: round(final_products, 3)},
            waste_products=waste_products,
            result=result,
            efficiency=efficiency,
            quality_modifier=quality_modifier,
            message=message
        )
    
    def _assemble_available_products(
        self,
        input_resources: Dict[int, float],
        equipment_quality: float,
        skills: Dict[str, float],
        batch_size: float,
        tech_level: int
    ) -> ProductionOutput:
        """
        Assemble finished goods based on available components.
        
        Args:
            input_resources: Available component resources
            equipment_quality: Quality of assembly equipment
            skills: Operator skills
            batch_size: Production batch size
            tech_level: Available technology level
            
        Returns:
            ProductionOutput for all assemblable products
        """
        total_products: Dict[int, float] = {}
        total_waste: Dict[int, float] = {}
        total_efficiency = 0.0
        total_quality = 0.0
        assembled_products = []
        
        # Find products that can be assembled with available components
        assemblable = self._find_assemblable_products(input_resources, tech_level)
        
        if not assemblable:
            return ProductionOutput(
                products={},
                waste_products={},
                result=ProductionResult.INSUFFICIENT_RESOURCES,
                efficiency=0.0,
                quality_modifier=0.0,
                message="No finished goods can be assembled with available components"
            )
        
        # Assemble each possible product
        remaining_resources = input_resources.copy()
        product_count = 0
        
        for product_id, max_quantity in assemblable.items():
            if max_quantity <= 0:
                continue
            
            # Assemble this product
            product_output = self._assemble_specific_product(
                remaining_resources, equipment_quality, skills, 
                min(max_quantity, batch_size), product_id, tech_level
            )
            
            if product_output.result != ProductionResult.FAILURE:
                # Add products to total
                for prod_id, quantity in product_output.products.items():
                    if prod_id in total_products:
                        total_products[prod_id] += quantity
                    else:
                        total_products[prod_id] = quantity
            
                # Add waste to total
                for waste_id, quantity in product_output.waste_products.items():
                    if waste_id in total_waste:
                        total_waste[waste_id] += quantity
                    else:
                        total_waste[waste_id] = quantity
            
                # Update running averages
                total_efficiency += product_output.efficiency
                total_quality += product_output.quality_modifier
                product_count += 1
                
                if product_id in FINISHED_GOODS:
                    assembled_products.append(FINISHED_GOODS[product_id].name)
                
                # Update remaining resources
                product = FINISHED_GOODS[product_id]
                produced_quantity = sum(product_output.products.values())
                for component_id, required_per_unit in product.required_components.items():
                    used_quantity = required_per_unit * produced_quantity
                    if component_id in remaining_resources:
                        remaining_resources[component_id] -= used_quantity
                        if remaining_resources[component_id] <= 0:
                            del remaining_resources[component_id]
    
        # Calculate average efficiency and quality
        if product_count > 0:
            avg_efficiency = total_efficiency / product_count
            avg_quality = total_quality / product_count
        else:
            avg_efficiency = 0.0
            avg_quality = 0.0
    
        # Round all quantities
        total_products = {k: round(v, 3) for k, v in total_products.items()}
        total_waste = {k: round(v, 3) for k, v in total_waste.items()}
        
        # Determine overall result
        if not total_products:
            result = ProductionResult.FAILURE
            message = "No finished goods were successfully assembled"
        elif avg_efficiency < 0.7:
            result = ProductionResult.PARTIAL_SUCCESS
            message = f"Low efficiency assembly of {', '.join(assembled_products)}"
        else:
            result = ProductionResult.SUCCESS
            message = f"Successfully assembled {', '.join(assembled_products)}"
        
        return ProductionOutput(
            products=total_products,
            waste_products=total_waste,
            result=result,
            efficiency=avg_efficiency,
            quality_modifier=avg_quality,
            message=message
        )
    
    def _find_assemblable_products(self, input_resources: Dict[int, float], tech_level: int) -> Dict[int, float]:
        """
        Find finished goods that can be assembled with available components.
        
        Args:
            input_resources: Available component resources
            tech_level: Available technology level
            
        Returns:
            Dictionary of product IDs to maximum assemblable quantities
        """
        assemblable = {}
        
        for product_id, product in FINISHED_GOODS.items():
            # Check tech level requirement
            if tech_level < product.tech_level:
                continue
            
            if not product.required_components:
                continue
            
            # Calculate maximum quantity that can be made
            max_quantity = float('inf')
            can_assemble = True
            
            for component_id, required_quantity in product.required_components.items():
                if component_id not in input_resources:
                    can_assemble = False
                    break
                
                available = input_resources[component_id]
                possible = available / required_quantity
                max_quantity = min(max_quantity, possible)
            
            if can_assemble and max_quantity > 0:
                assemblable[product_id] = max_quantity
        
        return assemblable
    
    def _calculate_input_quality(
        self, 
        input_resources: Dict[int, float], 
        required_components: Dict[int, float]
    ) -> float:
        """
        Calculate the average quality of input components.
        
        Args:
            input_resources: Available component resources
            required_components: Required components for assembly
            
        Returns:
            Average input quality (0.0-2.0)
        """
        total_quality = 0.0
        total_weight = 0.0
        
        for component_id, required_quantity in required_components.items():
            if component_id in COMPONENTS and component_id in input_resources:
                component = COMPONENTS[component_id]
                # Convert component quality to numeric value
                quality_values = {
                    ComponentQuality.BASIC: 0.6,
                    ComponentQuality.STANDARD: 1.0,
                    ComponentQuality.ADVANCED: 1.4,
                    ComponentQuality.PREMIUM: 1.8,
                    ComponentQuality.PROTOTYPE: 2.0,
                }
                quality = quality_values.get(component.quality, 1.0)
                weight = required_quantity
                
                total_quality += quality * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_quality / total_weight
        else:
            return 1.0  # Default quality
    
    def _calculate_assembly_waste(
        self, 
        product: FinishedGood, 
        input_quantity: float, 
        efficiency: float,
        complexity_factor: float
    ) -> Dict[int, float]:
        """
        Calculate waste products from finished goods assembly.
        
        Args:
            product: Finished good being assembled
            input_quantity: Total input component quantity
            efficiency: Process efficiency
            complexity_factor: Assembly complexity
            
        Returns:
            Dictionary of waste product IDs to quantities
        """
        # Base waste rate for assembly (lower than manufacturing)
        base_waste_rate = 0.05  # 5% base waste
        
        # Efficiency affects waste - lower efficiency means more waste
        efficiency_factor = 1.3 - (efficiency * 0.3)  # 1.0 to 1.3 range
        
        # Complexity affects waste - more complex assembly generates more waste
        complexity_waste_factor = 1.0 + (complexity_factor - 1.0) * 0.1
        
        # Product type affects waste generation
        type_waste_modifiers = {
            FinishedGoodType.CONSUMER: 1.0,      # Standard waste
            FinishedGoodType.INDUSTRIAL: 1.1,   # Slightly more waste
            FinishedGoodType.MILITARY: 1.4,     # High precision requirements
            FinishedGoodType.MEDICAL: 1.3,      # Precision assembly
            FinishedGoodType.SCIENTIFIC: 1.2,   # Moderate precision requirements
            FinishedGoodType.LUXURY: 1.5,       # Highest waste due to precision
            FinishedGoodType.SHIP_EQUIPMENT: 1.3, # High reliability requirements
        }
        
        type_modifier = type_waste_modifiers.get(product.good_type, 1.0)
        
        # Quality affects waste generation
        quality_waste_modifiers = {
            FinishedGoodQuality.ECONOMY: 0.8,    # Less waste due to lower standards
            FinishedGoodQuality.STANDARD: 1.0,   # Standard waste
            FinishedGoodQuality.PREMIUM: 1.2,    # More waste due to higher standards
            FinishedGoodQuality.LUXURY: 1.5,     # High waste due to perfection requirements
            FinishedGoodQuality.MILITARY: 1.3,   # High waste due to strict standards
        }
        
        quality_modifier = quality_waste_modifiers.get(product.quality, 1.0)
        
        # Calculate total waste
        total_waste_rate = (base_waste_rate * efficiency_factor * complexity_waste_factor * 
                           type_modifier * quality_modifier)
        total_waste = input_quantity * total_waste_rate
        
        # For now, return generic assembly waste (ID 3)
        # This will be expanded in the waste management system
        if total_waste > 0:
            return {3: round(total_waste, 3)}
        else:
            return {}
    
    def get_required_resources(self, output_quantity: float, product_id: Optional[int] = None) -> Dict[int, float]:
        if product_id is None or product_id not in FINISHED_GOODS:
            return {}
        
        product = FINISHED_GOODS[product_id]
        if not product.required_components:
            return {}
        
        # Account for average efficiency loss
        average_efficiency = 0.8
        adjusted_quantity = output_quantity / average_efficiency
        
        required = {}
        for component_id, required_per_unit in product.required_components.items():
            required[component_id] = round(required_per_unit * adjusted_quantity, 3)
        
        return required
    
    def get_expected_output(self, input_resources: Dict[int, float], tech_level: int = 1) -> Dict[int, float]:
        """
        Calculate the expected finished good output for given component inputs.
        
        Args:
            input_resources: Dictionary of component IDs to quantities
            tech_level: Available technology level
            
        Returns:
            Dictionary of expected finished good IDs to quantities
        """
        expected_output = {}
        
        # Use average efficiency for estimation
        average_efficiency = 0.8
        
        # Find what can be assembled
        assemblable = self._find_assemblable_products(input_resources, tech_level)
        
        for product_id, max_quantity in assemblable.items():
            expected_quantity = max_quantity * average_efficiency
            if expected_quantity > 0:
                expected_output[product_id] = round(expected_quantity, 3)
        
        return expected_output
    
    def _get_relevant_skills(self) -> List[str]:
        """
        Get the list of skills relevant to finished goods assembly.
        
        Returns:
            List of skill names that affect assembly efficiency and quality
        """
        return ["engineering", "assembly", "quality_control", "precision_work", "project_management"]
    
    def get_assembly_info(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about assembling a specific finished good.
        
        Args:
            product_id: ID of the finished good to get assembly info for
            
        Returns:
            Dictionary with assembly information, or None if product not found
        """
        if product_id not in FINISHED_GOODS:
            return None
        
        product = FINISHED_GOODS[product_id]
        
        # Get component names for the requirements
        component_info = {}
        for component_id, required_quantity in product.required_components.items():
            if component_id in COMPONENTS:
                component = COMPONENTS[component_id]
                component_info[component.name] = {
                    "required_quantity": required_quantity,
                    "base_value": component.base_value
                }
        
        return {
            "product_name": product.name,
            "product_type": product.good_type.name,
            "quality": product.quality.name,
            "assembly_complexity": product.assembly_complexity,
            "tech_level": product.tech_level,
            "required_components": component_info,
            "base_value": product.base_value,
            "estimated_waste_rate": 0.05 * (1.0 + (product.assembly_complexity - 1.0) * 0.1)
        }
    
    def estimate_assembly_cost(
        self, 
        product_id: int,
        quantity: float,
        equipment_quality: float,
        base_cost_per_hour: float = 200.0
    ) -> float:
        """
        Estimate the cost of assembling the given finished goods.
        
        Args:
            product_id: ID of finished good to assemble
            quantity: Quantity to assemble
            equipment_quality: Quality of assembly equipment (0.0-1.0)
            base_cost_per_hour: Base operational cost per hour
            
        Returns:
            Estimated total assembly cost
        """
        if product_id not in FINISHED_GOODS:
            return 0.0
        
        product = FINISHED_GOODS[product_id]
        
        # Calculate complexity factor
        complexity_factor = product.assembly_complexity
        
        # Tech level affects cost (higher tech is more expensive)
        tech_factor = 1.0 + (product.tech_level - 1) * 0.1
        
        # Estimate processing time
        base_time = quantity * 1.5  # 1.5 hours per unit base time
        time_modifier = 2.0 - equipment_quality  # Better equipment is faster
        processing_time = base_time * time_modifier * complexity_factor * tech_factor
        
        # Calculate cost
        return processing_time * base_cost_per_hour
    
    def get_optimal_batch_size(self, product_id: int) -> float:
        """
        Get the optimal batch size for assembling the given finished good.
        
        Args:
            product_id: ID of finished good to assemble
            
        Returns:
            Optimal batch size for efficiency
        """
        if product_id not in FINISHED_GOODS:
            return 1.0
        
        product = FINISHED_GOODS[product_id]
        
        # Base optimal size (smaller than manufacturing due to higher complexity)
        optimal_size = 3.0
        
        # Adjust based on assembly complexity
        complexity = product.assembly_complexity
        # More complex assembly benefits from smaller batches
        optimal_size *= (2.5 - complexity) / 2.5
        
        # Adjust based on tech level (higher tech benefits from smaller batches)
        tech_factor = max(0.5, 1.0 - (product.tech_level - 1) * 0.1)
        optimal_size *= tech_factor
        
        return max(1.0, optimal_size)