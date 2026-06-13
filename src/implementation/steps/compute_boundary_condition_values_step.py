# src/implementation/steps/compute_boundary_condition_values_step.py
from src.interfaces.step_interfaces.compute_boundary_condition_values_interface import ComputeBoundaryConditionValuesInterface
from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class ComputeBoundaryConditionValuesStep(ComputeBoundaryConditionValuesInterface):
    """
    Concrete implementation of S12.i.3 — compute_boundary_condition_values.

    Populates the physical properties (u, v, w, p) for a given boundary condition,
    strictly mapping the boundary 'type' to values defined in the configuration.
    """

    def run(self, state: MeshGeneratorStateInterface, config, index: int) -> None:
        """
        Computes results.boundary_conditions[index].values.

        Logic:
            1. Retrieve the boundary condition type computed in S12.i.2.
            2. Extract required physical values from the config object.
            3. Populate the 'values' dictionary within the Sovereign Container.
            4. Enforce strict adherence to the provided configuration (No-Defaults Policy).
        """
        # 1. Validation: Ensure previous steps have run and data is present
        if not hasattr(state, 'results_boundary_conditions') or index >= len(state.results_boundary_conditions):
            raise IndexError(f"Boundary condition at index {index} not initialized.")

        bc = state.results_boundary_conditions[index]
        bc_type = bc.get("type")

        if bc_type is None:
            raise ValueError(f"S12.i.3 requires 'type' to be computed for index {index} first.")

        # 2. Extract values from config
        # The config object must explicitly define parameters for the specific type.
        # We perform no internal defaulting; if the config is missing these keys, 
        # this will naturally raise a KeyError.
        config_values = config.get_values_for_type(bc_type)

        # 3. Construct and assign the values container
        # The structure must match BoundaryConditionValuesInterface
        values_container = {
            "u": config_values["u"],
            "v": config_values["v"],
            "w": config_values["w"],
            "p": config_values["p"]
        }

        # 4. Write result
        bc["values"] = values_container