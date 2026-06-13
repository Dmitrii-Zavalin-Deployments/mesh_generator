# src/implementation/steps/compute_y_max_step.py
from src.interfaces.step_interfaces.compute_y_max_interface import ComputeYMaxInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeYMaxStep(ComputeYMaxInterface):
    """
    Concrete implementation of S5 — compute_y_max.

    Calculates the maximum Y-coordinate of the parsed geometric model
    and updates the Sovereign Container state with the normalized value.
    """

    def __init__(self, geometry_model):
        """
        Initializes the step with the internal geometric model 
        parsed in step S1.
        """
        self.geometry_model = geometry_model

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Computes results.grid.y_max from the geometric model.
        
        Logic:
            1. Query internal geometry for the maximum Y boundary.
            2. Apply tolerance from config to normalize the result.
            3. Update state.results_grid['y_max'].
        """
        # 1. Perform numerical calculation
        # Accessing index [1] of the bounding box max coordinates
        calculated_y_max = self.geometry_model.get_bounding_box_max()[1]

        # 2. Apply config tolerance for deterministic output
        normalized_y_max = round(calculated_y_max / config.tolerance) * config.tolerance
            
        state.results_grid['y_max'] = float(normalized_y_max)