"""
src/state/grid_interface.py

Contract‑only interface for results.grid.
This file is part of the core architecture and is version‑controlled.
"""

from typing import TypedDict

class GridInterface(TypedDict, total=False):
    """
    Contract‑only interface for results.grid.

    Matches the schema defined in mesh_generator_results_schema.json.
    This interface ensures that the geometric extents (S2–S7) and the
    resolution parameters (S8–S10) are handled with strict type safety.
    """

    # Bounding box components (S2–S7)
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float

    # Grid resolution (S8–S10)
    # nx, ny, nz represent the discrete cell counts in each dimension
    nx: int
    ny: int
    nz: int