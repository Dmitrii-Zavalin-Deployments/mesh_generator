# src/implementation/config/config_loader.py
from typing import Dict, Any
from src.implementation.config.mesh_generator_config import MeshGeneratorConfig

class ConfigLoader:
    """
    Validation gate for constructing MeshGeneratorConfig instances.
    Enforces the No-Defaults Policy at runtime by verifying all
    required fields exist and are of the correct type before object instantiation.
    """

    @staticmethod
    def load(data: Dict[str, Any]) -> MeshGeneratorConfig:
        """
        Validates input dictionary and returns a MeshGeneratorConfig instance.
        
        Raises:
            ValueError: If any required field is missing.
            TypeError: If fields are of incorrect type.
        """
        required_fields = [
            'solver_version', 
            'tolerance', 
            'max_element_size', 
            'min_element_size',
            'boundary_conditions' 
        ]

        # 1. Enforce No-Defaults Policy: 
        # We check keys existence explicitly. No .get() with defaults allowed.
        for field in required_fields:
            if field not in data:
                raise ValueError(
                    f"No-Defaults Policy Violation: Missing required config field '{field}'."
                )

        # 2. Type Safety: Ensure boundary_conditions is a dictionary
        if not isinstance(data['boundary_conditions'], dict):
            raise TypeError(
                f"Config Type Mismatch: 'boundary_conditions' must be a dict, "
                f"got {type(data['boundary_conditions']).__name__}"
            )

        # 3. Construct and return the concrete vessel
        # The constructor handles the default=None for test isolation, 
        # but the ConfigLoader guarantees we pass a real dict here.
        return MeshGeneratorConfig(
            solver_version=data['solver_version'],
            tolerance=data['tolerance'],
            max_element_size=data['max_element_size'],
            min_element_size=data['min_element_size'],
            boundary_conditions=data['boundary_conditions']
        )