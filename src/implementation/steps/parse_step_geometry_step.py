import os
# PythonOCC Core imports for high-performance geometry processing
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add

# Domain imports
from src.interfaces.step_interfaces.parse_step_geometry_interface import ParseStepGeometryInterface
from src.implementation.models.geometry_model import GeometryModel 

class ParseStepGeometryStep(ParseStepGeometryInterface):
    """
    Concrete implementation of S1 — parse_step_geometry.

    This step is responsible for loading the actual CAD STEP file, parsing
    the topology into an OpenCASCADE TopoDS_Shape, and computing the exact
    mathematical bounding box for the mesh generation grid.
    """

    def run(self, state, config) -> GeometryModel:
        """
        Loads the STEP file referenced in the state, performs geometric 
        parsing using OpenCASCADE, and returns the GeometryModel.

        Args:
            state: The MeshGeneratorState Sovereign Container.
            config: The MeshGeneratorConfig object.
            
        Returns:
            GeometryModel: Encapsulated geometry object containing the 
                           TopoDS_Shape and spatial bounds.
        """
        # 0. Pre-flight check: Verify file exists to satisfy error propagation tests
        if not os.path.exists(state.inputs_step_file):
            raise FileNotFoundError(f"Input STEP file not found at: {state.inputs_step_file}")

        # 1. Initialize the STEP Reader
        step_reader = STEPControl_Reader()
        
        # 2. Attempt to read the file
        status = step_reader.ReadFile(state.inputs_step_file)

        if status != IFSelect_RetDone:
            raise RuntimeError(f"Step S1 failed: Unable to parse real STEP file '{state.inputs_step_file}'.")

        # 3. Transfer roots and extract the solid shape
        # The reader converts the STEP file into an internal TopoDS_Shape
        step_reader.TransferRoots()
        
        # Defensive Guard: Ensure we actually extracted a shape before accessing index 1
        if step_reader.NbShapes() == 0:
            raise RuntimeError(f"Step S1 failed: No shapes found in STEP file '{state.inputs_step_file}'. "
                               "Ensure the file contains valid geometric data (e.g., CLOSED_SHELL or BREP).")
        
        cad_solid = step_reader.Shape(1) 

        # 4. Calculate exact bounding box using OpenCASCADE mathematics
        bbox = Bnd_Box()
        brepbndlib_Add(cad_solid, bbox)
        
        # Get the bounds as a tuple (xmin, ymin, zmin, xmax, ymax, zmax)
        x_min, y_min, z_min, x_max, y_max, z_max = bbox.Get()

        # 5. Construct and return the GeometryModel
        # This replaces the mock dictionary with a physical geometric object
        return GeometryModel(
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            z_min=z_min,
            z_max=z_max,
            cad_solid=cad_solid
        )