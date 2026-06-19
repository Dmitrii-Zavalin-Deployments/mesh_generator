"""
src/pipeline/pipeline_builder_interface.py

The Pipeline Builder Contract.
Formalizes the bootstrap sequence: Validating configuration requirements 
before orchestrator instantiation.
"""

from typing import Any
from src.pipeline.pipeline_orchestrator_interface import PipelineOrchestratorInterface
from src.config.config_reader_interface import ConfigReaderInterface

class PipelineBuilderInterface:
    """
    Interface for the Pipeline Builder.
    
    Enforces the structural sequence: Configuration validation must occur 
    prior to pipeline orchestration. This ensures that downstream steps 
    always receive a guaranteed, valid configuration state.
    """

    def build(self, config_reader: ConfigReaderInterface, config_source: Any) -> PipelineOrchestratorInterface:
        """
        Assembles the execution pipeline.

        This method encapsulates the 'Bootstrap' phase. It ensures that 
        the configuration is successfully ingested and validated by the 
        config_reader before returning a ready-to-run orchestrator.

        Args:
            config_reader: The concrete reader instance used to ingest configuration.
            config_source: The raw source (e.g., file path) for the configuration.

        Returns:
            A fully assembled PipelineOrchestrator ready for execution.
            
        Raises:
            NotImplementedError: For direct invocations of the interface base class.
        """
        raise NotImplementedError("Concrete builders must implement the build() method.")