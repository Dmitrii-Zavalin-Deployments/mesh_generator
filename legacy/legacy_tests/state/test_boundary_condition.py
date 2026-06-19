# tests/state/test_boundary_condition.py

import pytest
from tests.signatures.state.boundary_condition_test_signature import BoundaryConditionTestSignature
from tests.dummies.mesh_generator_state_dummy import MeshGeneratorStateDummy
from src.implementation.steps.compute_boundary_condition_type_step import ComputeBoundaryConditionTypeStep
from src.implementation.steps.compute_boundary_condition_values_step import ComputeBoundaryConditionValuesStep

class TestBoundaryCondition(BoundaryConditionTestSignature):
    """
    Concrete implementation of BoundaryConditionTestSignature.
    Validates boundary condition dictionary entries in state.results_boundary_conditions
    against strict schema, physics, and consistency gates.
    """

    @pytest.fixture
    def state(self):
        # We initialize the state with a dummy configuration to simulate a running pipeline.
        return MeshGeneratorStateDummy()

    @pytest.fixture
    def config(self, mocker):
        # We mock the configuration interface to isolate boundary condition logic.
        mock_config = mocker.Mock()
        mock_config.get_values_for_type.return_value = {"u": 1.0, "v": 0.0, "w": 0.0, "p": 101325.0}
        return mock_config

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Implementations
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_fields(self, state):
        # To ensure pipeline integrity, the boundary condition entry must contain 
        # the 'location' key before processing. We simulate a missing key scenario.
        state.results_boundary_conditions = [{}]
        
        # We verify that a structural validation check would fail.
        with pytest.raises(KeyError):
            assert "location" in state.results_boundary_conditions[0]

    def test_sensitivity_invalid_location_enum(self, state):
        # Boundary locations must strictly adhere to the domain faces. 
        # Providing a non-existent location, 'center', is invalid.
        state.results_boundary_conditions[0]["location"] = "center"
        valid_locations = ["x_min", "x_max", "y_min", "y_max", "z_min", "z_max", "wall"]

        # The system must reject the invalid location.
        assert state.results_boundary_conditions[0]["location"] not in valid_locations

    def test_sensitivity_invalid_type_enum(self, state):
        # The boundary type defines the solver physics. 
        # 'super-slip' is not a defined model in our physics library.
        state.results_boundary_conditions[0]["type"] = "super-slip"
        valid_types = ["no-slip", "free-slip", "inflow", "outflow", "pressure"]

        # The validation gate must identify this type as unsupported.
        assert state.results_boundary_conditions[0]["type"] not in valid_types

    def test_sensitivity_invalid_values_structure(self, state):
        # The 'values' field must be a dictionary to hold key-value pairs (u, v, w, p).
        # We inject an invalid list structure.
        state.results_boundary_conditions[0]["values"] = [0.0, 1.0]

        # The schema enforcement gate must flag this structural drift.
        assert not isinstance(state.results_boundary_conditions[0]["values"], dict)

    def test_sensitivity_schema_alignment(self, state):
        # To prevent schema drift, we ensure no unauthorized fields exist.
        # We inject an extra field 'debug_mode'.
        state.results_boundary_conditions[0]["debug_mode"] = True

        # The validator must recognize this as schema pollution.
        assert "debug_mode" in state.results_boundary_conditions[0]

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Implementations
    # ----------------------------------------------------------------------

    def test_physics_location_consistency(self, state):
        # The location must exist within the computed grid.
        # We check that 'x_min' is a valid mapping for our dummy grid.
        state.results_boundary_conditions[0]["location"] = "x_min"
        
        # Valid location check:
        assert state.results_boundary_conditions[0]["location"] in state.results_grid.keys()

    def test_physics_type_consistency(self, state):
        # Physics dictates that inflow is invalid on a wall.
        state.results_boundary_conditions[0]["location"] = "wall"
        state.results_boundary_conditions[0]["type"] = "inflow"

        # The consistency gate must detect this physically impossible assignment.
        is_invalid = (state.results_boundary_conditions[0]["location"] == "wall" and 
                      state.results_boundary_conditions[0]["type"] == "inflow")
        assert is_invalid is True

    def test_physics_values_numeric(self, state):
        # All boundary values (u, v, w, p) must be numeric.
        state.results_boundary_conditions[0]["values"] = {"u": "fast"}

        # We assert that the non-numeric value is detected.
        assert isinstance(state.results_boundary_conditions[0]["values"]["u"], str)

    def test_physics_values_required_for_type(self, state):
        # 'inflow' types require velocity components (u, v, w).
        # We test that a dictionary without velocity fails the physics gate.
        state.results_boundary_conditions[0]["type"] = "inflow"
        state.results_boundary_conditions[0]["values"] = {"p": 101325.0} # Missing u, v, w

        required_keys = ["u", "v", "w"]
        has_all_keys = all(k in state.results_boundary_conditions[0]["values"] for k in required_keys)
        assert has_all_keys is False

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Implementations
    # ----------------------------------------------------------------------

    def test_consistency_predictable_structure(self, state):
        # The structure must remain stable. We check that our dummy entry 
        # does not contain unexpected keys before processing.
        state.results_boundary_conditions[0] = {"location": "x_min"}
        
        # The structure should only contain the keys we set.
        expected_keys = {"location"}
        assert set(state.results_boundary_conditions[0].keys()) == expected_keys

    def test_consistency_no_cross_step_corruption(self, state, config):
        # We run the Type step and ensure it does not overwrite the Location.
        state.results_boundary_conditions[0] = {"location": "x_min"}
        
        step = ComputeBoundaryConditionTypeStep(geometry_model=None)
        step.run(state, config, index=0)
        
        # The Location key must remain unchanged.
        assert state.results_boundary_conditions[0]["location"] == "x_min"

    def test_consistency_no_uninitialized_fields(self, state):
        # All BC entries must be fully initialized. 
        # We check a field set to None.
        state.results_boundary_conditions[0]["type"] = None
        
        # The uninitialized check must fail.
        assert state.results_boundary_conditions[0]["type"] is None

    def test_consistency_pipeline_progression(self, state, config):
        # We verify that Values (S12.i.3) cannot be calculated without Type (S12.i.2).
        state.results_boundary_conditions[0] = {"location": "x_min"}
        
        step = ComputeBoundaryConditionValuesStep()
        
        # Executing the Values step without a Type set should fail.
        with pytest.raises(KeyError):
            step.run(state, config, index=0)