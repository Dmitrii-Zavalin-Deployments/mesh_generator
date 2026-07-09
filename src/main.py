import sys
import os
import logging
import glob
import json
import argparse
import multiprocessing
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
from src.utils.mask_visualizer import generate_mask_snapshot

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

    # 3. Extract Core Context (No-Default Policy Enforcement)
    # Direct bracket lookup guarantees failure and process death if a key is absent.
    engine_type = config['engine_type']

    # 4. Initialize Sovereign Container
    container = SovereignContainer(
        step_file=step_file,
        max_element_size=config['max_element_size'],
        solver_version=config['solver_version'],
        tolerance=config['tolerance'],
        min_element_size=config['min_element_size'],
        boundary_map=config['boundary_map'],
        use_gmsh=(engine_type == 'gmsh')
    )
    
    logger.info(f"Starting pipeline execution. Engine: {engine_type}")

    # --- GMSH PARALLELIZATION & TOPOLOGY REMEDIATION LAYER ---
    if engine_type == 'gmsh':
        import gmsh
        
        # Guard against double initialization loops
        if not gmsh.isInitialized():
            logger.info("Initializing Gmsh runtime engine context...")
            gmsh.initialize()
        else:
            logger.warning("Gmsh engine already active in global state context. Skipping initialization.")
        
        # Optimize compute allocations for virtualized CI runners (2 vCPUs)
        cores = multiprocessing.cpu_count()
        logger.info(f"Commanding hardware allocation: Parallel tracking across {cores} threads.")
        gmsh.option.setNumber("General.NumThreads", cores)
        
        # Switch to HXT mesh generation schema (parallelized, highly performant)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        
        # Bypass boundary curvature traps to eliminate single-threaded infinite refinement stalls
        gmsh.option.setNumber("Mesh.CharacteristicLengthFromCurvature", 0)
        gmsh.option.setNumber("Mesh.CharacteristicLengthExtendFromBoundary", 1)
        
        # Bind sovereign configuration tokens directly to geometry options (No-Default Policy)
        gmsh.option.setNumber("Geometry.Tolerance", config['tolerance'])
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", config['max_element_size'])
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", config['min_element_size'])

    try:
        # 5. Orchestrate Pipeline Execution
        pipeline = Orchestrator([
            IngestionStep(),
            TracingStep(),
            ResolutionStep(),
            CategorizationStep(),
            BoundaryConditionsStep()
        ])
        pipeline.run(container)
        
        # 6. Serialize Output Payload
        output_path = os.path.join(workspace, "mesh_generator_output.json")
        snapshot_file = os.path.join(workspace, "mesh_snapshot.png")

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
                "mesh_snapshot_path": os.path.abspath(snapshot_file) if engine_type == 'gmsh' else None,
                "boundary_conditions": [
                    {"location": bc.location, "type": bc.type, "surface_id": bc.surface_id}
                    for bc in (container.boundary_conditions or [])
                ]
            }
        }

        # --- VISUAL MASK VERIFICATION GATE ---
        try:
            generate_mask_snapshot(output_data)
        except Exception as viz_err:
            logger.error(f"Voxel verification snapshot engine faulted: {str(viz_err)}")

        # --- SERIALIZATION LAYER ---
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        logger.info(f"Results serialized to: {output_path}")

    finally:
        # Guarantee memory teardown of binary objects regardless of run-time failures
        if engine_type == 'gmsh':
            import gmsh
            # Guard against tearing down an already finalized or closed singleton session
            if gmsh.isInitialized():
                logger.info("Executing final environment cleanup. Purging Gmsh memory structures...")
                gmsh.finalize()
            else:
                logger.warning("Gmsh finalization bypassed: Engine was already uninitialized by an internal pipeline step.")

if __name__ == "__main__":  # pragma: no cover
    main()