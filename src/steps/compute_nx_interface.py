"""
src/steps/compute_nx_interface.py

Contract‑only interface for step S8.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeNxInterface(StepInterfaceBase):
    """
    S8 — compute_nx

    Contract‑only interface for the step that computes:
        results.grid.nx

    This step acts as the resolution calculator for the X-axis. It derives 
    the discrete cell count (integer) from the continuous geometric 
    bounding box (x_min, x_max) and the resolution rules defined in 
    the configuration.

    Consumes:
        - grid extents (state.results_grid.x_min, state.results_grid.x_max)
        - runtime configuration (MeshGeneratorConfigInterface)

    Produces:
        - state.results_grid["nx"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.nx

        Must:
            - read previously‑computed x_min and x_max.
            - read config.max_element_size and config.min_element_size.
            - write exactly one property: state.results_grid["nx"].
            - perform no other mutation of the state.
            - contain no implementation logic.

        Implementations must override this method.
        """
        raise NotImplementedError