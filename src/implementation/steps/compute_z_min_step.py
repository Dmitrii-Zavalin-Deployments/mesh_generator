# src/implementation/steps/compute_z_min_step.py
from src.interfaces.step_interfaces.compute_z_min_interface import ComputeZMinInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeZMinStep(ComputeZMinInterface):
    """
    Concrete implementation of S6 — compute_z_min.

    Calculates the minimum Z-coordinate of the parsed geometric model
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
        Computes results.grid.z_min from the geometric model.
        
        Logic:
            1. Query internal geometry for the minimum Z boundary.
            2. Apply tolerance from config to normalize the result.
            3. Update state.results_grid['z_min'].
        """
        # 1. Perform numerical calculation
        # Accessing index [2] of the bounding box min coordinates (Z-axis)
        calculated_z_min = self.geometry_model.get_bounding_box_min()[2]

        # 2. Apply config tolerance for deterministic normalization
        normalized_z_min = round(calculated_z_min / config.tolerance) * config.tolerance
            
        state.results_grid['z_min'] = float(normalized_z_min)