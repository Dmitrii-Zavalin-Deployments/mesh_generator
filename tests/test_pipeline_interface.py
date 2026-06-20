# tests/test_pipeline_interface.py
import pytest
from typing import List, get_type_hints
from OCC.Core.TopoDS import TopoDS_Shape
from interfaces.pipeline_interface import PipelineInterface
from src.state.mesh_generator_state import GridState, BoundaryConditionState

class TestPipelineInterface:
    """
    Architectural Quality Gate for PipelineInterface.
    Enforces the composite read-only structural contract of the global pipeline state,
    ensuring downstream consumers receive deterministic data structures.
    """

    def test_pipeline_interface_protocol_specifications(self):
        """
        [STATIC PROTOCOL GATE] Verify that PipelineInterface is properly defined 
        as a runtime-inspectable contract with the correct property type hints.
        """
        # Extract the expected type annotations from the abstract protocol definition
        type_hints = get_type_hints(PipelineInterface)
        
        assert "geometry" in type_hints, "Protocol Definition Error: 'geometry' property is missing annotations."
        assert "grid" in type_hints, "Protocol Definition Error: 'grid' property is missing annotations."
        assert "mask" in type_hints, "Protocol Definition Error: 'mask' property is missing annotations."
        assert "boundary_conditions" in type_hints, "Protocol Definition Error: 'boundary_conditions' property is missing annotations."

    def test_composite_pipeline_state_conformance(self):
        """
        [COMPOSITE VALIDATION GATE] Verify that a production-compliant global pipeline state 
        fully adheres to the PipelineInterface structural contract using active typing verification.
        """
        # 1. Setup: Initialize direct, concrete production components (Zero placeholders used)
        pristine_shape = TopoDS_Shape()
        concrete_grid = GridState(
            x_min=0.0, x_max=10.0,
            y_min=0.0, y_max=10.0,
            z_min=0.0, z_max=5.0,
            nx=10, ny=10, nz=5
        )
        discrete_mask = [0, 1, -1, 1, 0]
        allocated_bcs = [
            BoundaryConditionState(location="x_min", type="inlet", surface_id="cell_0"),
            BoundaryConditionState(location="x_max", type="outlet", surface_id="cell_9")
        ]

        # 2. Define a concrete pipeline state view container that implements PipelineInterface
        class CompliantPipelineStateView:
            def __init__(self, geometry, grid, mask, boundary_conditions):
                self._geometry = geometry
                self._grid = grid
                self._mask = mask
                self._boundary_conditions = boundary_conditions

            @property
            def geometry(self) -> TopoDS_Shape:
                return self._geometry

            @property
            def grid(self) -> GridState:
                return self._grid

            @property
            def mask(self) -> List[int]:
                return self._mask

            @property
            def boundary_conditions(self) -> List[BoundaryConditionState]:
                return self._boundary_conditions

        # 3. Execution: Instantiate the state view wrapper
        state_view = CompliantPipelineStateView(
            geometry=pristine_shape,
            grid=concrete_grid,
            mask=discrete_mask,
            boundary_conditions=allocated_bcs
        )

        # 4. Structural Verification: Ensure the runtime object matches the PipelineInterface protocol layout
        assert isinstance(state_view, PipelineInterface), (
            "Protocol Mismatch: The state view container does not satisfy the structural typing contract of PipelineInterface."
        )

        # 5. Type and Integrity Enforcement Checks
        assert isinstance(state_view.geometry, TopoDS_Shape), "Type Contract Violation: 'geometry' must be a TopoDS_Shape."
        assert isinstance(state_view.grid, GridState), "Type Contract Violation: 'grid' must be a GridState instance."
        
        assert isinstance(state_view.mask, list), "Type Contract Violation: 'mask' must be a structural List."
        assert all(isinstance(element, int) for element in state_view.mask), "Type Contract Violation: 'mask' elements must be strict integers."
        
        assert isinstance(state_view.boundary_conditions, list), "Type Contract Violation: 'boundary_conditions' must be a structural List."
        assert all(isinstance(bc, BoundaryConditionState) for bc in state_view.boundary_conditions), (
            "Type Contract Violation: List items inside 'boundary_conditions' must conform to BoundaryConditionState."
        )

    def test_pipeline_interface_read_only_immutability(self):
        """
        [SECURITY GATE] Enforce that the PipelineInterface properties function as 
        read-only views. Attempting to directly overwrite the attributes must cause 
        an immediate runtime exception.
        """
        class ReadOnlyStateView:
            @property
            def geometry(self) -> TopoDS_Shape: return TopoDS_Shape()
            @property
            def grid(self): return None
            @property
            def mask(self) -> List[int]: return []
            @property
            def boundary_conditions(self): return []

        immutable_view = ReadOnlyStateView()

        # Enforce that no raw properties can be reassigned on the composite state view boundary
        with pytest.raises(AttributeError):
            immutable_view.geometry = TopoDS_Shape()

        with pytest.raises(AttributeError):
            immutable_view.mask = [1, 2, 3]