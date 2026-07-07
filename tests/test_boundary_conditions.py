# tests/test_boundary_conditions.py
import pytest
import numpy as np
import src.steps.categorization
from unittest.mock import patch, MagicMock
from src.steps.boundary_conditions import BoundaryConditionsStep
from src.state.mesh_generator_state import SovereignContainer, GridState
import src.steps.categorization as categorization_module

# --- LITERATE TEST SUITE ---

def test_boundary_conditions_guard_clause():
    """
    [CONSTITUTION PATH]
    The pipeline constitution requires grid and mask to be present before 
    boundary condition mapping can proceed.
    
    If these fields are None, we expect a RuntimeError to abort the process.
    """
    # Initialize container with null state dependencies to trigger the guard clause
    container = SovereignContainer(
        use_gmsh=False,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    
    # Ensure execution results in a pipeline initialization abort
    step = BoundaryConditionsStep()
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
        step.execute(container)

def test_boundary_conditions_all_faces():
    """
    [COVERAGE PATH: THE BOUNDARY TRAVERSAL]
    We achieve 100% path coverage across the spatial face detector under 
    the legacy fallback branch (use_gmsh=False).
    
    The domain is defined as a 3x3x3 grid (27 total cells). We use the 
    flattening formula: idx = i + nx * (j + ny * k).
    """
    # 1. Setup: Define a mapping that covers every coordinate extreme.
    bc_map = {
        "x_min": "inlet", "x_max": "outlet",
        "y_min": "wall_y", "y_max": "wall_y",
        "z_min": "wall_z", "z_max": "wall_z",
        "wall": "interior_wall"
    }
    
    container = SovereignContainer(
        use_gmsh=False,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map=bc_map
    )
    
    # Create the grid: 3x3x3 spatial decomposition. Grid domain is [0, 3] on all axes.
    container.grid = GridState(0, 3, 0, 3, 0, 3, 3, 3, 3)
    container.mask = [0] * 27 # 27 cells (3^3), initially marked as SOLID (0).
    
    # 2. Injection: Mark specific cells as INTERFACE (-1) to trigger logic branches.
    
    # Trigger x_min branch (i=0, j=1, k=1):
    container.mask[0 + 3*(1 + 3*1)] = -1

    # Trigger x_max branch (i=2, j=1, k=1):
    container.mask[2 + 3*(1 + 3*1)] = -1 
    
    # Trigger y_min branch (i=1, j=0, k=1):
    container.mask[1 + 3*(0 + 3*1)] = -1
    
    # Trigger y_max branch (i=1, j=2, k=1):
    container.mask[1 + 3*(2 + 3*1)] = -1
    
    # Trigger z_min branch (i=1, j=1, k=0):
    container.mask[1 + 3*(1 + 3*0)] = -1
    
    # Trigger z_max branch (i=1, j=1, k=2):
    container.mask[1 + 3*(1 + 3*2)] = -1
    
    # Trigger default 'wall' branch (Center cell: i=1, j=1, k=1):
    container.mask[1 + 3*(1 + 3*1)] = -1

    # 3. Execution: Run the boundary mapping step.
    step = BoundaryConditionsStep()
    step.execute(container)
    
    # 4. Verification:
    # We computed 7 interfaces; we expect exactly 7 boundary conditions to be registered.
    assert len(container.boundary_conditions) == 7
    
    # Validate that every branch was traversed by inspecting the resulting locations.
    locations = [bc.location for bc in container.boundary_conditions]
    assert "wall" in locations
    assert "x_min" in locations
    assert "x_max" in locations
    assert "y_min" in locations
    assert "y_max" in locations
    assert "z_min" in locations
    assert "z_max" in locations

def test_boundary_conditions_config_error():
    """
    [CONFIG PATH: MISSING CONDITION EXCEPTION]
    Boundary mapping relies on an exhaustive 'bc_map'. If a cell is detected 
    at a location not explicitly defined in the map, the system must 
    fail explicitly to prevent ambiguous simulation states.
    """
    # Scenario: We define a grid with a boundary at x_min, but omit 'x_min' from bc_map.
    container = SovereignContainer(
        use_gmsh=False,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={} # Explicitly empty
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [-1] # Cell 0 is an interface
    
    # Expect a KeyError when the step attempts to look up 'x_min'.
    step = BoundaryConditionsStep()
    with pytest.raises(KeyError, match="not defined in 'bc_map'"):
        step.execute(container)

def test_gmsh_voxelization_missing_cache_error():
    """
    [POST-CONDITION PATH: CACHE MISS EXCEPTION]
    When use_gmsh=True is specified, the step requires a pre-computed 
    global mesh cache containing the 'tets_vertices' matrix. If missing, 
    a RuntimeError must be raised.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"wall": "slip"}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [0]
    
    # Clear the global cache map to guarantee cache failure
    src.steps.categorization._GMSH_MESH_CACHE = {}
    
    step = BoundaryConditionsStep()
    with pytest.raises(RuntimeError, match="Global mesh cache missing tets_vertices matrix"):
        step.execute(container)

def test_gmsh_voxelization_degenerate_tets():
    """
    [MATHEMATICAL ROBUSTNESS PATH: DEGENERATE TETRAHEDRA]
    Verifies that flat or degenerate tetrahedra (which cause LinAlgError during 
    barycentric matrix inversion) are caught safely and skipped without crashing 
    the pipeline execution context.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"wall": "slip"}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [0]
    
    # Inject a completely flat/degenerate tetrahedron (all vertices flattened at origin)
    degenerate_tet = np.zeros((1, 4, 3))
    src.steps.categorization._GMSH_MESH_CACHE = {
        "tets_vertices": degenerate_tet
    }
    
    step = BoundaryConditionsStep()
    # Execution must pass cleanly, bypassing the degenerate element logic gracefully
    step.execute(container)
    
    # Since it was skipped, no corners are marked inside; cell defaults to Fluid (1)
    assert container.mask == [1]

def test_gmsh_voxelization_full_classification():
    """
    [HIGH-PERFORMANCE PATH: VOXEL CLASSIFICATION MATRIX]
    Validates Layer 2 high-performance voxelization across all three 
    possible core classification outcomes: Solid (8 corners inside), 
    Fluid (0 corners inside), and Wall/Interface (mixed corners inside).
    """
    bc_map = {"x_min": "inlet", "wall": "slip"}
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map=bc_map
    )
    
    # Establish a 1x1x1 unit voxel decomposition grid
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [0]
    
    # Scenario A: Wall / Interface Classification (Exactly 1 corner inside out of 8)
    # Tetrahedron bounds engineered to only enclose the origin point [0, 0, 0]
    wall_tet = np.array([[
        [0.5, -0.1, -0.1],
        [-0.1, 0.5, -0.1],
        [-0.1, -0.1, 0.5],
        [-0.1, -0.1, -0.1]
    ]])
    
    src.steps.categorization._GMSH_MESH_CACHE = {"tets_vertices": wall_tet}
    step = BoundaryConditionsStep()
    step.execute(container)
    
    # Mixed corners -> cell state maps to -1 (Wall) and triggers face assignment
    assert container.mask == [-1]
    assert len(container.boundary_conditions) == 1
    assert container.boundary_conditions[0].location == "x_min"
    
    # Scenario B: Solid Classification (All 8 corners inside)
    # Giant canonical tetrahedron that completely swallows the unit cube domain [0,1]^3
    solid_tet = np.array([[
        [10.0, -2.0, -2.0],
        [-2.0, 10.0, -2.0],
        [-2.0, -2.0, 10.0],
        [-2.0, -2.0, -2.0]
    ]])
    
    src.steps.categorization._GMSH_MESH_CACHE = {"tets_vertices": solid_tet}
    step.execute(container)
    
    # All 8 corners enclosed -> cell state maps to 0 (Solid)
    assert container.mask == [0]
    
    # Scenario C: Fluid Classification (0 corners inside)
    # Tetrahedron positioned far away into external space, leaving the domain completely empty
    fluid_tet = np.array([[
        [112.0, 100.0, 100.0],
        [100.0, 112.0, 100.0],
        [100.0, 100.0, 112.0],
        [100.0, 100.0, 100.0]
    ]])
    
    src.steps.categorization._GMSH_MESH_CACHE = {"tets_vertices": fluid_tet}
    step.execute(container)
    
    # 0 corners enclosed -> cell state maps to 1 (Fluid)
    assert container.mask == [1]

