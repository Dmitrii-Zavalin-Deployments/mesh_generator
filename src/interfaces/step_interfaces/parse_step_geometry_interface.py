# src/interfaces/step_interfaces/parse_step_geometry_interface.py
from .step_interface_base import StepInterfaceBase
from src.implementation.models.geometry_model import GeometryModel

class ParseStepGeometryInterface(StepInterfaceBase):
    """
    Contract-only interface for S1 — parse_step_geometry.

    Consumes:
        - state.inputs_step_file

    Produces:
        - GeometryModel: A sovereign container for the TopoDS_Shape and spatial extents.
          NOTE: This object is returned by the step and utilized by the Orchestrator
                to inject dependency data into subsequent geometric operations.

    This step must NOT compute any schema-level property.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state, config) -> GeometryModel:
        """
        Load and interpret the STEP file into a GeometryModel representation.
        Must not compute or mutate any schema-level property in the Sovereign Container.
        """
        raise NotImplementedError