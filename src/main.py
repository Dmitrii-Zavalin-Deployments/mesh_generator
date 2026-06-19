import sys
import json
from src.state.mesh_generator_state import SovereignContainer
from src.pipeline.orchestrator import Orchestrator
from src.steps.ingestion import IngestionStep
from src.steps.tracing import TracingStep
from src.steps.resolution import ResolutionStep
from src.steps.categorization import CategorizationStep
from src.steps.boundary_conditions import BoundaryConditionsStep

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_step_json> <output_json>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    # 1. Load Inputs
    with open(input_path, 'r') as f:
        input_data = json.load(f)

    # 2. Load Config
    with open("config/config.json", 'r') as f:
        config = json.load(f)

    # 3. Initialize Sovereign Container
    container = SovereignContainer(
        step_file=input_data['inputs']['step_file'],
        max_element_size=config['max_element_size'],
        solver_version=config['solver_version'],
        tolerance=config['tolerance'],
        min_element_size=config['min_element_size'],
        boundary_map=config['boundary_map']
    )

    # 4. Orchestrate Pipeline
    pipeline = Orchestrator([
        IngestionStep(),
        TracingStep(),
        ResolutionStep(),
        CategorizationStep(),
        BoundaryConditionsStep()
    ])
    pipeline.run(container)

    # 5. Serialize Output to JSON (Aligned with mesh_generator_output_schema.json)
    output_data = {
        "inputs": {
            "step_model": {"path": container.step_file} 
        },
        "config": {
            "solver_version": container.solver_version,
            "tolerance": container.tolerance,
            "max_element_size": container.max_element_size,
            "min_element_size": container.min_element_size,
            "boundary_map": container.bc_map
        },
        "results": {
            "grid": {
                "x_min": container.grid.x_min, "x_max": container.grid.x_max,
                "y_min": container.grid.y_min, "y_max": container.grid.y_max,
                "z_min": container.grid.z_min, "z_max": container.grid.z_max,
                "nx": container.grid.nx, "ny": container.grid.ny, "nz": container.grid.nz
            },
            "mask": container.mask,
            "boundary_conditions": [
                {"location": bc.location, "type": bc.type, "surface_id": bc.surface_id}
                for bc in container.boundary_conditions
            ]
        }
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    main()