def test_boundary_conditions_constitution_violation():
    """
    [ERROR PATH: CONSTITUTION VIOLATION]
    Verify that the system halts immediately if the required pre-requisites 
    (grid state or voxel mask) are missing from the SovereignContainer.
    """
    step = BoundaryConditionsStep()
    container = SovereignContainer("test.step", 0.1, "v1", 1e-6, 0.01, {}, False)
    
    # State setup: Grid is missing.
    # Logic: if container.grid is None or container.mask is None:
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
        step.execute(container)

def test_boundary_conditions_gmsh_missing_cache():
    """
    [ERROR PATH: POST-CONDITION VIOLATION]
    Verify that if the Gmsh engine is enabled, the pipeline enforces the existence
    of the global mesh vertex cache.
    """
    step = BoundaryConditionsStep()
    container = SovereignContainer("test.step", 0.1, "v1", 1e-6, 0.01, {}, True)
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [1]
    
    # We patch the cache to be empty.
    # Logic: if "tets_vertices" not in _GMSH_MESH_CACHE:
    with patch("src.steps.categorization._GMSH_MESH_CACHE", {}):
        with pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION"):
            step.execute(container)

def test_boundary_conditions_degenerate_tetrahedron_skip():
    """
    [ROBUSTNESS PATH: DEGENERATE GEOMETRY]
    Verify that the voxelizer gracefully skips degenerate tetrahedra (volume = 0)
    that cause singular matrix inversion failures rather than crashing the pipeline.
    """
    step = BoundaryConditionsStep()
    container = SovereignContainer("test.step", 0.1, "v1", 1e-6, 0.01, {}, True)
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [1]
    
    # Create a flat (singular) tetrahedron where all vertices lie on a line.
    degenerate_tet = np.array([[[0,0,0], [1,0,0], [2,0,0], [3,0,0]]])
    
    with patch("src.steps.categorization._GMSH_MESH_CACHE", {"tets_vertices": degenerate_tet}):
        # This execution should not raise LinAlgError because of the try/except block.
        step.execute(container)
        # Assertion: The process completed execution, skipping the degenerate element.
        assert container.mask is not None

