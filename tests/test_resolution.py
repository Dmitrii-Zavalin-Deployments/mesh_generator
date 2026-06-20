# tests/test_resolution.py
import logging
import pytest
from unittest.mock import patch
from OCC.Core.TopoDS import TopoDS_Shape
from src.steps.resolution import ResolutionStep
from src.state.mesh_generator_state import SovereignContainer, GridState

def get_dummy_container(bbox=None, cad_solid=None) -> SovereignContainer:
    """Helper to ensure contract adherence."""
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=2.0,
        solver_version="v1.0.0",
        tolerance=1e-4,
        min_element_size=0.5,
        boundary_map={"x_min": "inlet"}
    )
    container.bbox = bbox
    container.cad_solid = cad_solid
    return container

def test_resolution_logs_on_success(caplog):
    """
    [SUCCESS PATH]
    We simulate a valid geometry and existing bbox. We expect the step to 
    correctly calculate the grid resolution and log the successful configuration.
    """
    # 1. Setup: We mock the geometry analysis to ensure deterministic results.
    # We define a 10x10x10 box.
    bbox = (0.0, 0.0, 0.0, 10.0, 10.0, 10.0)
    container = get_dummy_container(bbox=bbox, cad_solid=TopoDS_Shape())
    step = ResolutionStep()

    # 2. Execution: We force the feature size to be 1.0 (between 0.5 and 2.0).
    with patch("src.steps.resolution.get_min_feature_size", return_value=1.0):
        with caplog.at_level(logging.INFO):
            step.execute(container)
            
            # 3. Assertions: Verify logic and logging
            assert "Starting ResolutionStep" in caplog.text
            assert "ResolutionStep successful" in caplog.text
            # Grid resolution: 10 / 1.0 = 10 cells.
            assert container.grid.nx == 10
            assert container.grid.ny == 10
            assert container.grid.nz == 10

def test_resolution_logs_error_on_missing_bbox(caplog):
    """
    [GUARD CLAUSE]
    If the TracingStep was skipped, the container lacks a bbox.
    We must catch this violation immediately.
    """
    container = get_dummy_container(bbox=None, cad_solid=TopoDS_Shape())
    step = ResolutionStep()
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
            step.execute(container)
        assert "CONSTITUTION VIOLATION" in caplog.text

def test_resolution_logs_error_on_geometry_violation(caplog):
    """
    [GEOMETRY GATE]
    If the detected feature size is smaller than the min_element_size,
    the simulation fidelity will be insufficient. We must block execution.
    """
    # 1. Setup: A tiny feature (0.1) vs a min_element_size of 0.5.
    container = get_dummy_container(bbox=(0,0,0,1,1,1), cad_solid=TopoDS_Shape())
    step = ResolutionStep()
    
    # 2. Execution: Force failure via mocking.
    with patch("src.steps.resolution.get_min_feature_size", return_value=0.1):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError, match="GEOMETRY VIOLATION"):
                step.execute(container)
            assert "GEOMETRY VIOLATION" in caplog.text