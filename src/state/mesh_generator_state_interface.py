"""
src/state/mesh_generator_state_interface.py

Contract‑only interface for the Mesh Generator Sovereign Container.
This acts as the single source of truth for the entire pipeline execution.
"""

from typing import TypedDict, List, Dict, Any
from OCC.Core.TopoDS import TopoDS_Shape
from src.state.grid_interface import GridInterface
from src.state.boundary_condition_interface import BoundaryConditionInterface

class MeshGeneratorStateInterface(TypedDict, total=False):
    """
    Contract‑only interface for the Mesh Generator Sovereign Container.
    
    This interface mirrors the structure of mesh_generator_output_schema.json.
    It encapsulates:
    1. The raw input reference.
    2. The structured internal model (for serialization).
    3. The transient internal geometry (for computation).
    4. The final results data blocks (grid, mask, BCs).
    """

    # ----------------------------------------------------------------------
    # Inputs (Mapped to Output Schema "inputs" block)
    # ----------------------------------------------------------------------
    inputs_step_file: str             # Path to the source STEP file
    inputs_step_model: Dict[str, Any] # Structured geometry/topology data

    # ----------------------------------------------------------------------
    # Transient Internal State (Used for computation, not exported to JSON)
    # ----------------------------------------------------------------------
    cad_solid: TopoDS_Shape           # In-memory OpenCASCADE B-Rep pointer

    # ----------------------------------------------------------------------
    # Results (Mapped to Output Schema "results" block)
    # ----------------------------------------------------------------------
    results_grid: GridInterface                # Grid extents and resolutions
    results_mask: List[int]                    # Flattened cell state (-1, 0, 1)
    results_boundary_conditions: List[BoundaryConditionInterface]