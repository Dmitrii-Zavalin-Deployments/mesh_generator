# src/implementation/steps/compute_y_min_step.py
from src.interfaces.step_interfaces.compute_y_min_interface import ComputeYMinInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeYMinStep(ComputeYMinInterface):
    """
    Concrete implementation of S4 — compute_y_min.

    Calculates the minimum Y-coordinate of the parsed geometric model
    and updates the Sovereign Container state.
    """

    def __init__(self, geometry_model):
        """
        Initializes the step with the internal geometric model 
        parsed in step S1.
        """
        self.geometry_model = geometry_model

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Computes results.grid.y_min from the geometric model.
        
        Logic:
            1. Query internal geometry for the minimum Y boundary.
            2. Apply tolerance from config to normalize the result.
            3. Update state.results_grid['y_min'].
        """
        # 1. Perform numerical calculation
        # Querying the bounding box; index [1] represents the Y-axis
        calculated_y_min = self.geometry_model.get_bounding_box_min()[1]

        # 2. Apply config tolerance to ensure deterministic normalization
        normalized_y_min = round(calculated_y_min / config.tolerance) * config.tolerance

        # 3. Update the Sovereign Container
        # Ensure the results_grid dictionary is initialized
        if state.results_grid is None:
            state.results_grid = {}
            
        state.results_grid['y_min'] = float(normalized_y_min)