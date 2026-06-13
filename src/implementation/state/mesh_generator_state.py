# src/implementation/state/mesh_generator_state.py
from typing import List
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.state.grid_interface import GridInterface
from src.interfaces.state.boundary_condition_interface import BoundaryConditionInterface

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
        results_boundary_conditions: List[BoundaryConditionInterface]
    ):
        # Explicitly assign fields to ensure no implicit defaults
        self.inputs_step_file = inputs_step_file
        self.results_grid = results_grid
        self.results_mask = results_mask
        self.results_boundary_conditions = results_boundary_conditions