"""
src/state/boundary_condition_interface.py

Contract‑only interface for a single boundary condition entry 
in results.boundary_conditions[i].

This file is part of the core architecture and is version‑controlled.
"""

from typing import TypedDict

class BoundaryConditionInterface(TypedDict, total=False):
    """
    Contract‑only interface for a single boundary condition entry.
    
    This matches the structure defined in both the results schema and the 
    final output schema. It contains no physics values, only the spatial
    and categorical descriptors required by the meshing engine.
    """

    # S12.i.1 — Domain localization flag
    # Maps to one of: "x_min", "x_max", "y_min", "y_max", "z_min", "z_max", "wall"
    location: str

    # S12.i.2 — Execution calculation behavior rule mapping
    # Maps to one of: "no-slip", "free-slip", "inflow", "outflow", "pressure"
    type: str

    # S12.i.3 — Unique tracking link pointing back to the CAD surface root
    # Used for identification and mapping back to the raw geometry.
    surface_id: str