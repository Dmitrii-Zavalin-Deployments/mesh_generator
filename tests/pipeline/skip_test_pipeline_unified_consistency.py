# tests/pipeline/test_pipeline_unified_consistency.py

import os
import pytest
import copy
from src.implementation.pipeline.orchestrator import Orchestrator
from tests.dummies.mesh_generator_state_dummy import MeshGeneratorStateDummy
from tests.signatures.pipeline.pipeline_unified_consistency_test_signature import PipelineUnifiedConsistencyTestSignature

class TestPipelineUnifiedConsistency(PipelineUnifiedConsistencyTestSignature):
    """
    Concrete implementation of PipelineUnifiedConsistencyTestSignature.
    Validates that the Orchestrator maintains state consistency, deterministic 
    outputs, and strict mutation boundaries.
    """

    @pytest.fixture(autouse=True)
    def verify_dummy_assets(self):
        """Ensures the static dummy STEP file exists before running tests."""
        state = MeshGeneratorStateDummy()
        if not os.path.exists(state.inputs_step_file):
            pytest.fail(f"Required dummy asset not found at {state.inputs_step_file}. "
                        "Please ensure 'dummy_model.stp' is placed in 'tests/dummies/'.")
        yield

    @pytest.fixture
    def setup_pipeline(self):
        """Initializes the orchestrator and state with valid dimensions."""
        state = MeshGeneratorStateDummy()
        
        # Ensure the dummy has valid dimensions for the 'Happy Path'
        state.results_grid = {
            'nx': 10, 'ny': 10, 'nz': 10, 
            'x_min': 0.0, 'x_max': 1.0, 
            'y_min': 0.0, 'y_max': 1.0, 
            'z_min': 0.0, 'z_max': 1.0
        }
        
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
        orchestrator, state, config = setup_pipeline
        initial_state = copy.deepcopy(state)
        
        orchestrator.run(state, config)
        
        # Validate that the expected physical mask was generated
        assert state.results_mask != initial_state.results_mask, "Field 'results_mask' was not updated."
        
        # Validate Navier-Stokes Semantic Contract for the Mask
        valid_mask_values = {-1, 0, 1}
        assert all(val in valid_mask_values for val in state.results_mask), \
            f"Invalid mask values found in pipeline output. Allowed: {valid_mask_values}"

    def test_pipeline_no_schema_mutation(self, setup_pipeline):
        orchestrator, state, config = setup_pipeline
        original_state = copy.deepcopy(state)
        
        orchestrator.run(state, config)
        
        # Verify that inputs/metadata (fields outside the results scope) remain identical
        assert state.inputs_step_file == original_state.inputs_step_file, \
            "Pipeline improperly mutated the input file path."

    def test_pipeline_deterministic_end_to_end_behaviour(self, setup_pipeline):
        orchestrator, state_1, config = setup_pipeline
        state_2 = copy.deepcopy(state_1)
        
        orchestrator.run(state_1, config)
        orchestrator.run(state_2, config)
        
        # End-to-end deterministic check
        assert state_1.results_mask == state_2.results_mask, "Pipeline output is not deterministic."
        assert state_1.results_grid == state_2.results_grid, "Pipeline grid output drift detected."

    def test_pipeline_no_hidden_side_effects(self, setup_pipeline):
        orchestrator, state, config = setup_pipeline
        original_config = copy.deepcopy(config)
        
        orchestrator.run(state, config)
        
        # Ensure the orchestrator strictly reads the config and does not modify it
        assert config == original_config, "Pipeline mutated the configuration object."

    def test_pipeline_schema_completeness(self, setup_pipeline):
        orchestrator, state, config = setup_pipeline
        
        orchestrator.run(state, config)
        
        # Check required fields are populated and structurally sound
        assert getattr(state, 'results_grid', None) is not None, "results_grid is missing."
        assert state.results_grid.get('nx', 0) > 0, "results_grid 'nx' must be positive."
        assert getattr(state, 'results_mask', None) is not None, "results_mask is missing."
        assert len(state.results_mask) > 0, "results_mask is empty."

    def test_pipeline_error_propagation_and_reporting(self, setup_pipeline):
        orchestrator, state, config = setup_pipeline
        
        # Inject invalid state to trigger fail-fast logic in ComputeMaskStep
        state.results_grid = {'nx': -999, 'ny': 10, 'nz': 10, 'x_min': 0.0, 'x_max': 1.0, 'y_min': 0.0, 'y_max': 1.0, 'z_min': 0.0, 'z_max': 1.0}
        
        # The pipeline MUST propagate the specific step-level failure up to the caller
        with pytest.raises(ValueError, match="Invalid mesh dimensions"): 
            orchestrator.run(state, config)