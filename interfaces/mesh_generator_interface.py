# interfaces/mesh_generator_interface.py
from typing import Protocol, List

class GridInterface(Protocol):
    """Structural contract for the grid state."""
    x_min: float; x_max: float
    y_min: float; y_max: float
    z_min: float; z_max: float
    nx: int; ny: int; nz: int

class BoundaryConditionInterface(Protocol):
    """Structural contract for a single BC."""
    location: str
    type: str
    surface_id: str