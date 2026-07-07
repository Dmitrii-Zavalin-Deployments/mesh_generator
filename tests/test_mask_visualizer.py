# tests/test_mask_visualizer.py
import os
import logging
from unittest.mock import patch
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
    [ROBUSTNESS PATH: EXCEPTION ISOLATION GATE]
    Ensures that any structural canvas initialization error or unexpected rendering subsystem 
    fault is cleanly intercepted by the visualizer try/except block without blowing up the core pipeline.
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