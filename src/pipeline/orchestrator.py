import json
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

class Orchestrator:
    """
    The central pipeline controller for the Mesh Generator.
    Acts as the exclusive Gatekeeper for validation, sequencing, and final assembly.
    """

    def _json_serializable_fallback(self, obj):
        """Fallback serializer for custom objects."""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    def _validate_config(self, config: dict):
        required = ['solver_version', 'tolerance', 'max_element_size', 'min_element_size', 'boundary_conditions']
        for field in required:
            if field not in config:
                raise ValueError(f"No-Defaults Policy Violation: Missing required config field '{field}'.")
        if not isinstance(config['boundary_conditions'], dict):
            raise TypeError("Config Type Mismatch: 'boundary_conditions' must be a dict.")

    def _validate_state(self, state: dict):
        required = ['inputs_step_file', 'results_grid', 'results_mask', 'results_boundary_conditions']
        for field in required:
            if field not in state:
                raise ValueError(f"No-Defaults Policy Violation: Missing required state field '{field}'.")

    def _ensure_keys(self, state, keys: list):
        for key in keys:
            if state.get('results_grid', {}).get(key) is None:
                raise ValueError(f"Orchestrator validation failed: '{key}' is missing in results_grid.")

    def run(self, raw_state: dict, raw_config: dict) -> str:
        # 1. Validation Gates
        self._validate_state(raw_state)
        self._validate_config(raw_config)

        # 2. State Initialization
        state = raw_state
        config = raw_config

        # 3. Geometry Initialization
        ParseStepGeometryStep().run(state, config)

        # 4. Calculate Bounds
        ComputeXMinStep().run(state, config)
        ComputeXMaxStep().run(state, config)
        ComputeYMinStep().run(state, config)
        ComputeYMaxStep().run(state, config)
        ComputeZMinStep().run(state, config)
        ComputeZMaxStep().run(state, config)

        # 5. Calculate Resolution
        self._ensure_keys(state, ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'])
        ComputeNxStep().run(state, config)
        ComputeNyStep().run(state, config)
        ComputeNzStep().run(state, config)

        # 6. Calculate Mask
        self._ensure_keys(state, ['nx', 'ny', 'nz'])
        ComputeMaskStep().run(state, config)

        # 7. Handle Boundary Conditions
        num_bcs = state.get('boundary_conditions_count', 0)
        if num_bcs == 0:
            raise ValueError("Pipeline Error: No boundaries detected for processing.")

        state['results_boundary_conditions'] = [{} for _ in range(num_bcs)]
        for i in range(num_bcs):
            ComputeBoundaryConditionLocationStep().run(state, config, index=i)
            ComputeBoundaryConditionTypeStep().run(state, config, index=i)

        # 8. Deterministic Final Assembly
        output_data = {
            "inputs": raw_state,
            "config": raw_config,
            "results": state.get('results_grid', {}) 
        }

        return json.dumps(
            output_data, 
            default=self._json_serializable_fallback, 
            indent=4, 
            sort_keys=True
        )