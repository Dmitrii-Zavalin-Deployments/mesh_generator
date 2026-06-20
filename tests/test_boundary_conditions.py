# tests/test_boundary_conditions.py
import pytest
from src.steps.boundary_conditions import BoundaryConditionsStep
from src.state.mesh_generator_state import SovereignContainer, GridState

# --- LITERATE TEST SUITE ---

def test_boundary_conditions_execution():
    """
    [FUNCTIONAL PATH]
    We create a 2x2x2 computational grid and simulate a boundary 
    condition at the 'x_min' face to ensure the mapping logic executes correctly.
    """
    
    # 1. Setup: Initialize SovereignContainer with a 2x2x2 grid.
    # Grid domain is [0, 2] on all axes.
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5, solver_version="v1.0.0",
        tolerance=1e-6, min_element_size=0.1,
        boundary_map={"x_min": "inlet"}
    )
    container.grid = GridState(0, 2, 0, 2, 0, 2, 2, 2, 2)
    
    # 2. Simulation: Set a mask of -1 (Interface) at index 0 (which is the x_min boundary).
    # Mask size is 8 (2*2*2).
    container.mask = [0] * 8
    container.mask[0] = -1 
    
    # 3. Execution: Run the BoundaryConditionsStep.
    step = BoundaryConditionsStep()
    step.execute(container)
    
    # 4. Verification: The step should have identified exactly one BC at 'x_min'.
    assert len(container.boundary_conditions) == 1
    assert container.boundary_conditions[0].location == "x_min"
    assert container.boundary_conditions[0].type == "inlet"

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
    # Both are None by default
    
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
        boundary_map={} # Missing "x_min"
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [-1] # The only cell is a boundary
    
    step = BoundaryConditionsStep()
    with pytest.raises(KeyError, match="not defined in 'bc_map'"):
        step.execute(container)