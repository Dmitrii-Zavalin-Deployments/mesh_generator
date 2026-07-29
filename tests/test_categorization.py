# tests/test_categorization.py
import os
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import src.steps.categorization as categorization_module
from src.state.mesh_generator_state import GridState, SovereignContainer
from src.steps.categorization import CategorizationStep

# --- TYPE-SAFETY CONSTITUTION METACLASS INTERCEPT ---

class TopoDS_Shape_Meta(type):
    """
    Metaclass to dynamically override isinstance() evaluation inside the 
    SovereignContainer state check. This permits real C++ shapes, local shims, 
    and mocks to seamlessly satisfy the pipeline constitution.
    """
    def __instancecheck__(cls, instance):
        return type(instance).__name__ in ("TopoDS_Shape", "MagicMock", "Mock", "DummyTopoDS_Shape")

class DummyTopoDS_Shape(metaclass=TopoDS_Shape_Meta):
    pass

@pytest.fixture(autouse=True)
def bypass_constitution_type_check():
    """ Automatically patches the state module's type target for all tests in this file. """
    with patch("src.state.mesh_generator_state.TopoDS_Shape", DummyTopoDS_Shape):
        yield

# --- LITERATE TEST SUITE ---

def test_categorization_guard_clause():
    """
    [CONSTITUTION PATH: GRID CHECK]
    Verify that the system raises a 'CONSTITUTION VIOLATION' if the 
    grid state is undefined, preventing downstream step execution failures.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"x_min": "inlet"}
    )
    
    # Explicitly break the constitution
    container.grid = None 
    
    # Expect a RuntimeError due to the lack of grid state
    step = CategorizationStep()
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: 'grid' is None"):
        step.execute(container)

def test_categorization_post_condition_violation():
    """
    [CONSTITUTION PATH: POST-CONDITION CHECK]
    Verifies that if an engine finishes execution but leaves the container's 
    mask state unpopulated, a Post-Condition Violation exception aborts the process.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # Force mock the Gmsh engine wrapper to complete while leaving the container empty
    step = CategorizationStep()
    with patch("src.steps.categorization._run_gmsh_engine") as mock_gmsh:
        mock_gmsh.return_value = None
        container.mask = None  # Ensure it remains unallocated
        with pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Categorization Engine failed"):
            step.execute(container)

def test_gmsh_engine_missing_bindings_error():
    """
    [GMSH ENGINE PATH: IMPORT ERROR GATING]
    Verifies that running the Gmsh engine in an environment where 
    the python binding is not installed safely raises an explicit 
    RuntimeError detailing missing bindings.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    step = CategorizationStep()
    
    # Intercept inside-scope import execution by temporarily hiding gmsh from sys.modules
    with patch.dict("sys.modules", {"gmsh": None}):
        with pytest.raises(RuntimeError, match="Gmsh Python bindings missing"):
            step.execute(container)

def test_gmsh_engine_topology_violation_error():
    """
    [GMSH ENGINE PATH: TOPOLOGY POST-CONDITION]
    When gmsh initializes but fails to generate 3D tetrahedra elements 
    (type 4 elements), the runtime context must catch the error and 
    throw a specific post-condition violation exception.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # Setup standard Gmsh mocks and configure stateful lifecycle hooks
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = False
    mock_gmsh.initialize.side_effect = lambda: setattr(mock_gmsh.is_initialized, 'return_value', True)
    
    mock_gmsh.model.mesh.getNodes.return_value = (np.array([1]), np.array([0.0, 0.0, 0.0]), [])
    # Return element type 1 (Lines) instead of type 4 (Tetrahedrons)
    mock_gmsh.model.mesh.getElements.return_value = ([1], [], [])
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        with pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Gmsh failed to generate 3D tetrahedral elements"):
            step.execute(container)

