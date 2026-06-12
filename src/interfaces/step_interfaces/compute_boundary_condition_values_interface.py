from .step_interface_base import StepInterfaceBase
from mesh_generator.state.state_interface import MeshGeneratorStateInterface


class ComputeBoundaryConditionValuesInterface(StepInterfaceBase):
    """
    S12.i.3 — compute_boundary_condition_i_values

    Contract‑only interface for the step that computes exactly one schema‑level property:
        results.boundary_conditions[i].values

    Consumes:
        - results.boundary_conditions[i].type
        - runtime configuration parameters (MeshGeneratorConfigInterface)
        - solver‑specific conventions (provided via config)

    Produces:
        - state.results_boundary_conditions[i]["values"]

    This interface defines *only* the structural contract.
    No logic, no defaults, and no computation are permitted here.
    All implementations must follow the Constitution and the Minimal Step Path.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config, index: int) -> None:
        """
        Compute exactly one schema‑level property:
            results.boundary_conditions[i].values

        Must:
            - read only previously‑computed properties:
                * results.boundary_conditions[i].type
                * configuration parameters (e.g., solver conventions, inflow/outflow rules)
            - write exactly one property:
                * results.boundary_conditions[i].values
            - perform no other mutation
            - contain no implementation logic here
            - enforce the Constitution and the Minimal Step Path
            - use the provided `index` to select the correct boundary‑condition entry

        Implementations must override this method.
        """
        raise NotImplementedError