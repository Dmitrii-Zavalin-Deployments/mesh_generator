import logging

import numpy as np
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
from OCC.Core.TopAbs import TopAbs_EDGE

# OCC Imports for feature detection
from OCC.Core.TopExp import TopExp_Explorer

from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import GridState, SovereignContainer

logger = logging.getLogger(__name__)

def get_min_feature_size(shape) -> float:
    """
    Utility function to analyze the geometry for adaptive fidelity.
    
    Traverses the topology of the shape to find the shortest edge,
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
        brepgprop.LinearProperties(edge, props)
        length = props.Mass()
        
        # Filter out degenerate/zero-length artifacts
        if length > 1e-7:
            min_length = min(min_length, length)
            
        explorer.Next()
        
    # 2. Return shortest edge if found
    if min_length != float('inf'):
        return float(min_length)
        
    # 3. Fallback: If no edges exist, use the smallest bounding box dimension.
    bbox = Bnd_Box()
    brepbndlib.Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    
    return float(min(xmax - xmin, ymax - ymin, zmax - zmin))


class ResolutionStep(StepInterface):
    """
    Refactored S8-S10: Grid Resolution with Adaptive Fidelity.
    
    Dynamically adjusts target resolution based on the minimum geometric 
    feature size. This value will serve as the mesh size guide for the 
    subsequent GmshCategorizer.
    """
    
    __slots__ = ()

    def execute(self, container: SovereignContainer):
        """
        Executes the resolution calculation.
        
        Args:
            container: The SovereignContainer instance. 
                       Requires a populated 'bbox' and 'cad_solid'.
        """
        logger.info("Starting ResolutionStep: calculating adaptive resolution.")
        
        # GUARD CLAUSE: Pipeline Topology Validation.
        if container.bbox is None or container.cad_solid is None:
            error_msg = "CONSTITUTION VIOLATION: Pipeline incomplete. Tracing/Ingestion steps must run before ResolutionStep."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # 1. INSPECTION: Determine the thinnest feature
        min_feature = get_min_feature_size(container.cad_solid)
        logger.info(f"ResolutionStep: Minimum feature detected at {min_feature:.4f}")
        
        # 2. CONSTRAINED ADAPTATION:
        # Check against resolution floor and ceiling.
        if min_feature < container.min_element_size:
            error_msg = f"GEOMETRY VIOLATION: Thinnest feature ({min_feature:.4f}) is smaller than minimum element size ({container.min_element_size:.4f})."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Determine the effective element size (to be passed to Gmsh)
        adaptive_el = min(container.max_element_size, max(container.min_element_size, min_feature))
        logger.info(f"ResolutionStep: Target element size (adaptive_el) set to {adaptive_el:.4f}")
        
        # 3. UNPACKING: Translate the tuple into readable spatial coordinates.
        x_min, y_min, z_min, x_max, y_max, z_max = container.bbox
        
        # 4. VIRTUAL DISCRETIZATION:
        # We calculate these for legacy compatibility and solver memory estimation.
        # Note: These now represent 'Virtual Resolution' rather than voxel counts.
        nx = max(1, int(np.ceil((x_max - x_min) / adaptive_el)))
        ny = max(1, int(np.ceil((y_max - y_min) / adaptive_el)))
        nz = max(1, int(np.ceil((z_max - z_min) / adaptive_el)))
        
        # 5. STATE PERSISTENCE:
        container.grid = GridState(
            x_min=x_min, x_max=x_max,
            y_min=y_min, y_max=y_max,
            z_min=z_min, z_max=z_max,
            nx=nx, ny=ny, nz=nz
        )
        logger.info(f"ResolutionStep successful: Virtual Grid initialized with dimensions {nx}x{ny}x{nz}.")