# tests/test_main.py
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from jsonschema import ValidationError

from src.main import main, validate_json


def test_validate_json_missing_schema(caplog):
    """Verifies that a missing schema file logs a warning and returns gracefully."""
    validate_json({"test": "data"}, "nonexistent_schema.json")
    assert "Schema file not found" in caplog.text


def test_validate_json_success_and_failure(tmp_path):
    """Verifies successful validation and ValidationError handling."""
    schema_file = tmp_path / "schema.json"
    schema_content = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"]
    }
    schema_file.write_text(json.dumps(schema_content))

    # Successful validation
    validate_json({"value": 42}, str(schema_file))

    # Failure validation
    with pytest.raises(ValidationError):
        validate_json({"value": "not-an-int"}, str(schema_file))


def test_main_step_file_not_found(tmp_path):
    """Verifies that main raises FileNotFoundError when the STEP file does not exist."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    test_args = [
        "src/main.py",
        "--input_output_folder", str(workspace),
        "--input_file_name", "missing.step",
        "--output_file_name", "output.json"
    ]
    
    with patch.object(sys, "argv", test_args), pytest.raises(FileNotFoundError, match="CONSTITUTION VIOLATION: STEP file not found"):
            main()


def test_main_config_file_not_found(tmp_path):
    """Verifies that main raises FileNotFoundError when config.json cannot be found."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    step_file = workspace / "test.step"
    step_file.write_text("DUMMY STEP CONTENT")
    
    test_args = [
        "src/main.py",
        "--input_output_folder", str(workspace),
        "--input_file_name", "test.step",
        "--output_file_name", "output.json"
    ]
    
    # Mock working directory search for config.json to fail
    with patch.object(sys, "argv", test_args), \
         patch("os.path.exists", side_effect=lambda p: False if "config" in str(p) else os.path.exists(p)), \
         pytest.raises(FileNotFoundError, match="CONSTITUTION VIOLATION: Configuration file not found"):
        main()

@patch("src.main.Orchestrator")
@patch("src.main.generate_mask_snapshot")
def class_test_main_success(mock_snapshot, mock_orchestrator_cls, tmp_path):
    """Tests the full successful execution path of main including gmsh operations and visualization fallbacks."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    step_file = workspace / "model.step"
    step_file.write_text("ISO-10303-21;")
    
    config_dir = workspace / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.json"
    config_data = {
        "max_element_size": 1.0,
        "min_element_size": 0.1,
        "tolerance": 1e-6
    }
    config_file.write_text(json.dumps(config_data))
    
    schema_dir = workspace / "schema"
    schema_dir.mkdir()
    (schema_dir / "mesh_generator_config_schema.json").write_text('{"type": "object"}')
    (schema_dir / "mesh_generator_output_schema.json").write_text('{"type": "object"}')

    # Mock gmsh module
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.side_effect = [False, True]  # First check False (initialize), cleanup check True
    
    mock_container_instance = MagicMock()
    mock_container_instance.step_file = str(step_file)
    mock_container_instance.tolerance = 1e-6
    mock_container_instance.max_element_size = 1.0
    mock_container_instance.min_element_size = 0.1
    mock_container_instance.grid = None
    mock_container_instance.mask = []

    test_args = [
        "src/main.py",
        "--input_output_folder", str(workspace),
        "--input_file_name", "model.step",
        "--output_file_name", "results/output.json"
    ]

    # Test visualization exception handling (RuntimeError, OSError, ValueError)
    mock_snapshot.side_effect = RuntimeError("Viz failed")

    with patch.object(sys, 'argv', test_args), \
         patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         patch("os.path.exists", side_effect=lambda p: bool("config.json" in str(p) or "schema" in str(p) or os.path.exists(p))), \
         patch("src.main.validate_json", return_value=None), \
         patch("src.main.SovereignContainer", return_value=mock_container_instance):
        
        main()
        
        # Verify orchestrator ran
        mock_orchestrator_cls.return_info.run.assert_called_once()
        mock_gmsh.initialize.assert_called_once()
        mock_gmsh.finalize.assert_called_once()


def test_main_absolute_paths_and_gmsh_already_initialized(tmp_path):
    """Tests execution using absolute input/output paths and when gmsh is already initialized."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    step_file = workspace / "abs_model.step"
    step_file.write_text("ISO-10303-21;")
    output_file = workspace / "abs_output.json"
    
    config_file = workspace / "config.json"
    config_data = {
        "max_element_size": 1.0,
        "min_element_size": 0.1,
        "tolerance": 1e-6
    }
    config_file.write_text(json.dumps(config_data))
    
    mock_gmsh = MagicMock()
    mock_gmsh.is_initialized.return_value = True  # Already initialized branch
    
    mock_container_instance = MagicMock()
    mock_container_instance.step_file = str(step_file)
    mock_container_instance.tolerance = 1e-6
    mock_container_instance.max_element_size = 1.0
    mock_container_instance.min_element_size = 0.1
    mock_container_instance.grid = MagicMock(
        x_min=0, x_max=1, y_min=0, y_max=1, z_min=0, z_max=1, nx=1, ny=1, nz=1
    )
    mock_container_instance.mask = [0]

    test_args = [
        "src/main.py",
        "--input_output_folder", str(workspace),
        "--input_file_name", str(step_file),
        "--output_file_name", str(output_file)
    ]

    with patch.object(sys, 'argv', test_args), \
         patch.dict("sys.modules", {"gmsh": mock_gmsh}), \
         patch("src.main.validate_json", return_value=None), \
         patch("src.main.Orchestrator"), \
         patch("src.main.generate_mask_snapshot") as mock_snap, \
         patch("os.path.exists", return_value=True):
        
        main()
        
        mock_gmsh.initialize.assert_not_called()
        mock_snap.assert_called_once()
        assert output_file.exists()
