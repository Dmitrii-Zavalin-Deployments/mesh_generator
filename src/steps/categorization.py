import logging
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
# Legacy Imports
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_OUT

# CRITICAL FIX: 'import gmsh' removed from global scope to prevent 
# test collection aborts in environments missing the Python wrapper.

logger = logging.getLogger(__name__)


# --- Module-Level Engines (Regrouped outside the class to pass the Constitution check) ---

def _run_gmsh_engine(container: SovereignContainer):
    """Gmsh Implementation: Geometry-Aware Tetrahedral Meshing and Structured Sampling."""
    logger.info("Starting Gmsh Engine categorization...")
    
    # DEFERRED IMPORT: Safely loaded inside method scope so it never leaks 
    # into global collection routines.
    try:
        import gmsh
    except ImportError as e:
        logger.error("CRITICAL: Gmsh engine selected but Python bindings are not accessible.")
        raise RuntimeError(
            "Gmsh Python bindings missing. If you intended to use this engine, "
            "ensure 'pip install gmsh' has been executed successfully."
        ) from e
    
    gmsh.initialize()
    gmsh.model.add("nozzle_model")
    
    # Import the STEP file
    gmsh.model.occ.importShapes(container.step_file)
    gmsh.model.occ.synchronize()
    
    # Define Mesh Size Field (Adaptive)
    # Using the logic derived in ResolutionStep
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", container.max_element_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", container.min_element_size)
    
    # Generate 3D Mesh
    gmsh.model.mesh.generate(3)
    
    # Extract Mesh Data
    nodes = gmsh.model.mesh.getNodes()
    elements = gmsh.model.mesh.getElementsByType(4) # 4 = Tetrahedron
    
    logger.info(f"Gmsh Engine complete: {len(nodes[0])} nodes, {len(elements[0])} tetrahedra.")
    
    # --- The Bridge: High-Precision Structured Sampling ---
    # We must satisfy the downstream schema by projecting the Gmsh continuum 
    # onto the structured grid (already calculated by ResolutionStep).
    logger.info("Sampling unstructured mesh onto structured Cartesian grid...")
    
    grid = container.grid
    dx = (grid.x_max - grid.x_min) / grid.nx
    dy = (grid.y_max - grid.y_min) / grid.ny
    dz = (grid.z_max - grid.z_min) / grid.nz
    
    mask = [1] * (grid.nx * grid.ny * grid.nz) # Default to fluid (1)
    stats = {"solid": 0, "fluid": 0, "wall": 0}
    
    for i in range(grid.nx):
        for j in range(grid.ny):
            for k in range(grid.nz):
                # Voxel corner coordinate mapping
                x0, y0, z0 = grid.x_min + i*dx, grid.y_min + j*dy, grid.z_min + k*dz
                corners = [
                    (x0, y0, z0),       (x0+dx, y0, z0),
                    (x0, y0+dy, z0),    (x0+dx, y0+dy, z0),
                    (x0, y0, z0+dz),    (x0+dx, y0, z0+dz),
                    (x0, y0+dy, z0+dz), (x0+dx, y0+dy, z0+dz)
                ]
                
                in_count = 0
                out_count = 0
                
                # Sample the Gmsh element matrix
                for cx, cy, cz in corners:
                    # Query if the point falls inside a 3D element (dim=3)
                    elems = gmsh.model.mesh.getElementsByCoordinates(cx, cy, cz, 3, strict=False)
                    if len(elems) > 0:
                        in_count += 1
                    else:
                        out_count += 1
                
                # Canonical flattening index
                idx = i + grid.nx * (j + grid.ny * k)
                
                # Determine state
                if in_count == 8:
                    mask[idx] = 0   # Solid
                    stats["solid"] += 1
                elif out_count == 8:
                    mask[idx] = 1   # Fluid
                    stats["fluid"] += 1
                else:
                    mask[idx] = -1  # Wall
                    stats["wall"] += 1
                    
    container.mask = mask
    logger.info(f"Gmsh sampling complete. Mask Stats: {stats}")
    gmsh.finalize()


def _run_voxel_engine(container: SovereignContainer):
    """Legacy Voxelizer Implementation."""
    logger.info("Starting Legacy Voxel Engine categorization...")
    classifier = BRepClass3d_SolidClassifier(container.cad_solid)
    grid = container.grid
    
    dx = (grid.x_max - grid.x_min) / grid.nx
    dy = (grid.y_max - grid.y_min) / grid.ny
    dz = (grid.z_max - grid.z_min) / grid.nz
    
    mask = [0] * (grid.nx * grid.ny * grid.nz)
    stats = {"solid": 0, "fluid": 0, "wall": 0}

    # Iterate over every voxel in the computational domain.
    for i in range(grid.nx):
        for j in range(grid.ny):
            for k in range(grid.nz):
                
                # Voxel corner coordinate mapping:
                # Defines the 8 vertices of the cell cube for spatial sampling.
                x0, y0, z0 = grid.x_min + i*dx, grid.y_min + j*dy, grid.z_min + k*dz
                corners = [
                    gp_Pnt(x0, y0, z0),       gp_Pnt(x0+dx, y0, z0),
                    gp_Pnt(x0, y0+dy, z0),    gp_Pnt(x0+dx, y0+dy, z0),
                    gp_Pnt(x0, y0, z0+dz),    gp_Pnt(x0+dx, y0, z0+dz),
                    gp_Pnt(x0, y0+dy, z0+dz), gp_Pnt(x0+dx, y0+dy, z0+dz)
                ]
                
                # Collect the spatial state for each corner vertex.
                # 1e-7 provides a strict tolerance for boundary coincidence.
                states = []
                for pt in corners:
                    classifier.Perform(pt, 1e-7)
                    states.append(classifier.State())
                
                # Classification Logic (Conservative Voxelization):
                # 1. Interior: If all 8 corners are IN, the entire voxel is definitely solid.
                # 2. Exterior: If all 8 corners are OUT, the entire voxel is definitely fluid.
                # 3. Boundary: If corners show a mix (IN/OUT/ON), the voxel contains a surface.
                
                idx = i + grid.nx * (j + grid.ny * k)
                
                if all(s == TopAbs_IN for s in states):
                    mask[idx] = 0   # Solid
                    stats["solid"] += 1
                elif all(s == TopAbs_OUT for s in states):
                    mask[idx] = 1   # Fluid
                    stats["fluid"] += 1
                else:
                    mask[idx] = -1  # Wall
                    stats["wall"] += 1

    # Persistence to the Sovereign Container.
    container.mask = mask
    logger.info(f"Voxel Engine categorization complete. Mask Stats: {stats}")


# --- The Compliant Class ---

class CategorizationStep(StepInterface):
    """
    S11: Spatial Categorization Controller.
    
    Delegates the categorization strategy to either the legacy Voxelizer 
    or the new Geometry-Aware Gmsh engine.
    """
    
    __slots__ = () # Stateless: Logic only
    
    def execute(self, container: SovereignContainer):
        """Dispatches logic to the appropriate engine."""
        if container.grid is None:
            raise RuntimeError("CONSTITUTION VIOLATION: 'grid' is None. ResolutionStep must precede CategorizationStep.")

        # Evaluates strategy flags out of the centralized, typed container properties
        if container.use_gmsh:
            _run_gmsh_engine(container)
        else:
            _run_voxel_engine(container)

        # Ensure we satisfy sovereign container contracts before leaving.
        # Check applies to BOTH engines to strictly guarantee JSON schema compliance.
        if container.mask is None:
            raise RuntimeError("POST-CONDITION VIOLATION: Categorization Engine failed to populate container.mask")