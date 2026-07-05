import logging
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
from OCC.Core.STEPControl import STEPControl_Reader

# Module-level logger is optimal for pytest capture and GHA observability
logger = logging.getLogger(__name__)

class IngestionStep(StepInterface):
    """
    Refactored S1: STEP File Ingestion.
    Loads the geometry and populates the SovereignContainer's cad_solid field.
    """
    
    __slots__ = () # Stateless: Logic only

    def execute(self, container: SovereignContainer):
        """
        Executes the ingestion process.
        
        Args:
            container: The SovereignContainer instance. 
                       Must have a valid step_file path initialized.
        """
        logger.info(f"Starting IngestionStep: {container.step_file}")
        reader = STEPControl_Reader()
        
        # Perform the read operation
        status = reader.ReadFile(container.step_file)
        
        if status != 1:
            error_msg = f"CONSTITUTION VIOLATION: Ingestion failed for: {container.step_file}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        reader.TransferRoots()
        
        # The setter in SovereignContainer will automatically validate 
        # that the shape returned by reader.OneShape() is a TopoDS_Shape.
        container.cad_solid = reader.OneShape()
        
        logger.info(f"IngestionStep successful: {container.step_file} loaded into memory.")