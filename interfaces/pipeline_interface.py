# interfaces/pipeline_interface.py
from typing import List, Protocol, runtime_checkable
from OCC.Core.TopoDS import TopoDS_Shape
from interfaces.mesh_generator_interface import GridInterface, BoundaryConditionInterface

@runtime_checkable
class PipelineInterface(Protocol):
    """
    Composite interface for the global pipeline state.
    Provides a read-only view of the final state.
    """

    @property
    def geometry(self) -> TopoDS_Shape: ...

    @property
    def grid(self) -> GridInterface: ...

    @property
    def mask(self) -> List[int]: ...

    @property
    def boundary_conditions(self) -> List[BoundaryConditionInterface]: ...