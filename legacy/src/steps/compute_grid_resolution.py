"""
src/steps/compute_grid_resolution.py

Concrete implementation of the Step 3 contract.
Handles the physical-to-discrete discretization math and handles stability enforcement.
"""

from typing import Any
import math

from src.steps.compute_grid_resolution_interface import ComputeGridResolutionInterface
from src.state.mesh_generator_state import MeshGeneratorStateInterface

class ComputeGridResolutionStep(ComputeGridResolutionInterface):
    """
    Concrete worker class implementing the uniform grid resolution calculation.
    """

    def run(self, state: MeshGeneratorStateInterface, config: Any) -> None:
        """
        Calculates grid resolution cells using max_element_size and min_element_size bounds.
        """
        # ----------------------------------------------------------------------
        # STEP 1: CONFIGURATION & DATA ACQUISITION
        # ----------------------------------------------------------------------
        grid = state["results"]["grid"]
        
        # Pull bounds from configuration mapping
        target_max = config.get("max_element_size")
        limit_min = config.get("min_element_size")
        
        if target_max is None or target_max <= 0:
            raise ValueError(
                f"[Compute Resolution Error] 'max_element_size' is required and must be > 0. Provided: {target_max}"
            )

        # ----------------------------------------------------------------------
        # STEP 2: DISCRETIZATION LOGIC
        # ----------------------------------------------------------------------
        # Calculate lengths of each dimension
        dx = grid["x_max"] - grid["x_min"]
        dy = grid["y_max"] - grid["y_min"]
        dz = grid["z_max"] - grid["z_min"]

        # Calculate number of cells (rounding up ensures cells do not exceed max allowed size)
        nx = max(math.ceil(dx / target_max), 1)
        ny = max(math.ceil(dy / target_max), 1)
        nz = max(math.ceil(dz / target_max), 1)

        # ----------------------------------------------------------------------
        # STEP 3: STABILITY GUARD (The 'Corridor' Check)
        # ----------------------------------------------------------------------
        # Derive the discrete cell sizes resulting from the ceiling operation
        actual_dx = dx / nx
        actual_dy = dy / ny
        actual_dz = dz / nz

        # Validate that discretization does not violate the solver's stability limit
        if limit_min is not None:
            if actual_dx < limit_min or actual_dy < limit_min or actual_dz < limit_min:
                raise ValueError(
                    f"[Compute Resolution Error] Resolution corridor violation: "
                    f"Requested max_element_size ({target_max}) results in cells "
                    f"too small (min actual dim: {min(actual_dx, actual_dy, actual_dz):.4f}) "
                    f"relative to min_element_size ({limit_min}). Simulation unstable."
                )

        # ----------------------------------------------------------------------
        # STEP 4: SOVEREIGN STATE INJECTION
        # ----------------------------------------------------------------------
        state["results"]["grid"]["nx"] = nx
        state["results"]["grid"]["ny"] = ny
        state["results"]["grid"]["nz"] = nz