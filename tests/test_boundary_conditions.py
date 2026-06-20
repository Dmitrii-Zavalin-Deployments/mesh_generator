# tests/test_boundary_conditions.py
import pytest
from src.steps.boundary_conditions import BoundaryConditionsStep
from src.state.mesh_generator_state import SovereignContainer, GridState

# --- LITERATE TEST SUITE ---

def test_boundary_conditions_all_faces():
    """
    [COVERAGE PATH]
    To reach 100% coverage, we must trigger every 'elif' branch in the boundary 
    detection logic. We use a 3x3x3 grid to isolate cells on specific faces 
    (e.g., center cells for y/z faces, avoiding the x_min priority).
    """
    
    # 1. Setup: Define a comprehensive BC map to cover all branches.
    bc_map = {
        "x_min": "inlet", "x_max": "outlet",
        "y_min": "wall_y", "y_max": "wall_y",
        "z_min": "wall_z", "z_max": "wall_z",
        "wall": "interior_wall"
    }
    
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5, solver_version="v1.0.0",
        tolerance=1e-6, min_element_size=0.1,
        boundary_map=bc_map
    )
    
    # Create a 3x3x3 grid. 
    # Indices are i,j,k [0..2]. Total cells = 27.
    container.grid = GridState(0, 3, 0, 3, 0, 3, 3, 3, 3)
    container.mask = [0] * 27 # Initialize all as Solid
    
    # 2. Injection: Mark specific cells to trigger the elif chain.
    # Logic priority: x_min -> x_max -> y_min -> y_max -> z_min -> z_max -> wall
    
    # i=2 (last column) triggers x_max: (2, 1, 1)
    # The x_min check (i=0) will fail, x_max check (i=2) will pass.
    container.mask[2 + 3*(1 + 3*1)] = -1 
    
    # i=1, j=0 (middle col, bottom row) triggers y_min: (1, 0, 1)
    container.mask[1 + 3*(0 + 3*1)] = -1
    
    # i=1, j=2 (middle col, top row) triggers y_max: (1, 2, 1)
    container.mask[1 + 3*(2 + 3*1)] = -1
    
    # i=1, j=1, k=0 (middle col, middle row, front) triggers z_min: (1, 1, 0)
    container.mask[1 + 3*(1 + 3*0)] = -1
    
    # i=1, j=1, k=2 (middle col, middle row, back) triggers z_max: (1, 1, 2)
    container.mask[1 + 3*(1 + 3*2)] = -1
    
    # i=1, j=1, k=1 (center cell) triggers wall: (1, 1, 1)
    container.mask[1 + 3*(1 + 3*1)] = -1

    # 3. Execution
    step = BoundaryConditionsStep()
    step.execute(container)
    
    # 4. Verification: Ensure all boundary types were mapped correctly.
    # We should have found 6 boundaries in total.
    assert len(container.boundary_conditions) == 6
    
    # Check that we captured the 'wall' type for the center cell
    locations = [bc.location for bc in container.boundary_conditions]
    assert "wall" in locations
    assert "x_max" in locations
    assert "y_min" in locations
    assert "y_max" in locations
    assert "z_min" in locations
    assert "z_max" in locations

def test_boundary_conditions_guard_clause():
    """
    [GUARD CLAUSE]
    Verify that the system raises a RuntimeError if the grid or mask 
    are not populated, preventing downstream null-pointer issues.
    """
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5, solver_version="v1.0.0",
        tolerance=1e-6, min_element_size=0.1, boundary_map={}
    )
    
    step = BoundaryConditionsStep()
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
        step.execute(container)

def test_boundary_conditions_config_error():
    """
    [CONFIG ERROR]
    Verify that the system raises a KeyError if a boundary location 
    is detected that is not provided in the bc_map.
    """
    # Grid is 1x1x1, which puts the cell at x_min AND x_max, y_min, etc.
    # We define an empty map, so 'x_min' will trigger an error.
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5, solver_version="v1.0.0",
        tolerance=1e-6, min_element_size=0.1,
        boundary_map={} 
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [-1] 
    
    step = BoundaryConditionsStep()
    with pytest.raises(KeyError, match="not defined in 'bc_map'"):
        step.execute(container)