from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Tuple, Any, Optional

from src.classes.waste_product import WasteProduct, WasteType, HazardLevel


class FacilityType(Enum):
    """Types of waste disposal facilities."""
    BASIC_DISPOSAL = auto()      # Basic waste disposal only
    RECYCLING_CENTER = auto()    # Can recycle some waste types
    HAZMAT_FACILITY = auto()     # Specialized for hazardous waste
    ADVANCED_RECYCLING = auto()  # Advanced recycling capabilities
    RESEARCH_FACILITY = auto()   # Experimental waste processing


class DisposalMethod(Enum):
    """Methods of waste disposal."""
    INCINERATION = auto()        # Burn waste (generates energy)
    CHEMICAL_TREATMENT = auto()  # Chemical neutralization
    CONTAINMENT = auto()         # Secure storage/containment
    RECYCLING = auto()           # Process into useful materials
    SPACE_JETTISON = auto()      # Eject into space (legal in some areas)
    SOLAR_DISPOSAL = auto()      # Send waste into a star


@dataclass
class WasteDisposalFacility:
    """
    Represents a waste disposal facility at a station.
    
    Facilities can dispose of waste products legally and may offer
    recycling services to recover useful materials from waste.
    """
    facility_id: str
    station_id: str
    facility_type: FacilityType
    name: str
    description: str = ""
    
    # Capacity and capabilities
    disposal_capacity: float = 1000.0  # Maximum waste volume per day
    current_load: float = 0.0  # Current waste being processed
    recycling_efficiency: float = 0.6  # Base recycling efficiency (0.0-1.0)
    
    # Accepted waste types and methods
    accepted_waste_types: List[WasteType] = field(default_factory=list)
    available_methods: List[DisposalMethod] = field(default_factory=list)
    
    # Special processing capabilities
    special_processes: Dict[str, float] = field(default_factory=dict)  # Process name to efficiency
    equipment_quality: float = 1.0  # Quality of facility equipment (0.0-2.0)
    
    # Pricing and costs
    base_disposal_cost: float = 5.0  # Base cost per unit of waste
    recycling_fee: float = 2.0  # Additional fee for recycling services
    hazmat_surcharge: float = 3.0  # Additional cost for hazardous materials
    
    # Operational status
    operational: bool = True
    maintenance_level: float = 1.0  # Affects efficiency (0.0-1.0)
    reputation: float = 1.0  # Facility reputation affects pricing
    
    def __post_init__(self):
        """Initialize facility based on type."""
        if not self.accepted_waste_types:
            self._set_default_capabilities()
    
    def _set_default_capabilities(self) -> None:
        """Set default capabilities based on facility type."""
        # Import WasteType here to ensure we get the same instance
        from src.classes.waste_product import WasteType as WT
        
        if self.facility_type == FacilityType.BASIC_DISPOSAL:
            self.accepted_waste_types = [WT.INERT, WT.SLAG, WT.TAILINGS]
            self.available_methods = [DisposalMethod.INCINERATION, DisposalMethod.CONTAINMENT]
            self.disposal_capacity = 500.0
            self.recycling_efficiency = 0.3
            self.equipment_quality = 0.6
            
        elif self.facility_type == FacilityType.RECYCLING_CENTER:
            self.accepted_waste_types = [WT.SLAG, WT.TAILINGS, WT.ORGANIC, WT.INERT]
            self.available_methods = [DisposalMethod.RECYCLING, DisposalMethod.INCINERATION]
            self.disposal_capacity = 800.0
            self.recycling_efficiency = 0.7
            self.equipment_quality = 1.2
            self.special_processes = {"metal_recovery": 0.8, "organic_composting": 0.6}
            
        elif self.facility_type == FacilityType.HAZMAT_FACILITY:
            self.accepted_waste_types = list(WT)  # Can handle all types
            self.available_methods = [DisposalMethod.CHEMICAL_TREATMENT, DisposalMethod.CONTAINMENT, 
                                    DisposalMethod.SPACE_JETTISON]
            self.disposal_capacity = 300.0
            self.recycling_efficiency = 0.4
            self.equipment_quality = 1.5
            self.special_processes = {"neutralization": 0.9, "stabilization": 0.8}
            
        elif self.facility_type == FacilityType.ADVANCED_RECYCLING:
            self.accepted_waste_types = list(WT)
            self.available_methods = [DisposalMethod.RECYCLING, DisposalMethod.CHEMICAL_TREATMENT]
            self.disposal_capacity = 1200.0
            self.recycling_efficiency = 0.9
            self.equipment_quality = 1.8
            self.special_processes = {"molecular_breakdown": 0.95, "element_separation": 0.85}
            
        elif self.facility_type == FacilityType.RESEARCH_FACILITY:
            self.accepted_waste_types = list(WT)
            self.available_methods = list(DisposalMethod)
            self.disposal_capacity = 200.0
            self.recycling_efficiency = 0.8
            self.equipment_quality = 2.0
            self.special_processes = {"experimental_processing": 1.0, "rare_element_extraction": 0.7}
    
    def can_accept_waste(self, waste_product: WasteProduct, quantity: float) -> Tuple[bool, str]:
        """
        Check if the facility can accept the given waste product.
        
        Args:
            waste_product: The waste product to check
            quantity: Amount of waste to dispose
            
        Returns:
            Tuple of (can_accept, reason_if_not)
        """
        if not self.operational:
            return False, "Facility is currently offline for maintenance"
        
        # Compare by name instead of identity to avoid enum instance issues
        accepted_type_names = [wt.name for wt in self.accepted_waste_types]
        if waste_product.waste_type.name not in accepted_type_names:
            return False, f"Facility does not accept {waste_product.waste_type.name.lower()} waste"
        
        # Check capacity
        waste_volume = quantity * waste_product.commodity.volume_per_unit
        if self.current_load + waste_volume > self.disposal_capacity:
            remaining_capacity = self.disposal_capacity - self.current_load
            return False, f"Insufficient capacity. Can only accept {remaining_capacity:.1f} m³ more waste"
        
        # Check special requirements for hazardous waste
        if waste_product.hazard_level in [HazardLevel.HIGH, HazardLevel.EXTREME]:
            if self.facility_type == FacilityType.BASIC_DISPOSAL:
                return False, "Basic disposal facility cannot handle hazardous waste"
        
        return True, "Waste can be accepted"
    
    def calculate_disposal_cost(self, waste_product: WasteProduct, quantity: float, 
                              method: DisposalMethod = DisposalMethod.INCINERATION) -> float:
        """
        Calculate the cost to dispose of waste.
        
        Args:
            waste_product: The waste product to dispose
            quantity: Amount of waste to dispose
            method: Disposal method to use
            
        Returns:
            Total disposal cost
        """
        base_cost = self.base_disposal_cost * quantity
        
        # Apply hazard level multiplier
        hazard_multipliers = {
            HazardLevel.HARMLESS: 0.5,
            HazardLevel.LOW: 1.0,
            HazardLevel.MODERATE: 2.0,
            HazardLevel.HIGH: 5.0,
            HazardLevel.EXTREME: 15.0,
        }
        hazard_cost = base_cost * hazard_multipliers.get(waste_product.hazard_level, 1.0)
        
        # Apply method-specific costs
        method_multipliers = {
            DisposalMethod.INCINERATION: 1.0,
            DisposalMethod.CHEMICAL_TREATMENT: 2.5,
            DisposalMethod.CONTAINMENT: 3.0,
            DisposalMethod.RECYCLING: 0.8,  # Cheaper due to material recovery
            DisposalMethod.SPACE_JETTISON: 1.5,
            DisposalMethod.SOLAR_DISPOSAL: 10.0,  # Very expensive
        }
        method_cost = hazard_cost * method_multipliers.get(method, 1.0)
        
        # Apply facility reputation modifier
        reputation_modifier = 0.5 + (self.reputation * 0.5)  # 0.5 to 1.0 multiplier
        
        # Apply maintenance level modifier (poor maintenance = higher costs)
        maintenance_modifier = 1.0 + (1.0 - self.maintenance_level) * 0.5
        
        total_cost = method_cost * reputation_modifier * maintenance_modifier
        
        return round(total_cost, 2)
    
    def dispose_waste(self, waste_product: WasteProduct, quantity: float,
                     method: DisposalMethod = DisposalMethod.INCINERATION) -> Tuple[float, Dict[str, Any]]:
        """
        Dispose of waste using the specified method.
        
        Args:
            waste_product: The waste product to dispose
            quantity: Amount of waste to dispose
            method: Disposal method to use
            
        Returns:
            Tuple of (cost, result_info)
        """
        can_accept, reason = self.can_accept_waste(waste_product, quantity)
        if not can_accept:
            return 0.0, {"success": False, "error": reason}
        
        if method not in self.available_methods:
            return 0.0, {"success": False, "error": f"Disposal method {method.name} not available"}
        
        cost = self.calculate_disposal_cost(waste_product, quantity, method)
        
        # Update facility load
        waste_volume = quantity * waste_product.commodity.volume_per_unit
        self.current_load += waste_volume
        
        # Generate result based on method
        result = {
            "success": True,
            "cost": cost,
            "method": method.name,
            "quantity_disposed": quantity,
            "volume_processed": waste_volume,
            "environmental_impact": 0.0,
            "byproducts": {}
        }
        
        # Method-specific results
        if method == DisposalMethod.INCINERATION:
            # Incineration may generate energy credits
            energy_generated = quantity * 0.1 * self.equipment_quality
            result["energy_generated"] = round(energy_generated, 2)
            result["environmental_impact"] = waste_product.environmental_impact * 0.3
            
        elif method == DisposalMethod.RECYCLING:
            # Recycling recovers materials
            recovered = self.recycle_waste(waste_product, quantity)
            result["recovered_materials"] = recovered
            result["environmental_impact"] = waste_product.environmental_impact * 0.1
            
        elif method == DisposalMethod.CHEMICAL_TREATMENT:
            # Chemical treatment neutralizes hazards
            result["environmental_impact"] = waste_product.environmental_impact * 0.05
            
        elif method == DisposalMethod.CONTAINMENT:
            # Containment has no immediate environmental impact
            result["environmental_impact"] = 0.0
            result["storage_location"] = f"Secure containment unit {self.facility_id}-{hash(waste_product.commodity.name) % 1000}"
            
        elif method == DisposalMethod.SPACE_JETTISON:
            # Space jettison has minimal local impact but may affect reputation
            result["environmental_impact"] = waste_product.environmental_impact * 0.2
            result["reputation_impact"] = -0.1 if waste_product.hazard_level != HazardLevel.HARMLESS else 0.0
            
        elif method == DisposalMethod.SOLAR_DISPOSAL:
            # Solar disposal completely eliminates waste
            result["environmental_impact"] = 0.0
            result["reputation_impact"] = 0.1  # Positive reputation for responsible disposal
        
        return cost, result
    
    def can_recycle_waste(self, waste_product: WasteProduct) -> bool:
        """Check if the facility can recycle the given waste product."""
        if not waste_product.recyclable:
            return False
        
        if DisposalMethod.RECYCLING not in self.available_methods:
            return False
        
        return waste_product.can_recycle(self.equipment_quality)
    
    def recycle_waste(self, waste_product: WasteProduct, quantity: float) -> Dict[int, float]:
        """
        Recycle waste into useful materials.
        
        Args:
            waste_product: The waste product to recycle
            quantity: Amount of waste to recycle
            
        Returns:
            Dictionary mapping resource_id to amount recovered
        """
        if not self.can_recycle_waste(waste_product):
            return {}
        
        # Calculate effective recycling efficiency
        base_efficiency = self.recycling_efficiency
        equipment_bonus = (self.equipment_quality - 1.0) * 0.2
        maintenance_penalty = (1.0 - self.maintenance_level) * 0.3
        
        effective_efficiency = max(0.1, min(0.95, base_efficiency + equipment_bonus - maintenance_penalty))
        
        # Apply special processes if available
        process_bonus = 0.0
        for process_name, process_efficiency in self.special_processes.items():
            if "recovery" in process_name.lower() or "recycling" in process_name.lower():
                process_bonus = max(process_bonus, process_efficiency - base_efficiency)
        
        final_efficiency = min(0.98, effective_efficiency + process_bonus)
        
        # Calculate recovered materials
        recovered_materials = {}
        for resource_id, base_yield in waste_product.recycling_products.items():
            recovered_amount = quantity * base_yield * final_efficiency
            if recovered_amount > 0.01:  # Only include meaningful amounts
                recovered_materials[resource_id] = round(recovered_amount, 3)
        
        return recovered_materials
    
    def get_available_methods(self, waste_product: WasteProduct) -> List[DisposalMethod]:
        """Get available disposal methods for a specific waste product."""
        available = []
        
        for method in self.available_methods:
            # Check if method is suitable for this waste type
            if method == DisposalMethod.RECYCLING and not self.can_recycle_waste(waste_product):
                continue
            
            # Check if facility can handle hazardous waste with this method
            if waste_product.hazard_level in [HazardLevel.HIGH, HazardLevel.EXTREME]:
                if method == DisposalMethod.INCINERATION and self.facility_type == FacilityType.BASIC_DISPOSAL:
                    continue
            
            available.append(method)
        
        return available
    
    def get_capacity_info(self) -> Dict[str, float]:
        """Get information about facility capacity."""
        return {
            "total_capacity": self.disposal_capacity,
            "current_load": self.current_load,
            "available_capacity": self.disposal_capacity - self.current_load,
            "utilization_percent": (self.current_load / self.disposal_capacity) * 100
        }
    
    def process_daily_operations(self) -> Dict[str, Any]:
        """
        Process daily facility operations (waste processing, maintenance, etc.).
        
        Returns:
            Dictionary with operation results
        """
        if not self.operational:
            return {"processed": 0.0, "maintenance_performed": False}
        
        # Process current waste load
        processing_rate = self.disposal_capacity * 0.8 * self.maintenance_level
        processed_amount = min(self.current_load, processing_rate)
        self.current_load = max(0.0, self.current_load - processed_amount)
        
        # Random maintenance events
        import random
        maintenance_performed = False
        if random.random() < 0.05:  # 5% chance of maintenance
            self.maintenance_level = min(1.0, self.maintenance_level + 0.1)
            maintenance_performed = True
        
        # Gradual wear and tear
        wear_rate = 0.001 * (1.0 + self.current_load / self.disposal_capacity)
        self.maintenance_level = max(0.3, self.maintenance_level - wear_rate)
        
        return {
            "processed": processed_amount,
            "maintenance_performed": maintenance_performed,
            "current_maintenance": self.maintenance_level,
            "operational_efficiency": self.maintenance_level * self.equipment_quality
        }
    
    def get_facility_info(self) -> str:
        """Get a formatted string with facility information."""
        status = "OPERATIONAL" if self.operational else "OFFLINE"
        capacity_info = self.get_capacity_info()
        
        info = f"{self.name} ({self.facility_type.name.replace('_', ' ').title()})\n"
        info += f"Status: {status}\n"
        info += f"Capacity: {capacity_info['current_load']:.1f}/{capacity_info['total_capacity']:.1f} m³ "
        info += f"({capacity_info['utilization_percent']:.1f}% utilized)\n"
        info += f"Equipment Quality: {self.equipment_quality:.1f}/2.0\n"
        info += f"Maintenance Level: {self.maintenance_level:.1f}/1.0\n"
        info += f"Recycling Efficiency: {self.recycling_efficiency:.1f}/1.0\n"
        
        info += f"Accepted Waste Types: {', '.join([wt.name.replace('_', ' ').title() for wt in self.accepted_waste_types])}\n"
        info += f"Available Methods: {', '.join([dm.name.replace('_', ' ').title() for dm in self.available_methods])}\n"
        
        if self.special_processes:
            info += f"Special Processes: {', '.join(self.special_processes.keys())}\n"
        
        return info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert facility to dictionary for serialization."""
        return {
            "facility_id": self.facility_id,
            "station_id": self.station_id,
            "facility_type": self.facility_type.name,
            "name": self.name,
            "description": self.description,
            "disposal_capacity": self.disposal_capacity,
            "current_load": self.current_load,
            "recycling_efficiency": self.recycling_efficiency,
            "accepted_waste_types": [wt.name for wt in self.accepted_waste_types],
            "available_methods": [dm.name for dm in self.available_methods],
            "special_processes": self.special_processes,
            "equipment_quality": self.equipment_quality,
            "base_disposal_cost": self.base_disposal_cost,
            "recycling_fee": self.recycling_fee,
            "hazmat_surcharge": self.hazmat_surcharge,
            "operational": self.operational,
            "maintenance_level": self.maintenance_level,
            "reputation": self.reputation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WasteDisposalFacility':
        """Create facility from dictionary representation."""
        facility_type = FacilityType[data["facility_type"]]
        # Import WasteType locally to ensure we get the same instance
        from src.classes.waste_product import WasteType as WT
        accepted_waste_types = [WT[wt] for wt in data.get("accepted_waste_types", [])]
        available_methods = [DisposalMethod[dm] for dm in data.get("available_methods", [])]
        
        facility = cls(
            facility_id=data["facility_id"],
            station_id=data["station_id"],
            facility_type=facility_type,
            name=data["name"],
            description=data.get("description", ""),
            disposal_capacity=data.get("disposal_capacity", 1000.0),
            current_load=data.get("current_load", 0.0),
            recycling_efficiency=data.get("recycling_efficiency", 0.6),
            accepted_waste_types=accepted_waste_types,
            available_methods=available_methods,
            special_processes=data.get("special_processes", {}),
            equipment_quality=data.get("equipment_quality", 1.0),
            base_disposal_cost=data.get("base_disposal_cost", 5.0),
            recycling_fee=data.get("recycling_fee", 2.0),
            hazmat_surcharge=data.get("hazmat_surcharge", 3.0),
            operational=data.get("operational", True),
            maintenance_level=data.get("maintenance_level", 1.0),
            reputation=data.get("reputation", 1.0)
        )
        
        return facility


class WasteDisposalManager:
    """
    Manager class for handling waste disposal operations across multiple facilities.
    
    This class coordinates waste disposal between different facilities and
    provides utilities for finding appropriate disposal options.
    """
    
    def __init__(self):
        self.facilities: Dict[str, WasteDisposalFacility] = {}
    
    def add_facility(self, facility: WasteDisposalFacility) -> None:
        """Add a waste disposal facility to the manager."""
        self.facilities[facility.facility_id] = facility
    
    def remove_facility(self, facility_id: str) -> bool:
        """Remove a facility from the manager."""
        if facility_id in self.facilities:
            del self.facilities[facility_id]
            return True
        return False
    
    def get_facility(self, facility_id: str) -> Optional[WasteDisposalFacility]:
        """Get a facility by its ID."""
        return self.facilities.get(facility_id)
    
    def get_facilities_by_station(self, station_id: str) -> List[WasteDisposalFacility]:
        """Get all facilities at a specific station."""
        return [facility for facility in self.facilities.values() 
                if facility.station_id == station_id]
    
    def find_suitable_facilities(self, waste_product: WasteProduct, quantity: float,
                               station_id: Optional[str] = None) -> List[Tuple[WasteDisposalFacility, List[DisposalMethod]]]:
        """
        Find facilities that can handle the given waste product.
        
        Args:
            waste_product: The waste product to dispose
            quantity: Amount of waste to dispose
            station_id: Optional station ID to limit search
            
        Returns:
            List of tuples (facility, available_methods)
        """
        suitable_facilities = []
        
        facilities_to_check = (
            self.get_facilities_by_station(station_id) if station_id 
            else self.facilities.values()
        )
        
        for facility in facilities_to_check:
            can_accept, _ = facility.can_accept_waste(waste_product, quantity)
            if can_accept:
                available_methods = facility.get_available_methods(waste_product)
                if available_methods:
                    suitable_facilities.append((facility, available_methods))
        
        # Sort by facility quality and capacity
        suitable_facilities.sort(
            key=lambda x: (x[0].equipment_quality, x[0].disposal_capacity - x[0].current_load),
            reverse=True
        )
        
        return suitable_facilities
    
    def get_best_disposal_option(self, waste_product: WasteProduct, quantity: float,
                                station_id: Optional[str] = None,
                                prefer_recycling: bool = True) -> Optional[Tuple[WasteDisposalFacility, DisposalMethod, float]]:
        """
        Get the best disposal option for a waste product.
        
        Args:
            waste_product: The waste product to dispose
            quantity: Amount of waste to dispose
            station_id: Optional station ID to limit search
            prefer_recycling: Whether to prefer recycling when available
            
        Returns:
            Tuple of (facility, method, cost) or None if no options available
        """
        suitable_facilities = self.find_suitable_facilities(waste_product, quantity, station_id)
        
        if not suitable_facilities:
            return None
        
        best_option = None
        best_score = float('-inf')
        
        for facility, methods in suitable_facilities:
            for method in methods:
                cost = facility.calculate_disposal_cost(waste_product, quantity, method)
                
                # Calculate score based on cost, environmental impact, and preferences
                score = 1000.0 - cost  # Lower cost is better
                
                if method == DisposalMethod.RECYCLING and prefer_recycling:
                    score += 500.0  # Bonus for recycling
                
                if method == DisposalMethod.SOLAR_DISPOSAL:
                    score += 200.0  # Bonus for complete elimination
                
                # Penalty for high environmental impact methods
                if method == DisposalMethod.SPACE_JETTISON:
                    score -= waste_product.environmental_impact * 100.0
                
                # Bonus for high-quality facilities
                score += facility.equipment_quality * 50.0
                score += facility.maintenance_level * 30.0
                
                if score > best_score:
                    best_score = score
                    best_option = (facility, method, cost)
        
        return best_option
    
    def process_all_facilities_daily(self) -> Dict[str, Dict[str, Any]]:
        """Process daily operations for all facilities."""
        results = {}
        for facility_id, facility in self.facilities.items():
            results[facility_id] = facility.process_daily_operations()
        return results
    
    def get_system_capacity_report(self, station_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a capacity report for the waste disposal system."""
        facilities_to_check = (
            self.get_facilities_by_station(station_id) if station_id 
            else self.facilities.values()
        )
        
        total_capacity = 0.0
        total_load = 0.0
        facility_count = 0
        operational_count = 0
        
        for facility in facilities_to_check:
            total_capacity += facility.disposal_capacity
            total_load += facility.current_load
            facility_count += 1
            if facility.operational:
                operational_count += 1
        
        return {
            "total_facilities": facility_count,
            "operational_facilities": operational_count,
            "total_capacity": total_capacity,
            "current_load": total_load,
            "available_capacity": total_capacity - total_load,
            "system_utilization": (total_load / total_capacity * 100) if total_capacity > 0 else 0.0
        }


