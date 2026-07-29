import logging

from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer

logger = logging.getLogger(__name__)

class TracingStep(StepInterface):
    """
    Refactored S2-S7: Domain Tracing via Gmsh.
    
    This step acts as the 'geometric surveyor'. Its primary responsibility is to 
    determine the spatial envelope of the loaded geometry using Gmsh. This envelope (the BBox)
    is the foundation upon which the subsequent ResolutionStep and MeshingStep will build.
    """
    
    __slots__ = () # Stateless: Logic only

    def execute(self, container: SovereignContainer):
        """
        Executes the spatial tracing process using Gmsh.
        
        Args:
            container: The SovereignContainer instance. 
                       Requires an initialized and loaded Gmsh session.
        """
        logger.info("Starting TracingStep: calculating bounding box via Gmsh.")
        
        # GUARD CLAUSE: Strict dependency enforcement.
        if container.cad_solid is None:
            error_msg = (
                "CONSTITUTION VIOLATION: 'cad_solid' is None. "
                "IngestionStep must run before TracingStep."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            import gmsh
        except ImportError as e:
            error_msg = "CONSTITUTION VIOLATION: Gmsh Python bindings missing during tracing."
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        if not gmsh.is_initialized():
            error_msg = "CONSTITUTION VIOLATION: Gmsh session not initialized during TracingStep."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # GEOMETRIC CALCULATION:
        # Retrieve the bounding box of the entire model (dim = -1, tag = -1)
        try:
            xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
            
            # DATA PERSISTENCE:
            container.bbox = (xmin, ymin, zmin, xmax, ymax, zmax)
            
            logger.info(f"TracingStep successful: BBox identified as {container.bbox}")
            
        except Exception as e:
            error_msg = f"TracingStep failed during geometric calculation: {e!s}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e