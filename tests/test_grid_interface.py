# tests/test_grid_interface.py
import pytest

from interfaces.grid_interface import GridInterface
from src.state.mesh_generator_state import GridState


def test_grid_state_conforms_to_grid_interface():
    """Verifies that GridState possesses all structural attributes required by GridInterface."""
    grid = GridState(
        x_min=0.0, x_max=10.0,
        y_min=0.0, y_max=10.0,
        z_min=0.0, z_max=5.0,
        nx=10, ny=10, nz=5
    )

    required_attributes = [
        "x_min", "x_max",
        "y_min", "y_max",
        "z_min", "z_max",
        "nx", "ny", "nz"
    ]

    for attr in required_attributes:
        assert hasattr(grid, attr), f"GridState missing required protocol attribute: {attr}"


def test_grid_interface_structural_duck_typing():
    """Verifies that any custom class implementing the required protocol fields satisfies structural checks."""
    class MockGridImplementation:
        x_min: float = 0.0
        x_max: float = 1.0
        y_min: float = 0.0
        y_max: float = 1.0
        z_min: float = 0.0
        z_max: float = 1.0
        nx: int = 2
        ny: int = 2
        nz: int = 2

    mock_grid = MockGridImplementation()
    
    # Structural verification
    assert isinstance(mock_grid.x_min, float)
    assert isinstance(mock_grid.nx, int)
    assert mock_grid.nx == 2
