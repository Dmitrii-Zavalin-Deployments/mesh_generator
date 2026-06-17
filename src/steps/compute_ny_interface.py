"""
src/steps/compute_ny_interface.py

Contract‑only interface for step S9.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeNyInterface(StepInterfaceBase):
    """
    S9 — compute_ny

    Contract‑only interface for the step that computes:
        results.grid.ny

    This step acts as the resolution calculator for the Y-axis. It derives 
    the discrete cell count (integer) from the continuous geometric 
    bounding box (y_min, y_max) and the resolution rules defined in 
    the configuration.

    Consumes:
        - grid extents (state.results_grid.y_min, state.results_grid.y_max)
        - runtime configuration (MeshGeneratorConfigInterface)

    Produces:
        - state.results_grid["ny"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.ny

        Must:
            - read previously‑computed y_min and y_max.
            - read config.max_element_size and config.min_element_size.
            - write exactly one property: state.results_grid["ny"].
            - perform no other mutation of the state.
            - contain no implementation logic.

        Implementations must override this method.
        """
        raise NotImplementedError