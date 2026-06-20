# tests/test_mesh_generator_interface.py
from src.state.mesh_generator_state import GridState, BoundaryConditionState

class TestMeshGeneratorInterfaces:
    """
    Architectural Quality Gate for Mesh Generator Protocols.
    This suite acts as the specification document for our spatial state structures.
    We enforce structural type validation, attribute contracts, and strict 
    memory performance policies across all discretized spatial states.
    """

    def test_grid_state_structural_conformance(self):
        """
        [PROTOCOL GATE]
        We define the spatial domain properties that every grid must strictly
        implement. This ensures consistency for the solver.
        """
        
        # We define a grid spanning x[-5, 5], y[0, 10], z[-1.5, 1.5]
        # with a resolution of 50x100x30 voxels.
        x_min, x_max = -5.0, 5.0
        y_min, y_max = 0.0, 10.0
        z_min, z_max = -1.5, 1.5
        grid_instance = GridState(
            x_min, x_max, y_min, y_max, z_min, z_max,
            nx=50, ny=100, nz=30
        )

        # The protocol mandates specific attribute types to prevent downstream 
        # casting errors in the mesh solver.
        expected_protocol_fields = {
            "x_min": float, "x_max": float,
            "y_min": float, "y_max": float,
            "z_min": float, "z_max": float,
            "nx": int, "ny": int, "nz": int
        }

        # We verify that the structure adheres to the schema.
        for field, expected_type in expected_protocol_fields.items():
            assert hasattr(grid_instance, field), f"Protocol Violation: Missing '{field}'."
            actual_value = getattr(grid_instance, field)
            assert isinstance(actual_value, expected_type), f"Type Violation: '{field}' must be {expected_type}."

        # Finally, we perform a spatial consistency check:
        # The span of the domain should match the arithmetic difference of the bounds.
        span_x = grid_instance.x_max - grid_instance.x_min
        span_y = grid_instance.y_max - grid_instance.y_min
        span_z = grid_instance.z_max - grid_instance.z_min

        # The expected spans are 10.0, 10.0, and 3.0 respectively.
        assert abs(span_x - 10.0) < 1e-9
        assert abs(span_y - 10.0) < 1e-9
        assert abs(span_z - 3.0) < 1e-9

    def test_grid_state_performance_contract(self):
        """
        [PERFORMANCE GATE]
        Law of Performance: GridState must be memory-efficient.
        To ensure dense traversal speeds, we prohibit the creation of 
        __dict__ overhead via Python slots.
        """
        grid_instance = GridState(0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1, 1, 1)
        
        # We assert that the object has strictly optimized memory allocation.
        assert not hasattr(grid_instance, "__dict__"), "Memory Violation: Unexpected __dict__."
        assert hasattr(grid_instance, "__slots__"), "Memory Violation: Missing __slots__ configuration."

    def test_boundary_condition_structural_conformance(self):
        """
        [PROTOCOL GATE]
        Boundary conditions define the simulation constraints. 
        We validate that every BC satisfies the contract for location, type, and ID.
        """
        
        # We initialize a test boundary for the 'z_max' face using a 'neumann' condition.
        bc_instance = BoundaryConditionState(
            location="z_max",
            type="neumann",
            surface_id="cell_84102"
        )

        # The contract requires strict mapping between attribute strings.
        expected_protocol_fields = {
            "location": str,
            "type": str,
            "surface_id": str
        }

        # We iterate and validate the field existence and type.
        for field, expected_type in expected_protocol_fields.items():
            assert hasattr(bc_instance, field), f"Protocol Violation: Missing '{field}'."
            actual_value = getattr(bc_instance, field)
            assert isinstance(actual_value, expected_type), f"Type Violation: '{field}' must be {expected_type}."

    def test_boundary_condition_performance_contract(self):
        """
        [PERFORMANCE GATE]
        Like GridState, BoundaryConditionState must maintain minimal runtime cost.
        We confirm __slots__ enforcement for high-throughput boundary traversal.
        """
        bc_instance = BoundaryConditionState("wall", "dirichlet", "cell_0")
        
        # The object must lack a dictionary to comply with performance policies.
        assert not hasattr(bc_instance, "__dict__"), "Memory Violation: __dict__ found."
        assert hasattr(bc_instance, "__slots__"), "Memory Violation: __slots__ not implemented."