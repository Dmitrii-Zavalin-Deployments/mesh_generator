class BoundaryConditionState:
    """
    State container for a single Boundary Condition.
    Preserves the nested structure defined in mesh_generator_results_schema.json.
    """
    __slots__ = ('location', 'surface_id', 'type')

    def __init__(self, location: str, type: str, surface_id: str):
        self.location = str(location)
        self.type = str(type)
        self.surface_id = str(surface_id)


class GridState:
    """
    State container for the Grid Extents and Resolution.
    Compatible with Gmsh unstructured grids and virtual resolutions.
    """
    __slots__ = ('nx', 'ny', 'nz', 'x_max', 'x_min', 'y_max', 'y_min', 'z_max', 'z_min')
    
    def __init__(self, x_min: float, x_max: float, y_min: float, y_max: float, z_min: float, z_max: float, nx: int, ny: int, nz: int):
        self.x_min, self.x_max = float(x_min), float(x_max)
        self.y_min, self.y_max = float(y_min), float(y_max)
        self.z_min, self.z_max = float(z_min), float(z_max)
        self.nx, self.ny, self.nz = int(nx), int(ny), int(nz)


class SovereignContainer:
    """
    THE SOVEREIGN CONTAINER
    
    Acts as the single source of truth for all data at every stage of the pipeline.
    Union of mesh_generator_input_schema, mesh_generator_config_schema, and mesh_generator_results_schema.
    
    Strictly enforces memory efficiency via __slots__ and explicit initialization.
    No default values or convenience fallbacks are permitted.
    """
    __slots__ = (
        '_bbox',
        '_boundary_conditions',
        '_cad_solid',
        '_grid',
        '_mask',
        'bc_map',
        'max_element_size',
        'min_element_size',
        'step_file',
        'tolerance'
    )

    def __init__(
        self, 
        step_file: str, 
        max_element_size: float, 
        tolerance: float, 
        min_element_size: float,
        boundary_map: dict
    ):
        """
        Explicit Initialization: No defaults permitted. 
        All pipeline configuration must be provided by the caller.
        """
        self.step_file = str(step_file)
        self.tolerance = float(tolerance)
        self.max_element_size = float(max_element_size)
        self.min_element_size = float(min_element_size)
        self.bc_map = dict(boundary_map)
        
        # --- Computed Fields (Initialized as None) ---
        self._grid = None
        self._mask = None
        self._boundary_conditions = None
        self._cad_solid = None
        self._bbox = None

    # --- Properties with Constitution Enforcement ---

    @property
    def grid(self) -> GridState | None: return self._grid

    @grid.setter
    def grid(self, value: GridState | None):
        if value is not None and not isinstance(value, GridState):
            raise TypeError("CONSTITUTION VIOLATION: 'grid' must be an instance of GridState.")
        self._grid = value

    @property
    def mask(self) -> list[int] | None: return self._mask

    @mask.setter
    def mask(self, value: list[int] | None):
        if value is not None and not isinstance(value, list):
            raise TypeError("CONSTITUTION VIOLATION: 'mask' must be a List.")
        self._mask = value

    @property
    def boundary_conditions(self) -> list[BoundaryConditionState] | None: return self._boundary_conditions

    @boundary_conditions.setter
    def boundary_conditions(self, value: list[BoundaryConditionState] | None):
        if value is not None and not isinstance(value, list):
            raise TypeError("CONSTITUTION VIOLATION: 'boundary_conditions' must be a List.")
        self._boundary_conditions = value
    
    @property
    def cad_solid(self) -> object | None: return self._cad_solid

    @cad_solid.setter
    def cad_solid(self, value: object | None):
        self._cad_solid = value
    
    @property
    def bbox(self) -> tuple | None: return self._bbox

    @bbox.setter
    def bbox(self, value: tuple | None):
        if value is not None and not isinstance(value, tuple):
            raise TypeError("CONSTITUTION VIOLATION: 'bbox' must be a tuple.")
        self._bbox = value