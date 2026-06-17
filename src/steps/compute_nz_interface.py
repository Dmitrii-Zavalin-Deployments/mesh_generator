"""
src/steps/compute_nz_interface.py

Contract‑only interface for step S10.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeNzInterface(StepInterfaceBase):
    """
    S10 — compute_nz

    Contract‑only interface for the step that computes:
        results.grid.nz

    This step acts as the resolution calculator for the Z-axis. It derives 
    the discrete cell count (integer) from the continuous geometric 
    bounding box (z_min, z_max) and the resolution rules defined in 
    the configuration.

    Consumes:
        - grid extents (state.results_grid.z_min, state.results_grid.z_max)
        - runtime configuration (MeshGeneratorConfigInterface)

    Produces:
        - state.results_grid["nz"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.nz

        Must:
            - read previously‑computed z_min and z_max.
            - read config.max_element_size and config.min_element_size.
            - write exactly one property: state.results_grid["nz"].
            - perform no other mutation of the state.
            - contain no implementation logic.

        Implementations must override this method.
        """
        raise NotImplementedError