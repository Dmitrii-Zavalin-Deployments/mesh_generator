# tests/test_boundary_conditions.py
import pytest
from src.steps.boundary_conditions import BoundaryConditionsStep
from src.state.mesh_generator_state import SovereignContainer, GridState

# --- LITERATE TEST SUITE ---

def test_boundary_conditions_all_faces():
    """
    [COVERAGE PATH: THE BOUNDARY TRAVERSAL]
    We aim for 100% path coverage by exercising the full if/elif chain of 
    the spatial boundary detector.
    
    The domain is defined as a 3x3x3 grid (27 total cells). We use the 
    flattening formula: idx = i + nx * (j + ny * k).
    """
    
    # 1. Setup: Define a mapping that covers every coordinate extreme.
    # The solver expects these definitions to map spatial locations to BC types.
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
    
    # Create the grid: 3x3x3 spatial decomposition.
    # Grid domain is [0, 3] on all axes.
    container.grid = GridState(0, 3, 0, 3, 0, 3, 3, 3, 3)
    container.mask = [0] * 27 # 27 cells (3^3), initially marked as SOLID (0).
    
    # 2. Injection: Mark specific cells as INTERFACE (-1) to trigger logic branches.
    # We strategically pick coordinates to ensure we hit every elif block.
    
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
    # We computed 6 interfaces; we expect exactly 6 boundary conditions to be registered.
    assert len(container.boundary_conditions) == 6
    
    # Validate that every branch was traversed by inspecting the resulting locations.
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
    The pipeline constitution requires grid and mask to be present before 
    boundary condition mapping.
    
    If these fields are None, we expect a RuntimeError to abort the process.
    """
    # Initialize container with null state dependencies.
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5, solver_version="v1.0.0",
        tolerance=1e-6, min_element_size=0.1, boundary_map={}
    )
    
    # Ensure execution results in a pipeline abort.
    step = BoundaryConditionsStep()
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
        step.execute(container)

def test_boundary_conditions_config_error():
    """
    [CONFIG ERROR]
    Boundary mapping relies on an exhaustive 'bc_map'. If a cell is detected 
    at a location not explicitly defined in the map, the system must 
    fail explicitly to prevent ambiguous simulation states.
    """
    # Scenario: We define a grid with a boundary at x_min, but omit 'x_min' from bc_map.
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5, solver_version="v1.0.0",
        tolerance=1e-6, min_element_size=0.1,
        boundary_map={} # Explicitly empty
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [-1] # Cell 0 is an interface
    
    # Expect a KeyError when the step attempts to look up 'x_min'.
    step = BoundaryConditionsStep()
    with pytest.raises(KeyError, match="not defined in 'bc_map'"):
        step.execute(container)