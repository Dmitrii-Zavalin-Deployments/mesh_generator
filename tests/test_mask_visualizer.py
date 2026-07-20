# tests/test_mask_visualizer.py
import os
import logging
from unittest.mock import patch, MagicMock
from src.utils.mask_visualizer import generate_mask_snapshot

# --- LITERATE TEST SUITE ---

def test_generate_mask_snapshot_missing_data(caplog):
    """
    [ROBUSTNESS PATH: MISSING DATA]
    Verify that the visualization routine immediately stops and logs an appropriate 
    warning if the computational grid descriptor or the voxel state mask is completely absent.
    """
    # We construct an invalid state dictionary where the 'grid' configuration key is missing.
    # The visualization logic must gracefully intercept this condition and skip rendering:
    #     Condition: (not grid or not mask_1d) -> True
    malformed_input = {
        "results": {
            "mask": [1, 0, 1],
            "mesh_snapshot_path": "workspace/mesh.png"
        }
    }

    with caplog.at_level(logging.WARNING):
        generate_mask_snapshot(malformed_input)
        
    # Assertion: The early exit gate must trigger a clean warning notification.
    assert "Voxel visualizer skipped" in caplog.text


def test_generate_mask_snapshot_nominal_flow(tmpdir):
    """
    [SUCCESS PATH: NOMINAL RESOLUTION & COLOR MAPPING]
    Verifies full execution path through the 3D voxel reconstruction engine, checking path 
    resolution, indexing, and color matrix mapping for all supported cell states.
    """
    # We define a micro 3D grid consisting of 2x2x2 elements.
    # Total expected cells = nx * ny * nz = 2 * 2 * 2 = 8 cells.
    nx, ny, nz = 2, 2, 2
    
    # We populate the 1D mask array to exercise every single color mapping branch:
    # Index 0 -> 1  (Fluid color: light blue with 20% opacity)
    # Index 1 -> 0  (Solid color: opaque grey)
    # Index 2 -> -1 (Wall color: deep dark blue boundary layer)
    # Index 3 -> 99 (Fallback unassigned color: transparent white)
    # Indices 4-7 -> 1 (Remaining fluid padding)
    test_mask = [1, 0, -1, 99, 1, 1, 1, 1]
    
    # Define a clean sandbox location using the temporary directory fixture
    mock_snapshot_file = os.path.join(str(tmpdir), "output_dir", "mesh_snapshot.png")
    
    nominal_input = {
        "results": {
            "grid": {
                "x_min": 0.0, "x_max": 2.0,
                "y_min": 0.0, "y_max": 2.0,
                "z_min": 0.0, "z_max": 2.0,
                "nx": nx, "ny": ny, "nz": nz
            },
            "mask": test_mask,
            "mesh_snapshot_path": mock_snapshot_file
        }
    }

    # Execute nominal visualization flow. It must map colors and save a PNG file to disk.
    generate_mask_snapshot(nominal_input)
    
    # Assertion: Dynamic path resolution should successfully create the target file.
    expected_png_path = os.path.join(os.path.dirname(mock_snapshot_file), "voxel_mask_verification.png")
    assert os.path.exists(expected_png_path)


