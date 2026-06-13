# src/implementation/steps/compute_x_min_step.py
from src.interfaces.step_interfaces.compute_x_min_interface import ComputeXMinInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeXMinStep(ComputeXMinInterface):
    """
    Concrete implementation of S2 — compute_x_min.
    
    This step calculates the minimum X-coordinate of the parsed geometric model
    and updates the Sovereign Container state accordingly.
    """

    def __init__(self, geometry_model):
        """
        Initializes the step with the internal geometric model 
        parsed in the previous step (S1).
        """
        self.geometry_model = geometry_model

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Computes results.grid.x_min from the geometric model.
        
        Logic:
            1. Query internal geometry for the minimum X boundary.
            2. Apply tolerance from config to normalize the result.
            3. Update state.results_grid['x_min'].
        """
        # 1. Perform numerical calculation
        # Accessing the geometric model to calculate the bounding box x_min
        calculated_x_min = self.geometry_model.get_bounding_box_min()[0]

        # 2. Apply config tolerance
        # Example: snapping or rounding based on config.tolerance
        normalized_x_min = round(calculated_x_min / config.tolerance) * config.tolerance

        # 3. Update the Sovereign Container
        # Per Constitution: Only update the specific property assigned to this step
        if state.results_grid is None:
            state.results_grid = {}
            
        state.results_grid['x_min'] = float(normalized_x_min)