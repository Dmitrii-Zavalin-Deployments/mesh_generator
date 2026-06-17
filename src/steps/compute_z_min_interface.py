"""
src/steps/compute_z_min_interface.py

Contract‑only interface for step S6.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeZMinInterface(StepInterfaceBase):
    """
    S6 — compute_z_min

    Contract‑only interface for the step that computes:
        results.grid.z_min

    This step is the geometric anchor for the Z-axis. It traverses the 
    parsed CAD B-Rep structure to determine the absolute minimum spatial 
    extent along the Z-axis of the domain.

    Consumes:
        - parsed geometry (state.cad_solid)
        - runtime configuration (MeshGeneratorConfigInterface - used for precision/tolerance)

    Produces:
        - state.results_grid["z_min"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.z_min

        Must:
            - perform a geometric query on state.cad_solid.
            - write exactly one property: state.results_grid["z_min"].
            - perform no other mutation of the state.
            - contain no implementation logic.

        Implementations must override this method.
        """
        raise NotImplementedError