def test_boundary_conditions_missing_map_key():
    """
    [ERROR PATH: MAPPING INTEGRITY]
    Verify that if a boundary surface is identified but not defined in the configuration 
    (bc_map), the system raises a KeyError to prevent undefined physical behavior.
    """
    step = BoundaryConditionsStep()
    # No boundary map provided
    container = SovereignContainer("test.step", 0.1, "v1", 1e-6, 0.01, {}, False)
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # We force a mask that creates an interface at x_min
    # mask = [1] is all fluid, so we manually force mask to -1
    container.mask = [-1]
    
    # Logic: if location not in bc_map: raise KeyError
    with pytest.raises(KeyError, match="CONSTITUTION VIOLATION"):
        step.execute(container)

def test_boundary_conditions_legacy_path():
    """
    [SUCCESS PATH: LEGACY FALLBACK]
    Verify that when use_gmsh is False, the pipeline skips the complex voxelization
    loop and proceeds directly to mapping existing mask data.
    """
    step = BoundaryConditionsStep()
    container = SovereignContainer("test.step", 0.1, "v1", 1e-6, 0.01, {"x_min": "inlet"}, False)
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # Force a wall interface at x_min
    container.mask = [-1]
    
    # Execution should bypass the GMSH cache and go straight to mapping.
    step.execute(container)
    
    # Assertion: One boundary condition must be registered.
    assert len(container.boundary_conditions) == 1
    assert container.boundary_conditions[0].location == "x_min"

def test_invalid_tolerance_raises_error():
    """
    [COVERAGE PATH: INVALID TOLERANCE HANDLING]
    We verify that the step raises a ValueError when a negative tolerance 
    is provided in the container configuration (Lines 55-57).
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=-0.5,  # Invalid tolerance < 0
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # Mock the mesh cache to pass initial checks
    categorization_module._GMSH_MESH_CACHE["tets_vertices"] = np.zeros((1, 4, 3))
    
    step = BoundaryConditionsStep()
    
    # The logic enforces tolerance >= 0. Expect ValueError.
    with pytest.raises(ValueError, match="CONSTITUTION VIOLATION: Invalid tolerance"):
        step.execute(container)

def test_optimization_branch_coverage():
    """
    [COVERAGE PATH: SKIP OPTIMIZATION]
    We ensure that the loop optimization (Line 103) is triggered. 
    By passing two identical tetrahedra, the second iteration will encounter 
    grid corners already marked 'True' in the 'corner_inside' array, 
    triggering the 'continue' statement.
    """
    # Setup a container with a 2x2x2 grid.
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"x_min": "inlet", "x_max": "outlet"}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [1] * 1 # Dummy mask to satisfy pipeline
    
    # Define a simple tetrahedron that covers the grid origin
    tet = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ])
    
    # Inject two identical tetrahedra into the cache to force re-evaluation of same points
    categorization_module._GMSH_MESH_CACHE["tets_vertices"] = np.array([tet, tet])
    
    step = BoundaryConditionsStep()
    
    # Execution should run without error, hitting line 103 on the second iteration
    step.execute(container)
    
    # Verify the classification occurred
    assert container.mask is not None
    assert len(container.boundary_conditions) > 0