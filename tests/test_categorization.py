# tests/test_categorization.py
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import src.steps.categorization as categorization_module
from src.state.mesh_generator_state import GridState, SovereignContainer
from src.steps.categorization import CategorizationStep


class TopoDS_Shape_Meta(type):
    def __instancecheck__(cls, instance):
        return type(instance).__name__ in ("TopoDS_Shape", "MagicMock", "Mock", "DummyTopoDS_Shape")

class DummyTopoDS_Shape(metaclass=TopoDS_Shape_Meta):
    pass

@pytest.fixture(autouse=True)
def bypass_constitution_type_check():
    with patch("src.state.mesh_generator_state.TopoDS_Shape", DummyTopoDS_Shape):
        yield

def test_categorization_guard_clause():
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"x_min": "inlet"}
    )
    container.grid = None 
    
    step = CategorizationStep()
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: 'grid' is None"):
        step.execute(container)

def test_categorization_post_condition_violation():
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    step = CategorizationStep()
    with (
        patch("src.steps.categorization._run_gmsh_engine") as mock_gmsh,
        pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Categorization Engine failed"),
    ):
        mock_gmsh.return_value = None
        container.mask = None
        step.execute(container)

def test_gmsh_engine_missing_bindings_error():
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    step = CategorizationStep()
    with (
        patch.dict("sys.modules", {"gmsh": None}),
        pytest.raises(RuntimeError, match="Gmsh Python bindings missing"),
    ):
        step.execute(container)

def test_gmsh_engine_topology_violation_error():
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = False
    mock_gmsh.initialize.side_effect = lambda: setattr(mock_gmsh.is_initialized, 'return_value', True)
    
    mock_gmsh.model.mesh.getNodes.return_value = (np.array([1]), np.array([0.0, 0.0, 0.0]), [])
    mock_gmsh.model.mesh.getElements.return_value = ([1], [], [])
    
    step = CategorizationStep()
    with (
        patch.dict("sys.modules", {"gmsh": mock_gmsh}),
        pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Gmsh failed to generate 3D tetrahedral elements"),
    ):
        step.execute(container)

def test_gmsh_engine_reused_session():
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    
    mock_gmsh.model.mesh.getNodes.return_value = (np.array([1, 2, 3, 4]), np.zeros(12), [])
    mock_gmsh.model.mesh.getElements.return_value = ([4], [np.array([1])], [np.array([1, 2, 3, 4])])
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step.execute(container)
        
    assert mock_gmsh.initialize.called
    assert mock_gmsh.finalize.called

def test_gmsh_engine_full_execution_flow_success():
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 2, 0, 2, 0, 2, 2, 2, 2)
    
    node_tags = np.array([1, 2, 3, 4])
    coord = np.array([0.0, 0.0, 0.0,  1.0, 0.0, 0.0,  0.0, 1.0, 0.0,  0.0, 0.0, 1.0])
    element_types = [4]
    element_tags = [np.array([101])]
    element_node_tags = [np.array([1, 2, 3, 4])]
    
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = False
    mock_gmsh.initialize.side_effect = lambda: setattr(mock_gmsh.is_initialized, 'return_value', True)
    
    mock_gmsh.model.mesh.getNodes.return_value = (node_tags, coord, [])
    mock_gmsh.model.mesh.getElements.return_value = (element_types, element_tags, element_node_tags)
    
    categorization_module._GMSH_MESH_CACHE.clear()
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step.execute(container)
        
    cache = categorization_module._GMSH_MESH_CACHE
    
    assert mock_gmsh.initialize.called
    assert mock_gmsh.finalize.called
    assert "nodes_map" in cache
    assert "tets_vertices" in cache
    assert cache["tets_vertices"].shape == (1, 4, 3)
    assert len(container.mask) == 8
    assert all(cell == 1 for cell in container.mask)
    assert mock_gmsh.fltk.initialize.called
    assert mock_gmsh.write.called

def test_gmsh_engine_visualization_failure_escalation():
    container = SovereignContainer(
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
    
    mock_gmsh.write.side_effect = Exception("Xvfb frame buffer allocation timeout")
    
    step = CategorizationStep()
    with (
        patch.dict("sys.modules", {"gmsh": mock_gmsh}),
        pytest.raises(Exception, match="Xvfb frame buffer allocation timeout"),
    ):
        step.execute(container)
        
    assert mock_gmsh.finalize.called
