# src/implementation/steps/compute_nz_step.py
import math
from src.interfaces.step_interfaces.compute_nz_interface import ComputeNzInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeNzStep(ComputeNzInterface):
    """
    Concrete implementation of S10 — compute_nz.

    Calculates the number of grid cells in the Z direction based on 
    the bounding box span and the maximum allowable element size.
    """

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Computes results.grid.nz.

        Logic:
            1. Read z_min and z_max from the Sovereign Container.
            2. Compute the spatial span.
            3. Calculate nz using config.max_element_size (rounding up to ensure 
               the cell size limit is strictly respected).
            4. Write the integer result to state.results_grid['nz'].
        """
        # 1. Access required inputs (Orchestrator guarantees valid state)
        z_min = state.results_grid['z_min']
        z_max = state.results_grid['z_max']

        # 2. Compute span
        span = z_max - z_min
        
        # 3. Calculate resolution
        # Use math.ceil to ensure the resulting cell size does not exceed max_element_size
        if span <= 0:
            nz = 1  # Minimal valid resolution for non-degenerate geometry
        else:
            nz = math.ceil(span / config.max_element_size)
            
            # Ensure at least 1 cell exists
            if nz < 1:
                nz = 1

        # 4. Write result
        state.results_grid['nz'] = int(nz)