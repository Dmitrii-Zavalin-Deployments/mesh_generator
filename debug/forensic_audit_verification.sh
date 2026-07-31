cat << 'EOF' > src/state/mesh_generator_state.py
class MeshGeneratorState:
    def __init__(
        self,
        step_file: str,
        tolerance: float,
        max_element_size: float,
        min_element_size: float
    ):
        """
        Explicit Initialization: No defaults permitted. 
        All pipeline configuration must be provided by the caller.
        """
        if step_file is None:
            raise ValueError("step_file cannot be None")
        if tolerance is None:
            raise ValueError("tolerance cannot be None")
        if max_element_size is None:
            raise ValueError("max_element_size cannot be None")
        if min_element_size is None:
            raise ValueError("min_element_size cannot be None")

        self.step_file = str(step_file)
        self.tolerance = float(tolerance)
        self.max_element_size = float(max_element_size)
        self.min_element_size = float(min_element_size)
        
        # --- Computed Fields (Initialized as None) ---
        self._grid = None
        self._mask = None
        self._cad_solid = None
EOF

# pytest