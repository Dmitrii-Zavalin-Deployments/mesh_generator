from typing import List
from .grid_interface import GridInterface
from .boundary_condition_interface import BoundaryConditionInterface

class MeshGeneratorStateInterface:
    """
    Contract‑only interface for the Mesh Generator Sovereign Container.
    No logic, no defaults, no computations.
    Matches the structure defined in Sections 2.2 and 2.3.
    """

    # Input Schema
    inputs_step_file: str

    # Results Schema
    results_grid: GridInterface
    results_mask: List[int]  # flattened mask array, values in {-1, 0, 1}
    results_boundary_conditions: List[BoundaryConditionInterface]