# Factory functions for creating common facility types
def create_basic_disposal_facility(station_id: str, facility_id: Optional[str] = None) -> WasteDisposalFacility:
    """Create a basic waste disposal facility."""
    if facility_id is None:
        facility_id = f"{station_id}_basic_disposal"
    
    return WasteDisposalFacility(
        facility_id=facility_id,
        station_id=station_id,
        facility_type=FacilityType.BASIC_DISPOSAL,
        name="Basic Waste Disposal",
        description="Standard waste disposal facility for common waste types"
    )


def create_recycling_center(station_id: str, facility_id: Optional[str] = None) -> WasteDisposalFacility:
    """Create a recycling center facility."""
    if facility_id is None:
        facility_id = f"{station_id}_recycling"
    
    return WasteDisposalFacility(
        facility_id=facility_id,
        station_id=station_id,
        facility_type=FacilityType.RECYCLING_CENTER,
        name="Recycling Center",
        description="Advanced facility specializing in waste recycling and material recovery"
    )


def create_hazmat_facility(station_id: str, facility_id: Optional[str] = None) -> WasteDisposalFacility:
    """Create a hazardous materials facility."""
    if facility_id is None:
        facility_id = f"{station_id}_hazmat"
    
    return WasteDisposalFacility(
        facility_id=facility_id,
        station_id=station_id,
        facility_type=FacilityType.HAZMAT_FACILITY,
        name="Hazmat Disposal Facility",
        description="Specialized facility for handling hazardous and toxic waste materials"
    )


def create_advanced_recycling_facility(station_id: str, facility_id: Optional[str] = None) -> WasteDisposalFacility:
    """Create an advanced recycling facility."""
    if facility_id is None:
        facility_id = f"{station_id}_advanced_recycling"
    
    return WasteDisposalFacility(
        facility_id=facility_id,
        station_id=station_id,
        facility_type=FacilityType.ADVANCED_RECYCLING,
        name="Advanced Recycling Facility",
        description="State-of-the-art facility with advanced recycling and material recovery capabilities"
    )


def create_research_facility(station_id: str, facility_id: Optional[str] = None) -> WasteDisposalFacility:
    """Create a research waste processing facility."""
    if facility_id is None:
        facility_id = f"{station_id}_research"
    
    return WasteDisposalFacility(
        facility_id=facility_id,
        station_id=station_id,
        facility_type=FacilityType.RESEARCH_FACILITY,
        name="Research Waste Processing Facility",
        description="Experimental facility for testing new waste processing technologies"
    )