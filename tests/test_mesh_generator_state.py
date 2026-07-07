# tests/test_mesh_generator_state.py
import pytest
from unittest.mock import MagicMock
from OCC.Core.TopoDS import TopoDS_Shape
from src.state.mesh_generator_state import (
    BoundaryConditionState, 
    GridState, 
    SovereignContainer
)

# --- LITERATE TEST SUITE ---

def test_state_initialization():
    """
    [INITIALIZATION PATH]
    Verify that our atomic state containers (BC and Grid) correctly 
    initialize and preserve the input data.
    """
    # BoundaryConditionState: Ensure inputs are cast to string for consistency.
    bc = BoundaryConditionState("x_min", "inlet", "cell_0")
    assert bc.location == "x_min"
    
    # GridState: Ensure inputs are cast to expected types (float/int).
    grid = GridState(0, 1, 0, 1, 0, 1, 10, 10, 10)
    assert grid.nx == 10

def test_sovereign_container_setup():
    """
    [CONSTRUCTOR PATH]
    Verify that the SovereignContainer initializes with the correct 
    schema-defined fields and starts with all computed states as 'None', 
    as required by the constitution.
    """
    container = SovereignContainer(
        use_gmsh=False,
        step_file="test.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"x": "y"}
    )
    
    # Assert initial state is strictly uninitialized for computed fields.
    assert container.grid is None
    assert container.mask is None
    assert container.boundary_conditions is None
    assert container.cad_solid is None
    assert container.bbox is None

def test_sovereign_container_setters_happy_path():
    """
    [HAPPY PATH]
    Verify that valid types are accepted by the container setters.
    This demonstrates the successful state transition for each attribute.
    """
    container = SovereignContainer("test.step", 0.5, "v1", 1e-6, 0.1, {}, True)
    
    # Transition: Set valid data structures
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    container.mask = [0, 1]
    container.boundary_conditions = [BoundaryConditionState("x", "y", "0")]
    # Mock the TopoDS_Shape to satisfy the setter's isinstance check
    container.cad_solid = MagicMock(spec=TopoDS_Shape)
    container.bbox = (0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
    
    # Assert successful state persistence
    assert isinstance(container.grid, GridState)
    assert container.mask == [0, 1]
    assert len(container.boundary_conditions) == 1
    assert container.bbox[0] == 0.0

def test_sovereign_container_type_violations():
    """
    [COVERAGE PATH: CONSTITUTIONAL VIOLATIONS]
    We enforce the constitution by attempting to pass invalid types to setters.
    This triggers the explicit TypeError blocks (Lines 78, 87, 96, 107, 116),
    ensuring 100% path coverage.
    """
    container = SovereignContainer("test.step", 0.5, "v1", 1e-6, 0.1, {}, True)
    
    # 1. Grid Check: Expect TypeError when passing a string instead of GridState.
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'grid' must be an instance of GridState"):
        container.grid = "Not a GridState object"
        
    # 2. Mask Check: Expect TypeError when passing non-list types.
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'mask' must be a List"):
        container.mask = "Not a list"
        
    # 3. BC Check: Expect TypeError when passing non-list types.
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'boundary_conditions' must be a List"):
        container.boundary_conditions = "Not a list"
        
    # 4. CAD Solid Check: Expect TypeError when passing non-TopoDS_Shape types.
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'cad_solid' must be a TopoDS_Shape"):
        container.cad_solid = "Not a shape"
        
    # 5. BBox Check: Expect TypeError when passing non-tuple types.
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'bbox' must be a tuple"):
        container.bbox = [0.0, 1.0] # Passing a List instead of a Tuple

def test_sovereign_container_use_gmsh_type_error():
    """
    [ERROR PATH: CONSTITUTION VIOLATION]
    Verify that the use_gmsh property setter explicitly rejects non-boolean values 
    by enforcing strict runtime type checking to block state corruption.
    """
    # We initialize a sovereign container with clean, validated baseline entries.
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={},
        use_gmsh=True
    )
    
    # We attempt to assign an integer value (1) to the use_gmsh property.
    # While 1 evaluates to truthy in raw Python, the type checker requires an explicit bool.
    # The evaluation criterion inside the state gate checks:
    #     isinstance(1, bool) -> False
    # This must intercept execution and bubble up a designated TypeError.
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'use_gmsh' must be a boolean."):
        container.use_gmsh = 1


def test_sovereign_container_use_gmsh_nominal_toggle():
    """
    [SUCCESS PATH: NOMINAL STATE MUTATION]
    Verify that the use_gmsh property setter cleanly modifies the structural flag 
    when provided with a clean and authentic boolean variable.
    """
    # We instantiate the baseline container state initially configured with use_gmsh as True.
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={},
        use_gmsh=True
    )
    
    # We alter the execution route by mutating the state flag to a legitimate boolean:
    #     New Target Value = False
    container.use_gmsh = False
    
    # Assertion: The value must be stored internally without throwing errors.
    assert container.use_gmsh is False