# src/implementation/steps/compute_boundary_condition_type_step.py
from src.interfaces.step_interfaces.compute_boundary_condition_type_interface import ComputeBoundaryConditionTypeInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeBoundaryConditionTypeStep(ComputeBoundaryConditionTypeInterface):
    """
    Concrete implementation of S12.i.2 — compute_boundary_condition_type.

    Determines the physical boundary condition type based on spatial location.
    The validation of inputs is handled centrally by the Orchestrator, allowing
    this class to focus purely on the transformation logic.
    """

    def __init__(self, geometry_model):
        """
        Initializes the step with the internal geometric model.
        """
        self.geometry_model = geometry_model

    def run(self, state: MeshGeneratorStateInterface, config, index: int) -> None:
        """
        Computes results.boundary_conditions[index].type using a concrete 
        mapping strategy.
        """
        # 1. Access location (Validation is performed by the Orchestrator)
        location = state.results_boundary_conditions[index]["location"]
        
        # 2. Concrete implementation: Explicit mapping
        # This replaces the previous placeholder comments and logic
        type_map = {
            "x_min": "inlet",
            "x_max": "outlet",
            "y_min": "wall",
            "y_max": "wall",
            "z_min": "symmetry",
            "z_max": "symmetry"
        }
        
        if location not in type_map:
            raise ValueError(f"Unknown boundary location encountered: {location}")
            
        # 3. Write result
        state.results_boundary_conditions[index]["type"] = type_map[location]