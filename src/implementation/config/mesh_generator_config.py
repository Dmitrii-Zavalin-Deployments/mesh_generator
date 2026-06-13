# src/implementation/config/mesh_generator_config.py
from src.interfaces.config.config_interface import MeshGeneratorConfigInterface

class MeshGeneratorConfig(MeshGeneratorConfigInterface):
    """
    Concrete implementation of the MeshGeneratorConfigInterface.
    Acts as an immutable data vessel for runtime configuration.
    
    Inherits from the Phase-2 contract to ensure 1:1 compliance.
    """
    def __init__(
        self, 
        solver_version: str, 
        tolerance: float, 
        max_element_size: float, 
        min_element_size: float
    ):
        # We explicitly assign fields to satisfy the No-Defaults Policy
        self.solver_version = solver_version
        self.tolerance = tolerance
        self.max_element_size = max_element_size
        self.min_element_size = min_element_size