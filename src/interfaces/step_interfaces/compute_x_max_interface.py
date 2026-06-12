from .step_interface_base import StepInterfaceBase
from interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class ComputeXMaxInterface(StepInterfaceBase):
    """
    S3 — compute_x_max

    Contract‑only interface for the step that computes:
        results.grid.x_max

    Consumes:
        - parsed geometry (internal, not stored in the Sovereign Container)

    Produces:
        - state.results_grid["x_max"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.x_max

        Must:
            - read only previously‑computed properties
            - write exactly one property
            - perform no other mutation
            - contain no implementation logic here

        Implementations must override this method.
        """
        raise NotImplementedError