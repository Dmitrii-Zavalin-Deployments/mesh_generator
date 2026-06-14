# src/interfaces/step_interfaces/compute_mask_interface.py
from .step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.implementation.models.geometry_model import GeometryModel

class ComputeMaskInterface(StepInterfaceBase):
    """
    S11 — compute_mask

    Contract‑only interface for the step that computes:
        results.mask

    Consumes:
        - GeometryModel: The internal B‑Rep shape (produced by S1)
        - results.grid.nx
        - results.grid.ny
        - results.grid.nz

    Produces:
        - state.results_mask (a flattened 1D array of ints in {-1, 0, 1})

    Description:
        This interface defines the structural contract for generating the solid/fluid 
        mask array. By requiring GeometryModel in the run signature, we guarantee 
        that the concrete implementation has access to the physical topology 
        needed for exact ray-casting.

        No logic, no defaults, and no computation are permitted here.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config, geometry_model: GeometryModel) -> None:
        """
        Compute exactly one schema‑level property:
            results.mask

        Must:
            - accept a valid GeometryModel for spatial classification
            - read only previously‑computed properties (nx, ny, nz)
            - write exactly one property: results.mask
            - follow the Constitution and the Minimal Step Path
        """
        raise NotImplementedError