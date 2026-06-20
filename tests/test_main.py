# tests/test_main.py
import pytest
import json
from unittest.mock import patch, mock_open
from jsonschema import ValidationError
from src.main import main
from tests.dummies.dummy_harness import dummy_in, get_mock_config

# --- STUB FOR SERIALIZATION ---
class SerializableStubContainer:
    """A data-only stub that mimics SovereignContainer to allow JSON serialization."""
    def __init__(self):
        self.step_file = "tests/data/sample_geometry.step"
        self.solver_version = "v1.0.0"
        self.tolerance = 1e-6
        self.max_element_size = 0.5
        self.min_element_size = 0.1
        self.bc_map = {}
        # Stub grid with primitive types
        self.grid = type('obj', (object,), {
            'x_min': 0.0, 'x_max': 1.0,
            'y_min': 0.0, 'y_max': 1.0,
            'z_min': 0.0, 'z_max': 1.0,
            'nx': 10, 'ny': 10, 'nz': 10
        })
        self.mask = [0, 1]
        self.boundary_conditions = []

# --- LITERATE TEST SUITE ---

def test_main_cli_argument_error():
    """[ERROR PATH: CLI ARGS] Verify system exits on bad args."""
    with patch("sys.argv", ["main.py", "only_one_arg"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1

def test_main_file_not_found():
    """[ERROR PATH: CONSTITUTIONAL VIOLATION] Verify crash if STEP file is missing."""
    mock_input_data = dummy_in()
    
    with patch("sys.argv", ["main.py", "in.json", "out.json"]), \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_input_data))), \
         patch("json.load", return_value=mock_input_data), \
         patch("src.main.validate_json"), \
         patch("os.path.exists", return_value=False):
        
        with pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):
            main()

def test_main_happy_path():
    """[SUCCESS PATH] Verify 100% coverage including validate_json execution."""
    input_data = dummy_in()
    config_data = get_mock_config()
    stub_container = SerializableStubContainer()

    # We patch validate (from jsonschema) instead of validate_json (from main)
    # to ensure the code inside validate_json executes.
    with patch("sys.argv", ["main.py", "in.json", "out.json"]), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[input_data, {}, config_data, {}]), \
         patch("jsonschema.validate"), \
         patch("os.path.exists", return_value=True), \
         patch("src.main.SovereignContainer", return_value=stub_container), \
         patch("src.main.Orchestrator") as mock_orch:
        
        main()
        
        mock_orch.return_value.run.assert_called_once()

def test_main_validation_failure():
    """[ERROR PATH: SCHEMA VIOLATION] Verify validation failure logic in validate_json."""
    mock_input_data = dummy_in()
    
    # We allow validate_json to run, but patch jsonschema.validate to raise the error.
    # This hits the try-except block in src.main.py lines 25-30.
    with patch("sys.argv", ["main.py", "in.json", "out.json"]), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[mock_input_data, {}]), \
         patch("jsonschema.validate", side_effect=ValidationError("Invalid Schema")), \
         patch("os.path.exists", return_value=True):
        
        with pytest.raises(ValidationError):
            main()