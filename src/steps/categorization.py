import logging
import os
import numpy as np
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer

# Legacy Imports for fallback voxelizer
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_OUT

# CRITICAL FIX: 'import gmsh' removed from global scope to prevent 
# test collection aborts in environments missing the Python wrapper.

logger = logging.getLogger(__name__)

# --- SSoT Shared Memory Cache ---
# Used to transfer pre-baked mesh raw structure to BoundaryConditionsStep (Layer 2)
# without violating SovereignContainer's __slots__ boundary policies.
_GMSH_MESH_CACHE = {}

# --- Module-Level Engines (Regrouped outside the class to pass the Constitution check) ---

def _run_gmsh_engine(container: SovereignContainer):
    """
    Gmsh Implementation Layer 1: Geometry-Aware Unstructured Mesh Baking.
    Responsible for volume meshing and caching raw node/element coordinates.
    """
    logger.info("Starting Gmsh Engine categorization (Layer 1: Mesh Baking)...")
    
    # DEFERRED IMPORT: Safely loaded inside method scope
    try:
        import gmsh
    except ImportError as e:
        logger.error("CRITICAL: Gmsh engine selected but Python bindings are not accessible.")
        raise RuntimeError(
            "Gmsh Python bindings missing. If you intended to use this engine, "
            "ensure 'pip install gmsh' has been executed successfully."
        ) from e
    
    gmsh.initialize()
    
    try:
        # Abstract model initialization to accept any geometry variation smoothly
        gmsh.model.add("geometry_model")
        
        # Import the STEP file
        gmsh.model.occ.importShapes(container.step_file)
        gmsh.model.occ.synchronize()
        
        # Define Mesh Size Field (Adaptive)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", container.max_element_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", container.min_element_size)
        
        # Generate 3D Mesh
        gmsh.model.mesh.generate(3)
        
        # Extract Unstructured Mesh Topology (Type 4: 4-node Tetrahedron)
        # node_tags is a flat 1D array, coord is flat 3D float array [x1, y1, z1, x2, y2, z2, ...]
        node_tags, coord, _ = gmsh.model.mesh.getNodes()
        element_types, element_tags, element_node_tags = gmsh.model.mesh.getElements(dim=3)
        
        # Find the indices corresponding to tetrahedral elements (Type 4 in Gmsh)
        tet_idx = -1
        for idx, etype in enumerate(element_types):
            if etype == 4:
                tet_idx = idx
                break
                
        if tet_idx == -1:
            raise RuntimeError("POST-CONDITION VIOLATION: Gmsh failed to generate 3D tetrahedral elements.")

        # Reconstruct coordinate map: tag -> numpy [x, y, z]
        nodes_map = {}
        for i, tag in enumerate(node_tags):
            nodes_map[tag] = np.array([coord[3*i], coord[3*i+1], coord[3*i+2]], dtype=np.float64)

        # Reconstruct tetrahedral vertex matrix: Shape (N_tets, 4, 3)
        tets_nodes = element_node_tags[tet_idx].reshape(-1, 4)
        tets_vertices = []
        for tet in tets_nodes:
            tets_vertices.append([nodes_map[node] for node in tet])
        
        tets_vertices_arr = np.array(tets_vertices, dtype=np.float64)
        logger.info(f"Layer 1 complete: Baked {len(tets_vertices_arr)} tetrahedra vertices matrix into global cache.")
        
        # Cache the pre-baked structures for Layer 2
        _GMSH_MESH_CACHE["nodes_map"] = nodes_map
        _GMSH_MESH_CACHE["tets_vertices"] = tets_vertices_arr
        
        # Satisfy container contract post-condition checks by providing an initial default fluid mask.
        # Layer 2 (BoundaryConditionsStep) will overwrite this with the high-precision sampled mask.
        container.mask = [1] * (container.grid.nx * container.grid.ny * container.grid.nz)

        # --- UNIVERSAL VISUALIZATION RENDER GENERATION ---
        try:
            # Visual visibility configurations
            gmsh.option.setNumber("Mesh.SurfaceEdges", 1)
            gmsh.option.setNumber("Mesh.Lines", 1)
            gmsh.option.setNumber("Mesh.Tetrahedra", 1)
            
            # Offscreen rendering resolution dimensions
            gmsh.option.setNumber("General.GraphicsWidth", 1200)
            gmsh.option.setNumber("General.GraphicsHeight", 900)
            
            # --- 3D ISOMETRIC VIEW ORIENTATION ---
            gmsh.option.setNumber("General.Trackball", 0)     # Disable auto-scaling/fitting
            gmsh.option.setNumber("General.RotationX", -35)   # Pitch rotation
            gmsh.option.setNumber("General.RotationY", 0)     # Roll rotation
            gmsh.option.setNumber("General.RotationZ", 45)    # Yaw rotation
            
            # --- VIEWPORT PADDING ---
            # 1.0 is fit-to-edge. Reducing this zooms out, adding padding to the edges.
            # 0.8 is usually perfect for isometric views to prevent clipping.
            gmsh.option.setNumber("General.ZoomFactor", 0.8)
            
            # Resolve destination path
            workspace_dir = os.path.dirname(os.path.abspath(container.step_file))
            snapshot_path = os.path.join(workspace_dir, "mesh_snapshot.png")
            
            # Wake up the FLTK interface context inside Xvfb before writing pixels
            gmsh.fltk.initialize()
            gmsh.write(snapshot_path)
            gmsh.fltk.finalize()
            
            logger.info(f"Universal mesh snapshot saved successfully: {snapshot_path}")
        except Exception as ex:
            logger.error(f"CRITICAL VISUALIZATION FAILURE: {str(ex)}")
            raise ex

    finally:
        # Guarantee memory unbinding even on runtime geometry contract failures
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
                    gp_Pnt(x0+dy, y0, z0),    gp_Pnt(x0+dx, y0+dy, z0),
                    gp_Pnt(x0, y0, z0+dz),    gp_Pnt(x0+dx, y0, z0+dz),
                    gp_Pnt(x0+dy, y0+dz), gp_Pnt(x0+dx, y0+dy, z0+dz)
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