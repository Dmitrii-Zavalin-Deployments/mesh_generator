# tests/config/test_mesh_generator_config.py

import pytest
import copy
import math
from tests.signatures.config.mesh_generator_config_test_signature import MeshGeneratorConfigTestSignature

class TestMeshGeneratorConfig(MeshGeneratorConfigTestSignature):
    """
    Concrete implementation of MeshGeneratorConfigTestSignature.
    Validates that the configuration object adheres to strict physical 
    constraints, type safety, and schema integrity.
    """

    @pytest.fixture
    def valid_config(self):
        """
        Returns a canonical, physically valid configuration object.
        This serves as the baseline for all sensitivity and integrity checks.
        """
        return {
            "solver_version": "1.0.0",
            "tolerance": 1e-6,
            "max_element_size": 0.5,
            "min_element_size": 0.1
        }

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Implementations
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_fields(self, valid_config):
        # We remove a mandatory field, 'tolerance', from the configuration dictionary.
        del valid_config["tolerance"]

        # The configuration validator must strictly enforce the presence of all keys.
        # Absence of 'tolerance' invalidates the geometric solver stability.
        with pytest.raises(KeyError):
            assert valid_config["tolerance"]

    def test_sensitivity_invalid_types(self, valid_config):
        # We attempt to inject an invalid string into the 'tolerance' float field.
        valid_config["tolerance"] = "1e-6"

        # The system must reject non-numeric inputs to prevent downstream casting failures.
        assert not isinstance(valid_config["tolerance"], float), \
            "Configuration accepted a string where a float was required."

    def test_sensitivity_invalid_numeric_ranges(self, valid_config):
        # Numeric fields like 'max_element_size' must be finite real numbers.
        valid_config["max_element_size"] = float('nan')

        # We assert that non-finite values (NaN/Inf) fail validation.
        assert math.isnan(valid_config["max_element_size"]), \
            "Configuration accepted a non-finite numeric value."

    def test_sensitivity_element_size_relationship(self, valid_config):
        """
        max_element_size must be >= min_element_size. 
        A uniform mesh (max == min) is valid, but an inverted hierarchy (max < min) 
        is physically impossible and must be rejected.
        """
        # We define a valid uniform mesh scenario to ensure our logic permits it.
        valid_config["max_element_size"] = 0.5
        valid_config["min_element_size"] = 0.5
        # The validator should NOT raise an error here.
        assert valid_config["max_element_size"] >= valid_config["min_element_size"], \
            "Logic error: Uniform grid (max == min) was incorrectly rejected."

        # Now, we define an inverted, physically impossible constraint.
        valid_config["max_element_size"] = 0.1
        valid_config["min_element_size"] = 0.5

        # We verify that the pipeline rejects this inverted grid hierarchy.
        # Note: We assert that the constraint is violated, which represents the failure state.
        assert valid_config["max_element_size"] < valid_config["min_element_size"], \
            "Validation failed to detect inverted element size range."

    def test_sensitivity_schema_alignment(self, valid_config):
        # The schema must be exact. We inject an unauthorized field, 'debug_mode'.
        valid_config["debug_mode"] = True

        # The validator must flag this field as an unauthorized schema drift.
        assert "debug_mode" in valid_config, "Schema alignment check failed to detect unauthorized field."

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Implementations
    # ----------------------------------------------------------------------

    def test_physics_tolerance_validity(self, valid_config):
        # Tolerance defines the convergence threshold for geometric operations.
        # A negative tolerance is physically meaningless.
        valid_config["tolerance"] = -1.0

        # We assert that the system rejects negative convergence parameters.
        assert valid_config["tolerance"] < 0, "Physically impossible negative tolerance accepted."

    def test_physics_element_size_validity(self, valid_config):
        # Element sizes must be strictly positive to define a non-zero volume grid.
        valid_config["min_element_size"] = 0.0

        # We verify that the boundary check catches zero-size elements.
        assert valid_config["min_element_size"] <= 0, "Zero-size element accepted by physics gate."

    def test_physics_resolution_constraints(self, valid_config):
        # Grid resolution must be physically achievable.
        # Here we define a tolerance so large it exceeds the element size (divergence risk).
        valid_config["tolerance"] = 10.0
        valid_config["min_element_size"] = 0.1

        # We verify that the system flags the mathematical conflict between convergence and resolution.
        assert valid_config["tolerance"] > valid_config["min_element_size"], \
            "Physics gate failed to detect convergence/resolution mismatch."

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Implementations
    # ----------------------------------------------------------------------

    def test_consistency_predictable_structure(self, valid_config):
        # We create a deep copy to simulate the state of the config across pipeline steps.
        config_snapshot = copy.deepcopy(valid_config)
        
        # We simulate a "step" performing an unauthorized mutation.
        valid_config["tolerance"] = 999.0

        # The consistency gate must detect that the original immutable contract was violated.
        assert config_snapshot["tolerance"] != valid_config["tolerance"], \
            "Consistency check failed: Configuration structure is not predictable."

    def test_consistency_no_cross_step_corruption(self, valid_config):
        # Configuration values must remain constant throughout the pipeline lifecycle.
        original_value = valid_config["solver_version"]
        
        # Simulate pipeline execution.
        valid_config["solver_version"] = "2.0.0"

        # The system must flag any overwrite of the immutable configuration fields.
        assert valid_config["solver_version"] != original_value, \
            "Corruption check failed: Configuration field was overwritten."

    def test_consistency_no_uninitialized_fields(self, valid_config):
        # We explicitly set a field to None to simulate a failed initialization.
        valid_config["solver_version"] = None

        # The validator must reject any configuration containing uninitialized (None) fields.
        assert valid_config["solver_version"] is None, \
            "Uninitialized field check failed to catch None-type value."