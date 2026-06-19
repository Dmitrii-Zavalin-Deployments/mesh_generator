# src/steps/boundary_conditions.py
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer, BoundaryConditionState

class BoundaryConditionsStep(StepInterface):
    """
    S12: Grid-Centric Boundary Condition Mapping.
    
    This step performs the final spatial classification of the grid. By iterating 
    over the discrete mask, it identifies 'interface' cells (mask == -1) and 
    maps them to specific boundary conditions (BCs) based on their spatial 
    proximity to the domain extremities.
    """
    
    __slots__ = () # Stateless: Logic only; strictly follows the constitutional template.

    def execute(self, container: SovereignContainer):
        """
        Executes boundary mapping based on grid-centric spatial analysis.
        
        Governance:
        - Validation: Ensures mandatory state fields (grid, mask) are present.
        - Mapping: Uses centroid projection to classify boundary locations.
        - Configuration: Dynamically assigns BC types from the 'bc_map' config.
        """
        # --- Constitution Check: Dependencies must be resolved by previous steps ---
        if container.grid is None or container.mask is None:
            raise RuntimeError(
                "CONSTITUTION VIOLATION: Pipeline order failure. "
                "'grid' and 'mask' must be computed before BoundaryConditionsStep."
            )

        grid = container.grid
        mask = container.mask
        tol = container.tolerance # User-defined geometric tolerance
        bc_map = container.bc_map # Configuration-defined BC lookup table

        bcs = []
        
        # --- Spatial Discretization Factors ---
        # Used to project the voxel index into coordinate space for boundary detection.
        dx = (grid.x_max - grid.x_min) / grid.nx
        dy = (grid.y_max - grid.y_min) / grid.ny
        dz = (grid.z_max - grid.z_min) / grid.nz

        # --- Domain Traversal ---
        # Iterate over every voxel index (i, j, k) to inspect classification status.
        for i in range(grid.nx):
            for j in range(grid.ny):
                for k in range(grid.nz):
                    idx = i + grid.nx * (j + grid.ny * k)
                    
                    # --- Conservative Voxel Filtering ---
                    # We only care about interface cells (mask == -1) where the
                    # geometry boundary resides. Fluid (1) and Solid (0) are ignored.
                    if mask[idx] != -1:
                        continue
                    
                    # --- Voxel Extent Calculation ---
                    # Calculate the physical bounds of the current voxel to accurately 
                    # check for alignment with domain boundaries.
                    vx_min, vx_max = grid.x_min + i * dx, grid.x_min + (i + 1) * dx
                    vy_min, vy_max = grid.y_min + j * dy, grid.y_min + (j + 1) * dy
                    vz_min, vz_max = grid.z_min + k * dz, grid.z_min + (k + 1) * dz
                    
                    # --- Boundary Intersection Detection ---
                    # Check if the voxel's faces coincide with the grid domain boundaries
                    # within the permitted geometric tolerance (tol).
                    location = "wall" # Default classification for interior interfaces
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
                    # Enforce explicit configuration: Every detected location must 
                    # be defined in the bc_map. If a location is missing, we raise 
                    # a configuration error to prevent silent simulation failure.
                    if location not in bc_map:
                        raise KeyError(
                            f"CONSTITUTION VIOLATION: Boundary location '{location}' "
                            "detected but not defined in 'bc_map' configuration."
                        )
                    
                    bc_type = bc_map[location]
                    
                    # --- State Registration ---
                    # Assign the cell index as the unique identifier to ensure 
                    # solver-side lookup consistency.
                    bcs.append(BoundaryConditionState(
                        location=location,
                        type=bc_type,
                        surface_id=f"cell_{idx}"
                    ))
                    
        # Persistence: Container setter validates the final list structure
        container.boundary_conditions = bcs