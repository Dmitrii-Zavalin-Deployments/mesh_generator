import logging
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.Bnd import Bnd_Box

logger = logging.getLogger(__name__)

class TracingStep(StepInterface):
    """
    Refactored S2-S7: Domain Tracing.
    
    This step acts as the 'geometric surveyor'. Its primary responsibility is to 
    determine the spatial envelope of the loaded geometry. This envelope (the BBox)
    is the foundation upon which the subsequent ResolutionStep and MeshingStep will build.
    """
    
    __slots__ = () # Stateless: Logic only

    def execute(self, container: SovereignContainer):
        """
        Executes the spatial tracing process.
        
        Args:
            container: The SovereignContainer instance. 
                       Requires a valid, non-None 'cad_solid' (loaded via IngestionStep).
        """
        logger.info("Starting TracingStep: calculating bounding box.")
        
        # GUARD CLAUSE: Strict dependency enforcement.
        # We cannot calculate a bounding box for geometry that hasn't been loaded.
        if container.cad_solid is None:
            error_msg = (
                "CONSTITUTION VIOLATION: 'cad_solid' is None. "
                "IngestionStep must run before TracingStep."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # INITIALIZATION: Create a new Bnd_Box object.
        bbox = Bnd_Box()
        
        # GEOMETRIC CALCULATION:
        # Use the static 'brepbndlib.Add' method to expand the bbox 
        # to encapsulate every part of the solid.
        try:
            brepbndlib.Add(container.cad_solid, bbox)
            
            # DATA PERSISTENCE:
            # bbox.Get() returns (xmin, ymin, zmin, xmax, ymax, zmax).
            # We explicitly unpack and cast to a tuple to ensure 
            # it matches the SovereignContainer setter contract.
            xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
            container.bbox = (xmin, ymin, zmin, xmax, ymax, zmax)
            
            logger.info(f"TracingStep successful: BBox identified as {container.bbox}")
            
        except Exception as e:
            logger.error(f"TracingStep failed during geometric calculation: {str(e)}")
            raise