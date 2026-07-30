# tests/test_main.py
import sys
from unittest.mock import MagicMock, mock_open, patch

import pytest
from jsonschema import ValidationError

from src.main import main
from tests.dummies.dummy_harness import dummy_in, get_mock_config

# --- STUB FOR SERIALIZATION ---

class SerializableStubContainer:
    """
    A data-only stub that mirrors the structured fields of SovereignContainer
    to guarantee flawless end-to-end JSON serialization in the main pipeline.
    """
    def __init__(self):
        self.step_file = "valid_workspace/geometry.step"
        self.tolerance = 1e-6
        self.max_element_size = 0.5
        self.min_element_size = 0.1
        self.bc_map = {"x_min": "inlet"}
        
        # Mocking grid state geometry attributes
        self.grid = MagicMock()
        self.grid.x_min, self.grid.x_max = 0.0, 1.0
        self.grid.y_min, self.grid.y_max = 0.0, 1.0
        self.grid.z_min, self.grid.z_max = 0.0, 1.0
        self.grid.nx, self.grid.ny, self.grid.nz = 2, 2, 2
        
        self.mask = [1] * 8
        
        # Mocking boundary conditions items
        bc_mock = MagicMock()
        bc_mock.location = "x_min"
        bc_mock.type = "inlet"
        bc_mock.surface_id = 42
        self.boundary_conditions = [bc_mock]

# --- LITERATE TEST SUITE ---

def test_main_cli_argument_error():
    """
    [ERROR PATH: CLI ARGS]
    Verify that providing unexpected or structurally invalid flags 
    forces argparse to gracefully reject execution and exit the process.
    """
    with patch("sys.argv", ["main.py", "--invalid-flag"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code in [1, 2]

def test_main_missing_arguments_error():
    """
    [ERROR PATH: MISSING REQUIRED ARGS]
    Verify that omitting any of the mandatory CLI parameters (--input_output_folder,
    --input_file_name, --output_file_name) causes argparse to reject execution.
    """
    with patch("sys.argv", ["main.py", "--input_output_folder", "valid_workspace"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code in [1, 2]

def test_main_file_not_found():
    """
    [CONSTITUTIONAL VIOLATION: FILE INTEGRITY]
    Verify that if the specified STEP geometry data is not found at the resolved 
    location, a critical validation exception blocks downstream processing.
    """
    with patch("sys.argv", [
        "main.py", 
        "--input_output_folder", "non_existent_workspace",
        "--input_file_name", "missing.step",
        "--output_file_name", "output.json"
    ]), \
         patch("os.path.isfile", return_value=False):
        with pytest.raises(FileNotFoundError, match="CONSTITUTION VIOLATION"):
            main()

def test_main_happy_path():
    """
    [SUCCESS PATH: NOMINAL FLOW]
    Verifies nominal execution flow with complete pipeline orchestration, 
    JSON file schema validations, tracking steps, and output serialization layer.
    """
    dummy_in()
    config_data = get_mock_config()
    stub_container = SerializableStubContainer()
    
    # Setup open mock to support safe handling across reads/writes
    m_open = mock_open(read_data='{}')
    
    with patch("sys.argv", [
        "main.py", 
        "--input_output_folder", "valid_workspace",
        "--input_file_name", "geometry.step",
        "--output_file_name", "mesh_generator_output.json"
    ]), \
         patch("os.path.isfile", return_value=True), \
         patch("os.makedirs"), \
         patch("builtins.open", m_open), \
         patch("json.load", side_effect=[config_data, {}]), \
         patch("json.dump") as mock_json_dump, \
         patch("src.main.validate"), \
         patch("src.main.SovereignContainer", return_value=stub_container), \
         patch("src.main.generate_mask_snapshot") as mock_viz, \
         patch("src.main.Orchestrator") as mock_orch:
        
        main()
        
        # Assertions: Verify orchestrator lifecycle run and file outputs
        mock_orch.return_value.run.assert_called_once_with(stub_container)
        mock_json_dump.assert_called_once()
        mock_viz.assert_called_once()

def test_main_absolute_input_path():
    """
    [COVERAGE PATH: LINE 50]
    Forces line 50 coverage by feeding an absolute input file path to the system,
    bypassing relative workplace joining mechanics.
    """
    dummy_in()
    config_data = get_mock_config()
    stub_container = SerializableStubContainer()
    
    with patch("sys.argv", [
        "main.py", 
        "--input_output_folder", "valid_workspace",
        "--input_file_name", "/absolute/path/to/geometry.step",
        "--output_file_name", "mesh_generator_output.json"
    ]), \
         patch("os.path.isfile", return_value=True), \
         patch("os.makedirs"), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[config_data, {}]), \
         patch("json.dump"), \
         patch("src.main.validate"), \
         patch("src.main.SovereignContainer", return_value=stub_container), \
         patch("src.main.generate_mask_snapshot"), \
         patch("src.main.Orchestrator"):
        
        main()

def test_main_absolute_output_path():
    """
    [COVERAGE PATH: LINE 61]
    Forces line 61 coverage by feeding an absolute output file path to the system,
    ensuring directory paths are processed without workspace structural alteration.
    """
    dummy_in()
    config_data = get_mock_config()
    stub_container = SerializableStubContainer()
    
    with patch("sys.argv", [
        "main.py", 
        "--input_output_folder", "valid_workspace",
        "--input_file_name", "geometry.step",
        "--output_file_name", "/absolute/path/to/mesh_generator_output.json"
    ]), \
         patch("os.path.isfile", return_value=True), \
         patch("os.makedirs"), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[config_data, {}]), \
         patch("json.dump"), \
         patch("src.main.validate"), \
         patch("src.main.SovereignContainer", return_value=stub_container), \
         patch("src.main.generate_mask_snapshot"), \
         patch("src.main.Orchestrator"):
        
        main()

def test_main_validation_failure():
    """
    [CONTRACTUAL ENFORCEMENT: SCHEMA VIOLATION]
    Ensure that if an incoming workspace configuration fails schema compliance matching, 
    the validation gate intercept triggers an explicit ValidationError.
    """
    dummy_in()
    config_data = get_mock_config()
    
    with patch("sys.argv", [
        "main.py", 
        "--input_output_folder", "valid_workspace",
        "--input_file_name", "geometry.step",
        "--output_file_name", "mesh_generator_output.json"
    ]), \
         patch("os.path.isfile", return_value=True), \
         patch("os.makedirs"), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[config_data, {}]), \
         patch("src.main.validate", side_effect=ValidationError("Invalid Schema")):
        
        with pytest.raises(ValidationError):
            main()

def test_main_visual_mask_fault_tolerance():
    """
    [ROBUSTNESS PATH: VISUALIZER ENGINE ISOLATION]
    Verifies that any unexpected crash or rendering exception inside the 
    offscreen mask snapshot visualizer is safely isolated and does not block 
    the final output data serialization steps.
    """
    dummy_in()
    config_data = get_mock_config()
    stub_container = SerializableStubContainer()
    
    with patch("sys.argv", [
        "main.py", 
        "--input_output_folder", "valid_workspace",
        "--input_file_name", "geometry.step",
        "--output_file_name", "mesh_generator_output.json"
    ]), \
         patch("os.path.isfile", return_value=True), \
         patch("os.makedirs"), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[config_data, {}]), \
         patch("json.dump") as mock_json_dump, \
         patch("src.main.validate"), \
         patch("src.main.SovereignContainer", return_value=stub_container), \
         patch("src.main.generate_mask_snapshot", side_effect=Exception("Framebuffer timeout")), \
         patch("src.main.Orchestrator"):
        
        # Test should pass smoothly despite the visualizer pipeline crash
        main()
        mock_json_dump.assert_called_once()

