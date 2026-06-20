# tests/test_tracing.py
import logging
import pytest
from unittest.mock import patch
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.gp import gp_Pnt
from src.steps.tracing import TracingStep
from src.state.mesh_generator_state import SovereignContainer

def get_dummy_container(step_path: str, cad_solid: TopoDS_Shape = None) -> SovereignContainer:
    """Helper to ensure full contract adherence."""
    container = SovereignContainer(
        step_file=step_path,
        max_element_size=2.0,
        solver_version="v1.0.0",
        tolerance=1e-4,
        min_element_size=0.5,
        boundary_map={"x_min": "inlet"}
    )
    if cad_solid is not None:
        container.cad_solid = cad_solid
    return container

def test_tracing_logs_on_success(caplog):
    # 1. Create a real TopoDS_Shape (A point)
    real_vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(0, 0, 0)).Shape()
    
    # 2. Instantiate with valid shape
    container = get_dummy_container("dummy.step", cad_solid=real_vertex)
    step = TracingStep()
    
    with caplog.at_level(logging.INFO):
        step.execute(container)
        
        assert "Starting TracingStep" in caplog.text
        assert "TracingStep successful" in caplog.text
        # FIX: Using pytest.approx handles the OpenCascade epsilon of 1e-07
        assert container.bbox == pytest.approx((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), abs=1e-6)

def test_tracing_logs_error_on_failure(caplog):
    # Pass None to trigger the Constitution Violation
    container = get_dummy_container("dummy.step", cad_solid=None)
    step = TracingStep()
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
            step.execute(container)
        assert "CONSTITUTION VIOLATION" in caplog.text

@patch("src.steps.tracing.brepbndlib.Add")
def test_tracing_logs_error_on_calculation_failure(mock_add, caplog):
    """
    COVERS: Lines 60-62 (the 'except' block).
    Forces an exception during brepbndlib.Add to verify error logging.
    """
    # 1. Setup: Mock the geometric calculation to raise an Exception
    mock_add.side_effect = Exception("Geometry engine crash")
    
    real_vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(0, 0, 0)).Shape()
    container = get_dummy_container("dummy.step", cad_solid=real_vertex)
    step = TracingStep()
    
    # 2. Execute and Verify logs/exception
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="Geometry engine crash"):
            step.execute(container)
            
        assert "TracingStep failed during geometric calculation" in caplog.text