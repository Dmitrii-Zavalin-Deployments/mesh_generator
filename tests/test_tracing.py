# tests/test_tracing.py
from unittest.mock import MagicMock, patch
import pytest

from src.state.mesh_generator_state import SovereignContainer
from src.steps.tracing import TracingStep
from tests.dummies.dummy_harness import dummy_in, get_mock_config


def test_tracing_step_cad_solid_none():
    """Verifies that executing TracingStep with a None cad_solid raises RuntimeError."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = None  # Explicitly None to trigger guard clause
    step = TracingStep()

    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: 'cad_solid' is None."):
        step.execute(container)


def test_tracing_step_import_error():
    """Verifies that missing gmsh bindings raise RuntimeError."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = MagicMock()

    with patch.dict("sys.modules", {"gmsh": None}), \
         pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Gmsh Python bindings missing during tracing."):
        step = TracingStep()
        step.execute(container)


def test_tracing_step_not_initialized():
    """Verifies that an uninitialized gmsh session raises RuntimeError."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = MagicMock()

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = False

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Gmsh session not initialized during TracingStep."):
        step = TracingStep()
        step.execute(container)


def test_tracing_step_success():
    """Verifies successful bounding box calculation and persistence in container."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = MagicMock()

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    mock_gmsh.model.getBoundingBox.return_value = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step = TracingStep()
        step.execute(container)

    assert container.bbox == (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)


def test_tracing_step_bounding_box_exception():
    """Verifies that exceptions during getBoundingBox are caught and re-raised as RuntimeError."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )
    container.cad_solid = MagicMock()

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True
    mock_gmsh.model.getBoundingBox.side_effect = Exception("Bounding box failure")

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         pytest.raises(RuntimeError, match="TracingStep failed during geometric calculation: Bounding box failure"):
        step = TracingStep()
        step.execute(container)
