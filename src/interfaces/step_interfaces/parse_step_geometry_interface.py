from .step_interface_base import StepInterfaceBase

class ParseStepGeometryInterface(StepInterfaceBase):
    """
    Contract‑only interface for S1 — parse_step_geometry.

    Consumes:
        - state.inputs_step_file

    Produces:
        - internal geometry object (B‑Rep shape, surfaces, topology)
          NOTE: This object is NOT stored in the Sovereign Container.
                It is kept internally for downstream steps.

    This step must NOT compute any schema‑level property.
    """

    ALLOWED_MEMBERS = {"run"}

    def run(self, state, config) -> None:
        """
        Load and interpret the STEP file into an internal geometric representation.
        Must not compute or mutate any schema‑level property in the Sovereign Container.
        """
        raise NotImplementedError