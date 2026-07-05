from typing import List, Optional
from OCC.Core.TopoDS import TopoDS_Shape

class BoundaryConditionState:
    """
    State container for a single Boundary Condition.
    Preserves the nested structure defined in mesh_generator_results_schema.json.
    """
    __slots__ = ('location', 'type', 'surface_id')

    def __init__(self, location: str, type: str, surface_id: str):
        self.location = str(location)
        self.type = str(type)
        self.surface_id = str(surface_id)

class GridState:
    """
    State container for the Grid Extents and Resolution.
    Compatible with both Cartesian Voxel grids and 'Virtual Grids' from Gmsh.
    """
    __slots__ = ('x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max', 'nx', 'ny', 'nz')
    
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
        'step_file', 'solver_version', 'tolerance', 'max_element_size', 'min_element_size',
        'bc_map', '_grid', '_mask', '_boundary_conditions', '_cad_solid', '_bbox'
    )

    def __init__(
        self, 
        step_file: str, 
        max_element_size: float, 
        solver_version: str, 
        tolerance: float, 
        min_element_size: float,
        boundary_map: dict
    ):
        """
        Explicit Initialization: No defaults permitted. 
        All pipeline configuration must be provided by the caller.
        """
        self.step_file = str(step_file)
        self.solver_version = str(solver_version)
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
    def grid(self) -> Optional[GridState]: return self._grid

    @grid.setter
    def grid(self, value: Optional[GridState]):
        if value is not None and not isinstance(value, GridState):
            raise TypeError("CONSTITUTION VIOLATION: 'grid' must be an instance of GridState.")
        self._grid = value

    @property
    def mask(self) -> Optional[List[int]]: return self._mask

    @mask.setter
    def mask(self, value: Optional[List[int]]):
        if value is not None and not isinstance(value, list):
            raise TypeError("CONSTITUTION VIOLATION: 'mask' must be a List.")
        self._mask = value

    @property
    def boundary_conditions(self) -> Optional[List[BoundaryConditionState]]: return self._boundary_conditions

    @boundary_conditions.setter
    def boundary_conditions(self, value: Optional[List[BoundaryConditionState]]):
        if value is not None and not isinstance(value, list):
            raise TypeError("CONSTITUTION VIOLATION: 'boundary_conditions' must be a List.")
        self._boundary_conditions = value
    
    @property
    def cad_solid(self) -> Optional[TopoDS_Shape]: return self._cad_solid

    @cad_solid.setter
    def cad_solid(self, value: Optional[TopoDS_Shape]):
        if value is not None and not isinstance(value, TopoDS_Shape):
            raise TypeError(f"CONSTITUTION VIOLATION: 'cad_solid' must be a TopoDS_Shape, not {type(value)}.")
        self._cad_solid = value
    
    @property
    def bbox(self) -> Optional[tuple]: return self._bbox

    @bbox.setter
    def bbox(self, value: Optional[tuple]):
        if value is not None and not isinstance(value, tuple):
            raise TypeError("CONSTITUTION VIOLATION: 'bbox' must be a tuple.")
        self._bbox = value