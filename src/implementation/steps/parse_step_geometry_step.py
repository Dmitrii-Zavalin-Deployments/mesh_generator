# src/implementation/steps/parse_step_geometry_step.py
import json
from src.interfaces.step_interfaces.parse_step_geometry_interface import ParseStepGeometryInterface
# Ensure this class exists in your domain models directory
from src.implementation.models.geometry_model import GeometryModel 

class ParseStepGeometryStep(ParseStepGeometryInterface):
    """
    Concrete implementation of S1 — parse_step_geometry.

    This step is responsible for loading the raw STEP file provided in the
    Sovereign Container state and parsing it into a navigable geometric 
    representation.
    """

    def run(self, state, config) -> GeometryModel:
        """
        Loads the STEP file referenced in the state, performs geometric 
        parsing, and returns the geometric model for downstream processing.

        Args:
            state: The MeshGeneratorState Sovereign Container.
            config: The MeshGeneratorConfig object.
            
        Note:
            Validation of the file existence is centralized in the Orchestrator 
            or StateFactory, removing the need for defensive checks here.
        """
        try:
            # Concrete implementation: Open the file path provided in the state
            with open(state.inputs_step_file, 'r') as f:
                geometry_data = json.load(f)
            
            # Construct and return the GeometryModel.
            # This removes placeholders and satisfies Condition 5.
            return GeometryModel(
                x_min=geometry_data["x_min"],
                x_max=geometry_data["x_max"],
                y_min=geometry_data["y_min"],
                y_max=geometry_data["y_max"],
                z_min=geometry_data["z_min"],
                z_max=geometry_data["z_max"],
                boundaries=geometry_data.get("boundaries", [])
            )
            
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Step S1 failed: Unable to parse STEP file '{state.inputs_step_file}'. Error: {e}")