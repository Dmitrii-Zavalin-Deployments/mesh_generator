"""
src/steps/compute_x_max_interface.py

Contract‑only interface for step S3.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeXMaxInterface(StepInterfaceBase):
    """
    S3 — compute_x_max

    Contract‑only interface for the step that computes:
        results.grid.x_max

    This step is a geometric query. It traverses the parsed CAD B-Rep 
    structure to determine the absolute maximum spatial extent along 
    the X-axis of the domain.

    Consumes:
        - parsed geometry (state.cad_solid)
        - runtime configuration (MeshGeneratorConfigInterface - used for tolerance/precision settings)

    Produces:
        - state.results_grid["x_max"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.x_max

        Must:
            - perform a geometric query on state.cad_solid.
            - write exactly one property: state.results_grid["x_max"].
            - perform no other mutation of the state.
            - contain no implementation logic.

        Implementations must override this method.
        """
        raise NotImplementedError