import logging

import numpy as np

from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
from src.steps.categorization import _GMSH_MESH_CACHE

# Configure module-level logger
logger = logging.getLogger(__name__)


class VoxelizationStep(StepInterface):
    """
    Grid-Centric Voxelization and Mask Generation.
    
    Handles the spatial discretization pipeline:
    - Voxelizes the pre-baked tetrahedral mesh from Layer 1 using high-performance
      AABB Bounding-Box overlap checks combined with barycentric point-in-tetrahedron math.
    - Classifies every grid cell as Solid (0), Fluid (1), or Wall (-1).
    """
    
    __slots__ = ()

    def execute(self, container: SovereignContainer):
        """
        Executes voxelization and mask generation based on grid-centric spatial analysis.
        """
        # --- Constitution Check: Dependencies must be resolved by previous steps ---
        if container.grid is None:
            error_msg = "CONSTITUTION VIOLATION: Pipeline order failure. 'grid' must be computed."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info("Starting High-Performance Voxelization and Mask Generation...")

        grid = container.grid
        tol = container.tolerance

        # Retrieve discretization factors
        dx = (grid.x_max - grid.x_min) / grid.nx
        dy = (grid.y_max - grid.y_min) / grid.ny
        dz = (grid.z_max - grid.z_min) / grid.nz

        # --- Vectorized Voxelization via Cached Mesh Data ---
        if "tets_vertices" not in _GMSH_MESH_CACHE:
            raise RuntimeError("POST-CONDITION VIOLATION: Global mesh cache missing tets_vertices matrix.")
            
        tets_vertices = _GMSH_MESH_CACHE["tets_vertices"]  # Shape (N_tets, 4, 3)
        
        # Resolve and validate barycentric tolerance from core configuration policy.
        if tol is None or tol < 0:
            error_msg = f"CONSTITUTION VIOLATION: Invalid tolerance '{tol}' provided in config. Tolerance must be >= 0."
            logger.error(error_msg)
            raise ValueError(error_msg)
        eps = tol
        logger.info(f"Barycentric constraint envelope initialized with epsilon: {eps}")

        # 1. Initialize corner inside-mask array of shape (nx+1, ny+1, nz+1)
        corner_inside = np.zeros((grid.nx + 1, grid.ny + 1, grid.nz + 1), dtype=bool)
        
        # Precompute all grid corner coordinates to avoid redundant math inside the loop
        x_coords = np.linspace(grid.x_min, grid.x_max, grid.nx + 1)
        y_coords = np.linspace(grid.y_min, grid.y_max, grid.ny + 1)
        z_coords = np.linspace(grid.z_min, grid.z_max, grid.nz + 1)
        
        logger.info("Computing spatial overlapping ranges (Axis-Aligned Bounding Box)...")
        
        # 2. Iterate through all tetrahedra to voxelize their coordinates
        for tet in tets_vertices:
            t_min = np.min(tet, axis=0)
            t_max = np.max(tet, axis=0)
            
            i_min = max(0, int(np.floor((t_min[0] - grid.x_min) / dx)))
            i_max = min(grid.nx, int(np.ceil((t_max[0] - grid.x_min) / dx)))
            
            j_min = max(0, int(np.floor((t_min[1] - grid.y_min) / dy)))
            j_max = min(grid.ny, int(np.ceil((t_max[1] - grid.y_min) / dy)))
            
            k_min = max(0, int(np.floor((t_min[2] - grid.z_min) / dz)))
            k_max = min(grid.nz, int(np.ceil((t_max[2] - grid.z_min) / dz)))
            
            A, B, C, D = tet[0], tet[1], tet[2], tet[3]
            Mat = np.column_stack([A - D, B - D, C - D])
            
            try:
                inv_Mat = np.linalg.inv(Mat)
            except np.linalg.LinAlgError:
                continue  # Skip degenerate/flat elements
            
            for i in range(i_min, i_max + 1):
                for j in range(j_min, j_max + 1):
                    for k in range(k_min, k_max + 1):
                        if corner_inside[i, j, k]:
                            continue
                        
                        P = np.array([x_coords[i], y_coords[j], z_coords[k]], dtype=np.float64)
                        bary_coords = inv_Mat.dot(P - D)
                        l1, l2, l3 = bary_coords[0], bary_coords[1], bary_coords[2]
                        l4 = 1.0 - l1 - l2 - l3
                        
                        if l1 >= -eps and l2 >= -eps and l3 >= -eps and l4 >= -eps:
                            corner_inside[i, j, k] = True

        # 3. Classify all cells using the classified corner grid
        mask = [1] * (grid.nx * grid.ny * grid.nz)
        stats = {"solid": 0, "fluid": 0, "wall": 0}
        
        for i in range(grid.nx):
            for j in range(grid.ny):
                for k in range(grid.nz):
                    corners = [
                        corner_inside[i, j, k],        corner_inside[i+1, j, k],
                        corner_inside[i, j+1, k],      corner_inside[i+1, j+1, k],
                        corner_inside[i, j, k+1],      corner_inside[i+1, j, k+1],
                        corner_inside[i, j+1, k+1],    corner_inside[i+1, j+1, k+1]
                    ]
                    
                    idx = i + grid.nx * (j + grid.ny * k)
                    
                    in_count = sum(corners)
                    if in_count == 8:
                        mask[idx] = 0
                        stats["solid"] += 1
                    elif in_count == 0:
                        mask[idx] = 1
                        stats["fluid"] += 1
                    else:
                        mask[idx] = -1
                        stats["wall"] += 1
        
        container.mask = mask
        logger.info(f"High-performance voxelization complete. Mask Stats: {stats}")