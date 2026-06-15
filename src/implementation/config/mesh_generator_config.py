from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class MeshGeneratorConfig(MeshGeneratorConfigInterface):
    """
    Concrete implementation of the MeshGeneratorConfigInterface.
    Acts as an immutable data vessel for runtime configuration.
    
    Inherits from the Phase-2 contract to ensure 1:1 compliance.
    """
    def __init__(
        self, 
        solver_version: str, 
        tolerance: float, 
        max_element_size: float, 
        min_element_size: float
    ):
        # 1. Type Validation (Catches 'test_sensitivity_invalid_types')
        if not isinstance(solver_version, str):
            raise TypeError(f"solver_version must be str, got {type(solver_version).__name__}")
        
        numeric_fields = {
            "tolerance": tolerance, 
            "max_element_size": max_element_size, 
            "min_element_size": min_element_size
        }
        
        for name, value in numeric_fields.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be int or float, got {type(value).__name__}")

        # 2. Range Validation (Catches 'test_sensitivity_invalid_numeric_ranges', 
        # 'test_physics_tolerance_validity', 'test_physics_element_size_validity')
        if tolerance <= 0:
            raise ValueError(f"Tolerance must be positive. Got: {tolerance}")
        
        if min_element_size <= 0 or max_element_size <= 0:
            raise ValueError("Element sizes must be > 0.")
            
        # 3. Relationship Validation (Catches 'test_sensitivity_element_size_relationship')
        if min_element_size >= max_element_size:
            raise ValueError(
                f"min_element_size ({min_element_size}) must be less than "
                f"max_element_size ({max_element_size})"
            )

        # Assignments (Only occur if validation passes)
        self.solver_version = solver_version
        self.tolerance = tolerance
        self.max_element_size = max_element_size
        self.min_element_size = min_element_size