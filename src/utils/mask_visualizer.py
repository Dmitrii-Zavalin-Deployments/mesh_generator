# src/utils/mask_visualizer.py
import os
import logging
import numpy as np
import matplotlib
# Force headless rendering backend to prevent X11 display connection errors
matplotlib.use('Agg')
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# --- UNIFIED VIEWPOINT CONSTANTS ---
# Standardizes the isometric viewpoint across all visualization engines
VIEW_ELEV = 30
VIEW_AZIM = -60

def generate_mask_snapshot(output_data: dict, fallback_save_dir: str = None):
    """
    Parses the pipeline output dictionary and saves a 3D voxel mask snapshot.
    Also extracts and saves a perfectly aligned snapshot of the raw STEP geometry.
    
    Optimizations implemented to prevent GitHub Actions CI timeouts:
      1. Hard-capped maximum axes limits to protect rendering workflows.
      2. Spatial grid striding (downsampling) to keep total voxel count manageable.
      3. Full-render visualization (showing Fluid, Solid, and Walls) with 
         transparency to ensure interior features like holes remain visible.
      4. Axes re-mapping and explicit box aspect ratios to perfectly align 
         Matplotlib outputs with standard CAD/Mesh orientations.
    """
    logger.info("Initializing optimized 3D voxel mask visualization...")
    
    try:
        results = output_data.get("results", {})
        grid = results.get("grid", {})
        mask_1d = results.get("mask", [])
        mesh_snapshot_path = results.get("mesh_snapshot_path", "")
        cad_solid = output_data.get("cad_solid") or results.get("cad_solid")
        
        if not grid or not mask_1d:
            logger.warning("Voxel visualizer skipped: 'grid' or 'mask' missing.")
            return

        # DYNAMIC PATH RESOLUTION
        if mesh_snapshot_path:
            save_dir = os.path.dirname(os.path.abspath(mesh_snapshot_path))
        elif fallback_save_dir:
            save_dir = os.path.abspath(fallback_save_dir)
        else:
            save_dir = os.getcwd()

        os.makedirs(save_dir, exist_ok=True)

        nx, ny, nz = grid["nx"], grid["ny"], grid["nz"]
        
        # --- OPTIMIZATION: SAFETY CEILING & STRIDING ---
        MAX_AXIS_CEILING = 150
        mask_3d = np.array(mask_1d, dtype=np.int8).reshape((nx, ny, nz), order='F')

        total_voxels = nx * ny * nz
        if total_voxels > 1_000_000 or nx > MAX_AXIS_CEILING or ny > MAX_AXIS_CEILING or nz > MAX_AXIS_CEILING:
            stride = 4 if total_voxels > 1_000_000 else 2
            logger.info(f"Applying spatial stride = {stride} for CI stability.")
            mask_3d = mask_3d[::stride, ::stride, ::stride]
            nx, ny, nz = mask_3d.shape

        # --- AXIS ORIENTATION ALIGNMENT ---
        # To align perfectly with the CAD viewer convention (where the hole axis CAD Y is vertical),
        # we map: Visual X = CAD X, Visual Y = CAD Z, Visual Z = CAD Y.
        mask_3d_vis = np.transpose(mask_3d, (0, 2, 1))  # Swap Y and Z axes
        nx_vis, ny_vis, nz_vis = mask_3d_vis.shape

        # --- VISUALIZATION MAPPING ---
        filled = (mask_3d_vis != 999) # Fill all active voxels
        
        colors = np.zeros((nx_vis, ny_vis, nz_vis, 4))
        # Fluid (1): Light Blue, high transparency
        colors[mask_3d_vis == 1] = [0.68, 0.85, 0.90, 0.20] 
        # Solid (0): Grey, opaque
        colors[mask_3d_vis == 0] = [0.50, 0.50, 0.50, 0.80] 
        # Wall (-1): Dark Blue, solid
        colors[mask_3d_vis == -1] = [0.05, 0.05, 0.20, 0.95] 

        # Generate coordinate edges matching the visual transposition
        x_edges = np.linspace(grid["x_min"], grid["x_max"], nx_vis + 1)
        y_edges = np.linspace(grid["z_min"], grid["z_max"], ny_vis + 1)  # Visual Y maps to CAD Z
        z_edges = np.linspace(grid["y_min"], grid["y_max"], nz_vis + 1)  # Visual Z maps to CAD Y
        X, Y, Z = np.meshgrid(x_edges, y_edges, z_edges, indexing='ij')

        # Compute uniform spans to lock exact proportional aspect ratio across both plots
        x_span = grid["x_max"] - grid["x_min"]
        y_span = grid["z_max"] - grid["z_min"]
        z_span = grid["y_max"] - grid["y_min"]

        # Initialize Voxel Plot
        fig = plt.figure(figsize=(10, 8), dpi=150)
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=VIEW_ELEV, azim=VIEW_AZIM)

        # Render Voxel Grid
        ax.voxels(X, Y, Z, filled, facecolors=colors, edgecolors=(0.3, 0.3, 0.3, 0.1), linewidth=0.2)

        # Enforce unified absolute scale boundaries matching the coordinate swap
        ax.set_xlim(grid["x_min"], grid["x_max"])
        ax.set_ylim(grid["z_min"], grid["z_max"])
        ax.set_zlim(grid["y_min"], grid["y_max"])
        
        # Explicitly apply bounding box aspect ratio to enforce matching pitch/roll/yaw appearance
        ax.set_box_aspect((x_span, y_span, z_span))

        # Label definitions matching spatial reassignment
        ax.set_title("Voxelization Grid Mask Boundary Map (CI Optimized)", fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel("X Axis (CAD X)", fontsize=9)
        ax.set_ylabel("Z Axis (CAD Z)", fontsize=9)
        ax.set_zlabel("Y Axis (CAD Y)", fontsize=9)
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=(0.68, 0.85, 0.90, 0.6), edgecolor='gray', label='Fluid (1)'),
            Patch(facecolor=(0.50, 0.50, 0.50, 0.9), edgecolor='gray', label='Solid (0)'),
            Patch(facecolor=(0.05, 0.05, 0.20, 0.9), edgecolor='gray', label='Wall (-1)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))

        destination_path = os.path.join(save_dir, "voxel_mask_verification.png")
        plt.savefig(destination_path, bbox_inches='tight', pad_inches=0.3, dpi=150)
        plt.close(fig)
        logger.info(f"Voxel verification chart saved: {destination_path}")

        # --- CLEAN NATIVE STEP CAD SNAPSHOT GENERATION ---
        if cad_solid is not None:
            try:
                from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
                from OCC.Core.TopExp import TopExp_Explorer
                from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE
                from OCC.Core.BRep import BRep_Tool
                from OCC.Core.TopLoc import TopLoc_Location
                from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
                from mpl_toolkits.mplot3d.art3d import Poly3DCollection

                logger.info("Extracting CAD boundary surfaces for aligned visualization...")

                BRepMesh_IncrementalMesh(cad_solid, 0.5)

                explorer_face = TopExp_Explorer(cad_solid, TopAbs_FACE)
                polygons = []

                while explorer_face.More():
                    face = explorer_face.Current()
                    explorer_face.Next()

                    loc = TopLoc_Location()
                    triangulation = BRep_Tool.Triangulation(face, loc)
                    if triangulation:
                        trsf = loc.Transformation()   # <-- REQUIRED FIX

                        nodes = triangulation.Nodes()
                        triangles = triangulation.Triangles()

                        for i in range(1, triangulation.NbTriangles() + 1):
                            tri = triangles.Value(i)
                            idx1, idx2, idx3 = tri.Get()

                            p1 = nodes.Value(idx1).Transformed(trsf)   # <-- FIX
                            p2 = nodes.Value(idx2).Transformed(trsf)   # <-- FIX
                            p3 = nodes.Value(idx3).Transformed(trsf)   # <-- FIX

                            polygons.append([
                                [p1.X(), p1.Z(), p1.Y()],
                                [p2.X(), p2.Z(), p2.Y()],
                                [p3.X(), p3.Z(), p3.Y()]
                            ])

                if polygons:
                    fig_cad = plt.figure(figsize=(10, 8), dpi=150)
                    ax_cad = fig_cad.add_subplot(111, projection='3d')
                    ax_cad.view_init(elev=VIEW_ELEV, azim=VIEW_AZIM)

                    poly_collection = Poly3DCollection(polygons, facecolors='lightgray',
                                                    edgecolors='none', alpha=0.5)
                    ax_cad.add_collection3d(poly_collection)

                    explorer_edge = TopExp_Explorer(cad_solid, TopAbs_EDGE)
                    while explorer_edge.More():
                        edge = explorer_edge.Current()
                        explorer_edge.Next()

                        curve = BRepAdaptor_Curve(edge)
                        first_param = curve.FirstParameter()
                        last_param = curve.LastParameter()

                        loc_edge = edge.Location()
                        trsf_edge = loc_edge.Transformation()   # <-- REQUIRED FIX

                        u_samples = np.linspace(first_param, last_param, 50)
                        x_pts, y_pts, z_pts = [], [], []

                        for u in u_samples:
                            pt = curve.Value(u).Transformed(trsf_edge)   # <-- FIX

                            x_pts.append(pt.X())
                            y_pts.append(pt.Z())
                            z_pts.append(pt.Y())

                        ax_cad.plot(x_pts, y_pts, z_pts, color='blue', linewidth=1.2)

                    ax_cad.set_xlim(grid["x_min"], grid["x_max"])
                    ax_cad.set_ylim(grid["z_min"], grid["z_max"])
                    ax_cad.set_zlim(grid["y_min"], grid["y_max"])
                    ax_cad.set_box_aspect((x_span, y_span, z_span))

                    ax_cad.set_title("CAD Structural Geometry Verification (STEP Native)",
                                    fontsize=12, fontweight='bold', pad=15)
                    ax_cad.set_xlabel("X Axis (CAD X)", fontsize=9)
                    ax_cad.set_ylabel("Z Axis (CAD Z)", fontsize=9)
                    ax_cad.set_zlabel("Y Axis (CAD Y)", fontsize=9)

                    cad_img_path = os.path.join(save_dir, "cad_geometry_snapshot.png")
                    plt.savefig(cad_img_path, bbox_inches='tight', pad_inches=0.3, dpi=150)
                    plt.close(fig_cad)
                    logger.info(f"CAD geometry snapshot successfully rendered: {cad_img_path}")

            except Exception as cad_err:
                logger.warning(f"Headless CAD boundary line parsing rendering skipped or unavailable: {str(cad_err)}")

    except Exception as e:
        error_msg = str(e)
        if "reshape" in error_msg:
            logger.error(f"Lattice dimension mismatch: {error_msg}")
        elif "timeout" in error_msg:
            logger.error(f"Non-blocking visualization capture routine failure: {error_msg}")
        else:
            logger.error(f"Visualization failure: {error_msg}")