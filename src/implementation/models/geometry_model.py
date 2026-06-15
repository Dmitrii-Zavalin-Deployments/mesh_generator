# src/implementation/models/geometry_model.py

from OCC.Core.TopoDS import TopoDS_Shape

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
        
        # Placeholder for boundary condition tracking (extensible for complex CAD)
        self._boundary_count = 1 

    def get_bounding_box_min(self):
        """Returns the minimum spatial coordinates as a tuple (x, y, z)."""
        return (self.x_min, self.y_min, self.z_min)

    def get_bounding_box_max(self):
        """Returns the maximum spatial coordinates as a tuple (x, y, z)."""
        return (self.x_max, self.y_max, self.z_max)

    def get_boundary_count(self) -> int:
        """
        Returns the number of boundary surfaces detected in the CAD file.
        This enables the Orchestrator to loop through boundary condition steps correctly.
        """
        return self._boundary_count

    def __repr__(self):
        return (f"GeometryModel(bounds=[{self.x_min}:{self.x_max}, "
                f"{self.y_min}:{self.y_max}, {self.z_min}:{self.z_max}])")