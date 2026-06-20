# src/steps/categorization.py
import logging
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_OUT

# Configure module-level logger for visibility in CI pipelines
logger = logging.getLogger(__name__)

class CategorizationStep(StepInterface):
    """
    S11: Conservative Spatial Categorization.
    
    Transforms the continuous CAD boundary into a discrete computational mask.
    This step employs an 8-corner sampling strategy per voxel to ensure that
    boundary features are captured without leaking or aliasing.
    """
    
    __slots__ = () 

    def execute(self, container: SovereignContainer):
        """
        Performs conservative voxelization.
        
        Args:
            container: The SovereignContainer instance. Requires a valid 'grid' 
                       and 'cad_solid' (OpenCascade TopoDS_Shape).
        """
        
        # GUARD CLAUSE: Ensure the spatial domain is defined.
        if container.grid is None:
            error_msg = "CONSTITUTION VIOLATION: 'grid' is None. ResolutionStep must precede CategorizationStep."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info("Starting Conservative Spatial Categorization...")
        
        # Initialize the geometry classifier for the CAD solid.
        classifier = BRepClass3d_SolidClassifier(container.cad_solid)
        grid = container.grid
        
        # Calculate voxel dimensions based on the total bounding box span.
        dx = (grid.x_max - grid.x_min) / grid.nx
        dy = (grid.y_max - grid.y_min) / grid.ny
        dz = (grid.z_max - grid.z_min) / grid.nz

        # Initialize the mask list.
        # Canonical flattening: index = i + nx * (j + ny * k)
        mask = [0] * (grid.nx * grid.ny * grid.nz)
        stats = {"solid": 0, "fluid": 0, "wall": 0}

        # Iterate over every voxel in the computational domain.
        for i in range(grid.nx):
            for j in range(grid.ny):
                for k in range(grid.nz):
                    
                    # Voxel corner coordinate mapping:
                    # Defines the 8 vertices of the cell cube for spatial sampling.
                    x0, y0, z0 = grid.x_min + i*dx, grid.y_min + j*dy, grid.z_min + k*dz
                    corners = [
                        gp_Pnt(x0, y0, z0),       gp_Pnt(x0+dx, y0, z0),
                        gp_Pnt(x0, y0+dy, z0),    gp_Pnt(x0+dx, y0+dy, z0),
                        gp_Pnt(x0, y0, z0+dz),    gp_Pnt(x0+dx, y0, z0+dz),
                        gp_Pnt(x0, y0+dy, z0+dz), gp_Pnt(x0+dx, y0+dy, z0+dz)
                    ]
                    
                    # Collect the spatial state for each corner vertex.
                    # 1e-7 provides a strict tolerance for boundary coincidence.
                    states = []
                    for pt in corners:
                        classifier.Perform(pt, 1e-7)
                        states.append(classifier.State())
                    
                    # Classification Logic (Conservative Voxelization):
                    # 1. Interior: If all 8 corners are IN, the entire voxel is definitely solid.
                    # 2. Exterior: If all 8 corners are OUT, the entire voxel is definitely fluid.
                    # 3. Boundary: If corners show a mix (IN/OUT/ON), the voxel contains a surface.
                    
                    idx = i + grid.nx * (j + grid.ny * k)
                    
                    if all(s == TopAbs_IN for s in states):
                        mask[idx] = 0   # Solid
                        stats["solid"] += 1
                    elif all(s == TopAbs_OUT for s in states):
                        mask[idx] = 1   # Fluid
                        stats["fluid"] += 1
                    else:
                        mask[idx] = -1  # Wall
                        stats["wall"] += 1

        # Persistence to the Sovereign Container.
        container.mask = mask
        logger.info(f"Categorization Complete: Solid={stats['solid']}, Fluid={stats['fluid']}, Wall={stats['wall']}")