# tests/test_categorization.py
import os
import pytest
from unittest.mock import patch, MagicMock
import numpy as np

# OpenCASCADE Mock Targets
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_OUT
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone

from src.steps.categorization import CategorizationStep
from src.state.mesh_generator_state import SovereignContainer, GridState
import src.steps.categorization as categorization_module

# --- HELPER DATA LOADER ---

def get_real_sphere_shape():
    """
    Parses the actual geometry from the dummy directory.
    We require a valid TopoDS_Shape to satisfy the SovereignContainer constitution.
    """
    file_path = os.path.join(os.path.dirname(__file__), "dummies", "sample_geometry.step")
    reader = STEPControl_Reader()
    if os.path.exists(file_path) and reader.ReadFile(file_path) == IFSelect_RetDone:
        reader.TransferRoots()
        return reader.Shape()
    # Fallback to a magic mock shape if the file is absent in an isolated test context
    return MagicMock()

# --- LITERATE TEST SUITE ---

def test_categorization_guard_clause():
    """
    [CONSTITUTION PATH: GRID CHECK]
    Verify that the system raises a 'CONSTITUTION VIOLATION' if the 
    grid state is undefined, preventing downstream step execution failures.
    """
    container = SovereignContainer(
        use_gmsh=False,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={"x_min": "inlet"}
    )
    
    # Explicitly break the constitution
    container.grid = None 
    
    # Expect a RuntimeError due to the lack of grid state
    step = CategorizationStep()
    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: 'grid' is None"):
        step.execute(container)

