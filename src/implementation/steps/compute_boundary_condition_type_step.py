# src/implementation/steps/compute_boundary_condition_type_step.py
from src.interfaces.step_interfaces.compute_boundary_condition_type_interface import ComputeBoundaryConditionTypeInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeBoundaryConditionTypeStep(ComputeBoundaryConditionTypeInterface):
    """
    Concrete implementation of S12.i.2 — compute_boundary_condition_type.

    Determines the physical boundary condition type (e.g., 'inlet', 'outlet', 'wall')
    for a specific boundary entity, based on its spatial location and 
    geometric classification.
    """

    def __init__(self, geometry_model):
        """
        Initializes the step with the internal geometric model for classification.
        """
        self.geometry_model = geometry_model

    def run(self, state: MeshGeneratorStateInterface, config, index: int) -> None:
        """
        Computes results.boundary_conditions[index].type.

        Logic:
            1. Access the location computed in S12.i.1.
            2. Query the internal geometry model for the specific surface type 
               associated with the entity at this index.
            3. Apply logic based on location (e.g., x_min is often an inlet).
            4. Write the type string to the Sovereign Container.
        """
        # 1. Retrieve the previously computed location
        if not hasattr(state, 'results_boundary_conditions') or index >= len(state.results_boundary_conditions):
            raise IndexError(f"Boundary condition at index {index} not initialized.")
            
        location = state.results_boundary_conditions[index].get("location")
        if location is None:
            raise ValueError(f"S12.i.2 requires 'location' to be computed for index {index} first.")

        # 2. Determine type
        # Logic: Query the B-Rep model for classification, then refine by location
        entity = self.geometry_model.get_boundary_entity(index)
        base_type = entity.get_physical_type() # e.g., 'no-slip', 'slip', 'pressure'
        
        # 3. Refine/Map type based on spatial context (example mapping)
        # In a real implementation, this would match domain-specific conventions
        if base_type == "wall" and location == "x_min":
            boundary_type = "inlet"
        elif base_type == "wall" and location == "x_max":
            boundary_type = "outlet"
        else:
            boundary_type = base_type

        # 4. Write result
        state.results_boundary_conditions[index]["type"] = boundary_type