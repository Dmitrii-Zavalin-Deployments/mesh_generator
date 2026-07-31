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

        if float(tolerance) < 0:
            raise ValueError("Tolerance cannot be negative")
        if float(max_element_size) <= 0:
            raise ValueError("Max element size must be positive")
        if float(min_element_size) <= 0:
            raise ValueError("Min element size must be positive")

        self.step_file = str(step_file)
        self.tolerance = float(tolerance)
        self.max_element_size = float(max_element_size)
        self.min_element_size = float(min_element_size)
        
        # --- Computed Fields (Initialized as None) ---
        self._grid = None
        self._mask = None
        self._cad_solid = None
EOF

python3 -c '
path = "tests/test_voxelization.py"
with open(path, "r") as f:
    content = f.read()

old_test = """@pytest.mark.parametrize("bad_tol", [None, -0.01])
def test_voxelization_invalid_tolerance(bad_tol):
    \"\"\"Verifies that invalid tolerances (None or negative) raise ValueError.\"\"\"
    container = SovereignContainer(
        step_file="tests/dummies/sample_geometry.step",
        max_element_size=0.5,
        tolerance=bad_tol,
        min_element_size=0.1
    )"""

new_test = """@pytest.mark.parametrize("bad_tol", [None, -0.01])
def test_voxelization_invalid_tolerance(bad_tol):
    \"\"\"Verifies that invalid tolerances (None or negative) raise ValueError.\"\"\"
    with pytest.raises(ValueError):
        SovereignContainer(
            step_file="tests/dummies/sample_geometry.step",
            max_element_size=0.5,
            tolerance=bad_tol,
            min_element_size=0.1
        )"""

if old_test in content:
    content = content.replace(old_test, new_test, 1)
    with open(path, "w") as f:
        f.write(content)
'

pytest