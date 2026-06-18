"""
src/pipeline/pipeline_orchestrator_interface.py

The Pipeline Orchestrator Contract.
Defines the execution lifecycle for assembling and executing the sequential 
step chain against the Sovereign State container.
"""

# FIX: Import ConfigInterface to enforce type safety
from src.state.mesh_generator_state import MeshGeneratorStateInterface, ConfigInterface
from src.pipeline.pipeline_interface import PipelineInterface

class PipelineOrchestratorInterface:
    """
    Interface for the Pipeline Engine.
    
    Enforces the execution contract for any orchestrator implementation 
    designed to coordinate the sequential execution of the mesh generation steps.
    """

    def run(self, state: MeshGeneratorStateInterface, config: ConfigInterface) -> PipelineInterface:
        """
        Executes the full pipeline sequence of steps.

        Args:
            state: The unified Sovereign State container to be processed.
            config: Read-only pipeline configuration adjustments (strict ConfigInterface).

        Returns:
            A read-only view of the finalized mesh generation state 
            conforming to the PipelineInterface contract.
            
        Raises:
            NotImplementedError: For direct invocations of the interface base class.
        """
        raise NotImplementedError("Concrete orchestrators must implement the run() method.")