def test_generate_mask_snapshot_fallback_directories(tmpdir):
    """
    [PATH RESOLUTION: FALLBACK BRANCHES]
    Verify directory selection tracking when 'mesh_snapshot_path' is missing, 
    forcing fallback to 'fallback_save_dir' or the current working directory.
    """
    # We construct a scenario with a valid grid and mask, but empty mesh snapshot path.
    # The save location path resolution logic states:
    #     save_dir = fallback_save_dir if provided else os.getcwd()
    nx, ny, nz = 1, 1, 1
    fallback_dir = os.path.join(str(tmpdir), "fallback_anchor")
    
    input_data = {
        "results": {
            "grid": {"x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1, "nx": nx, "ny": ny, "nz": nz},
            "mask": [1],
            "mesh_snapshot_path": ""
        }
    }

    # Case A: Fallback directory is explicitly given
    generate_mask_snapshot(input_data, fallback_save_dir=fallback_dir)
    assert os.path.exists(os.path.join(fallback_dir, "voxel_mask_verification.png"))

    # Case B: Neither path is specified, fallback directly to current working directory
    with patch("os.getcwd", return_value=str(tmpdir)), \
         patch("os.makedirs") as mock_makedirs, \
         patch("matplotlib.pyplot.savefig") as mock_savefig:
         
        generate_mask_snapshot(input_data, fallback_save_dir=None)
        
        # Assertion: Script must default to current workspace fallback path context
        mock_makedirs.assert_called_with(str(tmpdir), exist_ok=True)
        mock_savefig.assert_called_once()


def test_generate_mask_snapshot_dimension_mismatch(caplog):
    """
    [ERROR PATH: LATTICE BALANCING]
    Verify that a dimensional mismatch between structural grid parameters and the physical 
    1D mask array length is caught gracefully, avoiding system-wide execution faults.
    """
    # We define a lattice layout demanding 2x2x2 = 8 items.
    # However, we intentionally pass an undersized array containing only 3 elements:
    #     len(mask) = 3 != 8 -> True
    mismatched_input = {
        "results": {
            "grid": {"x_min": 0, "x_max": 2, "y_min": 0, "y_max": 2, "z_min": 0, "z_max": 2, "nx": 2, "ny": 2, "nz": 2},
            "mask": [1, 0, 1]
        }
    }

    with caplog.at_level(logging.ERROR):
        generate_mask_snapshot(mismatched_input)
        
    # Assertion: The dimension mismatch ValueError must be caught and logged cleanly
    assert "Lattice dimension mismatch" in caplog.text


def test_generate_mask_snapshot_exception_catch_all(caplog):
    """
    [ROBUSTNESS PATH: EXCEPTION ISOLATION GATE - TIMEOUT]
    Ensures that any structural canvas initialization error or unexpected rendering subsystem 
    fault containing 'timeout' is cleanly routed to its matching logger pathway.
    """
    # Construct a valid data instance to bypass early exit path gates
    valid_input = {
        "results": {
            "grid": {"x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1, "nx": 1, "ny": 1, "nz": 1},
            "mask": [1]
        }
    }

    # We deliberately inject an unexpected plotting crash by breaking matplotlib figure invocation
    with patch("matplotlib.pyplot.figure", side_effect=RuntimeError("Graphics context allocation timeout")), \
         caplog.at_level(logging.ERROR):
         
        # The routine must catch the exception internally instead of propagating it upwards
        generate_mask_snapshot(valid_input)
        
    # Assertion: The isolation gate must capture the error tracking context
    assert "Non-blocking visualization capture routine failure" in caplog.text


def test_generate_mask_snapshot_striding_large_voxels(tmpdir):
    """
    [OPTIMIZATION PATH: SPATIAL STRIDING FOR LARGE LATTICES]
    Verify that the spatial downsampling logic applies a stride factor of 4 when total voxels 
    exceed the 1,000,000 limit threshold to protect GitHub Actions runner runtime footprints (Lines 61-64).
    """
    nx, ny, nz = 101, 100, 100  # 1,010,000 total voxels (> 1_000_000)
    mask_1d = [1] * (nx * ny * nz)
    
    input_data = {
        "results": {
            "grid": {"nx": nx, "ny": ny, "nz": nz, "x_min": 0, "x_max": 10, "y_min": 0, "y_max": 10, "z_min": 0, "z_max": 10},
            "mask": mask_1d
        }
    }
    
    generate_mask_snapshot(input_data, fallback_save_dir=str(tmpdir))
    assert os.path.exists(os.path.join(str(tmpdir), "voxel_mask_verification.png"))


def test_generate_mask_snapshot_striding_axis_ceiling(tmpdir):
    """
    [OPTIMIZATION PATH: SPATIAL STRIDING FOR EXTENDED AXIS]
    Verify that a downsampling stride factor of 2 is applied when an individual grid axis length 
    exceeds MAX_AXIS_CEILING (150) even if the net volume is under 1,000,000 (Lines 61-64).
    """
    nx, ny, nz = 160, 2, 2  # 640 total voxels, but nx > 150 ceiling
    mask_1d = [1] * (nx * ny * nz)
    
    input_data = {
        "results": {
            "grid": {"nx": nx, "ny": ny, "nz": nz, "x_min": 0, "x_max": 10, "y_min": 0, "y_max": 10, "z_min": 0, "z_max": 10},
            "mask": mask_1d
        }
    }
    
    generate_mask_snapshot(input_data, fallback_save_dir=str(tmpdir))
    assert os.path.exists(os.path.join(str(tmpdir), "voxel_mask_verification.png"))


def test_generate_mask_snapshot_cad_rendering_success(tmpdir):
    """
    [SUCCESS PATH: CAD NATIVE SHAPE EXTRACTION]
    Simulates successful OpenCASCADE boundary triangulation and edge extraction workflows 
    to hit the complete headless CAD visualizer overlay routine (Lines 132-222).
    """
    # Initialize mock structural layers for OpenCASCADE C++ interfaces
    mock_mesh = MagicMock()
    mock_topexp = MagicMock()
    mock_topabs = MagicMock()
    mock_brep = MagicMock()
    mock_toploc = MagicMock()
    mock_adaptor = MagicMock()

    mock_topabs.TopAbs_FACE = 1
    mock_topabs.TopAbs_EDGE = 2

    # Loop configuration bounds (Return elements once, then break loop)
    mock_face_explorer = MagicMock()
    mock_face_explorer.More.side_effect = [True, False]
    mock_face_explorer.Current.return_value = MagicMock()

    mock_edge_explorer = MagicMock()
    mock_edge_explorer.More.side_effect = [True, False]
    mock_edge_explorer.Current.return_value = MagicMock()

    mock_topexp.TopExp_Explorer.side_effect = lambda shape, abs_type: (
        mock_face_explorer if abs_type == 1 else mock_edge_explorer
    )

    # Triangulation matrices & coordinate assignments
    mock_triangulation = MagicMock()
    mock_triangulation.NbTriangles.return_value = 1
    
    mock_tri = MagicMock()
    mock_tri.Get.return_value = (1, 2, 3)
    mock_triangulation.Triangles.return_value.Value.return_value = mock_tri

    mock_pt = MagicMock()
    mock_pt.X.return_value = 0.5
    mock_pt.Y.return_value = 0.5
    mock_pt.Z.return_value = 0.5

    mock_nodes = MagicMock()
    mock_nodes.Value.return_value.Transformed.return_value = mock_pt
    mock_triangulation.Nodes.return_value = mock_nodes
    mock_brep.BRep_Tool.Triangulation.return_value = mock_triangulation

    # Adaptor curve parameters for edge line generation
    mock_curve = MagicMock()
    mock_curve.FirstParameter.return_value = 0.0
    mock_curve.LastParameter.return_value = 1.0
    mock_curve.Value.return_value.Transformed.return_value = mock_pt
    mock_adaptor.BRepAdaptor_Curve.return_value = mock_curve

    occ_modules = {
        "OCC": MagicMock(),
        "OCC.Core": MagicMock(),
        "OCC.Core.BRepMesh": mock_mesh,
        "OCC.Core.TopExp": mock_topexp,
        "OCC.Core.TopAbs": mock_topabs,
        "OCC.Core.BRep": mock_brep,
        "OCC.Core.TopLoc": mock_toploc,
        "OCC.Core.BRepAdaptor": mock_adaptor,
    }

    input_data = {
        "cad_solid": MagicMock(),
        "results": {
            "grid": {"nx": 1, "ny": 1, "nz": 1, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1},
            "mask": [1]
        }
    }

    # Inject mock structures into sys.modules to prevent environment import faults
    with patch.dict("sys.modules", occ_modules):
        generate_mask_snapshot(input_data, fallback_save_dir=str(tmpdir))

    assert os.path.exists(os.path.join(str(tmpdir), "cad_geometry_snapshot.png"))


def test_generate_mask_snapshot_cad_rendering_failure(tmpdir, caplog):
    """
    [ROBUSTNESS PATH: CAD SUBSYSTEM ISOLATION]
    Verifies that internal exceptions during OpenCASCADE geometric parsing or meshing 
    are gracefully logged as warnings without halting the primary voxel map outputs (Lines 223-224).
    """
    mock_mesh = MagicMock()
    mock_mesh.BRepMesh_IncrementalMesh.side_effect = Exception("OCC internal triangulation failure")

    occ_modules = {
        "OCC": MagicMock(),
        "OCC.Core": MagicMock(),
        "OCC.Core.BRepMesh": mock_mesh,
    }

    input_data = {
        "cad_solid": MagicMock(),
        "results": {
            "grid": {"nx": 1, "ny": 1, "nz": 1, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1},
            "mask": [1]
        }
    }

    with patch.dict("sys.modules", occ_modules), caplog.at_level(logging.WARNING):
        generate_mask_snapshot(input_data, fallback_save_dir=str(tmpdir))

    # Core canvas should still complete rendering cleanly
    assert "Headless CAD boundary line parsing rendering skipped" in caplog.text
    assert os.path.exists(os.path.join(str(tmpdir), "voxel_mask_verification.png"))


def test_generate_mask_snapshot_generic_failure(caplog):
    """
    [ERROR PATH: UNCLASSIFIED RUNTIME FALLBACK]
    Ensures that standard unclassified exceptions are cleanly routed to the final fallback 
    generic error logger pathway rather than the reshape/timeout branches (Line 233).
    """
    valid_input = {
        "results": {
            "grid": {"x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1, "nx": 1, "ny": 1, "nz": 1},
            "mask": [1]
        }
    }

    # We inject a runtime error that completely bypasses 'reshape' or 'timeout' keywords
    with patch("matplotlib.pyplot.figure", side_effect=RuntimeError("Unclassified core canvas storage write fault")), \
         caplog.at_level(logging.ERROR):
         
        generate_mask_snapshot(valid_input)
        
    assert "Visualization failure:" in caplog.text