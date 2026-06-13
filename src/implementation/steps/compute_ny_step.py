# src/implementation/steps/compute_ny_step.py
import math
from src.interfaces.step_interfaces.compute_ny_interface import ComputeNyInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeNyStep(ComputeNyInterface):
    """
    Concrete implementation of S9 — compute_ny.

    Calculates the number of grid cells in the Y direction based on 
    the bounding box span and the maximum allowable element size.
    """

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Computes results.grid.ny.

        Logic:
            1. Read y_min and y_max from the Sovereign Container.
            2. Compute the spatial span.
            3. Calculate ny using config.max_element_size (rounding up to ensure 
               the cell size limit is strictly respected).
            4. Write the integer result to state.results_grid['ny'].
        """
        # 1. Access required inputs
        # The contract requires y_min and y_max to be present in the results_grid
        y_min = state.results_grid.get('y_min')
        y_max = state.results_grid.get('y_max')
        
        if y_min is None or y_max is None:
            raise ValueError("S9 compute_ny requires results.grid.y_min and y_max to be computed first.")

        # 2. Compute span
        span = y_max - y_min
        
        # 3. Calculate resolution
        # Use math.ceil to ensure the resulting cell size does not exceed max_element_size
        if span <= 0:
            ny = 1  # Minimal valid resolution for non-degenerate geometry
        else:
            ny = math.ceil(span / config.max_element_size)
            
            # Ensure at least 1 cell exists
            if ny < 1:
                ny = 1

        # 4. Write result
        state.results_grid['ny'] = int(ny)