# tests/test_resolution.py
import logging
from unittest.mock import MagicMock, patch

import pytest

from src.state.mesh_generator_state import GridState, SovereignContainer
from src.steps.resolution import ResolutionStep, get_min_feature_size


def get_dummy_container(bbox=None, cad_solid=None, min_element_size=0.5, max_element_size=2.0) -> SovereignContainer:
    """Standardized setup for testing pipeline state containers."""
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=max_element_size,
        tolerance=1e-4,
        min_element_size=min_element_size
    )
    container.cad_solid = cad_solid if cad_solid is not None else MagicMock()
    container.bbox = bbox
    return container


# --- UTILITY TEST SUITE: Gmsh Feature Detection & Bounding Box Fallback ---

def test_get_min_feature_size_curve_detection():
    mock_gmsh = MagicMock()
    mock_gmsh.model.getEntities.return_value = [(1, 1), (1, 2)]
    mock_gmsh.model.occ.getMass.side_effect = [5.0, 2.0]

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        min_feature = get_min_feature_size()
        assert min_feature == 2.0


def test_get_min_feature_size_bbox_fallback():
    mock_gmsh = MagicMock()
    # No curves returned or all curves filtered out
    mock_gmsh.model.getEntities.return_value = []
    mock_gmsh.model.getBoundingBox.return_value = (0.0, 0.0, 0.0, 10.0, 5.0, 20.0)

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        min_feature = get_min_feature_size()
        # Smallest dimension from bbox: min(10-0, 5-0, 20-0) = 5.0
        assert min_feature == 5.0


def test_get_min_feature_size_missing_gmsh_returns_inf():
    with patch.dict("sys.modules", {"gmsh": None}):
        min_feature = get_min_feature_size()
        assert min_feature == float('inf')


# --- ARCHITECTURAL GATE TEST SUITE: ResolutionStep ---

def test_resolution_missing_gmsh_bindings(caplog):
    container = get_dummy_container(bbox=(0.0, 0.0, 0.0, 10.0, 10.0, 10.0))
    step = ResolutionStep()

    with (
        patch.dict("sys.modules", {"gmsh": None}),
        caplog.at_level(logging.ERROR),
        pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Gmsh Python bindings missing"),
    ):
        step.execute(container)


def test_resolution_gmsh_not_initialized(caplog):
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = False
    container = get_dummy_container(bbox=(0.0, 0.0, 0.0, 10.0, 10.0, 10.0))
    step = ResolutionStep()

    with (
        patch.dict("sys.modules", {"gmsh": mock_gmsh}),
        caplog.at_level(logging.ERROR),
        pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Gmsh session not initialized"),
    ):
        step.execute(container)


def test_resolution_missing_cad_solid(caplog):
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    container = get_dummy_container(bbox=(0.0, 0.0, 0.0, 10.0, 10.0, 10.0), cad_solid=None)
    step = ResolutionStep()

    with (
        patch.dict("sys.modules", {"gmsh": mock_gmsh}),
        caplog.at_level(logging.ERROR),
        pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Pipeline incomplete"),
    ):
        step.execute(container)


def test_resolution_missing_bbox(caplog):
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    container = get_dummy_container(bbox=None)
    step = ResolutionStep()

    with (
        patch.dict("sys.modules", {"gmsh": mock_gmsh}),
        caplog.at_level(logging.ERROR),
        pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: 'bbox' is None"),
    ):
        step.execute(container)


def test_resolution_geometry_violation(caplog):
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    
    # Minimum feature size detected as 0.1, but container requires min_element_size = 0.5
    container = get_dummy_container(
        bbox=(0.0, 0.0, 0.0, 10.0, 10.0, 10.0),
        min_element_size=0.5
    )
    step = ResolutionStep()

    with (
        patch.dict("sys.modules", {"gmsh": mock_gmsh}),
        patch("src.steps.resolution.get_min_feature_size", return_value=0.1),
        caplog.at_level(logging.ERROR),
        pytest.raises(RuntimeError, match="GEOMETRY VIOLATION"),
    ):
        step.execute(container)


def test_resolution_success(caplog):
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    
    bbox = (0.0, 0.0, 0.0, 10.0, 10.0, 10.0)
    container = get_dummy_container(
        bbox=bbox,
        min_element_size=0.1,
        max_element_size=2.0
    )
    step = ResolutionStep()

    with (
        patch.dict("sys.modules", {"gmsh": mock_gmsh}),
        patch("src.steps.resolution.get_min_feature_size", return_value=1.0),
        caplog.at_level(logging.INFO),
    ):
        step.execute(container)
        
        assert "ResolutionStep successful" in caplog.text
        assert isinstance(container.grid, GridState)
        # Span = 10.0, adaptive_el = 1.0 -> nx = ny = nz = 10
        assert container.grid.nx == 10
        assert container.grid.ny == 10
        assert container.grid.nz == 10
