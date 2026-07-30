from typing import List, Protocol, runtime_checkable
from interfaces.mesh_generator_interface import GridInterface

@runtime_checkable
class PipelineInterface(Protocol):
    """
    Composite interface for the global pipeline state.
    Provides a read-only view of the final state.
    """

    @property
    def geometry(self) -> "TopoDS_Shape": 
        """The source CAD geometry."""
        ...

    @property
    def grid(self) -> GridInterface: 
        """The mesh configuration and resolution metrics."""
        ...

    @property
    def mask(self) -> List[int]: 
        """The computed occupancy or element mask."""
        ...