# tests/state/test_sovereign_container_contracts.py

import pytest
from src.state.mesh_generator_state import SovereignContainer
from tests.dummies.dummy_harness import dummy_in, dummy_out, get_mock_config

@pytest.fixture
def valid_config():
    """Provides a structurally perfect config that satisfies the strict schema."""
    config = get_mock_config()
    # Patching the missing boundary_map required by the new strict schema
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
    return SovereignContainer(
        step_file=in_data["inputs"]["step_file"],
        max_element_size=valid_config["max_element_size"],
        solver_version=valid_config["solver_version"],
        tolerance=valid_config["tolerance"],
        min_element_size=valid_config["min_element_size"],
        boundary_map=valid_config["boundary_map"]
    )


def test_input_contract_validation(instantiated_container):
    """
    Test 1: Input Contract Validation
    Verifies the Sovereign Container contains all required fields from dummy_in 
    with exact type parity.
    """
    in_data = dummy_in()
    
    # 1. Verify existence of the attribute
    assert hasattr(instantiated_container, 'step_file'), "Contract Violation: 'step_file' missing from container."
    
    # 2. Verify exact type parity
    assert isinstance(instantiated_container.step_file, str), "Contract Violation: 'step_file' must be a string."
    
    # 3. Verify value mapping matches the dummy_in harness
    assert instantiated_container.step_file == in_data["inputs"]["step_file"], "Contract Violation: Input data mapping failed."


def test_config_contract_validation(instantiated_container, valid_config):
    """
    Test 2: Config Contract Validation
    Verifies the Sovereign Container satisfies the configuration requirements 
    (config.json) with no missing parameters.
    """
    # 1. Verify existence of all config attributes
    expected_attrs = ['solver_version', 'tolerance', 'max_element_size', 'min_element_size', 'bc_map']
    for attr in expected_attrs:
        assert hasattr(instantiated_container, attr), f"Contract Violation: '{attr}' missing from container."
        
    # 2. Verify strict type parity based on config schema
    assert isinstance(instantiated_container.solver_version, str), "Contract Violation: 'solver_version' must be a string."
    assert isinstance(instantiated_container.tolerance, float), "Contract Violation: 'tolerance' must be a float."
    assert isinstance(instantiated_container.max_element_size, float), "Contract Violation: 'max_element_size' must be a float."
    assert isinstance(instantiated_container.min_element_size, float), "Contract Violation: 'min_element_size' must be a float."
    assert isinstance(instantiated_container.bc_map, dict), "Contract Violation: 'bc_map' must be a dictionary."


def test_results_contract_validation(instantiated_container):
    """
    Test 3: Results Contract Validation
    Verifies the Sovereign Container exposes all required output fields 
    dictated by the dummy_out schema, ready to be populated.
    """
    dummy_out()["results"]
    
    # 1. Verify that the properties exist on the object to hold the result schema
    assert hasattr(instantiated_container, 'grid'), "Contract Violation: 'grid' property missing."
    assert hasattr(instantiated_container, 'mask'), "Contract Violation: 'mask' property missing."
    assert hasattr(instantiated_container, 'boundary_conditions'), "Contract Violation: 'boundary_conditions' property missing."
    
    # 2. Verify initialization state (must be None prior to pipeline execution)
    assert instantiated_container.grid is None, "Contract Violation: 'grid' must initialize as None."
    assert instantiated_container.mask is None, "Contract Violation: 'mask' must initialize as None."
    assert instantiated_container.boundary_conditions is None, "Contract Violation: 'boundary_conditions' must initialize as None."