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
from src.implementation.pipeline.output_assembler import OutputAssembler

class Orchestrator:
    """
    The central pipeline controller for the Mesh Generator.
    
    Responsibilities:
    1. Validate inputs via factories.
    2. Centralize schema/key validation.
    3. Execute steps in the strict Minimal Step Path topological order.
    4. Trigger Final Output Assembly (Phase 5).
    """

    def _ensure_keys(self, state, keys: list):
        """Centralized validation: Ensure grid keys exist before calculation."""
        for key in keys:
            if state.results_grid.get(key) is None:
                raise ValueError(f"Orchestrator validation failed: '{key}' is missing in results_grid.")

    def run(self, raw_state: dict, raw_config: dict) -> str:
        try:
            # 1. Validation Gates
            state = StateFactory.create(raw_state)
            config = ConfigLoader.load(raw_config)

            # 2. Geometry Initialization
            parser = ParseStepGeometryStep()
            geometry_model = parser.run(state, config)

            # 3. Calculate Bounds
            ComputeXMinStep(geometry_model).run(state, config)
            ComputeXMaxStep(geometry_model).run(state, config)
            ComputeYMinStep(geometry_model).run(state, config)
            ComputeYMaxStep(geometry_model).run(state, config)
            ComputeZMinStep(geometry_model).run(state, config)
            ComputeZMaxStep(geometry_model).run(state, config)

            # 4. Calculate Resolution
            self._ensure_keys(state, ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'])
            ComputeNxStep().run(state, config)
            ComputeNyStep().run(state, config)
            ComputeNzStep().run(state, config)

            # 5. Calculate Mask
            self._ensure_keys(state, ['nx', 'ny', 'nz'])
            ComputeMaskStep(geometry_model).run(state, config)

            # 6. Handle Boundary Conditions
            # We now only execute the steps required by the schema: Location and Type.
            bc_steps = [
                ComputeBoundaryConditionLocationStep(geometry_model),
                ComputeBoundaryConditionTypeStep(geometry_model)
            ]

            num_bcs = geometry_model.get_boundary_count()
            
            if num_bcs == 0:
                raise ValueError("Pipeline Error: No boundaries detected for processing.")

            # Pre-allocate the boundary conditions list
            state.results_boundary_conditions = [{} for _ in range(num_bcs)]

            for i in range(num_bcs):
                for step in bc_steps:
                    step.run(state, config, index=i)

            # 7. Finalize (Assembly)
            return OutputAssembler.assemble(
                state=state, 
                config=config, 
                inputs=raw_state
            )

        except Exception as e:
            raise e