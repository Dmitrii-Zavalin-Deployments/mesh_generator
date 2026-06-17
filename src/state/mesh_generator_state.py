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

    def __iter__(self):
        """Allows direct iteration over state fields (e.g., for test inspection)."""
        return iter(self.__dict__.keys())

    def __getitem__(self, key):
        """
        Allows test suite to access object attributes like dictionary keys.
        Raises IndexError for integer keys to support sequence-style iteration.
        """
        if isinstance(key, int):
            raise IndexError("MeshGeneratorState is not a sequence; integer indices are not supported.")
            
        key_str = str(key)
        if hasattr(self, key_str):
            return getattr(self, key_str)
        raise KeyError(f"State does not contain attribute: {key_str}")

    def __setitem__(self, key, value):
        """Allows test suite to set attributes like dictionary keys."""
        setattr(self, str(key), value)