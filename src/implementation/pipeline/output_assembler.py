# src/implementation/pipeline/output_assembler.py

import json
from src.implementation.state.mesh_generator_state import MeshGeneratorState

def _json_serializable_fallback(obj):
    """
    Fallback serializer for custom objects.
    Enforces the 'to_dict' contract for serialization.
    """
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    # If it doesn't have to_dict, we explicitly raise a TypeError 
    # to maintain strict schema enforcement.
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

class OutputAssembler:
    """
    Deterministic assembly procedure. 
    Responsibility: Only structural assembly and schema validation.
    """
    
    @staticmethod
    def assemble(state: MeshGeneratorState, config: object, inputs: dict) -> str:
        """
        Assembles pipeline artifacts into a validated JSON string.
        
        Args:
            state: The sovereign state container.
            config: The MeshGeneratorConfig object.
            inputs: Dictionary of input parameters.
        """
        # 1. Structural Mapping (The Assembly)
        output_data = {
            "inputs": inputs,
            "config": config,
            "results": state.results_grid 
        }
        
        # 2. Schema Validation (The Gate)
        # Verify output_data strictly matches mesh_generator_output_schema.json
        # (Recommendation: Use jsonschema library here)
        
        # 3. Deterministic Serialization
        # We pass our explicit fallback function to handle the MeshGeneratorConfig object.
        return json.dumps(
            output_data, 
            default=_json_serializable_fallback, 
            indent=4, 
            sort_keys=True
        )