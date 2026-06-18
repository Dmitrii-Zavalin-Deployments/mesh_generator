"""
src/steps/compute_grid_extents_interface.py

Step 2: Compute Grid Extents
Responsible for mapping the raw geometric bounding box (from transients)
into the structured grid domain representation (in results).
"""

from typing import Any
from src.steps.step_interface_base import StepInterfaceBase
from src.state.mesh_generator_state import MeshGeneratorStateInterface

class ComputeGridExtentsInterface(StepInterfaceBase):
    """
    Spatial Architect Step.
    Consumes the pre-computed bounding box from the transient geometry 
    and initializes the CFD grid domain within the results.
    """
    
    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: Any) -> None:
        """
        Maps geometric extents to the CFD grid schema.
        
        This step acts as a bridge between the raw B-Rep geometry and the 
        computational mesh. It performs no heavy geometric lifting; it strictly 
        performs a data transformation/mapping.
        
        Args:
            state: The unified Sovereign State container.
            config: Optional configuration (e.g., domain padding or buffer zones).
            
        Raises:
            KeyError: If the parsing step (S1) did not populate the bounding_box.
        """
        # ----------------------------------------------------------------------
        # STEP 1: TRANSIENT DATA ACQUISITION
        # ----------------------------------------------------------------------
        # Extract the bounding box calculated in Step 1 (ParseGeometry)
        # Note: We are now working with standard Python floats.
        bbox = state["transients"]["bounding_box"]

        # ----------------------------------------------------------------------
        # STEP 2: GRID DOMAIN MAPPING
        # ----------------------------------------------------------------------
        grid_extents = {
            "x_min": bbox["x_min"],
            "x_max": bbox["x_max"],
            "y_min": bbox["y_min"],
            "y_max": bbox["y_max"],
            "z_min": bbox["z_min"],
            "z_max": bbox["z_max"],
            # Initialize resolution placeholders (to be computed by Step 3)
            "nx": 0, 
            "ny": 0,
            "nz": 0
        }

        # ----------------------------------------------------------------------
        # STEP 3: SOVEREIGN STATE INJECTION
        # ----------------------------------------------------------------------
        state["results"]["grid"] = grid_extents
        
        # ----------------------------------------------------------------------
        # STEP 4: VERIFICATION
        # ----------------------------------------------------------------------
        if (grid_extents["x_max"] <= grid_extents["x_min"] or 
            grid_extents["y_max"] <= grid_extents["y_min"] or 
            grid_extents["z_max"] <= grid_extents["z_min"]):
            raise ValueError("[Compute Extents Error] Computed grid volume is zero or negative.")