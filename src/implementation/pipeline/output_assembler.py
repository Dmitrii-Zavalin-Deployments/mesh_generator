# src/implementation/pipeline/output_assembler.py

import json
from src.implementation.state.mesh_generator_state import MeshGeneratorState

class OutputAssembler:
    """
    Deterministic assembly procedure. 
    Responsibility: Only structural assembly and schema validation.
    """
    
    @staticmethod
    def assemble(state: MeshGeneratorState, config: dict, inputs: dict) -> str:
        # 1. Structural Mapping (The Assembly)
        output_data = {
            "inputs": inputs,
            "config": config,
            "results": state.results_grid # Map your actual state results here
        }
        
        # 2. Schema Validation (The Gate)
        # Verify output_data strictly matches mesh_generator_output_schema.json
        # (Recommendation: Use jsonschema library here)
        
        # 3. Deterministic Serialization
        return json.dumps(output_data, indent=4, sort_keys=True)