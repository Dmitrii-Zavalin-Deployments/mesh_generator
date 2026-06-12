from .step_interface_base import StepInterfaceBase
from interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class ComputeBoundaryConditionTypeInterface(StepInterfaceBase):
    """
    S12.i.2 — compute_boundary_condition_i_type

    Contract‑only interface for the step that computes exactly one schema‑level property:
        results.boundary_conditions[i].type

    Consumes:
        - parsed geometry classification (internal, not stored in the Sovereign Container)
        - config parameters (MeshGeneratorConfigInterface)
        - results.boundary_conditions[i].location  (computed in S12.i.1)

    Produces:
        - state.results_boundary_conditions[i]["type"]

    This interface defines *only* the structural contract.
    No logic, no defaults, and no computation are permitted here.
    Implementations must follow the Constitution and the Minimal Step Path.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config, index: int) -> None:
        """
        Compute exactly one schema‑level property:
            results.boundary_conditions[i].type

        Must:
            - read only previously‑computed properties:
                * results.boundary_conditions[i].location
                * config parameters (e.g., solver conventions, tolerance)
                * internal geometry classification (not stored in state)
            - write exactly one property:
                * results.boundary_conditions[i].type
            - perform no other mutation
            - contain no implementation logic here
            - enforce the Constitution and the Minimal Step Path
            - compute only the 'type' field for boundary condition i

        Implementations must override this method.
        """
        raise NotImplementedError