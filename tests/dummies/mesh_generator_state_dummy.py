from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class MeshGeneratorStateDummy(MeshGeneratorStateInterface):
    """
    Test‑only dummy implementation of the Mesh Generator Sovereign Container.
    Acts as an object, but supports dictionary-style access for test compatibility.
    """

    def __init__(self):
        self.inputs_step_file = ""
        self.results_grid = {
            "x_min": 0.0,
            "x_max": 0.0,
            "y_min": 0.0,
            "y_max": 0.0,
            "z_min": 0.0,
            "z_max": 0.0,
            "nx": 0,
            "ny": 0,
            "nz": 0,
        }
        self.results_mask = []
        self.results_boundary_conditions = []

    def __getitem__(self, key):
        """Allows test suite to access object attributes via dictionary keys."""
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Allows test suite to set attributes via dictionary keys."""
        setattr(self, key, value)

    def override(self, **kwargs):
        """Overrides primary fields."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self