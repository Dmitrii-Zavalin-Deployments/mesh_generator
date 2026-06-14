# src/implementation/state/mesh_generator_state.py
from typing import List, Optional
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.state.grid_interface import GridInterface
from src.interfaces.state.boundary_condition_interface import BoundaryConditionInterface
from src.implementation.models.geometry_model import GeometryModel

class MeshGeneratorState(MeshGeneratorStateInterface):
    """
    Concrete implementation of the Mesh Generator Sovereign Container.
    Inherits directly from MeshGeneratorStateInterface.
    
    Acts as a pure data vessel. It requires all fields to be explicitly 
    provided during instantiation, enforcing the No-Defaults Policy.
    """

    def __init__(
        self,
        inputs_step_file: str,
        results_grid: GridInterface,
        results_mask: List[int],
        results_boundary_conditions: List[BoundaryConditionInterface],
        geometry_model: Optional[GeometryModel] = None
    ):
        # Explicitly assign fields
        self.inputs_step_file = inputs_step_file
        self.results_grid = results_grid
        self.results_mask = results_mask
        self.results_boundary_conditions = results_boundary_conditions
        
        # The GeometryModel is injected post-parsing via the Orchestrator
        self.geometry_model = geometry_model