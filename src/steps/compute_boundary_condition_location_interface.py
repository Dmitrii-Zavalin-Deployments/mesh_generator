"""
src/steps/compute_boundary_condition_location_interface.py

Contract‑only interface for step S12.i.1.
This file is part of the core architecture and is version‑controlled.
"""

from src.steps.step_interface_base import StepInterfaceBase
from src.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.config.config_interface import MeshGeneratorConfigInterface

class ComputeBoundaryConditionLocationInterface(StepInterfaceBase):
    """
    S12.i.1 — compute_boundary_condition_i_location

    Contract‑only interface for the step that computes:
        results.boundary_conditions[i].location

    This step determines which global domain face a given geometric surface
    corresponds to, based on the parsed geometry and global grid extents.

    Consumes:
        - parsed geometry (internal, accessed via state)
        - grid extents (from state.results_grid)
        - runtime configuration (MeshGeneratorConfigInterface)
        - the boundary‑condition index (int)

    Produces:
        - state.results_boundary_conditions[i]["location"]

    Allowed values:
        "x_min", "x_max", "y_min", "y_max", "z_min", "z_max", "wall"

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface, index: int) -> None:
        """
        Compute exactly one schema‑level property:
            results.boundary_conditions[i].location

        Must:
            - read only previously‑computed properties (grid extents, tolerance).
            - write exactly one property: results.boundary_conditions[index].location.
            - perform no other mutation of the state.
            - contain no implementation logic.
            - enforce the Single‑Responsibility Rule.

        Implementations must override this method.
        """
        raise NotImplementedError("Each step implementation must provide its own 'run' method.")