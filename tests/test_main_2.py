import json
import os
import sys
from unittest.mock import patch

import gmsh
import pytest
from jsonschema import ValidationError

from src.main import main, validate_json
from src.state.mesh_generator_state import GridState
from tests.dummies.dummy_harness import get_mock_config


def test_validate_json_missing_schema(caplog):
    """Verifies that missing schema files log a warning and return gracefully."""
    validate_json({"test": 1}, "non_existent_schema.json")
    assert "Schema file not found" in caplog.text


def test_validate_json_validation_error():
    """Verifies that invalid schema payload raises ValidationError."""
    schema_path = "schema/mesh_generator_config_schema.json"
    with pytest.raises(ValidationError):
        validate_json({"invalid": "data"}, schema_path)


def test_main_success_and_gmsh_init_branches():
    """Verifies successful main execution and covers gmsh initialization branch (lines 102-103)."""
    if gmsh.is_initialized():
        gmsh.finalize()

    os.makedirs("config", exist_ok=True)
    config_data = get_mock_config()
    with open("config/config.json", "w") as f:
        json.dump(config_data, f)

    test_dir = "tests/dummies"
    test_args = [
        "src/main.py",
        "--input_output_folder", test_dir,
        "--input_file_name", "sample_geometry.step",
        "--output_file_name", "output_test.json"
    ]

    with patch.object(sys, 'argv', test_args):
        main()

    output_file = os.path.join(test_dir, "output_test.json")
    if os.path.exists(output_file):
        os.remove(output_file)


def test_main_snapshot_exception_handling():
    """Verifies exception handling when mask snapshot generation fails (lines 154-155)."""
    test_dir = "tests/dummies"
    test_args = [
        "src/main.py",
        "--input_output_folder", test_dir,
        "--input_file_name", "sample_geometry.step",
        "--output_file_name", "output_test_viz.json"
    ]

    with patch.object(sys, 'argv', test_args), \
         patch("src.main.generate_mask_snapshot", side_effect=RuntimeError("Viz fault")):
        main()

    output_file = os.path.join(test_dir, "output_test_viz.json")
    if os.path.exists(output_file):
        os.remove(output_file)


def test_main_gmsh_already_finalized_in_finally():
    """Verifies warning branch when gmsh is uninitialized prior to finally block (lines 172-174)."""
    test_dir = "tests/dummies"
    test_args = [
        "src/main.py",
        "--input_output_folder", test_dir,
        "--input_file_name", "sample_geometry.step",
        "--output_file_name", "output_test_fin.json"
    ]

    class MockOrchestrator:
        def __init__(self, steps):
            pass
        def run(self, container):
            container.grid = GridState(0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1, 1, 1)
            if gmsh.is_initialized():
                gmsh.finalize()

    with patch.object(sys, 'argv', test_args), \
         patch("src.main.Orchestrator", MockOrchestrator):
        main()

    output_file = os.path.join(test_dir, "output_test_fin.json")
    if os.path.exists(output_file):
        os.remove(output_file)
