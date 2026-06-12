from .step_interface_base import StepInterfaceBase
from interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class ComputeMaskInterface(StepInterfaceBase):
    """
    S11 — compute_mask

    Contract‑only interface for the step that computes:
        results.mask

    Consumes:
        - parsed geometry (internal B‑Rep shape produced by S1)
        - results.grid.nx
        - results.grid.ny
        - results.grid.nz

    Produces:
        - state.results_mask  (a flattened 1D array of ints in {-1, 0, 1})

    Description:
        This step is responsible for generating the solid/fluid mask array for the CFD domain.
        The mask is a single schema‑level property and must be computed in exactly one step,
        in accordance with the Single‑Responsibility Rule and the Minimal Step Path.

        The mask classifies each grid cell as:
            - -1 : solid (point‑in‑solid classification)
            -  0 : fluid interior
            -  1 : boundary‑adjacent (distance‑to‑surface < threshold)

        This interface defines *only* the structural contract.
        No logic, no defaults, and no computation are permitted here.

        Implementations will rely on:
            - OpenCascade / pythonOCC for geometric queries
            - NumPy for array construction
            - (optionally) CGAL or SciPy for advanced spatial queries

        But none of that logic appears in this interface.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Compute exactly one schema‑level property:
            results.mask

        Must:
            - read only previously‑computed properties:
                * parsed geometry (internal, produced by S1)
                * results.grid.nx
                * results.grid.ny
                * results.grid.nz
            - write exactly one property:
                * results.mask
            - perform no other mutation
            - contain no implementation logic here
            - follow the Constitution and the Minimal Step Path

        Implementations must override this method.
        """
        raise NotImplementedError