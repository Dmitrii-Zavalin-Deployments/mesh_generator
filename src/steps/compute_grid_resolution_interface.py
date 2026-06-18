"""
src/steps/compute_grid_resolution_interface.py

Step 3: Compute Grid Resolution Interface
Defines the strict execution contract for determining the computational density 
of the grid based on continuous physical extents and discrete config constraints.
"""

from typing import Any
from src.steps.step_interface_base import StepInterfaceBase
from src.state.mesh_generator_state import MeshGeneratorStateInterface

class ComputeGridResolutionInterface(StepInterfaceBase):
    """
    Resolution Architect Interface.
    
    Enforces the formal contract for consuming physical domain extents and calculating 
    the integer grid counts (nx, ny, nz) required for the uniform simulation grid.
    """
    
    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: Any) -> None:
        """
        Executes the resolution calculations within the defined 'Resolution Corridor'.

        Args:
            state: The unified Sovereign State container to be modified.
            config: Read-only pipeline configuration adjustments containing size parameters.

        Raises:
            NotImplementedError: For direct invocations of the interface base class.
        """
        raise NotImplementedError("Concrete resolution steps must implement the run() method.")