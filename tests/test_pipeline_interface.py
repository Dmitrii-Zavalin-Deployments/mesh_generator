# tests/test_pipeline_interface.py

from interfaces.grid_interface import GridInterface

from interfaces.pipeline_interface import PipelineInterface
from interfaces.mesh_generator_interface import GridInterface
from src.state.mesh_generator_state import GridState


class CompletePipelineImplementation:
    """Mock class implementing all properties of PipelineInterface."""
    
    @property
    def geometry(self):
        return object()  # Represents the CAD geometry / TopoDS_Shape

    @property
    def grid(self) -> GridInterface:
        return GridState(
            x_min=0.0, x_max=1.0,
            y_min=0.0, y_max=1.0,
            z_min=0.0, z_max=1.0,
            nx=2, ny=2, nz=2
        )

    @property
    def mask(self) -> list[int]:
        return [1, 0, 1, 0]


class IncompletePipelineImplementation:
    """Mock class missing the 'mask' property."""
    
    @property
    def geometry(self):
        return object()

    @property
    def grid(self):
        return None


def test_pipeline_interface_runtime_check_success():
    """Verifies that an object implementing geometry, grid, and mask passes the runtime protocol check."""
    pipeline_obj = CompletePipelineImplementation()
    assert isinstance(pipeline_obj, PipelineInterface), "Valid implementation failed PipelineInterface runtime check."


def test_pipeline_interface_runtime_check_failure_missing_property():
    """Verifies that an incomplete object fails the runtime protocol check."""
    incomplete_obj = IncompletePipelineImplementation()
    assert not isinstance(incomplete_obj, PipelineInterface), "Incomplete implementation incorrectly passed PipelineInterface check."


def test_pipeline_interface_property_contracts():
    """Verifies that property getters return expected types and structures."""
    pipeline_obj = CompletePipelineImplementation()
    
    assert pipeline_obj.geometry is not None
    assert isinstance(pipeline_obj.grid, GridInterface)
    assert isinstance(pipeline_obj.mask, list)
    assert all(isinstance(val, int) for val in pipeline_obj.mask)
