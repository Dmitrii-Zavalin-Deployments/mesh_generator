from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class ComputeBoundaryConditionLocationInterface(StepInterfaceBase):
    """
    S12.i.1 — compute_boundary_condition_i_location

    Contract‑only interface for the step that computes:
        results.boundary_conditions[i].location

    This step determines which global domain face a given geometric surface
    corresponds to, based on:
        - the parsed geometry (B‑Rep)
        - the global grid extents:
            * results.grid.x_min
            * results.grid.x_max
            * results.grid.y_min
            * results.grid.y_max
            * results.grid.z_min
            * results.grid.z_max

    Consumes:
        - parsed geometry (internal, not stored in the Sovereign Container)
        - grid extents from state.results_grid
        - runtime configuration parameters (MeshGeneratorConfigInterface)
        - the boundary‑condition index (int)

    Produces:
        - state.results_boundary_conditions[i]["location"]

    The produced value must be one of:
        "x_min", "x_max",
        "y_min", "y_max",
        "z_min", "z_max",
        "wall"

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config, index: int) -> None:
        """
        Compute exactly one schema‑level property:
            results.boundary_conditions[i].location

        Must:
            - read only previously‑computed properties:
                * parsed geometry (internal)
                * results.grid.x_min
                * results.grid.x_max
                * results.grid.y_min
                * results.grid.y_max
                * results.grid.z_min
                * results.grid.z_max
                * config parameters (e.g., tolerance)
            - write exactly one property:
                * results.boundary_conditions[index].location
            - perform no other mutation
            - contain no implementation logic here
            - follow the Constitution and the Minimal Step Path
            - enforce the Single‑Responsibility Rule

        Implementations must override this method.
        """
        raise NotImplementedError