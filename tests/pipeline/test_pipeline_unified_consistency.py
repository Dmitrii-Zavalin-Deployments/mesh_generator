# tests/pipeline/test_pipeline_unified_consistency.py

import pytest
import copy
import os
from tests.signatures.pipeline.pipeline_unified_consistency_test_signature import PipelineUnifiedConsistencyTestSignature
from tests.dummies.mesh_generator_state_dummy import MeshGeneratorStateDummy
from src.implementation.pipeline.orchestrator import Orchestrator

class TestPipelineUnifiedConsistency(PipelineUnifiedConsistencyTestSignature):
    """
    Concrete implementation of PipelineUnifiedConsistencyTestSignature.
    Validates that the Orchestrator maintains state consistency, deterministic 
    outputs, and strict mutation boundaries.
    """

    @pytest.fixture(autouse=True)
    def verify_dummy_assets(self):
        """Ensures the static dummy STEP file exists before running tests."""
        # Instantiate a dummy to get the path it expects
        state = MeshGeneratorStateDummy()
        if not os.path.exists(state.inputs_step_file):
            pytest.fail(f"Required dummy asset not found at {state.inputs_step_file}. "
                        "Please ensure 'dummy_model.stp' is placed in 'tests/dummies/'.")
        yield

    @pytest.fixture
    def setup_pipeline(self):
        """Initializes the orchestrator and state."""
        state = MeshGeneratorStateDummy()
        # Mock config for the pipeline - fully compliant with No-Defaults Policy
        config = {
            "solver_version": "1.0.0",
            "tolerance": 1e-6,
            "max_element_size": 0.5,
            "min_element_size": 0.1,
            "boundary_conditions": {
                "wall": {"u": 0.0, "v": 0.0, "w": 0.0, "p": 101325.0},
                "inlet": {"u": 1.0, "v": 0.0, "w": 0.0, "p": 101325.0}
            }
        }
        return Orchestrator(), state, config

    # ----------------------------------------------------------------------
    # 3.2.3 — Pipeline‑Level Consistency Gate Implementations
    # ----------------------------------------------------------------------

    def test_pipeline_single_responsibility_per_step(self, setup_pipeline):
        """
        Validates that the orchestrator executes steps that only modify 
        expected fields, ensuring strict mutation boundaries.
        """
        orchestrator, state, config = setup_pipeline
        
        # 1. Capture state before execution
        initial_state = copy.deepcopy(state)
        
        # 2. Run the pipeline
        orchestrator.run(state, config)
        
        # 3. Define fields that SHOULD change (Results)
        results_fields = ['results_grid', 'results_mask', 'results_boundary_conditions']
        
        # 4. Define fields that should NOT change (Inputs/Metadata)
        immutable_fields = ['inputs_step_file']
        
        # Validation: Check that results were updated
        for field in results_fields:
            # We use .get() for safe dict access if state is a dict, or attribute access if object
            assert state[field] != initial_state[field], f"Field '{field}' was not updated by the pipeline."
            
        # Validation: Check that inputs/metadata remained untouched
        for field in immutable_fields:
            assert state[field] == initial_state[field], f"Field '{field}' was unexpectedly mutated by the pipeline."

    def test_pipeline_no_schema_mutation(self, setup_pipeline):
        """
        Ensures that executing the pipeline does not corrupt fields 
        outside the scope of the current step or the schema.
        """
        orchestrator, state, config = setup_pipeline
        original_state = copy.deepcopy(state)
        
        # Run execution
        orchestrator.run(state, config)
        
        # Verify that fields not touched by the pipeline remain identical
        assert state['inputs_step_file'] == original_state['inputs_step_file']

    def test_pipeline_deterministic_end_to_end_behaviour(self, setup_pipeline):
        """
        Runs the pipeline twice with identical inputs and asserts output equality.
        """
        orchestrator, state_1, config = setup_pipeline
        state_2 = copy.deepcopy(state_1)
        
        # Run pipeline 1
        orchestrator.run(state_1, config)
        
        # Run pipeline 2
        orchestrator.run(state_2, config)
        
        # Note: Depending on your state's implementation, you may need a custom equality check
        assert state_1 == state_2, "Pipeline output is not deterministic."

    def test_pipeline_no_hidden_side_effects(self, setup_pipeline):
        """
        Ensures the config object is not mutated during the pipeline run.
        """
        orchestrator, state, config = setup_pipeline
        original_config = copy.deepcopy(config)
        
        orchestrator.run(state, config)
        
        assert config == original_config, "Pipeline mutated the configuration object."

    def test_pipeline_schema_completeness(self, setup_pipeline):
        orchestrator, state, config = setup_pipeline
        
        # Pipeline must run to populate the state
        orchestrator.run(state, config)
        
        # Check required fields
        assert state['results_grid']['nx'] > 0
        assert len(state['results_mask']) > 0

    def test_pipeline_error_propagation_and_reporting(self, setup_pipeline):
        orchestrator, state, config = setup_pipeline
        
        # Inject invalid state
        state['inputs_step_file'] = "non_existent_file.stp"
        
        # Pipeline must run to trigger the exception
        with pytest.raises(Exception): 
            orchestrator.run(state, config)