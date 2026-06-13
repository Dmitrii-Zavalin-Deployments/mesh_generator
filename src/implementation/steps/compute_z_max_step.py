# src/implementation/steps/compute_z_max_step.py
from src.interfaces.step_interfaces.compute_z_max_interface import ComputeZMaxInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeZMaxStep(ComputeZMaxInterface):
    """
    Concrete implementation of S7 — compute_z_max.

    Calculates the maximum Z-coordinate of the parsed geometric model
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
        Computes results.grid.z_max from the geometric model.
        
        Logic:
            1. Query internal geometry for the maximum Z boundary.
            2. Apply tolerance from config to normalize the result.
            3. Update state.results_grid['z_max'].
        """
        # 1. Perform numerical calculation
        # Accessing index [2] of the bounding box max coordinates (Z-axis)
        calculated_z_max = self.geometry_model.get_bounding_box_max()[2]

        # 2. Apply config tolerance for deterministic normalization
        normalized_z_max = round(calculated_z_max / config.tolerance) * config.tolerance
            
        state.results_grid['z_max'] = float(normalized_z_max)