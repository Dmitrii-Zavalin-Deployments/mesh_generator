
class dummy_in(dict):
    """
    Schema-aligned harness for input data.
    Maps to: mesh_generator_input_schema.json
    """
    def __init__(self):
        super().__init__({
            "inputs": {
                "step_file": "tests/data/sample_geometry.step"
            }
        })
        # Transient attributes for in-memory handling
        self.cad_solid = None
        self.inputs_step_model = {}

    def override(self, **kwargs):
        """Updates nested schema dictionary or instance attributes."""
        for key, value in kwargs.items():
            if key in self["inputs"]:
                self["inputs"][key] = value
            else:
                setattr(self, key, value)
        return self

class dummy_out(dict):
    """
    Schema-aligned harness for results data.
    Maps to: mesh_generator_results_schema.json
    """
    def __init__(self):
        super().__init__({
            "results": {
                "grid": {
                    "x_min": 0.0, "x_max": 0.0,
                    "y_min": 0.0, "y_max": 0.0,
                    "z_min": 0.0, "z_max": 0.0,
                    "nx": 1, "ny": 1, "nz": 1
                },
                "mask": [],
                "boundary_conditions": []
            }
        })

    def override(self, **kwargs):
        """Updates nested results dictionary."""
        for key, value in kwargs.items():
            if key in self["results"]:
                self["results"][key] = value
            else:
                setattr(self, key, value)
        return self

def get_mock_config():
    """Returns a valid config matching mesh_generator_config_schema.json"""
    return {
        "solver_version": "v1.0.0",
        "tolerance": 1e-6,
        "max_element_size": 0.5,
        "min_element_size": 0.1,
        "boundary_map": {},
        "engine_type": "gmsh"
    }