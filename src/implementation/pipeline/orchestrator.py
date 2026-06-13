# src/implementation/pipeline/orchestrator.py
from src.implementation.config.config_loader import ConfigLoader
from src.implementation.state.state_factory import StateFactory
from src.implementation.steps.parse_step_geometry_step import ParseStepGeometryStep
from src.implementation.steps.compute_x_min_step import ComputeXMinStep
from src.implementation.steps.compute_x_max_step import ComputeXMaxStep
from src.implementation.steps.compute_y_min_step import ComputeYMinStep
from src.implementation.steps.compute_y_max_step import ComputeYMaxStep
from src.implementation.steps.compute_z_min_step import ComputeZMinStep
from src.implementation.steps.compute_z_max_step import ComputeZMaxStep
from src.implementation.steps.compute_nx_step import ComputeNxStep
from src.implementation.steps.compute_ny_step import ComputeNyStep
from src.implementation.steps.compute_nz_step import ComputeNzStep
from src.implementation.steps.compute_mask_step import ComputeMaskStep
from src.implementation.steps.compute_boundary_condition_location_step import ComputeBoundaryConditionLocationStep
from src.implementation.steps.compute_boundary_condition_type_step import ComputeBoundaryConditionTypeStep
from src.implementation.steps.compute_boundary_condition_values_step import ComputeBoundaryConditionValuesStep

class Orchestrator:
    """
    The central pipeline controller for the Mesh Generator.
    
    Responsibilities:
    1. Validate inputs via factories.
    2. Instantiate steps.
    3. Execute steps in the strict Minimal Step Path order.
    4. Maintain zero business logic.
    """

    def run(self, raw_state: dict, raw_config: dict) -> None:
        # 1. Validation Gates
        state = StateFactory.create(raw_state)
        config = ConfigLoader.load(raw_config)

        # 2. Geometry Initialization (Non-containerized internal state)
        parser = ParseStepGeometryStep()
        geometry_model = parser.run(state, config)

        # 3. Instantiate and sequence steps that require geometry
        # Logic for topological sorting: 
        # Grids/Extents -> Mask -> Boundary Conditions
        steps = [
            ComputeXMinStep(geometry_model),
            ComputeXMaxStep(geometry_model),
            ComputeYMinStep(geometry_model),
            ComputeYMaxStep(geometry_model),
            ComputeZMinStep(geometry_model),
            ComputeZMaxStep(geometry_model),
            ComputeNxStep(),
            ComputeNyStep(),
            ComputeNzStep(),
            ComputeMaskStep(),
        ]

        # 4. Execute standard grid steps
        for step in steps:
            step.run(state, config)

        # 5. Handle Boundary Conditions (Dependent on index)
        # Assuming number of BCs is known from geometry_model
        bc_steps = [
            ComputeBoundaryConditionLocationStep(geometry_model),
            ComputeBoundaryConditionTypeStep(geometry_model),
            ComputeBoundaryConditionValuesStep()
        ]

        num_bcs = geometry_model.get_boundary_count()
        for i in range(num_bcs):
            for step in bc_steps:
                step.run(state, config, index=i)

        # Final pipeline state is now fully populated in 'state'
        return state