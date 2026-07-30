import logging
import multiprocessing
import os
import numpy as np

from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer

logger = logging.getLogger(__name__)

# --- SSoT Shared Memory Cache ---
# Used to transfer pre-baked mesh raw structure to VoxelizationStep (Layer 2)
# without violating SovereignContainer's __slots__ boundary policies.
_GMSH_MESH_CACHE = {}

def _run_gmsh_engine(container: SovereignContainer):
    """
    Gmsh Implementation Layer 1: Geometry-Aware Unstructured Mesh Baking.
    Responsible for volume meshing and caching raw node/element coordinates.
    """
    logger.info("Starting Gmsh Engine categorization (Layer 1: Mesh Baking)...")
    
    try:
        import gmsh
    except ImportError as e:
        logger.error("CRITICAL: Gmsh engine selected but Python bindings are not accessible.")
        raise RuntimeError("Gmsh Python bindings missing.") from e
    
    # Defensive Initialization Guard against Sig 139 / double initialization collisions
    initialized_here = False
    if not gmsh.is_initialized():
        gmsh.initialize()
        initialized_here = True
    else:
        logger.warning("Gmsh context active. Performing hard-reset to avoid memory corruption.")
        gmsh.finalize()
        gmsh.initialize()
        initialized_here = True
    
    # RE-APPLY MULTITHREADING AND OPTIMIZATION (Prevent wipe from hard-reset)
    cores = multiprocessing.cpu_count()
    gmsh.option.setNumber("General.NumThreads", cores)
    gmsh.option.setNumber("Mesh.Algorithm3D", 10)
    gmsh.option.setNumber("General.Terminal", 0)   
    gmsh.option.setNumber("General.Verbosity", 1)  
    
    try:
        gmsh.model.add("geometry_model")
        gmsh.model.occ.importShapes(container.step_file)
        gmsh.model.occ.synchronize()
        
        # --- DYNAMIC GEOMETRY-AWARE ROTATION CENTER & VIEWPORT CONFIGURATION ---
        # Compute the bounding box of the imported model to dynamically target 
        # the rotation anchor and framing to its true geometric center and size.
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
        cx, cy, cz = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0
        
        gmsh.option.setNumber("General.RotationCenterX", cx)
        gmsh.option.setNumber("General.RotationCenterY", cy)
        gmsh.option.setNumber("General.RotationCenterZ", cz)
        
        # Define Mesh Size Field (Adaptive)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", container.max_element_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", container.min_element_size)
        
        # Loop Crash/Segfault Prevention
        # Switch 2D algorithm to MeshAdapt (2) to cleanly resolve complex/imperfect non-manifold CAD seams
        gmsh.option.setNumber("Mesh.Algorithm", 2)
        
        # Isolate 1D edge generation and purge duplicate boundary nodes before baking 2D surfaces or 3D volumes
        gmsh.model.mesh.generate(1)
        gmsh.model.mesh.removeDuplicateNodes()
        
        # Generate 3D Mesh
        gmsh.model.mesh.generate(3)
        
        # Extract Unstructured Mesh Topology (Type 4: 4-node Tetrahedron)
        # node_tags is a flat 1D array, coord is flat 3D float array [x1, y1, z1, x2, y2, z2, ...]
        node_tags, coord, _ = gmsh.model.mesh.getNodes()
        element_types, _element_tags, element_node_tags = gmsh.model.mesh.getElements(dim=3)
        
        # Find the indices corresponding to tetrahedral elements (Type 4 in Gmsh)
        tet_idx = -1
        for idx, etype in enumerate(element_types):
            if etype == 4:
                tet_idx = idx
                break
                
        if tet_idx == -1:
            raise RuntimeError("POST-CONDITION VIOLATION: Gmsh failed to generate 3D tetrahedral elements.")

        nodes_map = {tag: np.array([coord[3*i], coord[3*i+1], coord[3*i+2]], dtype=np.float64) 
                     for i, tag in enumerate(node_tags)}

        tets_nodes = element_node_tags[tet_idx].reshape(-1, 4)
        tets_vertices_arr = np.array([[nodes_map[node] for node in tet] for tet in tets_nodes], dtype=np.float64)
        
        _GMSH_MESH_CACHE["nodes_map"] = nodes_map
        _GMSH_MESH_CACHE["tets_vertices"] = tets_vertices_arr
        
        # Satisfy container contract post-condition checks by providing an initial default fluid mask.
        # Layer 2 (VoxelizationStep) will overwrite this with the high-precision sampled mask.
        container.mask = [1] * (container.grid.nx * container.grid.ny * container.grid.nz)

        # --- UNIVERSAL VISUALIZATION RENDER GENERATION ---
        try:
            # Offscreen rendering resolution dimensions
            gmsh.option.setNumber("General.GraphicsWidth", 1200)
            gmsh.option.setNumber("General.GraphicsHeight", 900)
            
            # --- FULLY DYNAMIC ISOMETRIC VIEWPORT ALIGNMENT ---
            # Disable automatic trackball override to enforce custom 3D rotation angles
            gmsh.option.setNumber("General.Trackball", 0)
            
            # EXACT MATHEMATICAL ISOMETRIC ROTATION (elev=35.264, azim=-45.0)
            gmsh.option.setNumber("General.RotationX", -54.735)
            gmsh.option.setNumber("General.RotationY", 0.0)
            gmsh.option.setNumber("General.RotationZ", -45.0)
            
            # Control border padding around model (30% buffer)
            gmsh.option.setNumber("General.DisplayBorderFactor", 0.3)
            
            # Resolve destination paths using the directory context of the input model
            workspace_dir = os.path.dirname(os.path.abspath(container.step_file))
            step_snapshot_path = os.path.join(workspace_dir, "step_snapshot.png")
            snapshot_path = os.path.join(workspace_dir, "mesh_snapshot.png")
            
            # Wake up the FLTK interface context inside Xvfb
            gmsh.fltk.initialize()
            
            # --- PHASE 1: GENERATE RAW STEP GEOMETRY SNAPSHOT ---
            # Temporarily turn off all mesh display elements to capture clean CAD boundaries
            gmsh.option.setNumber("Mesh.SurfaceEdges", 0)
            gmsh.option.setNumber("Mesh.Lines", 0)
            gmsh.option.setNumber("Mesh.Tetrahedra", 0)
            
            # Force system to recalculate viewport, auto-fit, and write raw geometry buffer
            gmsh.graphics.draw()
            gmsh.fltk.update()
            gmsh.write(step_snapshot_path)
            logger.info(f"Universal STEP snapshot saved successfully: {step_snapshot_path}")
            
            # --- PHASE 2: GENERATE MESH SNAPSHOT (PERFECTLY ALIGNED) ---
            # Restore visibility configurations for full mesh layout representation
            gmsh.option.setNumber("Mesh.SurfaceEdges", 1)
            gmsh.option.setNumber("Mesh.Lines", 1)
            gmsh.option.setNumber("Mesh.Tetrahedra", 1)
            
            # Refresh context frame and dump matching matrix pixel layout to disk
            gmsh.graphics.draw()
            gmsh.fltk.update()
            gmsh.write(snapshot_path)
            gmsh.fltk.finalize()
            
            logger.info(f"Universal mesh snapshot saved successfully: {snapshot_path}")
        except Exception as ex:
            logger.error(f"CRITICAL VISUALIZATION FAILURE: {ex!s}")
            raise

    finally:
        # Guarantee memory unbinding only if the context was spun up within this frame execution
        if initialized_here and gmsh.is_initialized():
            gmsh.finalize()

class CategorizationStep(StepInterface):
    __slots__ = () 
    def execute(self, container: SovereignContainer):
        if container.grid is None:
            raise RuntimeError("CONSTITUTION VIOLATION: 'grid' is None.")
        _run_gmsh_engine(container)
        if container.mask is None:
            raise RuntimeError("POST-CONDITION VIOLATION: Categorization Engine failed to populate container.mask")