# src/steps/tracing.py
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.Bnd import Bnd_Box

class TracingStep(StepInterface):
    """
    Refactored S2-S7: Domain Tracing.
    
    This step acts as the 'geometric surveyor'. Its primary responsibility is to 
    determine the spatial envelope of the loaded geometry. This envelope (the BBox)
    is the foundation upon which the subsequent ResolutionStep will build the grid.
    """
    
    __slots__ = () # Stateless: Logic only

    def execute(self, container: SovereignContainer):
        """
        Executes the spatial tracing process.
        
        Args:
            container: The SovereignContainer instance. 
                       Requires a valid, non-None 'cad_solid' (loaded via IngestionStep).
        """
        
        # GUARD CLAUSE: Strict dependency enforcement.
        # We cannot calculate a bounding box for geometry that hasn't been loaded.
        # This prevents downstream failures and enforces the pipeline execution order.
        if container.cad_solid is None:
            raise RuntimeError(
                "CONSTITUTION VIOLATION: 'cad_solid' is None. "
                "IngestionStep must run before TracingStep to provide the geometry."
            )

        # INITIALIZATION: Create a new Bnd_Box object.
        # In OpenCascade, a Bnd_Box is an empty volume container. 
        # It has no size until geometry is added to it.
        bbox = Bnd_Box()
        
        # GEOMETRIC CALCULATION: 
        # 'brepbndlib_Add' iterates through the TopoDS_Shape (the cad_solid).
        # It automatically expands the 'bbox' dimensions to encapsulate every 
        # vertex, edge, and face within the solid.
        brepbndlib_Add(container.cad_solid, bbox)
        
        # DATA PERSISTENCE:
        # bbox.Get() returns the raw (x_min, y_min, z_min, x_max, y_max, z_max) tuple.
        # We store this in the container so the 'ResolutionStep' can determine 
        # the grid resolution (nx, ny, nz) based on these bounds.
        container.bbox = bbox.Get()