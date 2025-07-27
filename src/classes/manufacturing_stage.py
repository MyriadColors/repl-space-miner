"""
Component manufacturing stage implementation for the production chain system.

This module implements the ComponentManufacturingStage class that converts refined
minerals into manufactured components, taking into account manufacturing complexity
and skill effects.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from src.classes.production_stage import ProductionStage, ProductionOutput, ProductionResult
from src.classes.mineral import MINERALS, Mineral
from src.classes.component import Component, ComponentType, COMPONENTS


class ComponentManufacturingStage(ProductionStage):
    """
    Production stage that converts refined minerals into manufactured components.
    
    The manufacturing process considers mineral quality, equipment capabilities,
    operator skills, and component complexity to determine output quality and yield.
    """
    
    def __init__(self):
        """Initialize the component manufacturing stage."""
        super().__init__("Component Manufacturing", base_efficiency=0.7)
        self.recipes: Dict[int, Dict[str, Any]] = {}  # component_id -> recipe data
        self.mineral_data: Dict[int, Mineral] = {}  # mineral_id -> Mineral object
    
    def add_recipe(self, component_id: int, recipe_data: Dict[str, Any]) -> None:
        """Add a manufacturing recipe for a component."""
        self.recipes[component_id] = recipe_data
        
    def get_component_name(self, component_id: int) -> str:
        """Get the name of a component, handling both dict and object access."""
        component = self.recipes.get(component_id, {})
        if isinstance(component, dict):
            name = component.get("name")
            if isinstance(name, str):
                return name
            return f"Component {component_id}"
        elif hasattr(component, 'name'):
            name = getattr(component, 'name')
            if isinstance(name, str):
                return name
            return f"Component {component_id}"
        else:
            return f"Component {component_id}"
    
    def process(
        self, 
        input_resources: Dict[int, float], 
        equipment_quality: float, 
        skills: Dict[str, float],
        batch_size: float = 1.0,
        target_component_id: Optional[int] = None
    ) -> ProductionOutput:
        """
        Process minerals into components.
        
        Args:
            input_resources: Dictionary of mineral IDs to quantities
            equipment_quality: Quality factor of the manufacturing equipment (0.0-1.0)
            skills: Dictionary of skill names to levels (0.0-1.0)
            batch_size: Size of the production batch
            target_component_id: Specific component to manufacture (optional)
            
        Returns:
            ProductionOutput containing manufactured components and waste products
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
        
        # If target component specified, validate it can be made with available minerals
        if target_component_id is not None:
            if target_component_id not in COMPONENTS:
                return ProductionOutput(
                    products={},
                    waste_products={},
                    result=ProductionResult.FAILURE,
                    efficiency=0.0,
                    quality_modifier=0.0,
                    message=f"Unknown component ID: {target_component_id}"
                )
            
            return self._manufacture_specific_component(
                input_resources, equipment_quality, skills, batch_size, target_component_id
            )
        
        # General manufacturing - determine what can be made with available minerals
        return self._manufacture_available_components(
            input_resources, equipment_quality, skills, batch_size
        )
    
    def _manufacture_specific_component(
        self,
        input_resources: Dict[int, float],
        equipment_quality: float,
        skills: Dict[str, float],
        batch_size: float,
        component_id: int
    ) -> ProductionOutput:
        component = COMPONENTS[component_id]
        
        # Check if we have the required minerals
        required_minerals = component.required_minerals
        if not required_minerals:
            return ProductionOutput(
                products={},
                waste_products={},
                result=ProductionResult.FAILURE,
                efficiency=0.0,
                quality_modifier=0.0,
                message=f"No mineral requirements defined for {component.name}"
            )
        
        # Calculate how many components we can make
        max_components = float('inf')
        for mineral_id, required_quantity in required_minerals.items():
            if mineral_id not in input_resources:
                mineral = MINERALS.get(mineral_id)
                mineral_name = mineral.name if mineral else str(mineral_id)
                return ProductionOutput(
                    products={},
                    waste_products={},
                    result=ProductionResult.INSUFFICIENT_RESOURCES,
                    efficiency=0.0,
                    quality_modifier=0.0,
                    message=f"Missing required mineral: {mineral_name}"
                )
            
            available = input_resources[mineral_id]
            possible = available / required_quantity
            max_components = min(max_components, possible)
        
        if max_components <= 0:
            return ProductionOutput(
                products={},
                waste_products={},
                result=ProductionResult.INSUFFICIENT_RESOURCES,
                efficiency=0.0,
                quality_modifier=0.0,
                message="Insufficient minerals for component manufacturing"
            )
        
        # Apply batch size constraint
        actual_components = min(max_components, batch_size)
        
        # Calculate process efficiency
        complexity_factor = component.manufacturing_complexity
        efficiency = self.calculate_efficiency(equipment_quality, skills, batch_size)
        
        # Apply complexity penalty to efficiency
        complexity_penalty = 1.0 - ((complexity_factor - 1.0) * 0.1)
        efficiency *= max(0.5, complexity_penalty)
        
        # Calculate actual output considering efficiency
        final_components = actual_components * efficiency
        
        # Calculate quality modifier
        input_quality = self._calculate_input_quality(input_resources, required_minerals)
        quality_modifier = self.calculate_quality_modifier(equipment_quality, skills, input_quality)
        
        # Calculate waste products
        total_input_used = sum(
            required_minerals[mineral_id] * actual_components 
            for mineral_id in required_minerals
        )
        waste_products = self._calculate_manufacturing_waste(
            component, total_input_used, efficiency, complexity_factor
        )
        
        # Determine result status
        if final_components <= 0:
            result = ProductionResult.FAILURE
            message = f"Manufacturing failed for {component.name}"
        elif efficiency < 0.6:
            result = ProductionResult.PARTIAL_SUCCESS
            message = f"Low efficiency manufacturing of {component.name}"
        else:
            result = ProductionResult.SUCCESS
            message = f"Successfully manufactured {component.name}"
        
        return ProductionOutput(
            products={component_id: round(final_components, 3)},
            waste_products=waste_products,
            result=result,
            efficiency=efficiency,
            quality_modifier=quality_modifier,
            message=message
        )
    
    def _manufacture_available_components(
        self,
        input_resources: Dict[int, float],
        equipment_quality: float,
        skills: Dict[str, float],
        batch_size: float
    ) -> ProductionOutput:
        """
        Manufacture components based on available minerals.
        
        Args:
            input_resources: Available mineral resources
            equipment_quality: Quality of manufacturing equipment
            skills: Operator skills
            batch_size: Production batch size
            
        Returns:
            ProductionOutput for all manufacturable components
        """
        total_products: Dict[int, float] = {}
        total_waste: Dict[int, float] = {}
        total_efficiency = 0.0
        total_quality = 0.0
        manufactured_components: List[str] = []
        
        # Find components that can be manufactured with available minerals
        manufacturable = self._find_manufacturable_components(input_resources)
        
        if not manufacturable:
            return ProductionOutput(
                products={},
                waste_products={},
                result=ProductionResult.INSUFFICIENT_RESOURCES,
                efficiency=0.0,
                quality_modifier=0.0,
                message="No components can be manufactured with available minerals"
            )
        
        # Manufacture each possible component
        remaining_resources = input_resources.copy()
        component_count = 0
        
        for component_id, max_quantity in manufacturable.items():
            if max_quantity <= 0:
                continue
            
            # Manufacture this component
            component_output = self._manufacture_specific_component(
                remaining_resources, equipment_quality, skills, 
                min(max_quantity, batch_size), component_id
            )
            
            if component_output.result != ProductionResult.FAILURE:
                # Add products to total
                for prod_id, quantity in component_output.products.items():
                    if prod_id in total_products:
                        total_products[prod_id] += quantity
                    else:
                        total_products[prod_id] = quantity
                
                # Add waste to total
                for waste_id, quantity in component_output.waste_products.items():
                    if waste_id in total_waste:
                        total_waste[waste_id] += quantity
                    else:
                        total_waste[waste_id] = quantity
                
                # Update running averages
                total_efficiency += component_output.efficiency
                total_quality += component_output.quality_modifier
                component_count += 1
                
                if component_id in COMPONENTS:
                    manufactured_components.append(COMPONENTS[component_id].name)
                
                # Update remaining resources
                component = COMPONENTS[component_id]
                produced_quantity = sum(component_output.products.values())
                for mineral_id, required_per_unit in component.required_minerals.items():
                    used_quantity = required_per_unit * produced_quantity
                    if mineral_id in remaining_resources:
                        remaining_resources[mineral_id] -= used_quantity
                        if remaining_resources[mineral_id] <= 0:
                            del remaining_resources[mineral_id]
        
        # Calculate average efficiency and quality
        if component_count > 0:
            avg_efficiency = total_efficiency / component_count
            avg_quality = total_quality / component_count
        else:
            avg_efficiency = 0.0
            avg_quality = 0.0
        
        # Round all quantities
        total_products = {k: round(v, 3) for k, v in total_products.items()}
        total_waste = {k: round(v, 3) for k, v in total_waste.items()}
        
        # Determine overall result
        if not total_products:
            result = ProductionResult.FAILURE
            message = "No components were successfully manufactured"
        elif avg_efficiency < 0.6:
            result = ProductionResult.PARTIAL_SUCCESS
            message = f"Low efficiency manufacturing of {', '.join(manufactured_components)}"
        else:
            result = ProductionResult.SUCCESS
            message = f"Successfully manufactured {', '.join(manufactured_components)}"
        
        return ProductionOutput(
            products=total_products,
            waste_products=total_waste,
            result=result,
            efficiency=avg_efficiency,
            quality_modifier=avg_quality,
            message=message
        )
    
    def _find_manufacturable_components(self, input_resources: Dict[int, float]) -> Dict[int, float]:
        """
        Find components that can be manufactured with available minerals.
        
        Args:
            input_resources: Available mineral resources
            
        Returns:
            Dictionary of component IDs to maximum manufacturable quantities
        """
        manufacturable = {}
        
        for component_id, component in COMPONENTS.items():
            if not component.required_minerals:
                continue
            
            # Calculate maximum quantity that can be made
            max_quantity = float('inf')
            can_manufacture = True
            
            for mineral_id, required_quantity in component.required_minerals.items():
                if mineral_id not in input_resources:
                    can_manufacture = False
                    break
                
                available = input_resources[mineral_id]
                possible = available / required_quantity
                max_quantity = min(max_quantity, possible)
            
            if can_manufacture and max_quantity > 0:
                manufacturable[component_id] = max_quantity
        
        return manufacturable
    
    def _calculate_input_quality(
        self, 
        input_resources: Dict[int, float], 
        required_minerals: Dict[int, float]
    ) -> float:
        """
        Calculate the average quality of input minerals.
        
        Args:
            input_resources: Available mineral resources
            required_minerals: Required minerals for manufacturing
            
        Returns:
            Average input quality (0.0-2.0)
        """
        total_quality = 0.0
        total_weight = 0.0
        
        for mineral_id, required_quantity in required_minerals.items():
            if mineral_id in MINERALS and mineral_id in input_resources:
                mineral = MINERALS[mineral_id]
                # Use mineral purity as quality indicator
                quality = getattr(mineral, 'purity', 0.8)
                weight = required_quantity
                
                total_quality += quality * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_quality / total_weight
        else:
            return 1.0  # Default quality
    
    def _calculate_manufacturing_waste(
        self, 
        component: Component, 
        input_quantity: float, 
        efficiency: float,
        complexity_factor: float
    ) -> Dict[int, float]:
        """
        Calculate waste products from component manufacturing.
        
        Args:
            component: Component being manufactured
            input_quantity: Total input material quantity
            efficiency: Process efficiency
            complexity_factor: Manufacturing complexity
            
        Returns:
            Dictionary of waste product IDs to quantities
        """
        # Base waste rate for manufacturing
        base_waste_rate = 0.15  # 15% base waste
        
        # Efficiency affects waste - lower efficiency means more waste
        efficiency_factor = 1.5 - (efficiency * 0.5)  # 1.0 to 1.5 range
        
        # Complexity affects waste - more complex manufacturing generates more waste
        complexity_waste_factor = 1.0 + (complexity_factor - 1.0) * 0.2
        
        # Component type affects waste generation
        type_waste_modifiers = {
            ComponentType.STRUCTURAL: 1.0,     # Standard waste
            ComponentType.ELECTRONIC: 1.3,    # More waste due to precision requirements
            ComponentType.MECHANICAL: 1.1,    # Slightly more waste
            ComponentType.POWER: 1.4,         # High waste due to complexity
            ComponentType.PROPULSION: 1.2,    # Moderate additional waste
            ComponentType.LIFE_SUPPORT: 1.3,  # High precision requirements
            ComponentType.WEAPONS: 1.5,       # Highest waste due to precision
            ComponentType.SHIELDS: 1.4,       # High complexity waste
            ComponentType.SENSORS: 1.3,       # Precision manufacturing waste
        }
        
        type_modifier = type_waste_modifiers.get(component.component_type, 1.0)
        
        # Calculate total waste
        total_waste_rate = base_waste_rate * efficiency_factor * complexity_waste_factor * type_modifier
        total_waste = input_quantity * total_waste_rate
        
        # For now, return generic manufacturing waste (ID 2)
        # This will be expanded in the waste management system
        if total_waste > 0:
            return {2: round(total_waste, 3)}
        else:
            return {}
    
    def get_required_resources(self, output_quantity: float, component_id: Optional[int] = None) -> Dict[int, float]:
        if component_id is None:
            return {}
        
        if component_id not in COMPONENTS:
            return {}
        
        component = COMPONENTS[component_id]
        if not component.required_minerals:
            return {}
        
        # Account for average efficiency loss
        average_efficiency = 0.7
        adjusted_quantity = output_quantity / average_efficiency
        
        required = {}
        for mineral_id, required_per_unit in component.required_minerals.items():
            required[mineral_id] = round(required_per_unit * adjusted_quantity, 3)
        
        return required
    
    def get_expected_output(self, input_resources: Dict[int, float]) -> Dict[int, float]:
        """
        Calculate the expected component output for given mineral inputs.
        
        Args:
            input_resources: Dictionary of mineral IDs to quantities
            
        Returns:
            Dictionary of expected component IDs to quantities
        """
        expected_output = {}
        
        # Use average efficiency for estimation
        average_efficiency = 0.7
        
        # Find what can be manufactured
        manufacturable = self._find_manufacturable_components(input_resources)
        
        for component_id, max_quantity in manufacturable.items():
            expected_quantity = max_quantity * average_efficiency
            if expected_quantity > 0:
                expected_output[component_id] = round(expected_quantity, 3)
        
        return expected_output
    
    def _get_relevant_skills(self) -> List[str]:
        """
        Get the list of skills relevant to component manufacturing.
        
        Returns:
            List of skill names that affect manufacturing efficiency and quality
        """
        return ["engineering", "manufacturing", "precision_work", "quality_control", "equipment_operation"]
    
    def get_manufacturing_info(self, component_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about manufacturing a specific component.
        
        Args:
            component_id: ID of the component to get manufacturing info for
            
        Returns:
            Dictionary with manufacturing information, or None if component not found
        """
        if component_id not in COMPONENTS:
            return None
        
        component = COMPONENTS[component_id]
        
        # Get mineral names for the requirements
        mineral_info = {}
        for mineral_id, required_quantity in component.required_minerals.items():
            if mineral_id in MINERALS:
                mineral = MINERALS[mineral_id]
                mineral_info[mineral.name] = {
                    "required_quantity": required_quantity,
                    "base_value": mineral.base_value
                }
        
        return {
            "component_name": component.name,
            "component_type": component.component_type.name,
            "quality": component.quality.name,
            "manufacturing_complexity": component.manufacturing_complexity,
            "tech_level": component.tech_level,
            "required_minerals": mineral_info,
            "base_value": component.base_value,
            "estimated_waste_rate": 0.15 * (1.0 + (component.manufacturing_complexity - 1.0) * 0.2)
        }
    
    def estimate_manufacturing_cost(
        self, 
        component_id: int,
        quantity: float,
        equipment_quality: float,
        base_cost_per_hour: float = 150.0
    ) -> float:
        """
        Estimate the cost of manufacturing the given components.
        
        Args:
            component_id: ID of component to manufacture
            quantity: Quantity to manufacture
            equipment_quality: Quality of manufacturing equipment (0.0-1.0)
            base_cost_per_hour: Base operational cost per hour
            
        Returns:
            Estimated total manufacturing cost
        """
        if component_id not in COMPONENTS:
            return 0.0
        
        component = COMPONENTS[component_id]
        
        # Calculate complexity factor
        complexity_factor = component.manufacturing_complexity
        
        # Estimate processing time
        base_time = quantity * 1.0  # 1 hour per unit base time
        time_modifier = 2.0 - equipment_quality  # Better equipment is faster
        processing_time = base_time * time_modifier * complexity_factor
        
        # Calculate cost
        return processing_time * base_cost_per_hour
    
    def get_optimal_batch_size(self, component_id: int) -> float:
        """
        Get the optimal batch size for manufacturing the given component.
        
        Args:
            component_id: ID of component to manufacture
            
        Returns:
            Optimal batch size for efficiency
        """
        if component_id not in COMPONENTS:
            return 1.0
        
        component = COMPONENTS[component_id]
        
        # Base optimal size
        optimal_size = 5.0  # Smaller than refining due to complexity
        
        # Adjust based on component complexity
        complexity = component.manufacturing_complexity
        # More complex components benefit from smaller batches
        optimal_size *= (2.0 - complexity) / 2.0
        
        return max(1.0, optimal_size)

    def process_materials(self, materials: Dict[int, float], duration: float) -> Tuple[Dict[int, float], Dict[int, float]]:
        total_products: Dict[int, float] = {}
        total_waste: Dict[int, float] = {}
        
        # Process each available recipe
        for component_id, recipe in self.recipes.items():
            if not isinstance(recipe, dict):
                continue
                
            required_minerals = recipe.get("inputs", {})
            if not required_minerals:
                continue
                
            # Calculate how many components we can make
            max_possible = float('inf')
            for mineral_id, required_qty in required_minerals.items():
                available = materials.get(mineral_id, 0.0)
                if required_qty > 0:
                    max_possible = min(max_possible, available / required_qty)
            
            if max_possible <= 0 or max_possible == float('inf'):
                continue
                
            # Apply efficiency and duration scaling
            actual_production = max_possible * self.base_efficiency * (duration / 3600.0)  # per hour base
            
            if actual_production > 0:
                total_products[component_id] = total_products.get(component_id, 0.0) + actual_production
                
                # Calculate waste (inefficiency)
                waste_factor = 1.0 - self.base_efficiency
                for mineral_id, required_qty in required_minerals.items():
                    waste_amount = (required_qty * actual_production) * waste_factor
                    if waste_amount > 0:
                        total_waste[mineral_id] = total_waste.get(mineral_id, 0.0) + waste_amount
        
        return total_products, total_waste
    
    def can_produce(self, component_id: int, quantity: float, available_materials: Dict[int, float]) -> bool:
        """
        Check if we can produce the specified quantity of a component.
        
        Args:
            component_id: ID of component to produce
            quantity: Desired quantity
            available_materials: Available mineral quantities
            
        Returns:
            True if production is possible
        """
        required = self.get_required_resources(quantity, component_id)
        
        for mineral_id, required_qty in required.items():
            if available_materials.get(mineral_id, 0.0) < required_qty:
                return False
                
        return True
    
    def get_production_info(self) -> Dict[str, Any]:
        return {
            "stage_id": getattr(self, 'stage_id', 'component_manufacturing'),
            "name": self.stage_name,
            "type": "manufacturing",
            "efficiency": self.base_efficiency,
            "recipes": len(self.recipes),
            "available_components": list(self.recipes.keys())
        }