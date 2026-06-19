"""
src/steps/parse_geometry_interface.py

Step 1: Parse Geometry Interface
Defines the architectural contract and structural workflow for importing raw CAD 
assets, evaluating topology, and initializing the Sovereign State's transient layer.
"""

from typing import Any, Dict, List
import os

# Base Architectural Framework
from src.steps.step_interface_base import StepInterfaceBase
from src.state.mesh_generator_state import MeshGeneratorStateInterface

# OCC/Physics Stack Imports
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.TopoDS import TopoDS_Shape


class ParseGeometryInterface(StepInterfaceBase):
    """
    Gateway Pipeline Step.
    Responsible for eating a raw file path and spitting structured B-Rep data 
    and geometric metadata directly into the Sovereign State container.
    """
    
    # Restrict class capabilities strictly to the orchestration entrypoint
    ALLOWED_MEMBERS = {"run"}

    def run(self, state: MeshGeneratorStateInterface, config: Any) -> None:
        """
        Executes the conversion chain from raw path string to validated in-memory physics metadata.
        
        This method defines the exact logical sequence required to satisfy the 
        state["transients"] data contract.
        
        Args:
            state: The authorative Single Source of Truth container for the pipeline.
            config: Read-only pipeline configuration adjustments (e.g., healing tolerances).
            
        Raises:
            FileNotFoundError: If the input path points to a non-existent asset.
            RuntimeError: If OpenCASCADE fails to read, translate, or compile the file topology.
        """
        # ----------------------------------------------------------------------
        # STEP 1: PATH EXTRACTION & DISK VALIDATION
        # ----------------------------------------------------------------------
        # Target: Isolate the incoming file pointer and perform a system smoke test.
        target_path: str = state["inputs"]["step_file"]
        
        if not os.path.exists(target_path):
            raise FileNotFoundError(
                f"[Parse Geometry Error] Targeted STEP asset does not exist at path: '{target_path}'"
            )

        # ----------------------------------------------------------------------
        # STEP 2: OPENCASCADE READER INITIALIZATION & LOADING
        # ----------------------------------------------------------------------
        # Target: Pass the file path into the C++ wrapper stream and check interface consistency.
        reader = STEPControl_Reader()
        read_status = reader.ReadFile(target_path)
        
        if read_status != IFSelect_RetDone:
            raise RuntimeError(
                f"[Parse Geometry Error] OpenCASCADE stream failed to ingest file structure. "
                f"Status code: {read_status}"
            )

        # ----------------------------------------------------------------------
        # STEP 3: TOPOLOGICAL TRANSLATION TO B-REP SHAPE
        # ----------------------------------------------------------------------
        # Target: Compile the raw entity structures into a single valid TopoDS_Shape object.
        reader.TransferRoot()
        extracted_shape: TopoDS_Shape = reader.Shape()
        
        if extracted_shape.IsNull():
            raise RuntimeError(
                "[Parse Geometry Error] CAD translation layer produced a null shape object."
            )

        # ----------------------------------------------------------------------
        # STEP 4: GEOMETRIC BOUNDING BOX EVALUATION
        # ----------------------------------------------------------------------
        # Target: Calculate the spatial boundaries of the shape for downstream grid generation.
        bounding_box_accumulator = Bnd_Box()
        brepbndlib_Add(extracted_shape, bounding_box_accumulator)
        
        # Extract floating-point limits from the OpenCASCADE calculation
        x_min, y_min, z_min, x_max, y_max, z_max = bounding_box_accumulator.Get()

        # ----------------------------------------------------------------------
        # STEP 5: TOPOLOGY EXPLORATION & METADATA EXTRACTION
        # ----------------------------------------------------------------------
        # Target: Loop through the topological faces to extract unique surface IDs and 
        # compute corresponding unit outward normal vectors [nx, ny, nz] for boundary analysis.
        #
        # Implementation Note for concrete subclasses:
        # Use OCC.Core.TopExp.TopExp_Explorer to extract TopAbs_FACE entities,
        # compile face strings or hashes into `all_surface_ids`, and evaluate analytical 
        # or mesh normals via OCC.Core.BRep.BRep_Tool into `surface_normals`.
        computed_surface_normals: Dict[str, List[float]] = {}
        computed_surface_ids: List[str] = []

        # ----------------------------------------------------------------------
        # STEP 6: SOVEREIGN STATE INJECTION (The Zero-Default Policy Contract)
        # ----------------------------------------------------------------------
        # Target: Explicitly populate the container keys. Downstream steps (S2-S5) 
        # are now completely decoupled from disk-level file operations.
        state["transients"]["shape"] = extracted_shape
        
        state["transients"]["bounding_box"] = {
            "x_min": float(x_min),
            "x_max": float(x_max),
            "y_min": float(y_min),
            "y_max": float(y_max),
            "z_min": float(z_min),
            "z_max": float(z_max),
        }
        
        state["transients"]["surface_normals"] = computed_surface_normals
        state["transients"]["all_surface_ids"] = computed_surface_ids