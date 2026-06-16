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
        # Instantiate a dummy to get the path it expects
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
        state.results_grid = {'nx': 10, 'ny': 10, 'nz': 10, 
                              'x_min': 0, 'x_max': 1, 
                              'y_min': 0, 'y_max': 1, 
                              'z_min': 0, 'z_max': 1}
        
        config = {
            "solver_version": "1.0.0",
            "tolerance": 1e-6,
            "max_element_size": 0.5,
            "min_element_size": 0.1
        }
        return Orchestrator(), state, config

    # ----------------------------------------------------------------------
    # Success Path Testing
    # ----------------------------------------------------------------------

    def test_pipeline_single_responsibility_per_step(self, setup_pipeline):
        orchestrator, state, config = setup_pipeline
        initial_state = copy.deepcopy(state)
        
        orchestrator.run(state, config)
        
        # Validate results were updated
        assert state.results_mask != initial_state.results_grid, "Field 'results_mask' was not updated."
        
        # Validate Navier-Stokes Semantic Contract
        valid_mask_values = {-1, 0, 1}
        assert all(val in valid_mask_values for val in state.results_mask), "Invalid mask values."

    # ----------------------------------------------------------------------
    # Error Handling & Fail-Fast Testing
    # ----------------------------------------------------------------------

    def test_pipeline_handles_negative_dimensions(self, setup_pipeline):
        """
        Validates that the pipeline correctly raises a ValueError when 
        invalid (non-positive) dimensions are provided.
        """
        orchestrator, state, config = setup_pipeline
        
        # Force invalid dimensions
        state.results_grid['nx'] = -999
        
        # Assert that the Orchestrator propagates the ValueError from the step
        with pytest.raises(ValueError, match="Invalid mesh dimensions"):
            orchestrator.run(state, config)

    # ----------------------------------------------------------------------
    # Integrity Testing
    # ----------------------------------------------------------------------

    def test_pipeline_no_hidden_side_effects(self, setup_pipeline):
        orchestrator, state, config = setup_pipeline
        original_config = copy.deepcopy(config)
        
        orchestrator.run(state, config)
        assert config == original_config, "Pipeline mutated the configuration object."

    def test_pipeline_deterministic_end_to_end_behaviour(self, setup_pipeline):
        orchestrator, state_1, config = setup_pipeline
        state_2 = copy.deepcopy(state_1)
        
        orchestrator.run(state_1, config)
        orchestrator.run(state_2, config)
        
        assert state_1.results_mask == state_2.results_mask, "Pipeline output is not deterministic."