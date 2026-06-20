# tests/test_tracing.py
import logging
import pytest
from unittest.mock import MagicMock, patch
from src.steps.tracing import TracingStep
from src.state.mesh_generator_state import SovereignContainer

def get_dummy_container(step_path: str, cad_solid=None) -> SovereignContainer:
    """Helper to ensure full contract adherence."""
    container = SovereignContainer(
        step_file=step_path,
        max_element_size=2.0,
        solver_version="v1.0.0",
        tolerance=1e-4,
        min_element_size=0.5,
        boundary_map={"x_min": "inlet"}
    )
    container.cad_solid = cad_solid
    return container

@patch("OCC.Core.BRepBndLib.brepbndlib.Add")
@patch("OCC.Core.Bnd.Bnd_Box.Get")
def test_tracing_logs_on_success(mock_bbox_get, mock_brep_add, caplog):
    # Mocking the BBox return values
    mock_bbox_get.return_value = (0.0, 0.0, 0.0, 10.0, 10.0, 10.0)
    
    # 1. Create container with a mock CAD solid
    container = get_dummy_container("dummy.step", cad_solid=MagicMock())
    step = TracingStep()
    
    # 2. Execute and verify logs
    with caplog.at_level(logging.INFO):
        step.execute(container)
        
        assert "Starting TracingStep" in caplog.text
        assert "TracingStep successful" in caplog.text
        assert container.bbox == (0.0, 0.0, 0.0, 10.0, 10.0, 10.0)

def test_tracing_logs_error_on_failure(caplog):
    # 1. Create container with cad_solid as None
    container = get_dummy_container("dummy.step", cad_solid=None)
    step = TracingStep()
    
    # 2. Verify failure
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
            step.execute(container)
            
        assert "CONSTITUTION VIOLATION" in caplog.text