# tests/pipeline/test_pipeline_unified_consistency.py

import copy
from tests.signatures.pipeline.pipeline_unified_consistency_test_signature import PipelineUnifiedConsistencyTestSignature

class TestPipelineUnifiedConsistency(PipelineUnifiedConsistencyTestSignature):
    
    # ... (Keep existing fixtures)

    def test_pipeline_single_responsibility_per_step(self, setup_pipeline):
        """
        Validates that the orchestrator executes steps that only modify 
        expected fields and ensures the new physical mask values are valid.
        """
        orchestrator, state, config = setup_pipeline
        
        # 1. Capture state before execution
        initial_state = copy.deepcopy(state)
        
        # 2. Run the pipeline
        orchestrator.run(state, config)
        
        # 3. Define fields that SHOULD change (Results)
        results_fields = ['results_grid', 'results_mask', 'results_boundary_conditions']
        
        # Validation: Check that results were updated
        for field in results_fields:
            assert state[field] != initial_state[field], f"Field '{field}' was not updated."
            
        # 4. NEW: Validate Navier-Stokes Semantic Contract for the Mask
        # Ensures that after the pipeline runs, the values are restricted to {-1, 0, 1}
        valid_mask_values = {-1, 0, 1}
        assert all(val in valid_mask_values for val in state['results_mask']), \
            f"Invalid mask values found in pipeline output. Allowed: {valid_mask_values}"
            
        # Validation: Check that inputs/metadata remained untouched
        immutable_fields = ['inputs_step_file']
        for field in immutable_fields:
            assert state[field] == initial_state[field], f"Field '{field}' was unexpectedly mutated."

    # ... (Keep other test methods)