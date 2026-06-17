# tests/state/test_boundary_condition.py

import pytest
from src.implementation.state.boundary_condition import BoundaryCondition
from tests.dummies.mesh_generator_state_dummy import MeshGeneratorStateDummy
from tests.signatures.state.boundary_condition_test_signature import BoundaryConditionTestSignature

class TestBoundaryCondition(BoundaryConditionTestSignature):
    """
    Concrete implementation of BoundaryConditionTestSignature.
    Validates boundary condition logic against physical grid constraints,
    type requirements, and pipeline consistency gates.
    """

    @pytest.fixture
    def dummy_state(self):
        """Provides a valid baseline state to validate physical consistency."""
        return MeshGeneratorStateDummy()

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Implementations
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_fields(self):
        # We attempt to instantiate a boundary condition without providing the 
        # required 'type' field.
        # The validator must raise a ValueError if mandatory attributes are missing.
        with pytest.raises(ValueError, match="type is required"):
            BoundaryCondition(location="x_min", values={"u": 0.0})

    def test_sensitivity_invalid_location_enum(self):
        # We attempt to define a boundary condition at an undefined location.
        # Boundary locations must strictly adhere to the allowed set (x_min, wall, etc).
        invalid_location = "deep_space"
        with pytest.raises(ValueError, match="Invalid location"):
            BoundaryCondition(location=invalid_location, type="no-slip", values={})

    def test_sensitivity_invalid_type_enum(self):
        # We attempt to use an unsupported boundary type.
        # The system must reject non-standard physics models.
        with pytest.raises(ValueError, match="Invalid type"):
            BoundaryCondition(location="x_min", type="super-slip", values={})

    def test_sensitivity_invalid_values_structure(self):
        # We provide a non-dictionary object for 'values'.
        # The configuration must enforce the BoundaryConditionValuesInterface structure.
        with pytest.raises(TypeError, match="values must be a dictionary"):
            BoundaryCondition(location="x_min", type="inflow", values=[0.0, 1.0])

    def test_sensitivity_schema_alignment(self):
        # We inject an extra, undocumented field into the BC definition.
        # The schema enforcement layer must reject structural drift.
        with pytest.raises(AttributeError):
            BoundaryCondition(location="x_min", type="inflow", values={}, debug_mode=True)

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Implementations
    # ----------------------------------------------------------------------

    def test_physics_location_consistency(self, dummy_state):
        # The location must exist within the grid extents defined by S2–S7.
        # Here we test a standard 'x_min' location against the dummy state.
        bc = BoundaryCondition(location="x_min", type="no-slip", values={})
        
        # Verify the location is a recognized boundary face.
        assert bc.location in ["x_min", "x_max", "y_min", "y_max", "z_min", "z_max", "wall"]

    def test_physics_type_consistency(self):
        # Inflow conditions are only physically valid on domain faces, not 'wall' boundaries.
        # We assert that the logic correctly flags a mismatch between geometry and flow type.
        with pytest.raises(ValueError, match="inflow invalid on wall"):
            BoundaryCondition(location="wall", type="inflow", values={"u": 1.0})

    def test_physics_values_numeric(self):
        # Boundary values must be numeric to be processed by the linear solver.
        # We test that string inputs are rejected.
        with pytest.raises(TypeError, match="values must be numeric"):
            BoundaryCondition(location="x_min", type="inflow", values={"u": "fast"})

    def test_physics_values_required_for_type(self):
        # An 'inflow' type requires specific velocity components (u, v, w).
        # We simulate a missing velocity requirement.
        with pytest.raises(ValueError, match="inflow requires velocity"):
            BoundaryCondition(location="x_min", type="inflow", values={"p": 101325})

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Implementations
    # ----------------------------------------------------------------------

    def test_consistency_predictable_structure(self):
        # Create a valid BC object.
        bc = BoundaryCondition(location="x_min", type="no-slip", values={})
        
        # We simulate a step trying to mutate the immutable boundary object.
        # The consistency gate must prevent runtime structural drift.
        with pytest.raises(AttributeError):
            bc.location = "x_max"

    def test_consistency_no_cross_step_corruption(self):
        # Ensure that unrelated steps cannot overwrite boundary values.
        bc = BoundaryCondition(location="x_min", type="no-slip", values={})
        original_type = bc.type
        
        # Any attempt to overwrite must be rejected by the implementation.
        with pytest.raises(AttributeError):
            bc.type = "outflow"
        assert bc.type == original_type

    def test_consistency_no_uninitialized_fields(self):
        # A fully initialized BC object must not have 'None' fields.
        bc = BoundaryCondition(location="x_min", type="no-slip", values={})
        assert bc.location is not None
        assert bc.type is not None
        assert bc.values is not None

    def test_consistency_pipeline_progression(self):
        # Pipeline progression requires that boundary condition values are only 
        # populated after the location and type have been locked.
        # We verify that a BC object cannot exist in a "partially computed" state.
        with pytest.raises(ValueError, match="incomplete state"):
             # Logic simulating incomplete initialization
             BoundaryCondition(location="x_min", type=None, values={})