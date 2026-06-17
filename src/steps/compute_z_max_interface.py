from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class ComputeZMaxInterface(StepInterfaceBase):
    """
    S7 — compute_z_max

    Contract‑only interface for the step that computes:
        results.grid.z_max

    Consumes:
        - parsed geometry (internal, not stored in the Sovereign Container)

    Produces:
        - state.results_grid["z_max"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.z_max

        Must:
            - read only previously‑computed properties
            - write exactly one property
            - perform no other mutation
            - contain no implementation logic here

        Implementations must override this method.
        """
        raise NotImplementedError