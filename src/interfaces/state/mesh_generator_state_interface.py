from typing import TypedDict, List, Dict, Any
from OCC.Core.TopoDS import TopoDS_Shape
from .grid_interface import GridInterface
from .boundary_condition_interface import BoundaryConditionInterface

class MeshGeneratorStateInterface(TypedDict, total=False):
    """
    Contract‑only interface for the Mesh Generator Sovereign Container.
    No logic, no defaults, no computations.
    
    This acts as the single source of truth for the entire pipeline.
    All data previously held in GeometryModel is now encapsulated here.
    """

    # ----------------------------------------------------------------------
    # Input Schema
    # ----------------------------------------------------------------------
    inputs_step_file: str
    
    # ----------------------------------------------------------------------
    # Geometry Schema (Consolidated from GeometryModel)
    # ----------------------------------------------------------------------
    cad_solid: TopoDS_Shape
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    boundary_conditions_config: Dict[str, Any]

    # ----------------------------------------------------------------------
    # Results Schema
    # ----------------------------------------------------------------------
    results_grid: GridInterface
    results_mask: List[int]  # flattened mask array, values in {-1, 0, 1}
    results_boundary_conditions: List[BoundaryConditionInterface]