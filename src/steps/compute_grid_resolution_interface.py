"""
src/steps/compute_grid_resolution_interface.py

Step 3: Compute Grid Resolution Interface
Responsible for determining the computational density of the grid 
based on the physical domain extents and the user-provided configuration.
"""

from typing import Any
import math

from src.steps.step_interface_base import StepInterfaceBase
from src.state.mesh_generator_state import MeshGeneratorStateInterface

class ComputeGridResolutionInterface(StepInterfaceBase):
    """
    Resolution Architect Interface.
    Defines the contract for consuming physical domain extents and calculating 
    the integer grid counts (nx, ny, nz) required for the simulation.
    """
    
    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: Any) -> None:
        """
        Calculates grid resolution cells.
        
        This step bridges the gap between the continuous physical space 
        (meters/inches) and the discrete computational space (cells).
        
        Args:
            state: The unified Sovereign State container.
            config: Configuration dictionary expected to contain 'cell_size'.
            
        Raises:
            ValueError: If 'cell_size' is missing or invalid (<= 0).
            KeyError: If grid extents were not initialized by Step 2.
        """
        # ----------------------------------------------------------------------
        # STEP 1: CONFIGURATION & DATA ACQUISITION
        # ----------------------------------------------------------------------
        # We fetch the physical extents we calculated in Step 2.
        grid = state["results"]["grid"]
        
        # We fetch the target cell size from config.
        # Ensure your config object has a 'cell_size' key.
        cell_size = config.get("cell_size")
        
        if cell_size is None or cell_size <= 0:
            raise ValueError(
                f"[Compute Resolution Error] Invalid or missing 'cell_size' in config: {cell_size}"
            )

        # ----------------------------------------------------------------------
        # STEP 2: DISCRETIZATION LOGIC
        # ----------------------------------------------------------------------
        # Calculate lengths of each dimension
        dx = grid["x_max"] - grid["x_min"]
        dy = grid["y_max"] - grid["y_min"]
        dz = grid["z_max"] - grid["z_min"]

        # Calculate number of cells (rounding up to ensure coverage)
        nx = math.ceil(dx / cell_size)
        ny = math.ceil(dy / cell_size)
        nz = math.ceil(dz / cell_size)

        # Ensure a minimum grid of 1x1x1 to prevent invalid states
        nx = max(nx, 1)
        ny = max(ny, 1)
        nz = max(nz, 1)

        # ----------------------------------------------------------------------
        # STEP 3: SOVEREIGN STATE INJECTION
        # ----------------------------------------------------------------------
        # Update the grid with the calculated resolution.
        state["results"]["grid"]["nx"] = nx
        state["results"]["grid"]["ny"] = ny
        state["results"]["grid"]["nz"] = nz