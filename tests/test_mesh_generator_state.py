# tests/test_mesh_generator_state.py
import pytest

from src.state.mesh_generator_state import GridState, SovereignContainer
from tests.dummies.dummy_harness import dummy_in, get_mock_config


def test_grid_state_initialization():
    """Verifies that GridState correctly converts and assigns spatial and resolution attributes."""
    grid = GridState(
        x_min="0.0", x_max="10.5",
        y_min=1, y_max=5.2,
        z_min=-1.0, z_max=3.0,
        nx="5", ny=10, nz="2"
    )

    assert grid.x_min == 0.0
    assert grid.x_max == 10.5
    assert grid.y_min == 1.0
    assert grid.y_max == 5.2
    assert grid.z_min == -1.0
    assert grid.z_max == 3.0
    assert grid.nx == 5
    assert grid.ny == 10
    assert grid.nz == 2


def test_sovereign_container_initialization_and_defaults():
    """Verifies SovereignContainer basic fields initialization using dummy harness structures and initial None state."""
    d_in = dummy_in()
    config = get_mock_config()

    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=str(config["max_element_size"]),
        tolerance=str(config["tolerance"]),
        min_element_size=str(config["min_element_size"])
    )

    assert container.step_file == "tests/dummies/sample_geometry.step"
    assert container.max_element_size == 0.5
    assert container.tolerance == 0.000001
    assert container.min_element_size == 0.1

    assert container.grid is None
    assert container.mask is None
    assert container.cad_solid is None
    assert container.bbox is None


def test_sovereign_container_grid_setter_and_validation():
    """Verifies grid property setter handles valid GridState and raises TypeError on invalid types."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    # Valid assignment
    valid_grid = GridState(0, 1, 0, 1, 0, 1, 2, 2, 2)
    container.grid = valid_grid
    assert container.grid is valid_grid

    # Reset to None
    container.grid = None
    assert container.grid is None

    # Invalid assignment raises TypeError
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'grid' must be an instance of GridState"):
        container.grid = "not_a_grid"


def test_sovereign_container_mask_setter_and_validation():
    """Verifies mask property setter handles valid lists and raises TypeError on invalid types."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    # Valid assignment
    container.mask = [1, 0, 1]
    assert container.mask == [1, 0, 1]

    # Reset to None
    container.mask = None
    assert container.mask is None

    # Invalid assignment raises TypeError
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'mask' must be a List"):
        container.mask = {"invalid": "type"}


def test_sovereign_container_cad_solid_setter():
    """Verifies cad_solid property setter accepts arbitrary objects or None."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    dummy_solid = object()
    container.cad_solid = dummy_solid
    assert container.cad_solid is dummy_solid

    container.cad_solid = None
    assert container.cad_solid is None


def test_sovereign_container_bbox_setter_and_validation():
    """Verifies bbox property setter handles valid tuples and raises TypeError on invalid types."""
    d_in = dummy_in()
    config = get_mock_config()
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    # Valid assignment
    valid_bbox = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    container.bbox = valid_bbox
    assert container.bbox == valid_bbox

    # Reset to None
    container.bbox = None
    assert container.bbox is None

    # Invalid assignment raises TypeError
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION: 'bbox' must be a tuple"):
        container.bbox = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
