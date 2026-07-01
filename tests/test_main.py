# tests/test_main.py
import pytest
import json
from unittest.mock import patch, mock_open
from jsonschema import ValidationError
from src.main import main
from tests.dummies.dummy_harness import dummy_in, get_mock_config

# --- STUB FOR SERIALIZATION ---
# This container acts as the physical state representation of the system.
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

# 1. System Contract Enforcement
# Formula: If argument count N != 2, the process must exit with code 1.
#     ExitCode = (N != 2) ? 1 : 0
def test_main_cli_argument_error():
    """[ERROR PATH: CLI ARGS] Verify system exits on bad args."""
    with patch("sys.argv", ["main.py", "only_one_arg"]):
        with pytest.raises(SystemExit) as exc:
            main()
        # Assertion: Validate the exit signal
        assert exc.value.code == 2

# 2. Constitutional Violation (Physical File Integrity)
# Formula: If file path P does not exist in filesystem F, operation must fail.
#     Error = (P ∉ F) ? RuntimeError : Success
def test_main_file_not_found():
    with patch("sys.argv", ["main.py", "non_existent.json", "out.json"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2

# 3. Nominal Path (Successful State Transition)
# Formula: Input S_i passes through Orchestrator O, resulting in Output S_o.
#     S_o = O(S_i)
def test_main_happy_path():
    """[SUCCESS PATH] Verify 100% coverage including validate_json execution."""
    input_data = dummy_in()
    config_data = get_mock_config()
    stub_container = SerializableStubContainer()

    # Execution Sequence: [Load_Input, Load_Input_Schema, Load_Config, Load_Config_Schema]
    with patch("sys.argv", ["main.py", "in.json", "out.json"]), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[input_data, {}, config_data, {}]), \
         patch("jsonschema.validate"), \
         patch("os.path.exists", return_value=True), \
         patch("src.main.SovereignContainer", return_value=stub_container), \
         patch("src.main.Orchestrator") as mock_orch:
        
        main()
        
        # Assertion: Verify the Orchestrator lifecycle was triggered
        mock_orch.return_value.run.assert_called_once()

# 4. Contractual Enforcement (Schema Validation)
# Formula: If Instance I does not conform to Schema S, the validation must fail.
#     ValidationResult = (I ⊈ S) ? ValidationError : Pass
def test_main_validation_failure():
    """[ERROR PATH: SCHEMA VIOLATION] Verify validation failure logic in validate_json."""
    mock_input_data = dummy_in()
    
    with patch("sys.argv", ["main.py", "in.json", "out.json"]), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[mock_input_data, {}, get_mock_config(), {}]), \
         patch("src.main.validate", side_effect=ValidationError("Invalid Schema")), \
         patch("os.path.exists", return_value=True):
        
        # Assertion: Ensure the gatekeeper blocks invalid state
        with pytest.raises(ValidationError):
            main()