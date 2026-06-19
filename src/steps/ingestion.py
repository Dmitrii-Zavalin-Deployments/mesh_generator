# src/steps/ingestion.py
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
from OCC.Core.STEPControl import STEPControl_Reader

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
        reader = STEPControl_Reader()
        
        # Perform the read operation
        status = reader.ReadFile(container.step_file)
        
        if status != 1:
            raise RuntimeError(
                f"CONSTITUTION VIOLATION: Ingestion failed. "
                f"Could not read STEP file at: {container.step_file}"
            )
            
        reader.TransferRoots()
        
        # The setter in SovereignContainer will automatically validate 
        # that the shape returned by reader.OneShape() is a TopoDS_Shape.
        container.cad_solid = reader.OneShape()