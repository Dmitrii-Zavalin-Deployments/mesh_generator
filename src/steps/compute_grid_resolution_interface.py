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
        (meters) and the discrete computational space (cells).
        
        Args:
            state: The unified Sovereign State container.
            config: Configuration dictionary expected to contain 'max_element_size'.
            
        Raises:
            ValueError: If 'max_element_size' is missing or invalid (<= 0).
            KeyError: If grid extents were not initialized by the previous step.
        """
        # ----------------------------------------------------------------------
        # STEP 1: CONFIGURATION & DATA ACQUISITION
        # ----------------------------------------------------------------------
        # We fetch the physical extents we calculated in the previous step.
        grid = state["results"]["grid"]
        
        # We fetch the target element size from config (Schema: mesh_generator_config_schema.json)
        target_element_size = config.get("max_element_size")
        
        if target_element_size is None or target_element_size <= 0:
            raise ValueError(
                f"[Compute Resolution Error] Invalid or missing 'max_element_size' in config: {target_element_size}"
            )

        # ----------------------------------------------------------------------
        # STEP 2: DISCRETIZATION LOGIC
        # ----------------------------------------------------------------------
        # Calculate lengths of each dimension
        dx = grid["x_max"] - grid["x_min"]
        dy = grid["y_max"] - grid["y_min"]
        dz = grid["z_max"] - grid["z_min"]

        # Calculate number of cells (rounding up ensures cells are <= max_element_size)
        nx = math.ceil(dx / target_element_size)
        ny = math.ceil(dy / target_element_size)
        nz = math.ceil(dz / target_element_size)

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