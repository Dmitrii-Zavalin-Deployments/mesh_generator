from typing import TypedDict

class BoundaryConditionValuesInterface(TypedDict, total=False):
    """
    Contract‑only interface for results.boundary_conditions[i].values.
    No logic, no defaults, no computations.
    Matches the schema in Sections 2.2 and 2.3.
    """

    u: float   # optional velocity component
    v: float   # optional velocity component
    w: float   # optional velocity component
    p: float   # optional pressure value