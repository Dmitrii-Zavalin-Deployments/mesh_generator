import numpy as np
import pytest

from src.state.mesh_generator_state import GridState, SovereignContainer
from src.steps.categorization import _GMSH_MESH_CACHE
from src.steps.voxelization import VoxelizationStep


def test_voxelization_grid_none():
    """Verifies that executing VoxelizationStep with a None grid raises RuntimeError."""
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1
    )
    container.grid = None
    step = VoxelizationStep()

    with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION: Pipeline order failure. 'grid' must be computed."):
        step.execute(container)


def test_voxelization_missing_mesh_cache():
    """Verifies that missing tets_vertices in global mesh cache raises RuntimeError."""
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    _GMSH_MESH_CACHE.clear()
    step = VoxelizationStep()

    with pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Global mesh cache missing tets_vertices matrix."):
        step.execute(container)


@pytest.mark.parametrize("bad_tol", [None, -0.01])
def test_voxelization_invalid_tolerance(bad_tol):
    """Verifies that invalid tolerances (None or negative) raise ValueError during initialization."""
    with pytest.raises(ValueError):
        SovereignContainer(
            step_file="tests/dummies/sample_geometry.step",
            max_element_size=0.5,
            tolerance=bad_tol,
            min_element_size=0.1
        )


def test_voxelization_degenerate_tetrahedron():
    """Verifies that degenerate tetrahedra raising LinAlgError are safely skipped."""
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1
    )
    container.grid = GridState(0, 1, 0, 1, 0, 1, 1, 1, 1)
    
    # Degenerate tet where all points are identical (zero volume / singular matrix)
    _GMSH_MESH_CACHE["tets_vertices"] = np.array([
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    ], dtype=np.float64)
    
    step = VoxelizationStep()
    step.execute(container)
    assert container.mask is not None
    
    _GMSH_MESH_CACHE.clear()


def test_voxelization_success_classifications():
    """Verifies successful voxelization covering solid, fluid, and wall cell classifications."""
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=1e-6,
        min_element_size=0.1
    )
    # Create a 2x1x1 grid to test multiple cells and classify branches
    container.grid = GridState(0.0, 2.0, 0.0, 1.0, 0.0, 1.0, 2, 1, 1)
    
    # Configure mock tetrahedra covering different grid regions
    _GMSH_MESH_CACHE["tets_vertices"] = np.array([
        # Encloses cell 0 fully -> solid (in_count = 8)
        [[-0.5, -0.5, -0.5], [1.5, -0.5, -0.5], [-0.5, 1.5, -0.5], [-0.5, -0.5, 1.5]],
        # Partial overlap for cell 1 -> wall (-1)
        [[1.2, 0.2, 0.2], [1.8, 0.2, 0.2], [1.2, 0.8, 0.2], [1.2, 0.2, 0.8]]
    ], dtype=np.float64)
    
    step = VoxelizationStep()
    step.execute(container)
    
    assert container.mask is not None
    assert len(container.mask) == 2  # nx * ny * nz = 2 * 1 * 1 = 2
    
    _GMSH_MESH_CACHE.clear()
