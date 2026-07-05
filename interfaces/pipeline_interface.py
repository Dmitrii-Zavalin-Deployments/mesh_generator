from typing import List, Protocol, runtime_checkable
from OCC.Core.TopoDS import TopoDS_Shape
from interfaces.mesh_generator_interface import GridInterface, BoundaryConditionInterface

@runtime_checkable
class PipelineInterface(Protocol):
    """
    Composite interface for the global pipeline state.
    Provides a read-only view of the final state.
    
    This contract remains valid for both Voxel-based and Gmsh-based 
    CategorizationSteps.
    """

    @property
    def geometry(self) -> TopoDS_Shape: 
        """The source CAD geometry (TopoDS_Shape)."""
        ...

    @property
    def grid(self) -> GridInterface: 
        """
        The mesh configuration. 
        Satisfies GridInterface via actual voxel counts or 
        calculated 'Virtual Resolution' from Gmsh.
        """
        ...

    @property
    def mask(self) -> List[int]: 
        """The computed occupancy or element mask."""
        ...

    @property
    def boundary_conditions(self) -> List[BoundaryConditionInterface]: 
        """The mapping of physical boundaries to conditions."""
        ...