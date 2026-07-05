import logging
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer
# Legacy Imports
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_OUT
# New Gmsh Imports
import gmsh

logger = logging.getLogger(__name__)

class CategorizationStep(StepInterface):
    """
    S11: Spatial Categorization Controller.
    
    Delegates the categorization strategy to either the legacy Voxelizer 
    or the new Geometry-Aware Gmsh engine.
    """
    
    __slots__ = ('use_gmsh',)

    def __init__(self, use_gmsh: bool = True):
        self.use_gmsh = use_gmsh

    def execute(self, container: SovereignContainer):
        """Dispatches logic to the appropriate engine."""
        if container.grid is None:
            raise RuntimeError("CONSTITUTION VIOLATION: 'grid' is None. ResolutionStep must precede CategorizationStep.")

        if self.use_gmsh:
            self._run_gmsh_engine(container)
        else:
            self._run_voxel_engine(container)

    def _run_gmsh_engine(self, container: SovereignContainer):
        """Gmsh Implementation: Geometry-Aware Tetrahedral Meshing."""
        logger.info("Starting Gmsh Engine categorization...")
        
        gmsh.initialize()
        gmsh.model.add("nozzle_model")
        
        # Import the STEP file
        gmsh.model.occ.importShapes(container.step_file)
        gmsh.model.occ.synchronize()
        
        # Define Mesh Size Field (Adaptive)
        # Using the logic derived in ResolutionStep
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", container.max_element_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", container.min_element_size)
        
        # Generate 3D Mesh
        gmsh.model.mesh.generate(3)
        
        # Extract Mesh Data
        nodes = gmsh.model.mesh.getNodes()
        elements = gmsh.model.mesh.getElementsByType(4) # 4 = Tetrahedron
        
        logger.info(f"Gmsh Engine complete: {len(nodes[0])} nodes, {len(elements[0])} tetrahedra.")
        
        gmsh.finalize()
        # Note: We keep the container.mask as None or a placeholder for now 
        # until the physics solver is updated to consume the unstructured mesh.

    def _run_voxel_engine(self, container: SovereignContainer):
        """Legacy Voxelizer Implementation."""
        logger.info("Starting Legacy Voxel Engine categorization...")
        classifier = BRepClass3d_SolidClassifier(container.cad_solid)
        grid = container.grid
        
        dx = (grid.x_max - grid.x_min) / grid.nx
        dy = (grid.y_max - grid.y_min) / grid.ny
        dz = (grid.z_max - grid.z_min) / grid.nz
        
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
        logger.info("Voxel Engine categorization complete.")