# tests/test_ingestion.py
import logging
import os
import pytest
from src.steps.ingestion import IngestionStep
from src.state.mesh_generator_state import SovereignContainer

def get_dummy_container(step_path: str) -> SovereignContainer:
    """
    To ensure pipeline integrity, we instantiate the container with 
    strict constraints on element size and versioning, satisfying the 
    SovereignContainer contract before ingestion.
    """
    return SovereignContainer(
        use_gmsh=False,
        step_file=step_path,
        max_element_size=2.0,
        solver_version="v1.0.0",
        tolerance=1e-4,
        min_element_size=0.5,
        boundary_map={"x_min": "inlet"}
    )

def test_ingestion_logs_on_success(caplog):
    # First, we identify the geometric source file.
    # We ensure the sample geometry exists within the test environment;
    # without this file, the ingestion sequence cannot commence.
    dummy_step_path = os.path.join("tests", "dummies", "sample_geometry.step")
    assert os.path.exists(dummy_step_path), f"Dummy file missing at {dummy_step_path}"

    # Next, we prepare the system state.
    # We inject the file path into the container, establishing the data contract.
    container = get_dummy_container(dummy_step_path)
    step = IngestionStep()
    
    # We initiate the ingestion process.
    # The IngestionStep must process the STEP file and transform it into a cad_solid.
    with caplog.at_level(logging.INFO):
        step.execute(container)
        
        # Finally, we assert the post-conditions:
        # The logs must reflect the sequence of operations, and the 
        # container must now hold a valid CAD solid.
        assert "Starting IngestionStep" in caplog.text
        assert "IngestionStep successful" in caplog.text
        assert container.cad_solid is not None, "Ingestion failed to populate cad_solid."

def test_ingestion_logs_error_on_failure(caplog):
    # We simulate a catastrophic system input by providing a non-existent file path.
    # This validates the system's ability to handle missing external resources.
    container = get_dummy_container("non_existent.step")
    step = IngestionStep()
    
    # Upon executing the step, we verify that the system raises a RuntimeError
    # as defined by the Constitution, rather than failing silently.
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            step.execute(container)
        
        # We confirm that the specific violation is captured in the diagnostic logs.
        assert "CONSTITUTION VIOLATION" in caplog.text