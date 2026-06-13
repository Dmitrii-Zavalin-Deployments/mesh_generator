# src/implementation/steps/compute_mask_step.py
from src.interfaces.step_interfaces.compute_mask_interface import ComputeMaskInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeMaskStep(ComputeMaskInterface):
    """
    Concrete implementation of S11 — compute_mask.

    Constructs the 1D domain mask array by performing spatial point-in-solid
    queries against the parsed geometric model for every cell in the grid.
    """

    def __init__(self, geometry_model):
        """
        Initializes the step with the geometry model parsed in S1.
        """
        self.geometry_model = geometry_model

    def run(self, state: MeshGeneratorStateInterface, config) -> None:
        """
        Computes results.mask.

        Logic:
            1. Retrieve grid dimensions (nx, ny, nz) from state.results_grid.
            2. Initialize a flattened array (1D list) of zeros.
            3. Iterate through all grid coordinates (i, j, k).
            4. Query the geometry_model for point classification (-1, 0, or 1).
            5. Store the final flattened mask in state.results_mask.
        """
        # 1. Retrieve dimensions
        # The Orchestrator guarantees these keys exist; defensive checks are removed.
        nx = state.results_grid['nx']
        ny = state.results_grid['ny']
        nz = state.results_grid['nz']
        
        # Pre-calculate cell sizes (logic inlined and optimized)
        dx = (state.results_grid['x_max'] - state.results_grid['x_min']) / nx
        dy = (state.results_grid['y_max'] - state.results_grid['y_min']) / ny
        dz = (state.results_grid['z_max'] - state.results_grid['z_min']) / nz

        # 2. Initialize mask (flattened size: nx * ny * nz)
        total_cells = nx * ny * nz
        mask = [0] * total_cells

        # 3. Iterate and classify
        # Logic inlined to avoid sideways structures/unauthorized helper methods
        for k in range(nz):
            z = state.results_grid['z_min'] + (k + 0.5) * dz
            for j in range(ny):
                y = state.results_grid['y_min'] + (j + 0.5) * dy
                for i in range(nx):
                    x = state.results_grid['x_min'] + (i + 0.5) * dx
                    
                    # 4. Classify point
                    # -1: Solid, 0: Fluid, 1: Boundary
                    value = self.geometry_model.classify_point(x, y, z)
                    
                    flat_index = k * (nx * ny) + j * nx + i
                    mask[flat_index] = int(value)

        # 5. Write result
        state.results_mask = mask