"""
src/steps/compute_boundary_condition_surface_id_interface.py

Contract‑only interface for step S12.i.3.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeBoundaryConditionSurfaceIdInterface(StepInterfaceBase):
    """
    S12.i.3 — compute_boundary_condition_i_surface_id

    Contract‑only interface for the step that computes:
        results.boundary_conditions[i].surface_id

    This step acts as the traceability link, connecting the abstracted 
    computational boundary condition back to the originating geometric face.

    Consumes:
        - parsed geometry (internal CAD topology)
        - the boundary‑condition index (int)

    Produces:
        - state.results_boundary_conditions[i]["surface_id"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface, index: int) -> None:
        """
        Compute exactly one schema‑level property:
            results.boundary_conditions[i].surface_id

        Must:
            - read the geometry associated with boundary index 'i'.
            - write exactly one property: results.boundary_conditions[index].surface_id.
            - perform no other mutation of the state.
            - contain no implementation logic.
            - enforce the Single‑Responsibility Rule.

        Implementations must override this method.
        """
        raise NotImplementedError