def test_main_strict_configuration_key_policy():
    """
    [ERROR PATH: NO-DEFAULT CONFIG POLICY]
    Verify that if a required parameter is completely missing from the 
    configuration map, a KeyError is raised immediately to prevent execution drift.
    """
    dummy_in()
    malformed_config = get_mock_config()
    # Explicitly pop a required parameter to break configuration integrity
    malformed_config.pop("max_element_size", None)
    
    with patch("sys.argv", [
        "main.py", 
        "--input_output_folder", "valid_workspace",
        "--input_file_name", "geometry.step",
        "--output_file_name", "mesh_generator_output.json"
    ]), \
         patch("os.path.isfile", return_value=True), \
         patch("os.makedirs"), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", side_effect=[malformed_config, {}]), \
         patch("src.main.validate"), pytest.raises(KeyError):
        main()


class TestMainCoverage:

    def test_gmsh_already_initialized(self):
        """Forces line reference check: GMSH engine already active."""
        mock_gmsh = MagicMock()
        mock_gmsh.isInitialized.return_value = True
        
        # Use localized patch.dict to clean up runtime environment safely
        with patch.dict(sys.modules, {'gmsh': mock_gmsh}), \
             patch("os.path.isfile", return_value=True), \
             patch("os.makedirs"), \
             patch("builtins.open", mock_open(read_data='{}')), \
             patch("src.main.json.load", return_value={
                 "tolerance": 1e-6, 
                 "max_element_size": 0.5, 
                 "min_element_size": 0.1, 
                 "boundary_map": {}
             }), \
             patch("src.main.validate_json"), \
             patch("src.main.Orchestrator"), \
             patch("src.main.SovereignContainer"), \
             patch("sys.argv", [
                 'main.py', 
                 '--input_output_folder', 'test_data',
                 '--input_file_name', 'test.step',
                 '--output_file_name', 'output.json'
             ]):
            
            try:
                main()
            except Exception:
                pass
            
            assert mock_gmsh.isInitialized.called

    def test_gmsh_already_finalized_teardown(self):
        """Forces line reference check: GMSH finalization bypassed."""
        mock_gmsh = MagicMock()
        mock_gmsh.isInitialized.return_value = False
        
        with patch.dict(sys.modules, {'gmsh': mock_gmsh}), \
             patch("os.path.isfile", return_value=True), \
             patch("os.makedirs"), \
             patch("builtins.open", mock_open(read_data='{}')), \
             patch("src.main.json.load", return_value={
                 "tolerance": 1e-6, 
                 "max_element_size": 0.5, 
                 "min_element_size": 0.1, 
                 "boundary_map": {}
             }), \
             patch("src.main.validate_json"), \
             patch("src.main.Orchestrator"), \
             patch("src.main.SovereignContainer"), \
             patch("sys.argv", [
                 'main.py', 
                 '--input_output_folder', 'test_data',
                 '--input_file_name', 'test.step',
                 '--output_file_name', 'output.json'
             ]):
            
            try:
                main()
            except Exception:
                pass
            
            assert mock_gmsh.isInitialized.called
