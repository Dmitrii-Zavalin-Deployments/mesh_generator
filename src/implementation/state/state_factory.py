# src/implementation/state/state_factory.py
from typing import Dict, Any
from src.implementation.state.mesh_generator_state import MeshGeneratorState

class StateFactory:
    """
    Validation gate for constructing MeshGeneratorState instances.
    Enforces the No-Defaults Policy at runtime.
    """

    @staticmethod
    def create(data: Dict[str, Any]) -> MeshGeneratorState:
        """
        Validates raw input data against the required schema.
        Raises ValueError if any field is missing, preventing
        partial or invalid state instantiation.
        """
        required_fields = [
            'inputs_step_file', 
            'results_grid', 
            'results_mask', 
            'results_boundary_conditions'
        ]

        # 1. Enforce No-Defaults Policy:
        # Check that every mandatory field exists in the input dictionary.
        for field in required_fields:
            if field not in data:
                raise ValueError(
                    f"No-Defaults Policy Violation: Missing required field '{field}' in State data."
                )

        # 2. Construct and return the concrete vessel
        # By this point, we are guaranteed that all fields are present.
        return MeshGeneratorState(
            inputs_step_file=data['inputs_step_file'],
            results_grid=data['results_grid'],
            results_mask=data['results_mask'],
            results_boundary_conditions=data['results_boundary_conditions']
        )