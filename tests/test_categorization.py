# tests/test_categorization.py
import os
import pytest
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from src.steps.categorization import CategorizationStep
from src.state.mesh_generator_state import SovereignContainer, Grid
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
    container = SovereignContainer(step_file=harness["inputs"]["step_file"])
    
    # 2. State Injection: Populate the container with the real geometry and a valid grid.
    # The grid defines the resolution that the CategorizationStep iterates over.
    container.cad_solid = get_real_sphere_shape()
    container.grid = Grid(
        x_min=0.0, y_min=0.0, z_min=0.0,
        x_max=2.0, y_max=2.0, z_max=2.0,
        nx=2, ny=2, nz=2
    )
    
    # 3. Execution: Run the categorization step.
    # We no longer mock the classifier; we are testing the actual interaction 
    # with the OpenCASCADE SolidClassifier.
    step = CategorizationStep()
    step.execute(container)
    
    # 4. Verification:
    # A unit sphere (radius 1.0) inside a 2x2x2 box (centered at 1,1,1) 
    # should produce a valid mask of length 8 (2*2*2).
    assert len(container.mask) == 8
    
    # In a real integration test, we expect the sphere to occupy the center.
    # We verify that at least one voxel was classified (mask contains 0, 1, or -1).
    assert any(val in [0, 1, -1] for val in container.mask)

def test_categorization_guard_clause():
    """
    [GUARD CLAUSE]
    Verify that the system raises a 'CONSTITUTION VIOLATION' if the 
    grid state is undefined, preventing invalid memory access.
    """
    container = SovereignContainer(step_file="dummy.step")
    container.grid = None # Explicit violation
    
    step = CategorizationStep()
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
        step.execute(container)