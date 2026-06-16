# src/implementation/steps/compute_mask_step.py
import numpy as np
from OCC.Core.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopAbs import TopAbs_IN, TopAbs_ON

from src.interfaces.step_interfaces.compute_mask_interface import ComputeMaskInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface
from src.implementation.models.geometry_model import GeometryModel

class ComputeMaskStep(ComputeMaskInterface):
    """
    Concrete implementation of S11 — compute_mask.

    Constructs the 1D domain mask array using NumPy for memory efficiency
    and the BRepClass3d_SolidClassifier for mathematically precise ray-casting
    against the geometric model.
    """

    def __init__(self, geometry_model: GeometryModel):
        """
        Initializes the step with the geometry model parsed in S1.
        Strict dependency injection policy enforced; no default values allowed.
        """
        if not isinstance(geometry_model, GeometryModel):
            raise TypeError(f"ComputeMaskStep expects GeometryModel, got {type(geometry_model)}")
        
        self.geometry_model = geometry_model

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Computes results.mask via optimized ray-casting.
        Logic:
            1. Retrieve grid dimensions.
            2. Pre-allocate contiguous memory via numpy.
            3. Instantiate the OpenCASCADE classifier.
            4. Perform ray-casting to identify Solid, Boundary, or Fluid cells.
            5. Finalize the array and store in state.
        Maps OpenCASCADE geometric classifications to Navier-Stokes solver schema:
            -1 : Wall (Boundary Condition)
             0 : Solid
             1 : Fluid (Interior)
        """
        # 1. Retrieve dimensions from state
        nx, ny, nz = state.results_grid['nx'], state.results_grid['ny'], state.results_grid['nz']
        if nx <= 0 or ny <= 0 or nz <= 0:
            raise ValueError(f"Invalid mesh dimensions (nx={nx}, ny={ny}, nz={nz}). Dimensions must be positive.")
                
        # Calculate cell sizes
        dx = (state.results_grid['x_max'] - state.results_grid['x_min']) / nx
        dy = (state.results_grid['y_max'] - state.results_grid['y_min']) / ny
        dz = (state.results_grid['z_max'] - state.results_grid['z_min']) / nz

        # 2. Pre-allocate contiguous memory (int8 is sufficient for [-1, 0, 1])
        total_cells = nx * ny * nz
        mask = np.zeros(total_cells, dtype=np.int8)

        # 3. Initialize the BRepClass3d_SolidClassifier
        classifier = BRepClass3d_SolidClassifier(self.geometry_model.cad_solid)
        
        # ENFORCE NO-DEFAULTS POLICY: 
        # Retrieve tolerance dynamically. Supports both dict (from tests) and Object.
        tolerance = config['tolerance'] if isinstance(config, dict) else config.tolerance

        # 4. Perform ray-casting iteration
        flat_index = 0
        for k in range(nz):
            z = state.results_grid['z_min'] + (k + 0.5) * dz
            for j in range(ny):
                y = state.results_grid['y_min'] + (j + 0.5) * dy
                for i in range(nx):
                    x = state.results_grid['x_min'] + (i + 0.5) * dx
                    
                    # Perform ray-casting for the point
                    pnt = gp_Pnt(x, y, z)
                    classifier.Perform(pnt, tolerance)
                    
                    # Map OpenCASCADE TopAbs to internal Navier-Stokes schema
                    status = classifier.State()
                    if status == TopAbs_IN:
                        mask[flat_index] = 0   # Solid
                    elif status == TopAbs_ON:
                        mask[flat_index] = -1  # Wall (Boundary)
                    else:
                        mask[flat_index] = 1   # Fluid (OUT)
                        
                    flat_index += 1

        # 5. Write result (cast back to list for JSON serialization)
        state.results_mask = mask.tolist()