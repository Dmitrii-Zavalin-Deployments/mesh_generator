# src/implementation/steps/compute_boundary_condition_location_step.py
from src.interfaces.step_interfaces.compute_boundary_condition_location_interface import ComputeBoundaryConditionLocationInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeBoundaryConditionLocationStep(ComputeBoundaryConditionLocationInterface):
    """
    Concrete implementation of S12.i.1 — compute_boundary_condition_location.

    Determines the specific grid boundary face (e.g., x_min, x_max, wall) 
    that a given boundary condition entity occupies, utilizing the 
    geometric model and the computed grid extents.
    """

    def __init__(self, geometry_model):
        """
        Initializes the step with the internal geometric model.
        """
        self.geometry_model = geometry_model

    def run(self, state: MeshGeneratorStateInterface, config, index: int) -> None:
        """
        Computes results.boundary_conditions[index].location.

        Logic:
            1. Retrieve grid bounds from the Sovereign Container.
            2. Extract bounding box of the geometric entity (BC i) from the model.
            3. Compare entity extents against grid extents using config.tolerance.
            4. Assign the appropriate classification string.
        """
        # 1. Access required inputs
        grid = state.results_grid
        tol = config.tolerance

        # Retrieve the geometric entity associated with this boundary condition
        entity = self.geometry_model.get_boundary_entity(index)
        e_min = entity.get_min_coords() # returns (x, y, z)
        e_max = entity.get_max_coords() # returns (x, y, z)

        # 2. Geometric Classification
        # We classify based on proximity to the grid bounding box faces
        # Priority order: faces first, then "wall" (internal/other)
        if abs(e_min[0] - grid['x_min']) <= tol:
            location = "x_min"
        elif abs(e_max[0] - grid['x_max']) <= tol:
            location = "x_max"
        elif abs(e_min[1] - grid['y_min']) <= tol:
            location = "y_min"
        elif abs(e_max[1] - grid['y_max']) <= tol:
            location = "y_max"
        elif abs(e_min[2] - grid['z_min']) <= tol:
            location = "z_min"
        elif abs(e_max[2] - grid['z_max']) <= tol:
            location = "z_max"
        else:
            location = "wall"

        # 3. Write result
        # Ensure the list of boundary conditions is initialized
        if not hasattr(state, 'results_boundary_conditions') or state.results_boundary_conditions is None:
            state.results_boundary_conditions = []

        # Ensure the specific index exists in the list
        while len(state.results_boundary_conditions) <= index:
            state.results_boundary_conditions.append({})

        # Assign the computed location
        state.results_boundary_conditions[index]['location'] = location