# tests/dummies/mesh_generator_state_dummy.py

from interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface


class MeshGeneratorStateDummy(dict, MeshGeneratorStateInterface):
    """
    Test‑only dummy implementation of the Mesh Generator Sovereign Container.
    Contains only primary schema fields. No logic. Deterministic. Override‑friendly.
    """

    def __init__(self):
        super().__init__({
            "inputs_step_file": "",
            "results_grid": {
                "x_min": 0.0,
                "x_max": 0.0,
                "y_min": 0.0,
                "y_max": 0.0,
                "z_min": 0.0,
                "z_max": 0.0,
                "nx": 0,
                "ny": 0,
                "nz": 0,
            },
            "results_mask": [],
            "results_boundary_conditions": []
        })

    def override(self, **kwargs):
        """Overrides primary fields in dict."""
        for key, value in kwargs.items():
            self[key] = value
        return self