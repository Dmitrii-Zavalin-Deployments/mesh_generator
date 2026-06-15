from src.interfaces.step_interfaces.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class ComputeNyInterface(StepInterfaceBase):
    """
    S9 — compute_ny

    Contract‑only interface for the step that computes:
        results.grid.ny

    Consumes:
        - results.grid.y_min
        - results.grid.y_max
        - runtime configuration parameters (MeshGeneratorConfigInterface)

    Produces:
        - state.results_grid["ny"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.ny

        Must:
            - read only previously‑computed properties:
                * results.grid.y_min
                * results.grid.y_max
                * config parameters (e.g., tolerance, min/max element size)
            - write exactly one property:
                * results.grid.ny
            - perform no other mutation
            - contain no implementation logic here
            - follow the Constitution and the Minimal Step Path

        Implementations must override this method.
        """
        raise NotImplementedError