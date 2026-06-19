# src/steps/resolution.py
import numpy as np
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer, GridState

# OCC Imports for feature detection
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.BRepGProp import brepgprop_LinearProperties
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.Bnd import Bnd_Box

def get_min_feature_size(shape) -> float:
    """
    Utility function to analyze the geometry for adaptive fidelity.
    
    It traverses the topology of the shape to find the shortest edge,
    which typically represents the thinnest feature (e.g., plate thickness).
    Falls back to the overall bounding box minimum dimension if no valid edges exist.
    """
    explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    min_length = float('inf')
    
    # 1. Traversal: Inspect all edges in the geometry
    while explorer.More():
        edge = explorer.Current()
        props = GProp_GProps()
        
        # Calculate linear properties. For edges, Mass() returns the length.
        brepgprop_LinearProperties(edge, props)
        length = props.Mass()
        
        # Filter out degenerate/zero-length artifacts
        if length > 1e-7:
            min_length = min(min_length, length)
            
        explorer.Next()
        
    # 2. Return shortest edge if found
    if min_length != float('inf'):
        return float(min_length)
        
    # 3. Fallback: If no edges exist (e.g., pure mathematical spheres), 
    # use the smallest bounding box dimension.
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    
    return float(min(xmax - xmin, ymax - ymin, zmax - zmin))


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
                f"GEOMETRY VIOLATION: Thinnest feature ({min_feature:.4f}) is smaller "
                f"than the minimum allowed element size ({container.min_element_size:.4f})."
            )
        
        # Determine the effective resolution:
        # If the feature is smaller than the user-desired max, we use the feature size 
        # (to avoid aliasing). Otherwise, we cap it at the user-defined max.
        adaptive_el = min(container.max_element_size, max(container.min_element_size, min_feature))
        
        # 3. UNPACKING: Translate the tuple into readable spatial coordinates.
        # The Bnd_Box provides the precise physical limits of the CAD geometry.
        x_min, y_min, z_min, x_max, y_max, z_max = container.bbox
        
        # 4. DISCRETIZATION LOGIC
        # We use the 'adaptive_el' instead of the global 'max_element_size'.
        # 1. Calculation: (Span / adaptive_el) gives the number of intervals.
        # 2. np.ceil: We always round up. It is better to have a slightly finer 
        #    grid that fully encapsulates the geometry than to truncate a cell 
        #    and lose physical boundary information.
        # 3. max(1, ...): The "Singularity Shield." Regardless of how small the 
        #    geometry is, we enforce at least 1 cell to prevent a zero-width grid 
        #    (which would cause the solver to crash).
        nx = max(1, int(np.ceil((x_max - x_min) / adaptive_el)))
        ny = max(1, int(np.ceil((y_max - y_min) / adaptive_el)))
        nz = max(1, int(np.ceil((z_max - z_min) / adaptive_el)))
        
        # 5. STATE PERSISTENCE:
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