# src/implementation/steps/compute_x_max_step.py
from src.interfaces.step_interfaces.compute_x_max_interface import ComputeXMaxInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeXMaxStep(ComputeXMaxInterface):
    """
    Concrete implementation of S3 — compute_x_max.
    
    Calculates the maximum X-coordinate of the parsed geometric model
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
        Computes results.grid.x_max from the geometric model.
        
        Logic:
            1. Query internal geometry for the maximum X boundary.
            2. Apply tolerance from config to normalize the result.
            3. Update state.results_grid['x_max'].
        """
        # 1. Perform numerical calculation
        # Accessing the geometric model to calculate the bounding box x_max
        calculated_x_max = self.geometry_model.get_bounding_box_max()[0]

        # 2. Apply config tolerance
        # Normalizing based on config.tolerance per the system architecture
        normalized_x_max = round(calculated_x_max / config.tolerance) * config.tolerance
            
        state.results_grid['x_max'] = float(normalized_x_max)