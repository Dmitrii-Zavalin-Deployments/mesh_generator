from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class ComputeNzInterface(StepInterfaceBase):
    """
    S10 — compute_nz

    Contract‑only interface for the step that computes:
        results.grid.nz

    Consumes:
        - results.grid.z_min
        - results.grid.z_max
        - runtime configuration parameters (MeshGeneratorConfigInterface)

    Produces:
        - state.results_grid["nz"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.nz

        Must:
            - read only previously‑computed properties:
                * results.grid.z_min
                * results.grid.z_max
                * config parameters (e.g., tolerance, min/max element size)
            - write exactly one property:
                * results.grid.nz
            - perform no other mutation
            - contain no implementation logic here
            - follow the Constitution and the Minimal Step Path

        Implementations must override this method.
        """
        raise NotImplementedError