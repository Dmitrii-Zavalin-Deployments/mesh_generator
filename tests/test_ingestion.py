import logging
import pytest
from src.steps.ingestion import IngestionStep
from src.state.mesh_generator_state import SovereignContainer

def test_ingestion_logs_on_success(caplog):
    # Set the logging level for the test
    with caplog.at_level(logging.INFO):
        container = SovereignContainer(...) # Initialize with valid dummy path
        step = IngestionStep()
        
        # Execute
        step.execute(container)
        
        # Verify the logs exist
        assert "Starting IngestionStep" in caplog.text
        assert "IngestionStep successful" in caplog.text

def test_ingestion_logs_error_on_failure(caplog):
    with caplog.at_level(logging.ERROR):
        container = SovereignContainer(step_file="non_existent.step")
        step = IngestionStep()
        
        with pytest.raises(RuntimeError):
            step.execute(container)
            
        # Verify that the error log was generated
        assert "CONSTITUTION VIOLATION" in caplog.text