# tests/test_resolution.py
import logging
import os
from unittest.mock import patch

import pytest
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopoDS import TopoDS_Shape

from src.state.mesh_generator_state import SovereignContainer
from src.steps.resolution import ResolutionStep, get_min_feature_size

# --- DUMMY GEOMETRY LOADER ---

# We define a loader to bridge the gap between static disk-based geometry
# and the runtime memory requirements of OpenCASCADE.
def get_real_sphere_shape():
    """Locates and parses the external STEP dummy file."""
    # Build path relative to this file: tests/dummies/sample_geometry.step
    file_path = os.path.join(os.path.dirname(__file__), "dummies", "sample_geometry.step")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing dummy file at: {file_path}")
    
    reader = STEPControl_Reader()
    if reader.ReadFile(file_path) == IFSelect_RetDone:
        reader.TransferRoots()
        return reader.Shape()
    
    raise RuntimeError(f"Failed to process STEP file: {file_path}")

# --- UTILITY TEST SUITE: Feature Detection Logic ---

def test_get_min_feature_size_edge_detection():
    # We verify the utility correctly identifies the smallest edge length.
    # To prevent low-level C++ deadlocks in headless environments, 
    # we isolate the system by mocking the topology explorer and property calculator.
    with patch("src.steps.resolution.TopExp_Explorer") as mock_explorer, \
         patch("src.steps.resolution.GProp_GProps") as mock_props, \
         patch("src.steps.resolution.brepgprop.LinearProperties"):
        
        # We simulate finding exactly two edges before terminating the iteration.
        mock_explorer.return_value.More.side_effect = [True, True, False]
        
        # Edge A = 5.0, Edge B = 2.0. 
        # The expected minimum feature size is min(5.0, 2.0) = 2.0.
        mock_props.return_value.Mass.side_effect = [5.0, 2.0]
        
        min_feature = get_min_feature_size(TopoDS_Shape())
        assert min_feature == 2.0

def test_get_min_feature_size_bbox_fallback():
    # If no edges are present, the system calculates the smallest bounding box dimension.
    # We intercept the library call to ensure zero native memory leaks.
    with patch("src.steps.resolution.TopExp_Explorer") as mock_explorer, \
         patch("src.steps.resolution.Bnd_Box") as mock_bbox, \
         patch("src.steps.resolution.brepbndlib"):
        
        mock_explorer.return_value.More.return_value = False
        
        # We supply an explicit bounding box: (xmin, ymin, zmin, xmax, ymax, zmax)
        # Yields dimensional lengths: 
        #     DeltaX = 10.0, DeltaY = 5.0, DeltaZ = 20.0
        # The minimum dimensional delta is min(10.0, 5.0, 20.0) = 5.0.
        mock_bbox.return_value.Get.return_value = (0.0, 0.0, 0.0, 10.0, 5.0, 20.0)
        
        min_feature = get_min_feature_size(TopoDS_Shape())
        assert min_feature == 5.0

# --- ARCHITECTURAL GATE TEST SUITE ---

def get_dummy_container(bbox=None, cad_solid=None) -> SovereignContainer:
    """Standardized setup for testing pipeline state containers."""
    container = SovereignContainer(
        use_gmsh=False,
        step_file="dummy.step",
        max_element_size=2.0,
        solver_version="v1.0.0",
        tolerance=1e-4,
        min_element_size=0.5,
        boundary_map={"x_min": "inlet"}
    )
    # Manual assignment ensures the object state persists past the constructor.
    container.cad_solid = cad_solid if cad_solid else TopoDS_Shape()
    container.bbox = bbox
    return container

def test_resolution_logs_on_success(caplog):
    # Setup: We use a real sphere geometry and a defined bounding box.
    # Span = 10.0. ElementSize = 1.0.
    cad_solid = get_real_sphere_shape()
    bbox = (0.0, 0.0, 0.0, 10.0, 10.0, 10.0)
    container = get_dummy_container(bbox=bbox, cad_solid=cad_solid)
    step = ResolutionStep()

    # Logic: Grid resolution N is calculated as:
    #     N = Span / ElementSize = 10.0 / 1.0 = 10
    with patch("src.steps.resolution.get_min_feature_size", return_value=1.0):
        with caplog.at_level(logging.INFO):
            step.execute(container)
            
            assert "ResolutionStep successful" in caplog.text
            assert container.grid.nx == 10

def test_resolution_logs_error_on_missing_bbox(caplog):
    # If the TracingStep was skipped, the container lacks a bbox.
    # The system must raise a RuntimeError (Constitution Violation) to prevent downstream failures.
    container = get_dummy_container(bbox=None)
    step = ResolutionStep()
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
            step.execute(container)

def test_resolution_logs_error_on_geometry_violation(caplog):
    # If the detected feature size (0.1) is smaller than the resolution floor (0.5),
    # the system must abort to prevent mesh aliasing.
    container = get_dummy_container(bbox=(0,0,0,1,1,1), cad_solid=TopoDS_Shape())
    step = ResolutionStep()
    
    # Validation: 0.1 < 0.5 triggers the GEOMETRY VIOLATION.
    with patch("src.steps.resolution.get_min_feature_size", return_value=0.1):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError, match="GEOMETRY VIOLATION"):
                step.execute(container)