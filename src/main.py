import sys
import os

# --- BOOTSTRAP: Add repo root to sys.path ---
# This ensures that 'import src...' works regardless of your current working directory.
# We append the directory containing the 'src' folder.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import glob
import json
import argparse
from jsonschema import validate, ValidationError
from src.state.mesh_generator_state import SovereignContainer
from src.pipeline.orchestrator import Orchestrator
from src.steps.ingestion import IngestionStep
from src.steps.tracing import TracingStep
from src.steps.resolution import ResolutionStep
from src.steps.categorization import CategorizationStep
from src.steps.boundary_conditions import BoundaryConditionsStep

# Configure logging for CI/CD and local observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("mesh_generator")

def validate_json(data, schema_path):
    """Strictly validates data against a JSON schema. Raises ValidationError on failure."""
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

    # 1. Dynamic STEP File Discovery (Generality Principle)
    # The module independently searches the workspace for its target geometry
    step_files = glob.glob(os.path.join(workspace, "*.step"))
    if not step_files:
        error_msg = f"CONSTITUTION VIOLATION: STEP file not found in workspace: {os.path.abspath(workspace)}"
        logger.critical(error_msg)
        raise RuntimeError(error_msg)
    step_file = step_files[0]

    # 2. Load & Validate Config
    with open("config/config.json", 'r') as f:
        config = json.load(f)
    validate_json(config, "schema/mesh_generator_config_schema.json")

    # 3. Initialize Sovereign Container
    container = SovereignContainer(
        step_file=step_file,
        max_element_size=config['max_element_size'],
        solver_version=config['solver_version'],
        tolerance=config['tolerance'],
        min_element_size=config['min_element_size'],
        boundary_map=config['boundary_map']
    )

    # 4. Orchestrate Pipeline
    logger.info("Starting pipeline execution.")
    pipeline = Orchestrator([
        IngestionStep(),
        TracingStep(),
        ResolutionStep(),
        CategorizationStep(),
        BoundaryConditionsStep()
    ])
    pipeline.run(container)
    logger.info("Pipeline execution completed successfully.")

    # 5. Serialize Output
    output_data = {
        "inputs": {"step_model": {"path": container.step_file}},
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

    # Automatically map output to the identical workspace folder target boundary
    output_path = os.path.join(workspace, "mesh_generator_output.json")
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    logger.info(f"Results serialized to: {output_path}")

if __name__ == "__main__":  # pragma: no cover
    main()