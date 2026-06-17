"""
src/steps/compute_boundary_condition_type_interface.py

Contract‑only interface for step S12.i.2.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class ComputeBoundaryConditionTypeInterface(StepInterfaceBase):
    """
    S12.i.2 — compute_boundary_condition_i_type

    Contract‑only interface for the step that computes:
        results.boundary_conditions[i].type

    This step acts as the policy engine for the mesh. It determines the 
    physical boundary type (e.g., "no-slip", "outflow") based on the 
    geometric location previously identified in S12.i.1.

    Consumes:
        - parsed geometry classification (internal)
        - runtime configuration (MeshGeneratorConfigInterface)
        - results.boundary_conditions[i].location (computed in S12.i.1)

    Produces:
        - state.results_boundary_conditions[i]["type"]

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface, index: int) -> None:
        """
        Compute exactly one schema‑level property:
            results.boundary_conditions[i].type

        Must:
            - read previously‑computed location and config parameters.
            - write exactly one property: results.boundary_conditions[index].type.
            - perform no other mutation of the state.
            - contain no implementation logic.
            - enforce the Single‑Responsibility Rule.

        Implementations must override this method.
        """
        raise NotImplementedError