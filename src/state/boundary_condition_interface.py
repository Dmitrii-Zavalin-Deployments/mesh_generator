from typing import TypedDict
from .boundary_condition_values_interface import BoundaryConditionValuesInterface

class BoundaryConditionInterface(TypedDict, total=False):
    """
    Contract‑only interface for a single boundary condition entry in
    results.boundary_conditions[i].

    No logic, no defaults, no computations.
    Matches the schema defined in Sections 2.2 and 2.3.
    """

    # S12.i.1 — location classification
    # One of: "x_min", "x_max", "y_min", "y_max", "z_min", "z_max", "wall"
    location: str

    # S12.i.2 — type classification
    # One of: "no-slip", "free-slip", "inflow", "outflow", "pressure"
    type: str

    # S12.i.3 — values object (u, v, w, p)
    values: BoundaryConditionValuesInterface
