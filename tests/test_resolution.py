# tests/test_resolution.py
import logging
import pytest
from unittest.mock import patch
from OCC.Core.TopoDS import TopoDS_Shape
from src.steps.resolution import ResolutionStep, get_min_feature_size
from src.state.mesh_generator_state import SovereignContainer

# --- UTILITY TEST SUITE: Feature Detection Logic ---

def test_get_min_feature_size_edge_detection():
    """
    [BRANCH COVERAGE: Edge Path]
    We verify the utility correctly identifies the smallest edge length.
    To prevent low-level C++ deadlocks in headless environments, all native
    extension functions must be fully patched.
    """
    # 1. Setup: We isolate the system by mocking both the topology explorer 
    # and the global C++ linear property calculator wrapper.
    with patch("src.steps.resolution.TopExp_Explorer") as mock_explorer, \
         patch("src.steps.resolution.GProp_GProps") as mock_props, \
         patch("src.steps.resolution.brepgprop_LinearProperties"):
        
        # We simulate finding exactly two edges before terminating the iteration.
        mock_explorer.return_value.More.side_effect = [True, True, False]
        
        # We specify two mock lengths: Edge A = 5.0, Edge B = 2.0.
        mock_props.return_value.Mass.side_effect = [5.0, 2.0]
        
        # 2. Execution: Run the feature size calculator inside our pure Python sandbox.
        min_feature = get_min_feature_size(TopoDS_Shape())
        
        # 3. Verification:
        # The algorithm must accurately isolate and return the lowest bound value.
        assert min_feature == 2.0

def test_get_min_feature_size_bbox_fallback():
    """
    [BRANCH COVERAGE: Fallback Path]
    If no edges are present, the system must calculate the smallest 
    bounding box dimension. We intercept the bounding box library call 
    to ensure zero native memory leaks.
    """
    # 1. Setup: We simulate a geometry lacking structural edge components.
    with patch("src.steps.resolution.TopExp_Explorer") as mock_explorer, \
         patch("src.steps.resolution.Bnd_Box") as mock_bbox, \
         patch("src.steps.resolution.brepbndlib"):
        
        # The explorer reports no edges instantly.
        mock_explorer.return_value.More.return_value = False
        
        # We supply an explicit bounding box output tuple:
        # Formatted as (xmin, ymin, zmin, xmax, ymax, zmax)
        # Yields dimensional lengths: DeltaX = 10.0, DeltaY = 5.0, DeltaZ = 20.0
        mock_bbox.return_value.Get.return_value = (0.0, 0.0, 0.0, 10.0, 5.0, 20.0)
        
        # 2. Execution: Run calculation.
        min_feature = get_min_feature_size(TopoDS_Shape())
        
        # 3. Verification:
        # The minimum dimensional delta among all bounds is 5.0 (the Y axis span).
        assert min_feature == 5.0

# --- ARCHITECTURAL GATE TEST SUITE: ResolutionStep ---

def get_dummy_container(bbox=None, cad_solid=None) -> SovereignContainer:
    """Standardized setup for testing pipeline state containers."""
    return SovereignContainer(
        step_file="dummy.step",
        max_element_size=2.0,
        solver_version="v1.0.0",
        tolerance=1e-4,
        min_element_size=0.5,
        boundary_map={"x_min": "inlet"}
    )

def test_resolution_logs_on_success(caplog):
    """
    [SUCCESS PATH]
    We simulate a valid geometry and existing bbox. We verify that the step 
    correctly calculates the grid resolution and logs the configuration.
    """
    # 1. Setup:
    bbox = (0.0, 0.0, 0.0, 10.0, 10.0, 10.0)
    container = get_dummy_container(bbox=bbox, cad_solid=TopoDS_Shape())
    step = ResolutionStep()

    # 2. Logic: We mock the feature size calculation to force an adaptive_el of 1.0.
    # Feature size 1.0 is between min(0.5) and max(2.0).
    with patch("src.steps.resolution.get_min_feature_size", return_value=1.0):
        with caplog.at_level(logging.INFO):
            step.execute(container)
            
            # 3. Verification: 
            # Span (10) / ElementSize (1.0) = 10 cells.
            assert "ResolutionStep successful" in caplog.text
            assert container.grid.nx == 10
            assert container.grid.ny == 10
            assert container.grid.nz == 10

def test_resolution_logs_error_on_missing_bbox(caplog):
    """
    [GUARD CLAUSE]
    If the TracingStep was skipped, the container lacks a bbox.
    The system must raise a RuntimeError and log the violation.
    """
    container = get_dummy_container(bbox=None)
    step = ResolutionStep()
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
            step.execute(container)
        assert "CONSTITUTION VIOLATION" in caplog.text

def test_resolution_logs_error_on_geometry_violation(caplog):
    """
    [GEOMETRY GATE]
    If the detected feature is smaller than the resolution floor,
    we must abort to prevent aliasing.
    """
    # 1. Setup: Feature size 0.1, Min allowed size 0.5.
    container = get_dummy_container(bbox=(0,0,0,1,1,1), cad_solid=TopoDS_Shape())
    step = ResolutionStep()
    
    # 2. Logic: Mock the feature size to be below threshold.
    with patch("src.steps.resolution.get_min_feature_size", return_value=0.1):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError, match="GEOMETRY VIOLATION"):
                step.execute(container)
            assert "GEOMETRY VIOLATION" in caplog.text