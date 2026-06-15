from src.interfaces.state.mesh_generator_state_interface import MeshGeneratorStateInterface

class MeshGeneratorStateDummy(MeshGeneratorStateInterface):
    """
    Test‑only dummy implementation of the Mesh Generator Sovereign Container.
    Acts as an object, but supports dictionary-style access for test compatibility.
    Includes equality checks for deterministic testing.
    """

    def __init__(self):
        # Set to a valid dummy path to resolve FileNotFoundError in pipeline tests
        self.inputs_step_file = os.path.join(os.path.dirname(__file__), "dummy_model.stp")
        self.results_grid = {
            "x_min": 0.0, "x_max": 0.0, "y_min": 0.0,
            "y_max": 0.0, "z_min": 0.0, "z_max": 0.0,
            "nx": 0, "ny": 0, "nz": 0,
        }
        self.results_mask = []
        self.results_boundary_conditions = []

    def __eq__(self, other):
        """Ensures deterministic comparison by checking internal state."""
        if not isinstance(other, MeshGeneratorStateDummy):
            return False
        return self.__dict__ == other.__dict__

    def __iter__(self):
        """Allows direct iteration over dummy state fields."""
        return iter(self.__dict__.keys())

    def __getitem__(self, key):
        """
        Allows test suite to access object attributes via dictionary keys.
        Raises IndexError for integer keys to support sequence-style iteration.
        """
        if isinstance(key, int):
            raise IndexError("MeshGeneratorStateDummy is not a sequence; integer indices are not supported.")
            
        key_str = str(key)
        if hasattr(self, key_str):
            return getattr(self, key_str)
        raise KeyError(f"State does not contain attribute: {key_str}")

    def __setitem__(self, key, value):
        """Allows test suite to set attributes via dictionary keys."""
        setattr(self, str(key), value)

    def override(self, **kwargs):
        """Overrides primary fields."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self