def test_gmsh_engine_reused_session():
    """
    [GMSH ENGINE PATH: REUSED SESSION]
    Verifies that if Gmsh is already initialized, the engine reuses the 
    existing context, performs a hard reset, and executes the finalize lifecycle.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True # PRE-INITIALIZED STATE
    
    # Return 4 nodes to match the indices referenced inside the tetrahedra array mappings
    mock_gmsh.model.mesh.getNodes.return_value = (np.array([1, 2, 3, 4]), np.zeros(12), [])
    mock_gmsh.model.mesh.getElements.return_value = ([4], [np.array([1])], [np.array([1, 2, 3, 4])])
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step.execute(container)
        
    # Verify reuse/reset path: finalize and re-initialize called during reset sequence
    assert mock_gmsh.initialize.called
    assert mock_gmsh.finalize.called

def test_gmsh_engine_full_execution_flow_success():
    """
    [GMSH ENGINE PATH: NOMINAL INTEGRATION FLOW]
    Simulates a successful and pristine Layer 1 unstructured mesh baking 
    execution sequence.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 2, 0, 2, 0, 2, 2, 2, 2) # 2x2x2 = 8 cells
    
    # Mocking standard arrays returned by GMSH C API
    node_tags = np.array([1, 2, 3, 4])
    coord = np.array([0.0, 0.0, 0.0,  1.0, 0.0, 0.0,  0.0, 1.0, 0.0,  0.0, 0.0, 1.0])
    element_types = [4] # Explicitly provide Type 4 Tetrahedrons
    element_tags = [np.array([101])]
    element_node_tags = [np.array([1, 2, 3, 4])]
    
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = False
    mock_gmsh.initialize.side_effect = lambda: setattr(mock_gmsh.is_initialized, 'return_value', True)
    
    mock_gmsh.model.mesh.getNodes.return_value = (node_tags, coord, [])
    mock_gmsh.model.mesh.getElements.return_value = (element_types, element_tags, element_node_tags)
    
    # Clear the cache prior to execution
    categorization_module._GMSH_MESH_CACHE.clear()
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step.execute(container)
        
    # Access the cache dynamically via the module reference
    cache = categorization_module._GMSH_MESH_CACHE
    
    # 1. Verify standard initialization and lifecycle teardown blocks
    assert mock_gmsh.initialize.called
    assert mock_gmsh.finalize.called
    
    # 2. Check the raw mesh matrix structures were extracted and cached for Layer 2
    assert "nodes_map" in cache
    assert "tets_vertices" in cache
    assert cache["tets_vertices"].shape == (1, 4, 3)
    
    # 3. Check baseline schema mask fulfillment (8 fluid elements allocated)
    assert len(container.mask) == 8
    assert all(cell == 1 for cell in container.mask)
    
    # 4. Verify visualizer hooks are invoked with strict viewport padding guidelines
    assert mock_gmsh.fltk.initialize.called
    assert mock_gmsh.write.called

def test_gmsh_engine_visualization_failure_escalation():
    """
    [GMSH ENGINE PATH: VISUALIZATION ROBUSTNESS]
    Verifies that an error raised inside the offscreen rendering buffer loop 
    is caught, handled, and re-thrown without bypassing critical memory lifecycle 
    garbage collection mechanisms (`gmsh.finalize()`).
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = False
    mock_gmsh.initialize.side_effect = lambda: setattr(mock_gmsh.is_initialized, 'return_value', True)
    
    mock_gmsh.model.mesh.getNodes.return_value = (np.array([1, 2, 3, 4]), np.zeros(12), [])
    mock_gmsh.model.mesh.getElements.return_value = ([4], [1], [np.array([1, 2, 3, 4])])
    
    # Force the graphics viewport pipeline write mechanism to throw an internal system exception
    mock_gmsh.write.side_effect = Exception("Xvfb frame buffer allocation timeout")
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        with pytest.raises(Exception, match="Xvfb frame buffer allocation timeout"):
            step.execute(container)
            
    # CRITICAL VERIFICATION: Ensure resource cleanup runs even on rendering crash loops
    assert mock_gmsh.finalize.called