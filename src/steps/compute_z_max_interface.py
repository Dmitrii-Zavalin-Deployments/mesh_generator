"""
src/steps/compute_z_max_interface.py

Contract‑only interface for step S7.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeZMaxInterface(StepInterfaceBase):
    """
    S7 — compute_z_max

    Contract‑only interface for the step that computes:
        results.grid.z_max

    This step is a geometric query. It traverses the parsed CAD B-Rep 
    structure to determine the absolute maximum spatial extent along 
    the Z-axis of the domain.

    Consumes:
        - parsed geometry (state.cad_solid)
        - runtime configuration (MeshGeneratorConfigInterface)

    Produces:
        - state.results_grid["z_max"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.z_max

        Must:
            - perform a geometric query on state.cad_solid.
            - write exactly one property: state.results_grid["z_max"].
            - perform no other mutation of the state.
            - contain no implementation logic.

        Implementations must override this method.
        """
        raise NotImplementedError