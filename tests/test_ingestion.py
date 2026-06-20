# tests/test_ingestion.py
import logging
import os
import pytest
from src.steps.ingestion import IngestionStep
from src.state.mesh_generator_state import SovereignContainer

def get_dummy_container(step_path: str) -> SovereignContainer:
    """Helper to satisfy the strict SovereignContainer contract."""
    return SovereignContainer(
        step_file=step_path,
        max_element_size=2.0,
        solver_version="v1.0.0",
        tolerance=1e-4,
        min_element_size=0.5,
        boundary_map={"x_min": "inlet"}
    )

def test_ingestion_logs_on_success(caplog):
    # 1. Setup: Reference the actual geometry dummy file
    # Ensure the path is relative to the project root (where pytest executes)
    dummy_step_path = os.path.join("tests", "dummies", "sample_geometry.step")
    
    assert os.path.exists(dummy_step_path), f"Dummy file missing at {dummy_step_path}"

    # 2. Instantiate with full contract
    container = get_dummy_container(dummy_step_path)
    step = IngestionStep()
    
    with caplog.at_level(logging.INFO):
        # 3. Execution
        step.execute(container)
        
        # 4. Assertions: Verify logic AND geometry loading
        assert "Starting IngestionStep" in caplog.text
        assert "IngestionStep successful" in caplog.text
        
        # Verify the actual geometry was loaded into the container
        # Since the dummy file is a valid sphere, cad_solid should not be None
        assert container.cad_solid is not None, "Ingestion failed to populate cad_solid."

def test_ingestion_logs_error_on_failure(caplog):
    # 1. Instantiate with non-existent path
    container = get_dummy_container("non_existent.step")
    step = IngestionStep()
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            step.execute(container)
        assert "CONSTITUTION VIOLATION" in caplog.text