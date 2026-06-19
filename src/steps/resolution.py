# src/steps/resolution.py
import numpy as np
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer, GridState

class ResolutionStep(StepInterface):
    """
    Refactored S8-S10: Grid Resolution.
    
    This step acts as the 'spatial discretizer'. It bridges the gap between 
    continuous physical geometry (defined by BBox) and the discrete computational 
    domain (the nx, ny, nz grid).
    """
    
    __slots__ = () # Stateless: Logic only

    def execute(self, container: SovereignContainer):
        """
        Executes the grid resolution calculation.
        
        Args:
            container: The SovereignContainer instance. 
                       Requires a populated 'bbox' from TracingStep and 
                       a 'max_element_size' configuration.
        """
        
        # GUARD CLAUSE: Pipeline Topology Validation.
        # We enforce that the TracingStep has already finished. If 'bbox' is None,
        # we have no physical extent to map to a grid, and the process must halt.
        if container.bbox is None:
            raise RuntimeError(
                "CONSTITUTION VIOLATION: 'bbox' is None. "
                "TracingStep must be executed before ResolutionStep."
            )

        # UNPACKING: Translate the tuple into readable spatial coordinates.
        # The Bnd_Box provides the precise physical limits of the CAD geometry.
        x_min, y_min, z_min, x_max, y_max, z_max = container.bbox
        
        # PARAMETRIZATION: Retrieve the resolution constraint.
        # 'max_element_size' is the user-defined fidelity. A smaller value 
        # produces a finer grid (more cells).
        max_el = container.max_element_size
        
        # DISCRETIZATION LOGIC:
        # 1. Calculation: (Span / max_element_size) gives the number of intervals.
        # 2. np.ceil: We always round up. It is better to have a slightly finer 
        #    grid that fully encapsulates the geometry than to truncate a cell 
        #    and lose physical boundary information.
        # 3. max(1, ...): The "Singularity Shield." Regardless of how small the 
        #    geometry is, we enforce at least 1 cell to prevent a zero-width grid 
        #    (which would cause the solver to crash).
        nx = max(1, int(np.ceil((x_max - x_min) / max_el)))
        ny = max(1, int(np.ceil((y_max - y_min) / max_el)))
        nz = max(1, int(np.ceil((z_max - z_min) / max_el)))
        
        # STATE PERSISTENCE:
        # We wrap the results in a 'GridState' object. This acts as an immutable
        # contract for the next steps (Categorization, BCs). By injecting this 
        # into 'container.grid', we trigger the SovereignContainer's setter 
        # validation to ensure the data is properly typed.
        container.grid = GridState(
            x_min=x_min, x_max=x_max,
            y_min=y_min, y_max=y_max,
            z_min=z_min, z_max=z_max,
            nx=nx, ny=ny, nz=nz
        )