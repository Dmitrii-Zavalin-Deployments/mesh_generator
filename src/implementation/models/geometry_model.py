# src/implementation/models/geometry_model.py

from OCC.Core.TopoDS import TopoDS_Shape

class BoundaryEntity:
    """
    A lightweight container for boundary entities.
    This fulfills the interface requirements for downstream steps 
    without needing complex CAD face-extraction logic yet.
    """
    def __init__(self, min_coords, max_coords):
        self.min_coords = min_coords
        self.max_coords = max_coords

    def get_min_coords(self):
        return self.min_coords

    def get_max_coords(self):
        return self.max_coords

class GeometryModel:
    """
    Sovereign container for CAD geometry and spatial bounds.
    
    This class is passed between steps to prevent redundant parsing of the
    raw STEP file. It holds the heavy CAD solid (TopoDS_Shape) and the 
    pre-computed bounding box metrics.
    """

    def __init__(
        self, 
        x_min: float, x_max: float, 
        y_min: float, y_max: float, 
        z_min: float, z_max: float, 
        cad_solid: TopoDS_Shape
    ):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max
        self.cad_solid = cad_solid
        
        # Placeholder for boundary condition tracking
        self._boundary_count = 1 

    def get_bounding_box_min(self):
        """Returns the minimum spatial coordinates as a tuple (x, y, z)."""
        return (self.x_min, self.y_min, self.z_min)

    def get_bounding_box_max(self):
        """Returns the maximum spatial coordinates as a tuple (x, y, z)."""
        return (self.x_max, self.y_max, self.z_max)

    def get_boundary_count(self) -> int:
        """Returns the number of boundary surfaces detected."""
        return self._boundary_count

    def get_boundary_entity(self, index: int):
        """
        Returns a BoundaryEntity object that conforms to the interface expected 
        by ComputeBoundaryConditionLocationStep.
        """
        # Return a dummy entity using the model's overall bounds as a placeholder
        # until specific face extraction logic is implemented.
        return BoundaryEntity(
            min_coords=self.get_bounding_box_min(),
            max_coords=self.get_bounding_box_max()
        )

    def __repr__(self):
        return (f"GeometryModel(bounds=[{self.x_min}:{self.x_max}, "
                f"{self.y_min}:{self.y_max}, {self.z_min}:{self.z_max}])")