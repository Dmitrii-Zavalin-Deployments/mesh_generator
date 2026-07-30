# tests/test_tracing.py
import logging
from unittest.mock import patch

import pytest
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Shape

from src.state.mesh_generator_state import SovereignContainer
from src.steps.tracing import TracingStep


def get_dummy_container(step_path: str, cad_solid: TopoDS_Shape = None) -> SovereignContainer:
    """
    Helper function to satisfy the SovereignContainer contract.
    We inject the necessary parameters to prevent pipeline initialization errors.
    """
    container = SovereignContainer(
        use_gmsh=False,
        step_file=step_path,
        max_element_size=2.0,
        tolerance=1e-4,
        min_element_size=0.5,
        boundary_map={"x_min": "inlet"}
    )
    if cad_solid is not None:
        container.cad_solid = cad_solid
    return container

def test_tracing_logs_on_success(caplog):
    # We establish a baseline geometric shape. 
    # Since TracingStep requires a valid TopoDS_Shape, we create a point at the origin.
    real_vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(0, 0, 0)).Shape()
    
    # We load this shape into the SovereignContainer.
    container = get_dummy_container("dummy.step", cad_solid=real_vertex)
    step = TracingStep()
    
    # We execute the TracingStep. 
    # Upon success, the system should populate the BBox and log the progress.
    with caplog.at_level(logging.INFO):
        step.execute(container)
        
        assert "Starting TracingStep" in caplog.text
        assert "TracingStep successful" in caplog.text
        
        # The expected Bounding Box for a single point is (0,0,0,0,0,0).
        # We use pytest.approx to accommodate the OpenCascade internal kernel epsilon (1e-07).
        assert container.bbox == pytest.approx((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), abs=1e-6)

def test_tracing_logs_error_on_failure(caplog):
    # The Constitution requires 'cad_solid' to be present. 
    # If we pass None, the TracingStep must enforce this dependency.
    container = get_dummy_container("dummy.step", cad_solid=None)
    step = TracingStep()
    
    # We verify that a RuntimeError is raised, halting the pipeline,
    # and ensuring the violation is clearly logged.
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
            step.execute(container)
        assert "CONSTITUTION VIOLATION" in caplog.text

@patch("src.steps.tracing.brepbndlib.Add")
def test_tracing_logs_error_on_calculation_failure(mock_add, caplog):
    # We simulate a catastrophic failure in the geometric kernel.
    # This ensures our error handling (the 'except' block) correctly logs and propagates exceptions.
    mock_add.side_effect = Exception("Geometry engine crash")
    
    real_vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(0, 0, 0)).Shape()
    container = get_dummy_container("dummy.step", cad_solid=real_vertex)
    step = TracingStep()
    
    # We confirm that the calculation failure is caught and re-raised for upstream handling.
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="Geometry engine crash"):
            step.execute(container)
            
        assert "TracingStep failed during geometric calculation" in caplog.text
