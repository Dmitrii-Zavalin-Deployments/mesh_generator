# tests/test_categorization.py
from unittest.mock import MagicMock, patch

import pytest

from src.state.mesh_generator_state import GridState, SovereignContainer
from src.steps.categorization import CategorizationStep, _run_gmsh_engine
from tests.dummies.dummy_harness import dummy_in, get_mock_config


def test_categorization_step_grid_none():
    """Verifies that executing CategorizationStep with a None grid raises RuntimeError."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.grid = None
    step = CategorizationStep()

    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: 'grid' is None."):
        step.execute(container)


def test_categorization_step_mask_none_post_condition():
    """Verifies that if mask remains None after engine execution, CategorizationStep raises RuntimeError."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    step = CategorizationStep()

    with patch("src.steps.categorization._run_gmsh_engine", return_value=None), \
         pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Categorization Engine failed to populate container.mask"):
        step.execute(container)


def test_run_gmsh_engine_import_error():
    """Verifies that missing gmsh bindings raise RuntimeError."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 2, 2, 2)

    with patch.dict("sys.modules", {"gmsh": None}), \
         pytest.raises(RuntimeError, match="Gmsh Python bindings missing."):
        _run_gmsh_engine(container)


def test_categorization_success_with_gmsh_mocks():
    """Verifies successful execution of categorization step and gmsh engine with full mocking."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 2, 2, 2)

    mock_gmsh = MagicMock()
    # Test both uninitialized (False) and active context reset (True) branches
    mock_gmsh.is_initialized.side_effect = [False, True]

    # Mock getNodes: 4 nodes with 3D coordinates
    mock_gmsh.model.mesh.getNodes.return_value = (
        [1, 2, 3, 4],
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        None
    )
    # Mock getElements: Type 4 (tetrahedron) elements
    mock_gmsh.model.mesh.getElements.return_value = (
        [4],
        [[1]],
        [[1, 2, 3, 4]]
    )
    mock_gmsh.model.getBoundingBox.return_value = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         patch("os.path.dirname", return_value="tests/dummies"):
        step = CategorizationStep()
        step.execute(container)

    assert container.mask is not None
    assert len(container.mask) == 8  # 2 * 2 * 2


def test_run_gmsh_engine_missing_tet_elements():
    """Verifies that missing Type 4 tetrahedral elements raises RuntimeError post-condition violation."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    mock_gmsh.model.mesh.getNodes.return_value = ([1], [0.0, 0.0, 0.0], None)
    # Return element type 2 (triangle) instead of 4 (tetrahedron)
    mock_gmsh.model.mesh.getElements.return_value = ([2], [[1]], [[1, 2, 3]])
    mock_gmsh.model.getBoundingBox.return_value = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Gmsh failed to generate 3D tetrahedral elements."):
        _run_gmsh_engine(container)


def test_run_gmsh_engine_visualization_exception():
    """Verifies that visualization failures during rendering are logged and re-raised."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    mock_gmsh.model.mesh.getNodes.return_value = (
        [1, 2, 3, 4],
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        None
    )
    mock_gmsh.model.mesh.getElements.return_value = ([4], [[1]], [[1, 2, 3, 4]])
    mock_gmsh.model.getBoundingBox.return_value = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    
    # Trigger an exception during visualization draw step
    mock_gmsh.graphics.draw.side_effect = Exception("Offscreen render failure")

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         patch("os.path.dirname", return_value="tests/dummies"), \
         pytest.raises(Exception, match="Offscreen render failure"):
        _run_gmsh_engine(container)
