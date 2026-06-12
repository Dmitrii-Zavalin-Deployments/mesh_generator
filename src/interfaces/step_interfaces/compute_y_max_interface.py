from .step_interface_base import StepInterfaceBase
from interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class ComputeYMaxInterface(StepInterfaceBase):
    """
    S5 — compute_y_max

    Contract‑only interface for the step that computes:
        results.grid.y_max

    Consumes:
        - parsed geometry (internal, not stored in the Sovereign Container)

    Produces:
        - state.results_grid["y_max"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    Implementations must follow the Constitution:
        - compute exactly one schema‑level property
        - read only previously‑computed properties
        - write exactly one property
        - perform no additional mutation
        - contain no algorithmic logic here
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Compute exactly one schema‑level property:
            results.grid.y_max

        Must:
            - read only the parsed geometry produced by S1
            - extract the y_max bounding‑box component
            - write exactly one field: state.results_grid["y_max"]
            - perform no other computation or mutation
            - contain no implementation logic here

        This method is intentionally unimplemented.
        Concrete implementations must override this method.
        """
        raise NotImplementedError