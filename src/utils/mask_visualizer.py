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
    Parses the pipeline output dictionary, reconstructs the 3D physical 
    computational lattice bounds, and saves a 3D color-coded voxel mask snapshot.
    
    This function automatically parses the 'mesh_snapshot_path' from the results
    to ensure the voxel mask chart is saved directly in the same directory context
    (e.g., data/testing-input-output/) alongside the gmsh rendering.
    
    Color Convention:
      - Fluid  (1)  -> Semi-transparent Light Blue (allows looking inside)
      - Solid  (0)  -> Opaque Grey
      - Wall   (-1) -> Opaque Dark Blue/Black
    """
    logger.info("Initializing 3D spatial voxel mask visualization render...")
    
    try:
        results = output_data.get("results", {})
        grid = results.get("grid", {})
        mask_1d = results.get("mask", [])
        mesh_snapshot_path = results.get("mesh_snapshot_path", "")
        
        if not grid or not mask_1d:
            logger.warning("Voxel visualizer skipped: 'grid' or 'mask' missing from results.")
            return

        # DYNAMIC PATH RESOLUTION: Pull directly from the Gmsh output location
        if mesh_snapshot_path:
            save_dir = os.path.dirname(os.path.abspath(mesh_snapshot_path))
        elif fallback_save_dir:
            save_dir = os.path.abspath(fallback_save_dir)
        else:
            save_dir = os.getcwd()

        # Guarantee directory existence
        os.makedirs(save_dir, exist_ok=True)

        nx, ny, nz = grid["nx"], grid["ny"], grid["nz"]
        
        # Verify array dimensional balance
        if len(mask_1d) != (nx * ny * nz):
            raise ValueError(
                f"Lattice dimension mismatch. Mask size ({len(mask_1d)}) "
                f"does not match dimensions nx*ny*nz ({nx}*{ny}*{nz}={nx*ny*nz})."
            )

        # 1. Instantiate 3D structures for matplotlib voxel rendering
        filled = np.ones((nx, ny, nz), dtype=bool)
        colors = np.empty(filled.shape, dtype=object)

        # 2. Reconstruct spatial maps using matching SSoT index mapping sequence:
        # idx = i + nx * (j + ny * k)
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    idx = i + nx * (j + ny * k)
                    state = mask_1d[idx]
                    
                    if state == 1:    # Fluid
                        # Light blue with 20% opacity to see interior structures
                        colors[i, j, k] = (0.68, 0.85, 0.90, 0.20)
                    elif state == 0:  # Solid
                        # Opaque grey
                        colors[i, j, k] = (0.50, 0.50, 0.50, 0.85)
                    elif state == -1: # Wall
                        # Deep dark blue boundary layer
                        colors[i, j, k] = (0.05, 0.05, 0.20, 0.95)
                    else:
                        # Fallback unassigned
                        colors[i, j, k] = (1.00, 1.00, 1.00, 0.00)

        # 3. Generate physical coordinate edge boundaries for true-scale plotting
        x_edges = np.linspace(grid["x_min"], grid["x_max"], nx + 1)
        y_edges = np.linspace(grid["y_min"], grid["y_max"], ny + 1)
        z_edges = np.linspace(grid["z_min"], grid["z_max"], nz + 1)
        
        X, Y, Z = np.meshgrid(x_edges, y_edges, z_edges, indexing='ij')

        # 4. Initialize Plot Canvas
        fig = plt.figure(figsize=(10, 8), dpi=150)
        ax = fig.add_subplot(111, projection='3d')
        
        # Apply standard fixed perspective angles matching your setup
        ax.view_init(elev=15, azim=30)

        # 5. Render Voxel Grid
        ax.voxels(X, Y, Z, filled, facecolors=colors, edgecolors=(0.3, 0.3, 0.3, 0.15), linewidth=0.5)

        # Label definitions and geometric bounds
        ax.set_title("Voxelization Grid Mask Classification Map", fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel("X Axis Dimension", fontsize=9)
        ax.set_ylabel("Y Axis Dimension", fontsize=9)
        ax.set_zlabel("Z Axis Dimension", fontsize=9)
        
        # 6. Construct Custom Legend Context
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=(0.68, 0.85, 0.90, 0.6), edgecolor='gray', label='Fluid (1) - Translucent'),
            Patch(facecolor=(0.50, 0.50, 0.50, 0.9), edgecolor='gray', label='Solid (0)'),
            Patch(facecolor=(0.05, 0.05, 0.20, 0.9), edgecolor='gray', label='Wall (-1)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))

        # 7. Flush Framebuffer and write directly to destination directory context
        destination_path = os.path.join(save_dir, "voxel_mask_verification.png")
        plt.savefig(destination_path, bbox_inches='tight', dpi=150)
        plt.close(fig)
        
        logger.info(f"Voxel mask visual verification chart successfully saved: {destination_path}")
        
    except Exception as e:
        logger.error(f"Non-blocking visualization capture routine failure: {str(e)}")