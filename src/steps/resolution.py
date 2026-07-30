import logging

import numpy as np

from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import GridState, SovereignContainer

logger = logging.getLogger(__name__)

def get_min_feature_size() -> float:
    """
    Utility function to analyze geometry via Gmsh for adaptive fidelity.
    
    Traverses all curves (1-entities) in the active Gmsh model to find the shortest edge,
    which typically represents the thinnest feature (e.g., plate thickness).
    Falls back to the overall bounding box minimum dimension if no valid curves exist.
    """
    try:
        import gmsh
    except ImportError:
        return float('inf')

    curves = gmsh.model.getEntities(1)
    min_length = float('inf')
    
    for dim, tag in curves:
        try:
            length = gmsh.model.occ.getMass(dim, tag)
            if length > 1e-7:
                min_length = min(min_length, length)
        except Exception:
            continue
            
    if min_length != float('inf'):
        return float(min_length)
        
    # Fallback: Use the smallest bounding box dimension of the model
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
    return float(min(xmax - xmin, ymax - ymin, zmax - zmin))


class ResolutionStep(StepInterface):
    """
    Refactored S8-S10: Grid Resolution with Adaptive Fidelity via Gmsh.
    
    Dynamically adjusts target resolution based on the minimum geometric 
    feature size extracted from the active Gmsh session and the bounding box
    provided by TracingStep.
    """
    
    __slots__ = ()

    def execute(self, container: SovereignContainer):
        """
        Executes the resolution calculation using Gmsh and container state.
        
        Args:
            container: The SovereignContainer instance. 
                       Requires TracingStep to have populated container.bbox.
        """
        logger.info("Starting ResolutionStep: calculating adaptive resolution via Gmsh.")
        
        try:
            import gmsh
        except ImportError as e:
            error_msg = "CONSTITUTION VIOLATION: Gmsh Python bindings missing during resolution."
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        if not gmsh.is_initialized():
            error_msg = "CONSTITUTION VIOLATION: Gmsh session not initialized during ResolutionStep."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        if container.cad_solid is None:
            error_msg = "CONSTITUTION VIOLATION: Pipeline incomplete. Ingestion step must run before ResolutionStep."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # 1. INSPECTION: Retrieve bounding box from container state populated by TracingStep
        if container.bbox is None:
            error_msg = "CONSTITUTION VIOLATION: 'bbox' is None. TracingStep must precede ResolutionStep."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        x_min, y_min, z_min, x_max, y_max, z_max = container.bbox

        # Determine the thinnest feature via Gmsh entity traversal
        min_feature = get_min_feature_size()
        logger.info(f"ResolutionStep: Minimum feature detected at {min_feature:.4f}")
        
        # 2. CONSTRAINED ADAPTATION:
        if min_feature < container.min_element_size:
            error_msg = f"GEOMETRY VIOLATION: Thinnest feature ({min_feature:.4f}) is smaller than minimum element size ({container.min_element_size:.4f})."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        adaptive_el = min(container.max_element_size, max(container.min_element_size, min_feature))
        logger.info(f"ResolutionStep: Target element size (adaptive_el) set to {adaptive_el:.4f}")
        
        # 3. VIRTUAL DISCRETIZATION:
        nx = max(1, int(np.ceil((x_max - x_min) / adaptive_el)))
        ny = max(1, int(np.ceil((y_max - y_min) / adaptive_el)))
        nz = max(1, int(np.ceil((z_max - z_min) / adaptive_el)))
        
        # 4. STATE PERSISTENCE:
        container.grid = GridState(
            x_min=x_min, x_max=x_max,
            y_min=y_min, y_max=y_max,
            z_min=z_min, z_max=z_max,
            nx=nx, ny=ny, nz=nz
        )
        logger.info(f"ResolutionStep successful: Virtual Grid initialized with dimensions {nx}x{ny}x{nz}.")