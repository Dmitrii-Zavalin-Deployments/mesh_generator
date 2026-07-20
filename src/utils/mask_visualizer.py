import os
import logging
import numpy as np
import matplotlib
# Force headless rendering backend to prevent X11 display connection errors
matplotlib.use('Agg')
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def generate_mask_snapshot(output_data: dict, fallback_save_dir: str = None):
    """
    Parses the pipeline output dictionary and saves a 3D voxel mask snapshot.
    
    Optimizations implemented to prevent GitHub Actions CI timeouts:
      1. Hard-capped maximum axes limits to protect rendering workflows.
      2. Spatial grid striding (downsampling) to keep total voxel count manageable.
      3. Full-render visualization (showing Fluid, Solid, and Walls) with 
         transparency to ensure interior features like holes remain visible.
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
        mask_3d = np.array(mask_1d, dtype=np.int8).reshape((nx, ny, nz), order='F')

        total_voxels = nx * ny * nz
        if total_voxels > 1_000_000 or nx > MAX_AXIS_CEILING or ny > MAX_AXIS_CEILING or nz > MAX_AXIS_CEILING:
            stride = 4 if total_voxels > 1_000_000 else 2
            logger.info(f"Applying spatial stride = {stride} for CI stability.")
            mask_3d = mask_3d[::stride, ::stride, ::stride]
            nx, ny, nz = mask_3d.shape

        # --- VISUALIZATION MAPPING ---
        # Render everything (Fluid, Solid, Wall) so the hole remains visible.
        # We use alpha transparency on the fluid to allow "looking into" the object.
        filled = (mask_3d != 999) # Fill all voxels
        
        colors = np.zeros((nx, ny, nz, 4))
        # Fluid (1): Light Blue, high transparency
        colors[mask_3d == 1] = [0.68, 0.85, 0.90, 0.20] 
        # Solid (0): Grey, opaque
        colors[mask_3d == 0] = [0.50, 0.50, 0.50, 0.80] 
        # Wall (-1): Dark Blue, solid
        colors[mask_3d == -1] = [0.05, 0.05, 0.20, 0.95] 

        # Generate coordinate edges
        x_edges = np.linspace(grid["x_min"], grid["x_max"], nx + 1)
        y_edges = np.linspace(grid["y_min"], grid["y_max"], ny + 1)
        z_edges = np.linspace(grid["z_min"], grid["z_max"], nz + 1)
        X, Y, Z = np.meshgrid(x_edges, y_edges, z_edges, indexing='ij')

        # Initialize Plot
        fig = plt.figure(figsize=(10, 8), dpi=150)
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=15, azim=30)

        # Render Voxel Grid
        ax.voxels(X, Y, Z, filled, facecolors=colors, edgecolors=(0.3, 0.3, 0.3, 0.1), linewidth=0.2)

        # Label definitions and geometric bounds
        ax.set_title("Voxelization Grid Mask Boundary Map (CI Optimized)", fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel("X Axis Dimension", fontsize=9)
        ax.set_ylabel("Y Axis Dimension", fontsize=9)
        ax.set_zlabel("Z Axis Dimension", fontsize=9)
        
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
        
    except Exception as e:
        logger.error(f"Visualization failure: {str(e)}")