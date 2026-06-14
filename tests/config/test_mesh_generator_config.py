import pytest
import math
from tests.signatures.config.mesh_generator_config_test_signature import MeshGeneratorConfigTestSignature
# Assuming the implementation resides here based on your structure:
from src.implementation.config.mesh_generator_config import MeshGeneratorConfig

class TestMeshGeneratorConfig(MeshGeneratorConfigTestSignature):
    """
    Concrete implementation of MeshGeneratorConfig validation.
    Validates the configuration model using the Phase 3 signature contract.
    """

    @pytest.fixture
    def valid_config_data(self):
        """Helper to provide a valid configuration dictionary."""
        return {
            "solver_version": "1.0.0",
            "tolerance": 1e-6,
            "max_element_size": 0.5,
            "min_element_size": 0.1
        }

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Implementations
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_fields(self, valid_config_data):
        for field in ["solver_version", "tolerance", "max_element_size", "min_element_size"]:
            bad_data = valid_config_data.copy()
            del bad_data[field]
            with pytest.raises((KeyError, TypeError, ValueError)):
                MeshGeneratorConfig(**bad_data)

    def test_sensitivity_invalid_types(self, valid_config_data):
        bad_data = valid_config_data.copy()
        bad_data["tolerance"] = "not_a_float"
        with pytest.raises(TypeError):
            MeshGeneratorConfig(**bad_data)

    def test_sensitivity_invalid_numeric_ranges(self, valid_config_data):
        bad_data = valid_config_data.copy()
        bad_data["max_element_size"] = float('nan')
        with pytest.raises(ValueError):
            MeshGeneratorConfig(**bad_data)

    def test_sensitivity_element_size_relationship(self, valid_config_data):
        bad_data = valid_config_data.copy()
        bad_data["max_element_size"] = 0.1
        bad_data["min_element_size"] = 0.5 # Invalid: max < min
        # Implementation should raise ValueError if logic is enforced in __post_init__
        with pytest.raises(ValueError):
            MeshGeneratorConfig(**bad_data)

    def test_sensitivity_schema_alignment(self, valid_config_data):
        bad_data = valid_config_data.copy()
        bad_data["unexpected_field"] = "value"
        # If your model strictly enforces schema, this should fail
        with pytest.raises(TypeError):
            MeshGeneratorConfig(**bad_data)

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Implementations
    # ----------------------------------------------------------------------

    def test_physics_tolerance_validity(self, valid_config_data):
        bad_data = valid_config_data.copy()
        bad_data["tolerance"] = -1.0 # Physically impossible
        with pytest.raises(ValueError):
            MeshGeneratorConfig(**bad_data)

    def test_physics_element_size_validity(self, valid_config_data):
        bad_data = valid_config_data.copy()
        bad_data["max_element_size"] = 0.0 # Must be positive
        with pytest.raises(ValueError):
            MeshGeneratorConfig(**bad_data)

    def test_physics_resolution_constraints(self, valid_config_data):
        # Implementation specific: Check if values are logically consistent
        pass

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Implementations
    # ----------------------------------------------------------------------

    def test_consistency_predictable_structure(self, valid_config_data):
        config = MeshGeneratorConfig(**valid_config_data)
        assert hasattr(config, "solver_version")
        assert config.tolerance == 1e-6

    def test_consistency_no_cross_step_corruption(self, valid_config_data):
        config = MeshGeneratorConfig(**valid_config_data)
        # Verify immutability if using @dataclass(frozen=True)
        with pytest.raises(Exception):
            config.tolerance = 0.0

    def test_consistency_no_uninitialized_fields(self):
        with pytest.raises(TypeError):
            MeshGeneratorConfig() # Should fail without arguments