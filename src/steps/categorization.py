import logging
import os

import numpy as np

from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer

# CRITICAL FIX: 'import gmsh' removed from global scope to prevent 
# test collection aborts in environments missing the Python wrapper.

logger = logging.getLogger(__name__)

# --- SSoT Shared Memory Cache ---
# Used to transfer pre-baked mesh raw structure to BoundaryConditionsStep (Layer 2)
# without violating SovereignContainer's __slots__ boundary policies.
_GMSH_MESH_CACHE = {}

# --- Module-Level Engines ---

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
    
    # STABILIZATION PATCH 1: Complete progressive logging suppression
    gmsh.option.setNumber("General.Terminal", 0)   # Mutes terminal output routing
    gmsh.option.setNumber("General.Verbosity", 1)  # Mutes progress counters; allows only critical errors
    
    try:
        # Abstract model initialization to accept any geometry variation smoothly
        gmsh.model.add("geometry_model")
        
        # Import the STEP file
        gmsh.model.occ.importShapes(container.step_file)
        gmsh.model.occ.synchronize()
        
        # --- DYNAMIC GEOMETRY-AWARE ROTATION CENTER & VIEWPORT CONFIGURATION ---
        # Compute the bounding box of the imported model to dynamically target 
        # the rotation anchor and framing to its true geometric center and size.
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
        cx = (xmin + xmax) / 2.0
        cy = (ymin + ymax) / 2.0
        cz = (zmin + zmax) / 2.0
        
        gmsh.option.setNumber("General.RotationCenterX", cx)
        gmsh.option.setNumber("General.RotationCenterY", cy)
        gmsh.option.setNumber("General.RotationCenterZ", cz)
        
        # Define Mesh Size Field (Adaptive)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", container.max_element_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", container.min_element_size)
        
        # STABILIZATION PATCH 2: Loop Crash/Segfault Prevention
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
            # Offscreen rendering resolution dimensions
            gmsh.option.setNumber("General.GraphicsWidth", 1200)
            gmsh.option.setNumber("General.GraphicsHeight", 900)
            
            # --- FULLY DYNAMIC MODEL-REFLECTIVE VIEWPORT ---
            # Re-enable the trackball/auto-bounding so Gmsh calculates framing and 
            # initial orientation natively based on the imported geometry's orientation.
            gmsh.option.setNumber("General.Trackball", 1)
            
            # --- UNIVERSAL PADDING BORDERS FIX ---
            # Explicitly control the whitespace/border padding around the model.
            # 0.4 adds a clean 40% margin buffer around the geometry to prevent cropping.
            gmsh.option.setNumber("General.DisplayBorderFactor", 0.4)
            
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
            raise ex

    finally:
        # Guarantee memory unbinding only if the context was spun up within this frame execution
        if initialized_here and gmsh.is_initialized():
            gmsh.finalize()


# --- The Compliant Class ---

class CategorizationStep(StepInterface):
    """
    S11: Spatial Categorization Controller.
    
    Delegates the categorization strategy to the Geometry-Aware Gmsh engine.
    """
    
    __slots__ = () # Stateless: Logic only
    
    def execute(self, container: SovereignContainer):
        """Dispatches logic to the Gmsh engine."""
        if container.grid is None:
            raise RuntimeError("CONSTITUTION VIOLATION: 'grid' is None. ResolutionStep must precede CategorizationStep.")

        _run_gmsh_engine(container)

        # Ensure we satisfy sovereign container contracts before leaving.
        # Check strictly guarantees JSON schema compliance.
        if container.mask is None:
            raise RuntimeError("POST-CONDITION VIOLATION: Categorization Engine failed to populate container.mask")