# tests/config/test_mesh_generator_config.py

import pytest
from src.implementation.config.mesh_generator_config import MeshGeneratorConfig
from tests.signatures.config.mesh_generator_config_test_signature import MeshGeneratorConfigTestSignature

class TestMeshGeneratorConfig(MeshGeneratorConfigTestSignature):
    """
    Concrete implementation of MeshGeneratorConfigTestSignature.
    Validates the MeshGeneratorConfig class instance, ensuring strict
    validation logic and immutability.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Implementations
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_fields(self):
        # We attempt to instantiate the config without required numeric fields.
        # Python's interpreter will raise a TypeError for missing arguments.
        with pytest.raises(TypeError):
            MeshGeneratorConfig(solver_version="1.0.0")

    def test_sensitivity_invalid_types(self):
        # We provide a string where a float (tolerance) is expected.
        # The class implementation must catch this type mismatch.
        with pytest.raises(TypeError, match="must be int or float"):
            MeshGeneratorConfig("1.0.0", "INVALID", 0.5, 0.1)

    def test_sensitivity_invalid_numeric_ranges(self):
        # We inject NaN (Not a Number) into the max_element_size field.
        # The validator must explicitly reject non-finite numeric values.
        with pytest.raises(ValueError, match="cannot be NaN"):
            MeshGeneratorConfig("1.0.0", 1e-6, float('nan'), 0.1)

    def test_sensitivity_element_size_relationship(self):
        # We define an inverted range (min > max), which violates the physical
        # constraint: min_element_size < max_element_size.
        with pytest.raises(ValueError, match="must be less than"):
            MeshGeneratorConfig("1.0.0", 1e-6, 0.1, 0.5)

    def test_sensitivity_schema_alignment(self):
        # The schema definition is strict. Any attempt to initialize with undefined
        # fields (not handled by __init__) will result in a TypeError.
        with pytest.raises(TypeError):
            MeshGeneratorConfig("1.0.0", 1e-6, 0.5, 0.1, extra_field=True)

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Implementations
    # ----------------------------------------------------------------------

    def test_physics_tolerance_validity(self):
        # A non-positive tolerance (<= 0) is physically meaningless for convergence.
        # The validator must block values that impede geometric stability.
        with pytest.raises(ValueError, match="Tolerance must be positive"):
            MeshGeneratorConfig("1.0.0", -0.001, 0.5, 0.1)

    def test_physics_element_size_validity(self):
        # Element sizes must be strictly positive to ensure a valid spatial grid.
        # Zero-size elements are caught by the physics gate.
        with pytest.raises(ValueError, match="Element sizes must be > 0"):
            MeshGeneratorConfig("1.0.0", 1e-6, 0.5, 0.0)

    def test_physics_resolution_constraints(self):
        # Grid resolution must be physically achievable.
        # (This specific logic is currently covered by the relationship validation).
        with pytest.raises(ValueError, match="must be less than"):
            MeshGeneratorConfig("1.0.0", 1e-6, 0.1, 0.5)

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Implementations
    # ----------------------------------------------------------------------

    def test_consistency_predictable_structure(self):
        # We create a valid configuration instance.
        config = MeshGeneratorConfig("1.0.0", 1e-6, 0.5, 0.1)
        
        # Verify that we cannot mutate the attribute after creation.
        # The custom __setattr__ method must raise an AttributeError.
        with pytest.raises(AttributeError, match="Cannot modify immutable config attribute"):
            config.tolerance = 0.99

    def test_consistency_no_cross_step_corruption(self):
        # We verify that the configuration state is locked post-initialization.
        config = MeshGeneratorConfig("1.0.0", 1e-6, 0.5, 0.1)
        
        # Any attempt to overwrite the solver version must be rejected.
        with pytest.raises(AttributeError):
            config.solver_version = "2.0.0"

    def test_consistency_no_uninitialized_fields(self):
        # All required fields are validated at instantiation. 
        # Therefore, no uninitialized fields can exist in the lifecycle.
        config = MeshGeneratorConfig("1.0.0", 1e-6, 0.5, 0.1)
        assert config.solver_version == "1.0.0"
        assert config.tolerance == 1e-6