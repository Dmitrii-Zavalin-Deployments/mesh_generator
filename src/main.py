import sys
import os
import logging
import glob
import json
import argparse
from jsonschema import validate, ValidationError

# --- BOOTSTRAP ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state.mesh_generator_state import SovereignContainer
from src.pipeline.orchestrator import Orchestrator
from src.steps.ingestion import IngestionStep
from src.steps.tracing import TracingStep
from src.steps.resolution import ResolutionStep
from src.steps.categorization import CategorizationStep
from src.steps.boundary_conditions import BoundaryConditionsStep

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("mesh_generator")

def validate_json(data, schema_path):
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    try:
        validate(instance=data, schema=schema)
        logger.info(f"Schema validation passed: {schema_path}")
    except ValidationError as e:
        logger.error(f"SCHEMA VIOLATION: {schema_path}")
        raise e

def main():
    parser = argparse.ArgumentParser(description="Modular Workspace Mesh Generator")
    parser.add_argument("--input_output_folder", required=True, help="Path to workspace directory")
    args = parser.parse_args()

    workspace = args.input_output_folder
    logger.info(f"Pipeline initialized. Workspace: {workspace}")

    # 1. Discover STEP File
    step_files = glob.glob(os.path.join(workspace, "*.step"))
    if not step_files:
        error_msg = f"CONSTITUTION VIOLATION: STEP file not found in workspace: {os.path.abspath(workspace)}"
        logger.critical(error_msg)
        raise RuntimeError(error_msg)
    step_file = step_files[0]

    # 2. Load and Validate Config
    with open("config/config.json", 'r') as f:
        config = json.load(f)
    validate_json(config, "schema/mesh_generator_config_schema.json")

    # 3. Initialize Sovereign Container
    # Strictly accessing keys; if missing, KeyError forces process termination (No Defaults).
    container = SovereignContainer(
        step_file=step_file,
        max_element_size=config['max_element_size'],
        solver_version=config['solver_version'],
        tolerance=config['tolerance'],
        min_element_size=config['min_element_size'],
        boundary_map=config['boundary_map'],
        use_gmsh=(config.get('engine_type') == 'gmsh')
    )

    # 4. Orchestrate Pipeline
    # No-Default Policy: config['engine_type'] must exist.
    engine_type = config['engine_type']
    use_gmsh = (engine_type == "gmsh")
    
    logger.info(f"Starting pipeline execution. Engine: {engine_type}")
    
    pipeline = Orchestrator([
        IngestionStep(),
        TracingStep(),
        ResolutionStep(),
        CategorizationStep(),
        BoundaryConditionsStep()
    ])
    pipeline.run(container)
    
    # 5. Serialize Output (Defensive)
    output_data = {
        "inputs": {"step_model": {"path": container.step_file}},
        "config": {
            "engine_type": engine_type,
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
            } if container.grid else None,
            "mask": container.mask if container.mask is not None else [],
            "boundary_conditions": [
                {"location": bc.location, "type": bc.type, "surface_id": bc.surface_id}
                for bc in (container.boundary_conditions or [])
            ]
        }
    }

    output_path = os.path.join(workspace, "mesh_generator_output.json")
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    logger.info(f"Results serialized to: {output_path}")

if __name__ == "__main__":
    main()