# tests/state/test_sovereign_container_contracts.py

import pytest

from src.state.mesh_generator_state import SovereignContainer
from tests.dummies.dummy_harness import dummy_in, get_mock_config

# -------------------------------------------------------------------------
# SETUP: Infrastructure for Structural Verification
# -------------------------------------------------------------------------

@pytest.fixture
def valid_config():
    """Provides a structurally perfect config that satisfies the strict schema."""
    config = get_mock_config()
    
    # The configuration requires a boundary_map to define spatial constraints.
    # We explicitly patch this to satisfy the strict schema requirements.
    config["boundary_map"] = {
        "x_min": "inflow", "x_max": "outflow",
        "y_min": "no-slip", "y_max": "no-slip",
        "z_min": "no-slip", "z_max": "no-slip",
        "wall": "no-slip"
    }
    return config

@pytest.fixture
def instantiated_container(valid_config):
    """Provides a cleanly initialized container for structural probing."""
    in_data = dummy_in()
    
    # We instantiate the SovereignContainer. This represents the 'Physical State'
    # of the system before any computation occurs.
    return SovereignContainer(
        step_file=in_data["inputs"]["step_file"],
        max_element_size=valid_config["max_element_size"],
        solver_version=valid_config["solver_version"],
        tolerance=valid_config["tolerance"],
        min_element_size=valid_config["min_element_size"],
        boundary_map=valid_config["boundary_map"],
        use_gmsh=True
    )

# -------------------------------------------------------------------------
# CONTRACT TESTS: The Literate Narrative
# -------------------------------------------------------------------------

def test_input_contract_validation(instantiated_container):
    """
    Narrative: We must verify that the input 'step_file' contract is honored.
    The container must hold the file reference exactly as defined in the input harness.
    """
    in_data = dummy_in()
    
    # 1. Verification of the attribute: 'step_file'
    # The SovereignContainer must provide an entry point for the STEP geometry.
    assert hasattr(instantiated_container, 'step_file'), "Contract Violation: 'step_file' missing from container."
    
    # 2. Type parity verification:
    # We define the type expectation as a standard string.
    assert isinstance(instantiated_container.step_file, str), "Contract Violation: 'step_file' must be a string."
    
    # 3. Value parity:
    # We assert that the container data equals the input harness data.
    #    (container.step_file) == (harness.step_file)
    assert instantiated_container.step_file == in_data["inputs"]["step_file"], "Contract Violation: Input data mapping failed."


def test_config_contract_validation(instantiated_container, valid_config):
    """
    Narrative: We verify the configuration contract.
    The container acts as the single source of truth for simulation parameters.
    """
    # We list the mandatory configuration attributes:
    #    solver_version, tolerance, max_element_size, min_element_size, bc_map
    expected_attrs = ['solver_version', 'tolerance', 'max_element_size', 'min_element_size', 'bc_map']
    
    # Each attribute must exist and conform to its schema-defined type.
    for attr in expected_attrs:
        # Check for existence
        assert hasattr(instantiated_container, attr), f"Contract Violation: '{attr}' missing from container."
        
    # We validate the type definitions for the simulation physics:
    #    Solver Version (str), Tolerance (float), Max Size (float), Min Size (float), BC Map (dict)
    assert isinstance(instantiated_container.solver_version, str), "Contract Violation: 'solver_version' must be a string."
    assert isinstance(instantiated_container.tolerance, float), "Contract Violation: 'tolerance' must be a float."
    assert isinstance(instantiated_container.max_element_size, float), "Contract Violation: 'max_element_size' must be a float."
    assert isinstance(instantiated_container.min_element_size, float), "Contract Violation: 'min_element_size' must be a float."
    assert isinstance(instantiated_container.bc_map, dict), "Contract Violation: 'bc_map' must be a dictionary."


def test_results_contract_validation(instantiated_container):
    """
    Narrative: We verify the results contract.
    Before execution, the container must reserve space for the outputs (grid, mask, BCs).
    """
    # The result schema dictates three placeholders:
    #      Grid (Structural Mesh), Mask (Fluid/Solid mapping), Boundary Conditions
    
    # 1. Existence Check:
    # The attributes must be defined to hold the future computation.
    assert hasattr(instantiated_container, 'grid'), "Contract Violation: 'grid' property missing."
    assert hasattr(instantiated_container, 'mask'), "Contract Violation: 'mask' property missing."
    assert hasattr(instantiated_container, 'boundary_conditions'), "Contract Violation: 'boundary_conditions' property missing."
    
    # 2. State Check:
    # A fresh container must initialize these values to None to prevent 'dirty' data.
    #      State = None (Empty/Initialized)
    assert instantiated_container.grid is None, "Contract Violation: 'grid' must initialize as None."
    assert instantiated_container.mask is None, "Contract Violation: 'mask' must initialize as None."
    assert instantiated_container.boundary_conditions is None, "Contract Violation: 'boundary_conditions' must initialize as None."