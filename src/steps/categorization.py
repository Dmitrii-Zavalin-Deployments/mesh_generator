# src/steps/categorization.py
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_OUT

class CategorizationStep(StepInterface):
    """
    S11: Conservative Spatial Categorization.
    
    Classifies cells by checking all 8 corners of the voxel against 
    the BRepClass3d_SolidClassifier.
    """
    
    __slots__ = ()

    def execute(self, container: SovereignContainer):
        if container.grid is None:
            raise RuntimeError("CONSTITUTION VIOLATION: 'grid' is None.")

        classifier = BRepClass3d_SolidClassifier(container.cad_solid)
        grid = container.grid
        
        dx = (grid.x_max - grid.x_min) / grid.nx
        dy = (grid.y_max - grid.y_min) / grid.ny
        dz = (grid.z_max - grid.z_min) / grid.nz

        mask = [0] * (grid.nx * grid.ny * grid.nz)

        for i in range(grid.nx):
            for j in range(grid.ny):
                for k in range(grid.nz):
                    # Define the 8 corners of the voxel
                    x0, y0, z0 = grid.x_min + i*dx, grid.y_min + j*dy, grid.z_min + k*dz
                    corners = [
                        gp_Pnt(x0, y0, z0), gp_Pnt(x0+dx, y0, z0),
                        gp_Pnt(x0, y0+dy, z0), gp_Pnt(x0+dx, y0+dy, z0),
                        gp_Pnt(x0, y0, z0+dz), gp_Pnt(x0+dx, y0, z0+dz),
                        gp_Pnt(x0, y0+dy, z0+dz), gp_Pnt(x0+dx, y0+dy, z0+dz)
                    ]
                    
                    states = []
                    for pt in corners:
                        classifier.Perform(pt, 1e-7)
                        states.append(classifier.State())
                    
                    # Logic:
                    # All IN -> Solid (0)
                    # All OUT -> Fluid (1)
                    # Mixed -> Wall (-1)
                    if all(s == TopAbs_IN for s in states):
                        mask[i + grid.nx * (j + grid.ny * k)] = 0
                    elif all(s == TopAbs_OUT for s in states):
                        mask[i + grid.nx * (j + grid.ny * k)] = 1
                    else:
                        mask[i + grid.nx * (j + grid.ny * k)] = -1

        container.mask = mask