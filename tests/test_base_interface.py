# tests/test_base_interface.py
import pytest
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer

# 1. Literate Testing Standard: Validating the Constitution
# [cite_start]The StepInterface acts as the constitution for all processing steps[cite: 144].
# It enforces that only the 'execute' method is allowed, preventing developers
# [cite_start]from adding hidden logic, helper functions, or side-effect methods[cite: 144].

class TestBaseInterface(StepInterface):
    # 1:1 Interface Inheritance Rule: We inherit from StepInterface.
    
    def execute(self, container: SovereignContainer):
        # [cite_start]We must implement 'execute' to satisfy the base transformation signature[cite: 145].
        pass
        
    def test_strict_method_enforcement(self):
        # We validate that the constitution intercepts illegal method additions.
        # If a developer attempts to add a forbidden method to a pipeline step,
        # the __init_subclass__ hook must raise a TypeError.
        
        # [cite_start]The expected behavior is an explicit exception with a "CONSTITUTION VIOLATION" message[cite: 145].
        with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
            class RogueStep(StepInterface):
                def execute(self, container):
                    pass
                
                # [cite_start]This helper method is strictly forbidden under the constitution[cite: 145].
                def hidden_helper(self):
                    pass

        # If the exception is raised correctly, it guarantees our pipeline 
        # steps remain pure, sequential, and stateless.