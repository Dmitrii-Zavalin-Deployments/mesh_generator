# tests/test_ingestion.py
from unittest.mock import MagicMock, patch
import pytest

from src.state.mesh_generator_state import SovereignContainer
from src.steps.ingestion import IngestionStep
from tests.dummies.dummy_harness import dummy_in, get_mock_config


def test_ingestion_success():
    """Verifies successful STEP file ingestion via Gmsh when uninitialized."""
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
        step = IngestionStep()
        step.execute(container)

    mock_gmsh.initialize.assert_called_once()
    mock_gmsh.open.assert_called_once_with(container.step_file)
    mock_gmsh.model.occ.synchronize.assert_called_once()
    assert container.cad_solid == "gmsh_loaded_shape"


def test_ingestion_already_initialized():
    """Verifies ingestion behavior when Gmsh context is already initialized."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step = IngestionStep()
        step.execute(container)

    mock_gmsh.initialize.assert_not_called()
    mock_gmsh.open.assert_called_once_with(container.step_file)
    mock_gmsh.model.occ.synchronize.assert_called_once()
    assert container.cad_solid == "gmsh_loaded_shape"


def test_ingestion_import_error():
    """Verifies that missing Gmsh Python bindings raise RuntimeError during ingestion."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    with patch.dict("sys.modules", {"gmsh": None}):
        step = IngestionStep()
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Gmsh Python bindings missing during ingestion."):
            step.execute(container)


def test_ingestion_open_failure():
    """Verifies that failures during Gmsh file opening or synchronization raise RuntimeError."""
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
    mock_gmsh.open.side_effect = Exception("File read error")

    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step = IngestionStep()
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Gmsh ingestion failed for:.*File read error"):
            step.execute(container)
