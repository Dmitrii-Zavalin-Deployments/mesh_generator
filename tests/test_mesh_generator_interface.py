# tests/test_mesh_generator_interface.py
from interfaces.mesh_generator_interface import GridInterface, BoundaryConditionInterface
from src.state.mesh_generator_state import GridState, BoundaryConditionState

# 1. Literate Testing Standard: Validating Domain Structures
# The GridInterface and BoundaryConditionInterface define the structural 
# [cite_start]contracts for the discretized spatial domain and physical boundaries[cite: 141, 143].

class TestGridInterface(GridInterface):
    # 1:1 Interface Inheritance Rule: We inherit from GridInterface.
    
    def test_grid_state_compliance(self):
        # We instantiate a dummy GridState object. 
        # [cite_start]To maintain strict determinism, no default values or convenience fallbacks are permitted[cite: 22].
        # All spatial boundaries and resolution intervals must be explicitly provided.
        x_min = 0.0
        x_max = 10.0
        y_min = 0.0
        y_max = 5.0
        z_min = 0.0
        z_max = 2.0
        nx = 20
        ny = 10
        nz = 4
        
        grid_dummy = GridState(
            x_min=x_min, x_max=x_max, 
            y_min=y_min, y_max=y_max, 
            z_min=z_min, z_max=z_max, 
            nx=nx, ny=ny, nz=nz
        )
        
        # [cite_start]We compute the expected span in the x-direction based on the grid contract[cite: 141, 142]:
        # Span_x = x_max - x_min
        expected_span_x = 10.0 - 0.0
        
        # The span calculated from the initialized dummy must exactly match the expected span.
        assert abs((grid_dummy.x_max - grid_dummy.x_min) - expected_span_x) < 1e-9


class TestBoundaryConditionInterface(BoundaryConditionInterface):
    # 1:1 Interface Inheritance Rule: We inherit from BoundaryConditionInterface.
    
    def test_boundary_condition_state_compliance(self):
        # We instantiate a dummy BoundaryConditionState object representing a boundary mapped to the x_min wall.
        location = "x_min"
        bc_type = "wall"
        surface_id = "cell_104"
        
        bc_dummy = BoundaryConditionState(location=location, type=bc_type, surface_id=surface_id)
        
        # We verify that the string references for location, type, and surface_id 
        # [cite_start]are accurately preserved to fulfill the interface contract[cite: 143].
        assert bc_dummy.location == "x_min"
        assert bc_dummy.type == "wall"
        assert bc_dummy.surface_id == "cell_104"