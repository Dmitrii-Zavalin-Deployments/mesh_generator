# tests/test_ingestion.py
import logging
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

def test_ingestion_logs_on_success(caplog, tmp_path):
    # 1. Setup: Create a temp dummy file
    dummy_step = tmp_path / "test_geometry.step"
    dummy_step.write_text("dummy")

    # 2. Instantiate with full contract
    container = get_dummy_container(str(dummy_step))
    step = IngestionStep()
    
    with caplog.at_level(logging.INFO):
        step.execute(container)
        assert "Starting IngestionStep" in caplog.text
        assert "IngestionStep successful" in caplog.text

def test_ingestion_logs_error_on_failure(caplog):
    # 1. Instantiate with non-existent path
    container = get_dummy_container("non_existent.step")
    step = IngestionStep()
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            step.execute(container)
        assert "CONSTITUTION VIOLATION" in caplog.text