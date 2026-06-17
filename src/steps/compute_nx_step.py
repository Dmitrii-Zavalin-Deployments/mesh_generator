# src/implementation/steps/compute_nx_step.py
import math
from src.interfaces.steps.compute_nx_interface import ComputeNxInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeNxStep(ComputeNxInterface):
    """
    Concrete implementation of S8 — compute_nx.

    Calculates the number of grid cells in the X direction based on 
    the bounding box span and the maximum allowable element size.
    """

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Computes results.grid.nx.

        Logic:
            1. Read x_min and x_max from the Sovereign Container.
            2. Compute the spatial span.
            3. Calculate nx using config.max_element_size (rounding up to ensure 
               the cell size limit is strictly respected).
            4. Write the integer result to state.results_grid['nx'].
        """
        # 1. Access required inputs (Direct access assumes validation by Orchestrator)
        x_min = state.results_grid['x_min']
        x_max = state.results_grid['x_max']

        # 2. Compute span
        span = x_max - x_min
        
        # 3. Calculate resolution
        # We use math.ceil to ensure that the resulting cell size does not exceed 
        # the max_element_size specified in the configuration.
        if span <= 0:
            nx = 1  # Minimal valid resolution for non-degenerate geometry
        else:
            nx = math.ceil(span / config.max_element_size)
            
            # Ensure at least 1 cell exists
            if nx < 1:
                nx = 1

        # 4. Write result
        state.results_grid['nx'] = int(nx)