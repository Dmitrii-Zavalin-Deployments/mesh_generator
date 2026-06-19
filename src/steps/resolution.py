# src/steps/resolution.py
import numpy as np
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer, GridState
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.GProp import GProp_GProps

def get_min_feature_size(shape) -> float:
    """
    Utility function to analyze the geometry.
    In a real implementation, you would use BRepExtrema or 
    Medial Axis analysis here to find the actual minimum thickness.
    For this prototype, we return a mock value representing feature detection.
    """
    # TODO: Implement robust feature detection here (e.g., using BRepExtrema)
    return 0.1 

class ResolutionStep(StepInterface):
    """
    Refactored S8-S10: Grid Resolution with Adaptive Fidelity.
    
    Dynamically adjusts grid resolution based on the minimum geometric 
    feature size to prevent aliasing of thin structural members.
    """
    
    __slots__ = () # Stateless: Logic only

    def execute(self, container: SovereignContainer):
        """
        Executes the grid resolution calculation with adaptive constraints.
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

        # 1. INSPECTION: Determine the thinnest feature
        min_feature = get_min_feature_size(container.cad_solid)
        
        # 2. CONSTRAINED ADAPTATION:
        # Check against the container's resolution floor and ceiling.
        if min_feature < container.min_element_size:
            raise RuntimeError(
                f"GEOMETRY VIOLATION: Thinnest feature ({min_feature}) is smaller "
                f"than the minimum allowed element size ({container.min_element_size})."
            )
        
        # Determine the effective resolution:
        # If the feature is smaller than the user-desired max, we use the feature size 
        # (to avoid aliasing). Otherwise, we cap it at the user-defined max.
        adaptive_el = min(container.max_element_size, max(container.min_element_size, min_feature))
        
        # UNPACKING: Translate the tuple into readable spatial coordinates.
        # The Bnd_Box provides the precise physical limits of the CAD geometry.
        x_min, y_min, z_min, x_max, y_max, z_max = container.bbox
        
        # 4. DISCRETIZATION LOGIC
        # We use the 'adaptive_el' instead of the global 'max_element_size'.
        # 1. Calculation: (Span / max_element_size) gives the number of intervals.
        # 2. np.ceil: We always round up. It is better to have a slightly finer 
        #    grid that fully encapsulates the geometry than to truncate a cell 
        #    and lose physical boundary information.
        # 3. max(1, ...): The "Singularity Shield." Regardless of how small the 
        #    geometry is, we enforce at least 1 cell to prevent a zero-width grid 
        #    (which would cause the solver to crash).
        nx = max(1, int(np.ceil((x_max - x_min) / adaptive_el)))
        ny = max(1, int(np.ceil((y_max - y_min) / adaptive_el)))
        nz = max(1, int(np.ceil((z_max - z_min) / adaptive_el)))
        
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