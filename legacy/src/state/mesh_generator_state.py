"""
src/state/mesh_generator_state.py

Sovereign Container Module for the Mesh Generator Pipeline.
This file serves as the absolute, single source of truth for all data 
at every stage of execution, enforcing strict structural symmetry 
with the input and results JSON schemas.
"""

from typing import TypedDict, List, Dict
from OCC.Core.TopoDS import TopoDS_Shape


# ==============================================================================
# 1. RESULTS SUB-INTERFACES (Mapped to mesh_generator_results_schema.json)
# ==============================================================================

class GridInterface(TypedDict):
    """
    Structured grid extents and resolution for the Navier–Stokes solver.
    """
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    nx: int
    ny: int
    nz: int


class BoundaryConditionInterface(TypedDict):
    """
    Boundary condition location, type, and source attribution.
    
    Allowed 'location' values: "x_min", "x_max", "y_min", "y_max", "z_min", "z_max", "wall"
    Allowed 'type' values:     "no-slip", "free-slip", "inflow", "outflow", "pressure"
    """
    location: str
    type: str
    surface_id: str


class ResultsInterface(TypedDict):
    """
    The final CFD-ready domain representation aggregate.
    """
    grid: GridInterface
    mask: List[int]  # Flattened array mapping: -1 = Wall, 0 = Solid, 1 = Fluid
    boundary_conditions: List[BoundaryConditionInterface]


# ==============================================================================
# 2. INPUT & TRANSIENT SUB-INTERFACES
# ==============================================================================

class InputsInterface(TypedDict):
    """
    Raw execution parameters mapped to mesh_generator_input_schema.json.
    """
    step_file: str


class BoundingBoxInterface(TypedDict):
    """
    Explicitly typed geometric bounding box to prevent typo bugs 
    during grid calculations.
    """
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float


class ParsedGeometryInterface(TypedDict):
    """
    In-memory transient state containing the parsed OpenCASCADE topology 
    and extracted metadata. Powers fast, deterministic steps from S2 to S12.
    """
    # The active B-Rep object (The absolute source of truth for geometric queries)
    shape: TopoDS_Shape

    # Cached geometric bounds evaluated during S1, consumed by S2-S7
    bounding_box: BoundingBoxInterface

    # Maps unique surface strings to their calculated outward unit normal vector [nx, ny, nz]
    surface_normals: Dict[str, List[float]]

    # Master list of all individual surface IDs recognized in the CAD model
    all_surface_ids: List[str]

# ==============================================================================
# 3. THE CONFIG
# ==============================================================================

class ConfigInterface(TypedDict):
    """
    Configuration parameters used during this mesh generation run.
    Mapped directly to the config block in mesh_generator_output_schema.json.
    """
    solver_version: str
    tolerance: float
    max_element_size: float
    min_element_size: float

# ==============================================================================
# 4. THE SOVEREIGN CONTAINER (Unified Single Source of Truth)
# ==============================================================================

class MeshGeneratorStateInterface(TypedDict):
    """
    The Unified State Container representing the strict union of the 
    Input, Configuration, Transient, and Results schemas.
    """
    inputs: InputsInterface
    config: ConfigInterface  # Added to guarantee strict schema symmetry
    transients: ParsedGeometryInterface
    results: ResultsInterface