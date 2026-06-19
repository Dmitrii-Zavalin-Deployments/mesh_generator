"""
src/pipeline/pipeline_interface.py

The Global State View Contract.
This file is part of the core architecture and is version‑controlled.
"""

from typing import List
from OCC.Core.TopoDS import TopoDS_Shape

# COMPILED SIGNATURE: Sub-interfaces are safely routed from the consolidated Single Source of Truth
from src.state.mesh_generator_state import GridInterface, BoundaryConditionInterface

class PipelineInterface:
    """
    Contract‑only composite interface for the global pipeline state.
    Provides a read‑only view of the final state after the Minimal Step Chain.
    
    This interface serves as the primary gateway for PipelineCoherenceSignatures 
    to validate the structural integrity of the generated mesh without accessing 
    the internal, mutable Sovereign Container.
    """

    @property
    def geometry(self) -> TopoDS_Shape:
        """
        Access to the internal B-Rep geometry model (TopoDS_Shape).
        Required for topological coherence checks.
        """
        raise NotImplementedError("Subclasses must implement the 'geometry' property.")

    @property
    def grid(self) -> GridInterface:
        """
        Access to the finalized grid extents and resolution.
        Maps directly to results.grid in the output schema.
        """
        raise NotImplementedError("Subclasses must implement the 'grid' property.")

    @property
    def mask(self) -> List[int]:
        """
        Access to the finalized fluid/solid mask array.
        Maps directly to results.mask in the output schema.
        """
        raise NotImplementedError("Subclasses must implement the 'mask' property.")

    @property
    def boundary_conditions(self) -> List[BoundaryConditionInterface]:
        """
        Access to the finalized list of boundary conditions.
        Maps directly to results.boundary_conditions in the output schema.
        """
        raise NotImplementedError("Subclasses must implement the 'boundary_conditions' property.")