def test_categorization_post_condition_violation():
    """
    [CONSTITUTION PATH: POST-CONDITION CHECK]
    Verifies that if an engine finishes execution but leaves the container's 
    mask state unpopulated, a Post-Condition Violation exception aborts the process.
    """
    container = SovereignContainer(
        use_gmsh=False,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # Force mock the voxel engine wrapper to complete while leaving the container empty
    step = CategorizationStep()
    with patch("src.steps.categorization._run_voxel_engine") as mock_voxel:
        mock_voxel.return_value = None
        container.mask = None  # Ensure it remains unallocated
        with pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Categorization Engine failed"):
            step.execute(container)

@patch("src.steps.categorization.BRepClass3d_SolidClassifier")
def test_categorization_legacy_solid_branch(mock_classifier_class):
    """
    [LEGACY VOXEL ENGINE: SOLID CLASSIFICATION]
    Forces the legacy 'Solid' branch mapping. We mock the classifier 
    to report TopAbs_IN for all tested corner coordinates.
    """
    # 1. Setup Mock
    mock_classifier = MagicMock()
    mock_classifier.State.return_value = TopAbs_IN
    mock_classifier_class.return_value = mock_classifier
    
    # 2. Setup Container with valid geometry and legacy mode flag
    container = SovereignContainer(
        use_gmsh=False,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.cad_solid = get_real_sphere_shape() 
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1) # 1x1x1 grid
    
    # 3. Execute
    step = CategorizationStep()
    step.execute(container)
    
    # 4. Assert: Voxel mask 0 corresponds directly to Solid domain
    assert container.mask[0] == 0 
    assert mock_classifier.Perform.called

@patch("src.steps.categorization.BRepClass3d_SolidClassifier")
def test_categorization_legacy_fluid_branch(mock_classifier_class):
    """
    [LEGACY VOXEL ENGINE: FLUID CLASSIFICATION]
    Forces the legacy 'Fluid' branch mapping. We mock the classifier 
    to report TopAbs_OUT for all sampled corners.
    """
    # 1. Setup Mock
    mock_classifier = MagicMock()
    mock_classifier.State.return_value = TopAbs_OUT
    mock_classifier_class.return_value = mock_classifier
    
    # 2. Setup Container
    container = SovereignContainer(
        use_gmsh=False,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.cad_solid = get_real_sphere_shape()
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # 3. Execute
    step = CategorizationStep()
    step.execute(container)
    
    # 4. Assert: Voxel mask 1 corresponds directly to Fluid domain
    assert container.mask[0] == 1

def test_gmsh_engine_missing_bindings_error():
    """
    [GMSH ENGINE PATH: IMPORT ERROR GATING]
    Verifies that running the Gmsh engine in an environment where 
    the python binding is not installed safely raises an explicit 
    RuntimeError detailing missing bindings.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    step = CategorizationStep()
    
    # Intercept inside-scope import execution by temporarily hiding gmsh from sys.modules
    with patch.dict("sys.modules", {"gmsh": None}):
        with pytest.raises(RuntimeError, match="Gmsh Python bindings missing"):
            step.execute(container)

def test_gmsh_engine_topology_violation_error():
    """
    [GMSH ENGINE PATH: TOPOLOGY POST-CONDITION]
    When gmsh initializes but fails to generate 3D tetrahedra elements 
    (type 4 elements), the runtime context must catch the error and 
    throw a specific post-condition violation exception.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="dummy.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # Setup standard Gmsh mocks
    mock_gmsh = MagicMock()
    mock_gmsh.model.mesh.getNodes.return_value = (np.array([1]), np.array([0.0, 0.0, 0.0]), [])
    # Return element type 1 (Lines) instead of type 4 (Tetrahedrons)
    mock_gmsh.model.mesh.getElements.return_value = ([1], [], [])
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        with pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Gmsh failed to generate 3D tetrahedral elements"):
            step.execute(container)

def test_gmsh_engine_full_execution_flow_success():
    """
    [GMSH ENGINE PATH: NOMINAL INTEGRATION FLOW]
    Simulates a successful and pristine Layer 1 unstructured mesh baking 
    execution sequence. Validates matrix caching, automated offscreen 
    visualization rendering, and fallback fluid mask generation.
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 2, 0, 2, 0, 2, 2, 2, 2) # 2x2x2 = 8 cells
    
    # Mocking standard arrays returned by GMSH C API
    np.array([1, 2, 3, 4])
    np.array([0.0, 0.0, 0.0,  1.0, 0.0, 0.0,  0.0, 1.0, 0.0,  0.0, 0.0, 1.0])
    element_types = [4] # Explicitly provide Type 4 Tetrahedrons
    [np.array([101])]
    [np.array([1, 2, 3, 4])]
    
    mock_gmsh = MagicMock()
    mock_gmsh.model.mesh.getNodes.return_value = (np.array([1, 2, 3, 4]), np.array([0.0, 0.0, 0.0,  1.0, 0.0, 0.0,  0.0, 1.0, 0.0,  0.0, 0.0, 1.0]), [])
    mock_gmsh.model.mesh.getElements.return_value = ([4], [np.array([101])], [np.array([1, 2, 3, 4])])
    
    # 2. Use the module reference to clear the cache
    categorization_module._GMSH_MESH_CACHE.clear()
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        step.execute(container)
        
    # 3. Access the cache dynamically via the module reference
    cache = categorization_module._GMSH_MESH_CACHE
    
    assert mock_gmsh.initialize.called
    assert mock_gmsh.finalize.called
    
    # Assertions now use the 'live' cache reference
    assert "nodes_map" in cache
    assert "tets_vertices" in cache
    assert cache["tets_vertices"].shape == (1, 4, 3)
    
    assert len(container.mask) == 8
    assert all(cell == 1 for cell in container.mask)
    
    assert mock_gmsh.fltk.initialize.called
    assert mock_gmsh.write.called

def test_gmsh_engine_visualization_failure_escalation():
    """
    [GMSH ENGINE PATH: VISUALIZATION ROBUSTNESS]
    Verifies that an error raised inside the offscreen rendering buffer loop 
    is caught, handled, and re-thrown without bypassing critical memory lifecycle 
    garbage collection mechanisms (`gmsh.finalize()`).
    """
    container = SovereignContainer(
        use_gmsh=True,
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    mock_gmsh = MagicMock()
    mock_gmsh.model.mesh.getNodes.return_value = (np.array([1, 2, 3, 4]), np.zeros(12), [])
    mock_gmsh.model.mesh.getElements.return_value = ([4], [1], [np.array([1, 2, 3, 4])])
    
    # Force the graphics viewport pipeline write mechanism to throw an internal system exception
    mock_gmsh.write.side_effect = Exception("Xvfb frame buffer allocation timeout")
    
    step = CategorizationStep()
    with patch.dict("sys.modules", {"gmsh": mock_gmsh}):
        with pytest.raises(Exception, match="Xvfb frame buffer allocation timeout"):
            step.execute(container)
            
    # CRITICAL VERIFICATION: Ensure resource cleanup run even on rendering crash loops
    assert mock_gmsh.finalize.called