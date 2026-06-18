"""
src/config/config_interface.py

Contract‑only interface for Mesh Generator runtime configuration.
This file is part of the core architecture and is version‑controlled.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class MeshGeneratorConfigInterface:
    """
    Contract‑only interface for Mesh Generator runtime configuration.

    This interface defines the minimal set of configuration parameters
    required by the pipeline steps.

    These parameters are:
        - NOT part of the Input Schema
        - NOT part of the Sovereign Container
        - Injected at runtime only
        - Validated against mesh_generator_config.schema.json

    This interface defines *only* the structural contract.
    No logic, no defaults, and no computation are permitted.
    """

    # Version identifier of the meshing/solver backend.
    solver_version: str

    # Geometric tolerance used during STEP parsing and point-in-solid classification.
    tolerance: float

    # Maximum allowed mesh element size used when computing grid resolution.
    max_element_size: float

    # Minimum allowed mesh element size used when computing grid resolution.
    min_element_size: float