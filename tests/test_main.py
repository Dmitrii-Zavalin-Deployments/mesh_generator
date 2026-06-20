# tests/test_main.py
import pytest
import sys
import json
from unittest.mock import patch, mock_open, MagicMock
from jsonschema import ValidationError
from src.main import main

# --- LITERATE TEST SUITE ---

def test_main_cli_argument_error():
    """
    [ERROR PATH: CLI ARGS]
    Verify that the system exits with code 1 if incorrect arguments are provided.
    """
    with patch("sys.argv", ["main.py", "only_one_arg"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1

def test_main_file_not_found():
    """
    [ERROR PATH: CONSTITUTIONAL VIOLATION]
    Verify that the pipeline crashes (RuntimeError) if the STEP file 
    path defined in the input JSON does not exist.
    """
    # Mocking inputs
    mock_input_data = {"inputs": {"step_file": "non_existent.step"}}
    
    with patch("sys.argv", ["main.py", "in.json", "out.json"]), \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_input_data))), \
         patch("json.load", return_value=mock_input_data), \
         patch("src.main.validate_json"), \
         patch("os.path.exists", return_value=False):
        
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
            main()

def test_main_happy_path():
    """
    [SUCCESS PATH]
    Verify the full orchestration: Loading inputs, validation, 
    SovereignContainer initialization, Pipeline execution, and Serialization.
    """
    # 1. Setup Mocked Data
    input_data = {"inputs": {"step_file": "test.step"}}
    config_data = {
        "max_element_size": 1.0, "solver_version": "1.0",
        "tolerance": 1e-5, "min_element_size": 0.1, "boundary_map": {}
    }
    
    # 2. Setup Container Mock
    mock_container = MagicMock()
    mock_container.step_file = "test.step"
    mock_container.grid = MagicMock()
    mock_container.boundary_conditions = []

    # 3. Patching Execution
    # We patch open to return data for both input and config files
    with patch("sys.argv", ["main.py", "in.json", "out.json"]), \
         patch("builtins.open", mock_open()) as mocked_file, \
         patch("json.load", side_effect=[input_data, config_data]), \
         patch("src.main.validate_json"), \
         patch("os.path.exists", return_value=True), \
         patch("src.main.SovereignContainer", return_value=mock_container), \
         patch("src.main.Orchestrator") as mock_orch:
        
        # Run main
        main()
        
        # Verify Orchestrator was initialized and ran
        mock_orch.return_value.run.assert_called_once_with(mock_container)
        
        # Verify result serialization
        mocked_file().write.assert_called()

def test_main_validation_failure():
    """
    [ERROR PATH: SCHEMA VIOLATION]
    Verify that if the input JSON is invalid, validation failure propagates.
    """
    with patch("sys.argv", ["main.py", "in.json", "out.json"]), \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("json.load", return_value={}), \
         patch("src.main.validate_json", side_effect=ValidationError("Invalid")):
        
        with pytest.raises(ValidationError):
            main()