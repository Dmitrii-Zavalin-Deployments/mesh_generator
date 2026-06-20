# tests/test_categorization.py
import pytest
from unittest.mock import patch, MagicMock
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_OUT
from src.steps.categorization import CategorizationStep
from src.state.mesh_generator_state import SovereignContainer, Grid

# --- MOCK INFRASTRUCTURE ---

def get_mock_container():
    """Provides a container with a defined grid for testing."""
    container = SovereignContainer(step_file="dummy.step")
    # Define a 2x2x2 grid
    container.grid = Grid(
        x_min=0.0, y_min=0.0, z_min=0.0,
        x_max=2.0, y_max=2.0, z_max=2.0,
        nx=2, ny=2, nz=2
    )
    return container

# --- LITERATE TEST SUITE ---

def test_categorization_guard_clause():
    # We verify that the system raises an error if the grid is missing.
    container = SovereignContainer(step_file="dummy.step")
    container.grid = None
    step = CategorizationStep()
    
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
        step.execute(container)

def test_categorization_logic_solid_voxel():
    # We simulate a "Solid" voxel where the classifier returns TopAbs_IN for all corners.
    container = get_mock_container()
    step = CategorizationStep()
    
    # We patch the classifier to always return IN (Solid)
    with patch("src.steps.categorization.BRepClass3d_SolidClassifier") as mock_classifier:
        instance = mock_classifier.return_value
        instance.State.return_value = TopAbs_IN
        
        step.execute(container)
        
        # In a 2x2x2 grid, all 8 voxels should be 0 (Solid).
        assert all(v == 0 for v in container.mask)

def test_categorization_logic_mixed_boundary():
    # We simulate a "Wall" voxel. 
    # If we force the classifier to alternate states, the logic must classify it as -1 (Wall).
    container = get_mock_container()
    step = CategorizationStep()
    
    with patch("src.steps.categorization.BRepClass3d_SolidClassifier") as mock_classifier:
        instance = mock_classifier.return_value
        # Use side_effect to toggle: first 4 corners IN, next 4 corners OUT
        instance.State.side_effect = [TopAbs_IN] * 4 + [TopAbs_OUT] * 4
        
        step.execute(container)
        
        # Verify that the logic identified the wall (-1).
        assert -1 in container.mask