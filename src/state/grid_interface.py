from typing import TypedDict

class GridInterface(TypedDict, total=False):
    """
    Contract‑only interface for results.grid.
    No logic, no defaults, no computations.
    Matches the Sovereign Container definition in Section 2.3.
    """

    # Bounding box components (S2–S7)
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float

    # Grid resolution (S8–S10)
    nx: int
    ny: int
    nz: int