from .step_interface_base import StepInterfaceBase
from mesh_generator.state.state_interface import MeshGeneratorStateInterface


class ComputeNxInterface(StepInterfaceBase):
    """
    S8 — compute_nx

    Contract‑only interface for the step that computes:
        results.grid.nx

    Consumes:
        - results.grid.x_min
        - results.grid.x_max
        - runtime configuration parameters (MeshGeneratorConfigInterface)

    Produces:
        - state.results_grid["nx"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.nx

        Must:
            - read only previously‑computed properties:
                * results.grid.x_min
                * results.grid.x_max
                * config parameters (e.g., tolerance, min/max element size)
            - write exactly one property:
                * results.grid.nx
            - perform no other mutation
            - contain no implementation logic here
            - follow the Constitution and the Minimal Step Path

        Implementations must override this method.
        """
        raise NotImplementedError