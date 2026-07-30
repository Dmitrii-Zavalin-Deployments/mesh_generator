# tests/test_resolution.py
from unittest.mock import MagicMock, patch

import pytest

from src.state.mesh_generator_state import SovereignContainer
from src.steps.resolution import ResolutionStep, get_min_feature_size
from tests.dummies.dummy_harness import dummy_in, get_mock_config


def test_get_min_feature_size_import_error():
    """Verifies that missing gmsh bindings in get_min_feature_size return float('inf')."""
    with patch.dict("sys.modules", {"gmsh": None}):
        assert get_min_feature_size() == float('inf')


def test_get_min_feature_size_success_curves():
    """Verifies successful minimum feature size extraction from gmsh curve entities."""
    mock_gmsh = MagicMock()
    mock_gmsh.model.getEntities.return_value = [(1, 1), (1, 2)]
    mock_gmsh.model.occ.getMass.side_effect = [0.2, 0.05]

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        res = get_min_feature_size()
        assert res == 0.05


def test_get_min_feature_size_curve_exceptions_and_fallback():
    """Verifies graceful handling of curve measurement errors and fallback to bounding box."""
    mock_gmsh = MagicMock()
    mock_gmsh.model.getEntities.return_value = [(1, 1)]
    mock_gmsh.model.occ.getMass.side_effect = RuntimeError("Unmeasurable")
    mock_gmsh.model.getBoundingBox.return_value = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0)

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        res = get_min_feature_size()
        # Smallest dimension of bounding box [1.0, 2.0, 3.0] is 1.0
        assert res == 1.0


def test_resolution_step_import_error():
    """Verifies that missing gmsh bindings raise RuntimeError during ResolutionStep execution."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    with patch.dict("sys.modules", {"gmsh": None}):
        step = ResolutionStep()
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Gmsh Python bindings missing during resolution."):
            step.execute(container)


def test_resolution_step_not_initialized():
    """Verifies that uninitialized gmsh session raises RuntimeError during ResolutionStep execution."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = False

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step = ResolutionStep()
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Gmsh session not initialized during ResolutionStep."):
            step.execute(container)


def test_resolution_step_cad_solid_none():
    """Verifies that missing cad_solid raises RuntimeError during ResolutionStep execution."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = None

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step = ResolutionStep()
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Pipeline incomplete. Ingestion step must run before ResolutionStep."):
            step.execute(container)


def test_resolution_step_bbox_none():
    """Verifies that missing bbox raises RuntimeError during ResolutionStep execution."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = "loaded"
    container.bbox = None

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step = ResolutionStep()
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: 'bbox' is None. TracingStep must precede ResolutionStep."):
            step.execute(container)


def test_resolution_step_geometry_violation():
    """Verifies that feature size smaller than minimum element size triggers GEOMETRY VIOLATION."""
    d_in = dummy_in()
    config = get_mock_config()  # min_element_size = 0.1
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = "loaded"
    container.bbox = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         patch("src.steps.resolution.get_min_feature_size", return_value=0.05):
        step = ResolutionStep()
        with pytest.raises(RuntimeError, match="GEOMETRY VIOLATION: Thinnest feature.*is smaller than minimum element size"):
            step.execute(container)


def test_resolution_step_success():
    """Verifies successful grid initialization and discretization in ResolutionStep."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = "loaded"
    container.bbox = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         patch("src.steps.resolution.get_min_feature_size", return_value=0.2):
        step = ResolutionStep()
        step.execute(container)

    assert container.grid is not None
    assert container.grid.nx == 5
    assert container.grid.ny == 5
    assert container.grid.nz == 5
