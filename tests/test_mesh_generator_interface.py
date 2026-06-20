# tests/test_mesh_generator_interface.py
from src.state.mesh_generator_state import GridState, BoundaryConditionState

class TestMeshGeneratorInterfaces:
    """
    Architectural Quality Gate for Mesh Generator Protocols.
    Enforces structural type validation, attribute contracts, and strict 
    memory performance policies across discretized spatial states.
    """

    def test_grid_state_structural_conformance(self):
        """
        [PROTOCOL GATE] Verify that GridState strictly implements every spatial property 
        and type definition mandated by the structural GridInterface contract.
        """
        # 1. Setup: Explicit initialization with deterministic domain properties
        # No convenience defaults or fallbacks are allowed under the state layout contract.
        grid_instance = GridState(
            x_min=-5.0, x_max=5.0,
            y_min=0.0, y_max=10.0,
            z_min=-1.5, z_max=1.5,
            nx=50, ny=100, nz=30
        )

        # 2. Define the complete structural dictionary expected by GridInterface
        expected_protocol_fields = {
            "x_min": float, "x_max": float,
            "y_min": float, "y_max": float,
            "z_min": float, "z_max": float,
            "nx": int, "ny": int, "nz": int
        }

        # 3. Verification: Exhaustively assert field presence and structural type-safety
        for field, expected_type in expected_protocol_fields.items():
            assert hasattr(grid_instance, field), (
                f"Protocol Violation: GridState is missing required attribute '{field}'."
            )
            actual_value = getattr(grid_instance, field)
            assert isinstance(actual_value, expected_type), (
                f"Type Violation: Attribute '{field}' must be a strict {expected_type.__name__}, "
                f"got {type(actual_value).__name__}."
            )

        # 4. Functional Verification: Ensure spatial properties map to consistent domain spans
        assert (grid_instance.x_max - grid_instance.x_min) == 10.0
        assert (grid_instance.y_max - grid_instance.y_min) == 10.0
        assert (grid_instance.z_max - grid_instance.z_min) == 3.0

    def test_grid_state_performance_contract(self):
        """
        [PERFORMANCE GATE] Enforce Rule 0 (Law of Performance). GridState must utilize 
        __slots__ to completely eliminate internal dictionary (__dict__) overhead.
        """
        grid_instance = GridState(0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1, 1, 1)
        
        assert not hasattr(grid_instance, "__dict__"), (
            "Constitution Violation: GridState contains a __dict__ payload, bypassing memory overhead bounds."
        )
        assert hasattr(grid_instance, "__slots__"), (
            "Constitution Violation: GridState failed to explicitly configure __slots__."
        )

    def test_boundary_condition_structural_conformance(self):
        """
        [PROTOCOL GATE] Verify that BoundaryConditionState satisfies every attribute 
        and typing definition mandated by the BoundaryConditionInterface contract.
        """
        # 1. Setup: Instantiate with strict operational string variables
        bc_instance = BoundaryConditionState(
            location="z_max",
            type="neumann",
            surface_id="cell_84102"
        )

        # 2. Define the exact structural attributes expected by BoundaryConditionInterface
        expected_protocol_fields = {
            "location": str,
            "type": str,
            "surface_id": str
        }

        # 3. Verification: Complete coverage of fields and primitive type assertions
        for field, expected_type in expected_protocol_fields.items():
            assert hasattr(bc_instance, field), (
                f"Protocol Violation: BoundaryConditionState is missing required attribute '{field}'."
            )
            actual_value = getattr(bc_instance, field)
            assert isinstance(actual_value, expected_type), (
                f"Type Violation: Attribute '{field}' must be a strict {expected_type.__name__}, "
                f"got {type(actual_value).__name__}."
            )

    def test_boundary_condition_performance_contract(self):
        """
        [PERFORMANCE GATE] Enforce Rule 0 (Law of Performance). BoundaryConditionState must 
        utilize __slots__ to maintain minimal runtime cost during dense traversal.
        """
        bc_instance = BoundaryConditionState("wall", "dirichlet", "cell_0")
        
        assert not hasattr(bc_instance, "__dict__"), (
            "Constitution Violation: BoundaryConditionState contains a __dict__ payload, bypassing memory overhead bounds."
        )
        assert hasattr(bc_instance, "__slots__"), (
            "Constitution Violation: BoundaryConditionState failed to explicitly configure __slots__."
        )