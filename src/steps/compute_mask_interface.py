"""
src/steps/compute_mask_interface.py

Contract‑only interface for step S11.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeMaskInterface(StepInterfaceBase):
    """
    S11 — compute_mask

    Contract‑only interface for the step that computes:
        results.mask

    This step is the "Voxelizer". It maps the continuous B-Rep geometry 
    into a discrete, flattened 1D array of integers representing the 
    domain state.

    Consumes:
        - parsed geometry (state.cad_solid)
        - grid resolution (state.results_grid.nx, ny, nz)
        - tolerance (config.tolerance)

    Produces:
        - state.results_mask (flattened 1D array of ints in {-1, 0, 1})

    Physical Mapping:
        -1 : Wall (Boundary Condition)
         0 : Solid
         1 : Fluid (Interior)

    This interface defines *only* the structural contract.
    No logic, no defaults, and no computation are permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface) -> None:
        """
        Compute exactly one schema‑level property:
            results.mask

        Must:
            - utilize state.cad_solid for spatial classification.
            - read only previously‑computed grid properties (nx, ny, nz).
            - write exactly one property: state.results_mask.
            - perform no other mutation of the state.
            - contain no implementation logic.

        Implementations must override this method.
        """
        raise NotImplementedError