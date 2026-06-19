from typing import List

class BoundaryConditionState:
    """
    State container for a single Boundary Condition.
    Preserves the nested structure defined in mesh_generator_results_schema.json.
    """
    __slots__ = ('location', 'type', 'surface_id')

    def __init__(self, location: str, type: str, surface_id: str):
        # Explicit initialization. Missing arguments will naturally raise TypeError.
        self.location = location
        self.type = type
        self.surface_id = surface_id


class GridState:
    """
    State container for the Grid Extents and Resolution.
    Preserves the nested structure defined in mesh_generator_results_schema.json.
    """
    __slots__ = (
        'x_min', 'x_max', 
        'y_min', 'y_max', 
        'z_min', 'z_max', 
        'nx', 'ny', 'nz'
    )

    def __init__(
        self, 
        x_min: float, x_max: float, 
        y_min: float, y_max: float, 
        z_min: float, z_max: float, 
        nx: int, ny: int, nz: int
    ):
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)
        self.z_min = float(z_min)
        self.z_max = float(z_max)
        
        self.nx = int(nx)
        self.ny = int(ny)
        self.nz = int(nz)


class MeshGeneratorState:
    """
    THE SOVEREIGN CONTAINER
    
    Acts as the single source of truth for all data at every stage of the pipeline.
    Union of mesh_generator_input_schema, mesh_generator_config_schema, and mesh_generator_results_schema.
    
    Strictly enforces memory efficiency via __slots__ and explicit initialization.
    No default values or convenience fallbacks are permitted.
    """
    __slots__ = (
        # --- INPUT SCHEMA PROPERTIES ---
        'step_file',
        
        # --- CONFIG SCHEMA PROPERTIES ---
        'solver_version',
        'tolerance',
        'max_element_size',
        'min_element_size',
        
        # --- RESULTS SCHEMA PROPERTIES ---
        'grid',
        'mask',
        'boundary_conditions'
    )

    def __init__(
        self,
        step_file: str,
        solver_version: str,
        tolerance: float,
        max_element_size: float,
        min_element_size: float,
        grid: GridState,
        mask: List[int],
        boundary_conditions: List[BoundaryConditionState]
    ):
        """
        Initialization is strictly deterministic. The orchestrator must explicitly 
        provide all fields. For data that is not yet computed (like the mask), 
        the orchestrator must explicitly pass an empty list (e.g., `mask=[]`).
        """
        self.step_file = str(step_file)
        
        self.solver_version = str(solver_version)
        self.tolerance = float(tolerance)
        self.max_element_size = float(max_element_size)
        self.min_element_size = float(min_element_size)
        
        # Nested structures (Preserving symmetry with JSON schemas)
        if not isinstance(grid, GridState):
            raise TypeError("CONSTITUTION VIOLATION: 'grid' must be an instance of GridState.")
        self.grid = grid
        
        if not isinstance(mask, list):
            raise TypeError("CONSTITUTION VIOLATION: 'mask' must be a List.")
        self.mask = mask
        
        if not isinstance(boundary_conditions, list):
            raise TypeError("CONSTITUTION VIOLATION: 'boundary_conditions' must be a List.")
        self.boundary_conditions = boundary_conditions