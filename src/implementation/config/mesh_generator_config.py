# src/implementation/config/mesh_generator_config.py

import math
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
        min_element_size: float,
        boundary_conditions: dict
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
            
            # Explicit NaN check
            if math.isnan(value):
                raise ValueError(f"{name} cannot be NaN.")

        # 2. Range Validation
        if tolerance <= 0:
            raise ValueError(f"Tolerance must be positive. Got: {tolerance}")
        
        if min_element_size <= 0 or max_element_size <= 0:
            raise ValueError("Element sizes must be > 0.")
            
        # 3. Relationship Validation
        if min_element_size >= max_element_size:
            raise ValueError(
                f"min_element_size ({min_element_size}) must be less than "
                f"max_element_size ({max_element_size})"
            )

        # Assignments (Use super() to bypass the immutability guard during initialization)
        super().__setattr__('solver_version', solver_version)
        super().__setattr__('tolerance', tolerance)
        super().__setattr__('max_element_size', max_element_size)
        super().__setattr__('min_element_size', min_element_size)
        super().__setattr__('boundary_conditions', boundary_conditions)

    def get_values_for_type(self, bc_type: str):
        """
        Retrieves configuration values. 
        Enforces No-Defaults Policy: If type is missing, we raise an error.
        """
        if bc_type not in self.boundary_conditions:
            raise ValueError(
                f"No-Defaults Policy Violation: No configuration provided for BC type: '{bc_type}'"
            )
        
        return self.boundary_conditions[bc_type]

    def __setattr__(self, name, value):
        """
        Enforce immutability: Prevent modifications after object creation.
        This forces the test to raise an AttributeError if it tries to corrupt state.
        """
        if hasattr(self, name):
            raise AttributeError(f"Cannot modify immutable config attribute: '{name}'")
        super().__setattr__(name, value)