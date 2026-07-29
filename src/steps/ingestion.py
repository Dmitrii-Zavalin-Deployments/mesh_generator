import logging
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer

# Module-level logger is optimal for pytest capture and GHA observability
logger = logging.getLogger(__name__)

class IngestionStep(StepInterface):
    """
    Refactored S1: STEP File Ingestion via Gmsh.
    Loads the CAD geometry into the active Gmsh session.
    """
    
    __slots__ = () # Stateless: Logic only

    def execute(self, container: SovereignContainer):
        """
        Executes the ingestion process using Gmsh.
        
        Args:
            container: The SovereignContainer instance. 
                       Must have a valid step_file path initialized.
        """
        logger.info(f"Starting IngestionStep: {container.step_file}")
        
        try:
            import gmsh
        except ImportError as e:
            error_msg = "CONSTITUTION VIOLATION: Gmsh Python bindings missing during ingestion."
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        if not gmsh.is_initialized():
            gmsh.initialize()
            
        try:
            # Open the STEP file directly using the Gmsh CAD kernel
            gmsh.open(container.step_file)
            gmsh.model.occ.synchronize()
        except Exception as e:
            error_msg = f"CONSTITUTION VIOLATION: Gmsh ingestion failed for: {container.step_file}. Details: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
            
        # Store a marker or model reference in cad_solid to satisfy the container state check
        container.cad_solid = "gmsh_loaded_shape"
        
        logger.info(f"IngestionStep successful: {container.step_file} loaded into Gmsh memory.")