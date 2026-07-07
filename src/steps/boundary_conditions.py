import logging
import numpy as np
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer, BoundaryConditionState

# Configure module-level logger
logger = logging.getLogger(__name__)

class BoundaryConditionsStep(StepInterface):
    """
    S12: Grid-Centric Boundary Condition Mapping.
    
    Handles Layer 2 of the Meshing Pipeline:
    - Voxelizes the pre-baked tetrahedral mesh from Layer 1 using high-performance
      AABB Bounding-Box overlap checks combined with barycentric point-in-tetrahedron math.
    - Classifies every grid cell as Solid (0), Fluid (1), or Wall (-1).
    - Maps the boundary conditions of interface cells (mask == -1) to respective physical faces.
    """
    
    __slots__ = ()

    def execute(self, container: SovereignContainer):
        """
        Executes boundary mapping based on grid-centric spatial analysis.
        """
        # --- Constitution Check: Dependencies must be resolved by previous steps ---
        if container.grid is None or container.mask is None:
            error_msg = "CONSTITUTION VIOLATION: Pipeline order failure. 'grid' and 'mask' must be computed."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info("Starting Boundary Condition Mapping (Layer 2: High-Performance Voxelization)...")

        grid = container.grid
        bc_map = container.bc_map 
        tol = container.tolerance

        # Retrieve discretization factors
        dx = (grid.x_max - grid.x_min) / grid.nx
        dy = (grid.y_max - grid.y_min) / grid.ny
        dz = (grid.z_max - grid.z_min) / grid.nz

        # --- Layer 2: Vectorized Voxelization via Cached Mesh Data ---
        if container.use_gmsh:
            from src.steps.categorization import _GMSH_MESH_CACHE
            
            if "tets_vertices" not in _GMSH_MESH_CACHE:
                raise RuntimeError("POST-CONDITION VIOLATION: Global mesh cache missing tets_vertices matrix.")
                
            tets_vertices = _GMSH_MESH_CACHE["tets_vertices"]  # Shape (N_tets, 4, 3)
            
            # Resolve and validate barycentric tolerance from core configuration policy.
            # Strict enforcement: tolerance must be defined and >= 0.
            if tol is None or tol < 0:
                error_msg = f"CONSTITUTION VIOLATION: Invalid tolerance '{tol}' provided in config. Tolerance must be >= 0."
                logger.error(error_msg)
                raise ValueError(error_msg)
            eps = tol
            logger.info(f"Barycentric constraint envelope initialized with epsilon: {eps}")

            # 1. Initialize corner inside-mask array of shape (nx+1, ny+1, nz+1)
            # True indicates that the vertex point lies inside the solid domain geometry.
            corner_inside = np.zeros((grid.nx + 1, grid.ny + 1, grid.nz + 1), dtype=bool)
            
            # Precompute all grid corner coordinates to avoid redundant math inside the loop
            x_coords = np.linspace(grid.x_min, grid.x_max, grid.nx + 1)
            y_coords = np.linspace(grid.y_min, grid.y_max, grid.ny + 1)
            z_coords = np.linspace(grid.z_min, grid.z_max, grid.nz + 1)
            
            logger.info("Computing spatial overlapping ranges (Axis-Aligned Bounding Box)...")
            
            # 2. Iterate through all tetrahedra to voxelize their coordinates
            for tet in tets_vertices:
                # Find the AABB bounds of the current tetrahedron
                t_min = np.min(tet, axis=0)
                t_max = np.max(tet, axis=0)
                
                # Map coordinate bounds directly to grid corner indices
                i_min = max(0, int(np.floor((t_min[0] - grid.x_min) / dx)))
                i_max = min(grid.nx, int(np.ceil((t_max[0] - grid.x_min) / dx)))
                
                j_min = max(0, int(np.floor((t_min[1] - grid.y_min) / dy)))
                j_max = min(grid.ny, int(np.ceil((t_max[1] - grid.y_min) / dy)))
                
                k_min = max(0, int(np.floor((t_min[2] - grid.z_min) / dz)))
                k_max = min(grid.nz, int(np.ceil((t_max[2] - grid.z_min) / dz)))
                
                # Set up local barycentric solver coefficients
                # Vertices of the tetrahedron: A, B, C, D
                A, B, C, D = tet[0], tet[1], tet[2], tet[3]
                Mat = np.column_stack([A - D, B - D, C - D])
                
                try:
                    inv_Mat = np.linalg.inv(Mat)
                except np.linalg.LinAlgError:
                    continue  # Skip degenerate/flat elements
                
                # Check each grid corner inside the tetrahedron's bounding box
                for i in range(i_min, i_max + 1):
                    for j in range(j_min, j_max + 1):
                        for k in range(k_min, k_max + 1):
                            if corner_inside[i, j, k]:
                                continue  # Already classified as inside
                                
                            # Convert index to physical coordinate
                            P = np.array([x_coords[i], y_coords[j], z_coords[k]], dtype=np.float64)
                            
                            # Solve for barycentric coordinates
                            # l = inv_Mat * (P - D)
                            bary_coords = inv_Mat.dot(P - D)
                            l1, l2, l3 = bary_coords[0], bary_coords[1], bary_coords[2]
                            l4 = 1.0 - l1 - l2 - l3
                            
                            # Point is inside if all barycentric coordinates match the validated policy boundary
                            if l1 >= -eps and l2 >= -eps and l3 >= -eps and l4 >= -eps:
                                corner_inside[i, j, k] = True

            # 3. Classify all cells using the classified corner grid
            mask = [1] * (grid.nx * grid.ny * grid.nz)
            stats = {"solid": 0, "fluid": 0, "wall": 0}
            
            for i in range(grid.nx):
                for j in range(grid.ny):
                    for k in range(grid.nz):
                        # Extract the 8 corners of the current voxel cell
                        corners = [
                            corner_inside[i, j, k],         corner_inside[i+1, j, k],
                            corner_inside[i, j+1, k],       corner_inside[i+1, j+1, k],
                            corner_inside[i, j, k+1],         corner_inside[i+1, j, k+1],
                            corner_inside[i, j+1, k+1],       corner_inside[i+1, j+1, k+1]
                        ]
                        
                        idx = i + grid.nx * (j + grid.ny * k)
                        
                        # Apply physical classification:
                        # 1. Solid: All 8 corners are inside
                        # 2. Fluid: All 8 corners are outside
                        # 3. Wall (Interface): Mixed corners
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
        else:
            # Voxelizer fallback (Legacy branch has already populated container.mask)
            mask = container.mask

        bcs = []
        
        # --- Domain Traversal for Boundary Condition Mapping ---
        # Maps identified interface cells (mask == -1) to specific boundary conditions
        for i in range(grid.nx):
            for j in range(grid.ny):
                for k in range(grid.nz):
                    idx = i + grid.nx * (j + grid.ny * k)
                    
                    # We only care about interface cells (mask == -1)
                    if mask[idx] != -1:
                        continue
                    
                    # --- Voxel Extent Calculation ---
                    vx_min, vx_max = grid.x_min + i * dx, grid.x_min + (i + 1) * dx
                    vy_min, vy_max = grid.y_min + j * dy, grid.y_min + (j + 1) * dy
                    vz_min, vz_max = grid.z_min + k * dz, grid.z_min + (k + 1) * dz
                    
                    # --- Boundary Intersection Detection ---
                    location = "wall" 
                    if abs(vx_min - grid.x_min) < tol:
                        location = "x_min"
                    elif abs(vx_max - grid.x_max) < tol:
                        location = "x_max"
                    elif abs(vy_min - grid.y_min) < tol:
                        location = "y_min"
                    elif abs(vy_max - grid.y_max) < tol:
                        location = "y_max"
                    elif abs(vz_min - grid.z_min) < tol:
                        location = "z_min"
                    elif abs(vz_max - grid.z_max) < tol:
                        location = "z_max"
                    
                    # --- Physical Condition Assignment ---
                    if location not in bc_map:
                        error_msg = f"CONSTITUTION VIOLATION: Boundary location '{location}' detected but not defined in 'bc_map'."
                        logger.error(error_msg)
                        raise KeyError(error_msg)
                    
                    bc_type = bc_map[location]
                    
                    # --- State Registration ---
                    bcs.append(BoundaryConditionState(
                        location=location,
                        type=bc_type,
                        surface_id=f"cell_{idx}"
                    ))
                    
        # Persistence: Container setter validates the final list structure
        container.boundary_conditions = bcs
        logger.info(f"Mapping complete. Identified {len(bcs)} boundary conditions.")