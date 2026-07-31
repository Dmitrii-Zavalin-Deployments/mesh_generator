# src/utils/mask_visualizer.py
import logging
import os

import matplotlib
import numpy as np

# Force headless rendering backend to prevent X11 display connection errors
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

logger = logging.getLogger(__name__)


def generate_mask_snapshot(
    output_data: dict, 
    fallback_save_dir: str | None = None, 
    elev: float = 35.264, 
    azim: float = -45.0
):
    """
    Parses the pipeline output dictionary and saves a 3D voxel mask snapshot.
    
    Optimizations implemented to prevent GitHub Actions CI timeouts:
      1. Hard-capped maximum axes limits to protect rendering workflows.
      2. Spatial grid striding (downsampling) to keep total voxel count manageable.
      3. Standard native (X, Y, Z) mapping and explicit box aspect ratios to 
         align Matplotlib outputs directly with the true domain coordinate space.
    """
    logger.info("Initializing optimized 3D voxel mask visualization...")
    
    try:
        results = output_data.get("results", {})
        grid = results.get("grid", {})
        mask_1d = results.get("mask", [])
        mesh_snapshot_path = results.get("mesh_snapshot_path", "")
        
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
        mask_3d = np.array(mask_1d, dtype=np.int32).reshape((nx, ny, nz), order='F')

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

    except (ValueError, TypeError, RuntimeError, OSError, IndexError, KeyError, AttributeError) as e:
        error_msg = str(e)
        if "reshape" in error_msg:
            logger.error(f"Lattice dimension mismatch: {error_msg}")
        elif "timeout" in error_msg:
            logger.error(f"Non-blocking visualization capture routine failure: {error_msg}")
        else:
            logger.error(f"Visualization failure: {error_msg}")