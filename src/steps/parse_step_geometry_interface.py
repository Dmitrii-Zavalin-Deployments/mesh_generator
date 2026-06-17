"""
src/steps/parse_step_geometry_interface.py

Contract‑only interface for step S1.
This file is part of the core architecture and is version‑controlled.
"""

from src.interfaces.steps.step_interface_base import StepInterfaceBase
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface
from src.implementation.models.geometry_model import GeometryModel

class ParseStepGeometryInterface(StepInterfaceBase):
    """
    S1 — parse_step_geometry

    Contract‑only interface for the step that initializes the geometry:
        output: GeometryModel

    This is the "Bootstrap" step. It transforms the raw input file (provided
    via state/config) into the internal geometric representation required 
    by all downstream operations.

    Consumes:
        - state.inputs_step_file (path to file)
        - runtime configuration (MeshGeneratorConfigInterface)

    Produces:
        - GeometryModel (The sovereign container for B-Rep data)

    This interface defines *only* the structural contract.
    No logic, no defaults, no computation is permitted.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: MeshGeneratorConfigInterface) -> GeometryModel:
        """
        Bootstrap the pipeline by converting raw input into a usable GeometryModel.

        Must:
            - load the geometry from the file path provided in state/config.
            - perform no schema-level mutations in this method (the returned
              model is injected by the orchestrator).
            - contain no implementation logic.

        Implementations must override this method and return a valid GeometryModel.
        """
        raise NotImplementedError