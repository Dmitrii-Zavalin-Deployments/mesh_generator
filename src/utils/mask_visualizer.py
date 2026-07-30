# src/utils/mask_visualizer.py
import logging
import os

import matplotlib
import numpy as np

# Force headless rendering backend to prevent X11 display connection errors
matplotlib.use('Agg')
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def generate_mask_snapshot(
    output_data: dict, 
    fallback_save_dir: str | None = None, 
    elev: float = 35.264, 
    azim: float = -45.0
):
    """
    Parses the pipeline output dictionary and saves a 3D voxel mask snapshot.
    Also extracts and saves a perfectly aligned snapshot of the raw STEP geometry if available.
    
    Optimizations implemented to prevent GitHub Actions CI timeouts:
      1. Hard-capped maximum axes limits to protect rendering workflows.
      2. Spatial grid striding (downsampling) to keep total voxel count manageable.
      3. Dynamic deflection mesh sizing based on physical bounding box scale.
      4. Standard native (X, Y, Z) mapping and explicit box aspect ratios to 
         align Matplotlib outputs directly with the true STEP file coordinate space.
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

        # --- NATIVE AXIS MAPPING ---
        mask_3d_vis = mask_3d
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

        # Generate coordinate edges matching native (X, Y, Z) CAD geometry
        x_edges = np.linspace(grid["x_min"], grid["x_max"], nx_vis + 1)
        y_edges = np.linspace(grid["y_min"], grid["y_max"], ny_vis + 1)
        z_edges = np.linspace(grid["z_min"], grid["z_max"], nz_vis + 1)
        X, Y, Z = np.meshgrid(x_edges, y_edges, z_edges, indexing='ij')

        # Compute dynamic bounding box spans
        x_span = grid["x_max"] - grid["x_min"]
        y_span = grid["y_max"] - grid["y_min"]
        z_span = grid["z_max"] - grid["z_min"]
        max_span = max(x_span, y_span, z_span)

        # Initialize Voxel Plot
        fig = plt.figure(figsize=(10, 8), dpi=150)
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=elev, azim=azim)

        # Render Voxel Grid
        ax.voxels(X, Y, Z, filled, facecolors=colors, edgecolors=(0.3, 0.3, 0.3, 0.1), linewidth=0.2)

        # Enforce unified absolute scale boundaries directly from STEP coordinate bounds
        ax.set_xlim(grid["x_min"], grid["x_max"])
        ax.set_ylim(grid["y_min"], grid["y_max"])
        ax.set_zlim(grid["z_min"], grid["z_max"])
        
        # Explicitly apply true bounding box aspect ratio to enforce 1:1 spatial proportion
        ax.set_box_aspect((x_span, y_span, z_span))

        # Native label definitions matching CAD world coordinate frame
        ax.set_title("Voxelization Grid Mask Boundary Map (CI Optimized)", fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel("X Axis (CAD X)", fontsize=9)
        ax.set_ylabel("Y Axis (CAD Y)", fontsize=9)
        ax.set_zlabel("Z Axis (CAD Z)", fontsize=9)
        
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
        # Only attempt OCC extraction if cad_solid is a valid TopoDS_Shape object (not a string backend marker)
        if cad_solid is not None and not isinstance(cad_solid, str):
            try:
                from mpl_toolkits.mplot3d.art3d import Poly3DCollection
                from OCC.Core.BRep import BRep_Tool
                from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
                from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
                from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
                from OCC.Core.TopExp import TopExp_Explorer
                from OCC.Core.TopLoc import TopLoc_Location

                logger.info("Extracting CAD boundary surfaces for aligned visualization...")

                # DYNAMIC DEFLECTION SCALE: Adapt mesh deflection based on model scale (0.5% of max span)
                dynamic_deflection = max(0.001, 0.005 * max_span)
                BRepMesh_IncrementalMesh(cad_solid, dynamic_deflection)

                explorer_face = TopExp_Explorer(cad_solid, TopAbs_FACE)
                polygons = []

                while explorer_face.More():
                    face = explorer_face.Current()
                    explorer_face.Next()

                    loc = TopLoc_Location()
                    triangulation = BRep_Tool.Triangulation(face, loc)
                    if triangulation:
                        trsf = loc.Transformation()

                        nodes = triangulation.Nodes()
                        triangles = triangulation.Triangles()

                        for i in range(1, triangulation.NbTriangles() + 1):
                            tri = triangles.Value(i)
                            idx1, idx2, idx3 = tri.Get()

                            p1 = nodes.Value(idx1).Transformed(trsf)
                            p2 = nodes.Value(idx2).Transformed(trsf)
                            p3 = nodes.Value(idx3).Transformed(trsf)

                            polygons.append([
                                [p1.X(), p1.Y(), p1.Z()],
                                [p2.X(), p2.Y(), p2.Z()],
                                [p3.X(), p3.Y(), p3.Z()]
                            ])

                if polygons:
                    fig_cad = plt.figure(figsize=(10, 8), dpi=150)
                    ax_cad = fig_cad.add_subplot(111, projection='3d')
                    ax_cad.view_init(elev=elev, azim=azim)

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
                        trsf_edge = loc_edge.Transformation()

                        u_samples = np.linspace(first_param, last_param, 50)
                        x_pts, y_pts, z_pts = [], [], []

                        for u in u_samples:
                            pt = curve.Value(u).Transformed(trsf_edge)
                            x_pts.append(pt.X())
                            y_pts.append(pt.Y())
                            z_pts.append(pt.Z())

                        ax_cad.plot(x_pts, y_pts, z_pts, color='blue', linewidth=1.2)

                    ax_cad.set_xlim(grid["x_min"], grid["x_max"])
                    ax_cad.set_ylim(grid["y_min"], grid["y_max"])
                    ax_cad.set_zlim(grid["z_min"], grid["z_max"])
                    ax_cad.set_box_aspect((x_span, y_span, z_span))

                    ax_cad.set_title("CAD Structural Geometry Verification (STEP Native)",
                                    fontsize=12, fontweight='bold', pad=15)
                    ax_cad.set_xlabel("X Axis (CAD X)", fontsize=9)
                    ax_cad.set_ylabel("Y Axis (CAD Y)", fontsize=9)
                    ax_cad.set_zlabel("Z Axis (CAD Z)", fontsize=9)

                    cad_img_path = os.path.join(save_dir, "cad_geometry_snapshot.png")
                    plt.savefig(cad_img_path, bbox_inches='tight', pad_inches=0.3, dpi=150)
                    plt.close(fig_cad)
                    logger.info(f"CAD geometry snapshot successfully rendered: {cad_img_path}")

            except Exception as cad_err:
                logger.warning(f"Headless CAD boundary line parsing rendering skipped or unavailable: {cad_err!s}")

    except Exception as e:
        error_msg = str(e)
        if "reshape" in error_msg:
            logger.error(f"Lattice dimension mismatch: {error_msg}")
        elif "timeout" in error_msg:
            logger.error(f"Non-blocking visualization capture routine failure: {error_msg}")
        else:
            logger.error(f"Visualization failure: {error_msg}")