# tests/test_categorization.py
import os
import pytest
from unittest.mock import patch, MagicMock
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_OUT
from OCC.Core.IFSelect import IFSelect_RetDone
from src.steps.categorization import CategorizationStep
# FIXED: We align our import with the core production state contract
from src.state.mesh_generator_state import SovereignContainer, GridState
from tests.dummies.dummy_harness import dummy_in

# --- DUMMY DATA LOADER ---

def get_real_sphere_shape():
    """Parses the actual geometry from the dummy directory."""
    file_path = os.path.join(os.path.dirname(__file__), "dummies", "sample_geometry.step")
    reader = STEPControl_Reader()
    if reader.ReadFile(file_path) == IFSelect_RetDone:
        reader.TransferRoots()
        return reader.Shape()
    raise RuntimeError(f"Failed to load dummy geometry: {file_path}")

# --- LITERATE TEST SUITE ---

def test_categorization_integration():
    """
    [INTEGRATION PATH]
    We use the dummy_in harness and real STEP geometry to verify 
    the CategorizationStep logic in a production-like environment.
    """
    
    # 1. Setup: Initialize using the dummy harness configuration.
    harness = dummy_in()
    container = SovereignContainer(
        step_file=harness["inputs"]["step_file"],
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"x_min": "inlet"}
    )
    
    # 2. State Injection: Populate the container with real geometry.
    container.cad_solid = get_real_sphere_shape()
    
    # FIXED: Instantiate GridState to satisfy SovereignContainer validation
    container.grid = GridState(
        x_min=0.0, x_max=2.0,
        y_min=0.0, y_max=2.0,
        z_min=0.0, z_max=2.0,
        nx=2, ny=2, nz=2
    )
    
    # 3. Execution: Run the categorization step.
    step = CategorizationStep()
    step.execute(container)
    
    # 4. Verification: A 2x2x2 grid yields an 8-cell computational mask.
    assert len(container.mask) == 8
    assert any(val in [0, 1, -1] for val in container.mask)

def test_categorization_guard_clause():
    """
    [GUARD CLAUSE]
    Verify that the system raises a 'CONSTITUTION VIOLATION' if the 
    grid state is undefined, preventing invalid memory access downstream.
    """
    container = SovereignContainer(
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"x_min": "inlet"}
    )
    container.grid = None 
    
    step = CategorizationStep()
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
        step.execute(container)

@patch("src.steps.categorization.BRepClass3d_SolidClassifier")
def test_categorization_branch_solid(mock_classifier_class):
    """Forces the 'Solid' branch (Lines 84-85) to reach 100% coverage."""
    # 1. Setup Mock
    mock_classifier = MagicMock()
    mock_classifier.State.return_value = TopAbs_IN # Force ALL corners IN
    mock_classifier_class.return_value = mock_classifier
    
    # 2. Setup Container
    harness = dummy_in()
    container = SovereignContainer(
        step_file=harness["inputs"]["step_file"],
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"x_min": "inlet"}
    )
    container.cad_solid = MagicMock() # Mock the shape
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1) # 1x1x1 grid
    
    # 3. Execute
    step = CategorizationStep()
    step.execute(container)
    
    # 4. Assert
    assert container.mask[0] == 0  # Solid
    assert mock_classifier.Perform.called

@patch("src.steps.categorization.BRepClass3d_SolidClassifier")
def test_categorization_branch_fluid(mock_classifier_class):
    """Forces the 'Fluid' branch (Lines 86-88) to reach 100% coverage."""
    # 1. Setup Mock
    mock_classifier = MagicMock()
    mock_classifier.State.return_value = TopAbs_OUT # Force ALL corners OUT
    mock_classifier_class.return_value = mock_classifier
    
    # 2. Setup Container
    container = SovereignContainer(
        step_file="test.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.cad_solid = MagicMock()
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # 3. Execute
    step = CategorizationStep()
    step.execute(container)
    
    # 4. Assert
    assert container.mask[0] == 1  # Fluid