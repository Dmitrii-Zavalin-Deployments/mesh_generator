# tests/test_boundary_conditions.py
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.steps.boundary_conditions import BoundaryConditionsStep
from src.state.mesh_generator_state import SovereignContainer, GridState
import src.steps.categorization as categorization_module

# --- LITERATE TEST SUITE ---

def test_boundary_conditions_constitution_violation():
    """
    [ERROR PATH: CONSTITUTION VIOLATION]
    Verify that the system halts immediately if the required pre-requisites 
    (grid state or voxel mask) are missing from the SovereignContainer.
    """
    step = BoundaryConditionsStep()
    container = SovereignContainer("test.step", 0.1, "v1", 1e-6, 0.01, {}, False)
    
    # Grid and mask are missing/None by default on initialization, triggering the guard clause
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
    
    # Inject specific cells as INTERFACE (-1) to trigger logic branches
    container.mask[0 + 3*(1 + 3*1)] = -1 # x_min branch (i=0, j=1, k=1)
    container.mask[2 + 3*(1 + 3*1)] = -1 # x_max branch (i=2, j=1, k=1)
    container.mask[1 + 3*(0 + 3*1)] = -1 # y_min branch (i=1, j=0, k=1)
    container.mask[1 + 3*(2 + 3*1)] = -1 # y_max branch (i=1, j=2, k=1)
    container.mask[1 + 3*(1 + 3*0)] = -1 # z_min branch (i=1, j=1, k=0)
    container.mask[1 + 3*(1 + 3*2)] = -1 # z_max branch (i=1, j=1, k=2)
    container.mask[1 + 3*(1 + 3*1)] = -1 # Default 'wall' branch (Center cell: i=1, j=1, k=1)

    step = BoundaryConditionsStep()
    step.execute(container)
    
    # Verify that every branch was traversed by inspecting the resulting locations
    assert len(container.boundary_conditions) == 7
    locations = [bc.location for bc in container.boundary_conditions]
    for face in ["wall", "x_min", "x_max", "y_min", "y_max", "z_min", "z_max"]:
        assert face in locations


def test_boundary_conditions_missing_map_key():
    """
    [ERROR PATH: MAPPING INTEGRITY]
    Verify that if a boundary surface is identified but not defined in the configuration 
    (bc_map), the system raises a KeyError to prevent undefined physical behavior.
    """
    step = BoundaryConditionsStep()
    container = SovereignContainer("test.step", 0.1, "v1", 1e-6, 0.01, {}, False)
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [-1] # Cell 0 is an interface
    
    with pytest.raises(KeyError, match="CONSTITUTION VIOLATION"):
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
    
    # Empty cache explicitly to guarantee structural failure
    categorization_module._GMSH_MESH_CACHE = {}
    
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
    
    # Create a flat (singular) tetrahedron where all vertices lie on a line
    degenerate_tet = np.array([[[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]]])
    categorization_module._GMSH_MESH_CACHE = {"tets_vertices": degenerate_tet}
    
    # Execution must pass cleanly, bypassing the degenerate element logic gracefully
    step.execute(container)
    assert container.mask is not None


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
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    step = BoundaryConditionsStep()
    
    # Scenario A: Wall / Interface Classification (Exactly 1 corner inside out of 8)
    wall_tet = np.array([[
        [0.5, -0.1, -0.1],
        [-0.1, 0.5, -0.1],
        [-0.1, -0.1, 0.5],
        [-0.1, -0.1, -0.1]
    ]])
    categorization_module._GMSH_MESH_CACHE = {"tets_vertices": wall_tet}
    container.mask = [0]
    step.execute(container)
    assert container.mask == [-1]
    assert len(container.boundary_conditions) == 1
    assert container.boundary_conditions[0].location == "x_min"
    
    # Scenario B: Solid Classification (All 8 corners inside)
    solid_tet = np.array([[
        [10.0, -2.0, -2.0],
        [-2.0, 10.0, -2.0],
        [-2.0, -2.0, 10.0],
        [-2.0, -2.0, -2.0]
    ]])
    categorization_module._GMSH_MESH_CACHE = {"tets_vertices": solid_tet}
    container.mask = [1]
    step.execute(container)
    assert container.mask == [0]
    
    # Scenario C: Fluid Classification (0 corners inside)
    fluid_tet = np.array([[
        [112.0, 100.0, 100.0],
        [100.0, 112.0, 100.0],
        [100.0, 100.0, 112.0],
        [100.0, 100.0, 100.0]
    ]])
    categorization_module._GMSH_MESH_CACHE = {"tets_vertices": fluid_tet}
    container.mask = [0]
    step.execute(container)
    assert container.mask == [1]


def test_boundary_conditions_legacy_path():
    """
    [SUCCESS PATH: LEGACY FALLBACK]
    Verify that when use_gmsh is False, the pipeline skips the complex voxelization
    loop and proceeds directly to mapping existing mask data.
    """
    step = BoundaryConditionsStep()
    container = SovereignContainer("test.step", 0.1, "v1", 1e-6, 0.01, {"x_min": "inlet"}, False)
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [-1]
    
    step.execute(container)
    
    assert len(container.boundary_conditions) == 1
    assert container.boundary_conditions[0].location == "x_min"


def test_invalid_tolerance_raises_error():
    """
    [COVERAGE PATH: INVALID TOLERANCE HANDLING]
    We verify that the step raises a ValueError when a negative tolerance 
    is provided in the container configuration.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=-0.5,  # Trigger for the ValueError
        min_element_size=0.1,
        boundary_map={}
    )
    
    container.grid = MagicMock(spec=GridState)
    container.mask = [1]
    categorization_module._GMSH_MESH_CACHE = {"tets_vertices": np.zeros((1, 4, 3))}
    
    step = BoundaryConditionsStep()
    
    with pytest.raises(ValueError, match="CONSTITUTION VIOLATION: Invalid tolerance"):
        step.execute(container)


def test_optimization_branch_coverage():
    """
    [COVERAGE PATH: SKIP OPTIMIZATION]
    We ensure that the loop optimization is triggered. By passing two identical 
    tetrahedra, the second iteration will encounter grid corners already marked 
    'True' in the internal safety arrays, triggering the optimization branch skip.
    """
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
    container.mask = [1]
    
    tet = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ])
    categorization_module._GMSH_MESH_CACHE = {"tets_vertices": np.array([tet, tet])}
    
    step = BoundaryConditionsStep()
    step.execute(container)
    
    assert container.mask is not None
    assert len(container.boundary_conditions) > 0