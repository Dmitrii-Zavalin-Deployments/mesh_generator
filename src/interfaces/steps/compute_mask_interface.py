# src/interfaces/steps/compute_mask_interface.py
from .step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeMaskInterface(StepInterfaceBase):
    """
    S11 — compute_mask

    Contract‑only interface for the step that computes:
        results.mask

    Consumes:
        - GeometryModel: Provided via constructor injection (S1).
        - results.grid.nx, ny, nz: Provided via state.
        - tolerance: Provided via config (MeshGeneratorConfig).

    Produces:
        - state.results_mask (a flattened 1D array of ints in {-1, 0, 1})

    Description:
        This interface defines the structural contract for generating the solid/fluid 
        mask array. By utilizing constructor injection for the GeometryModel, we 
        ensure the 'run' signature remains uniform across all pipeline steps.

        Physical Mapping:
            -1 : Wall (Boundary Condition)
             0 : Solid
             1 : Fluid (Interior)

        No logic, no defaults, and no computation are permitted here.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Compute exactly one schema‑level property:
            results.mask

        Must:
            - utilize the injected GeometryModel for spatial classification
            - read only previously‑computed properties (nx, ny, nz)
            - write exactly one property: results.mask
            - follow the Constitution and the Minimal Step Path
        """
        raise NotImplementedError