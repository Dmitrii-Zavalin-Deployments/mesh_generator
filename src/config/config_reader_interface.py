"""
src/config/config_reader_interface.py

The Configuration Ingestion Contract.
Responsible for transforming raw data sources (files, env vars, etc.) 
into a validated ConfigInterface object.
"""

from typing import Any
from src.state.mesh_generator_state import ConfigInterface

class ConfigReaderInterface:
    """
    Interface for configuration ingestion.
    
    Any class implementing this must provide a way to ingest raw data 
    and output a strictly typed ConfigInterface.
    """

    def read(self, source: Any) -> ConfigInterface:
        """
        Ingests the configuration source and returns the validated 
        state dictionary.

        Args:
            source: A path (str/Path) or raw configuration object.

        Returns:
            A strictly typed ConfigInterface matching your schema.

        Raises:
            NotImplementedError: If the concrete reader is not implemented.
        """
        raise NotImplementedError("Concrete readers must implement the read() method.")