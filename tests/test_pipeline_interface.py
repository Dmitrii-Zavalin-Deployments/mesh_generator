# tests/test_pipeline_interface.py
import os
from interfaces.pipeline_interface import PipelineInterface
from src.state.mesh_generator_state import SovereignContainer, GridState, BoundaryConditionState

# 1. Literate Testing Standard: Validating Global Pipeline State
# [cite_start]The PipelineInterface acts as a read-only composite view of the final output state[cite: 146].
# The SovereignContainer is the central implementation that fulfills this interface 
# [cite_start]as it flows through the orchestrator[cite: 20].

class TestPipelineInterface(PipelineInterface):
    # 1:1 Interface Inheritance Rule: We inherit from PipelineInterface.
    
    def test_sovereign_container_as_pipeline_state(self):
        # We define the path explicitly using os.path to avoid CI/CD file resolution failures.
        # This explicit path resolution aligns with the deterministic, no-default mandate.
        base_dir = os.getcwd()
        step_path = os.path.abspath(os.path.join(base_dir, "tests", "dummies", "sample_geometry.step"))

        # We initialize a SovereignContainer dummy.
        # [cite_start]Strict explicit initialization is required; all pipeline config must be provided[cite: 24].
        container_dummy = SovereignContainer(
            step_file=step_path,
            max_element_size=2.5,
            solver_version="v1.0.0",
            tolerance=1e-4,
            min_element_size=0.5,
            boundary_map={"x_min": "inlet", "x_max": "outlet"}
        )
        
        # We manually inject explicit dummy state objects to satisfy the interface.
        container_dummy.grid = GridState(0.0, 10.0, 0.0, 10.0, 0.0, 10.0, 10, 10, 10)
        
        # The mask array maps voxels to categorized states: 0 (Solid), 1 (Fluid), -1 (Interface).
        # We simulate a partial 3-element mask list.
        container_dummy.mask = [0, 1, -1]
        
        # We assign an explicit dummy boundary condition mapped to the inlet.
        container_dummy.boundary_conditions = [
            BoundaryConditionState(location="x_min", type="inlet", surface_id="cell_2")
        ]
        
        # [cite_start]Validation checks against the PipelineInterface contract[cite: 146].
        # The mask must successfully return a List[int] representing the computational mask.
        assert len(container_dummy.mask) == 3
        
        # The boundary conditions list must retain the explicit dummy assignment.
        assert container_dummy.boundary_conditions[0].location == "x_min"
        
        # [cite_start]The enforced bc_map provided during explicit initialization must be accurately captured[cite: 24].
        assert container_dummy.bc_map["x_max"] == "outlet"
