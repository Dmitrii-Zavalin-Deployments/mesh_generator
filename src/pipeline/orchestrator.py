# src/pipeline/orchestrator.py
from typing import List
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer

class Orchestrator:
    """
    The sole entity authorized to execute the solver.
    Governs sequencing and strictly passes state without modification.
    """
    __slots__ = ('steps',)

    def __init__(self, steps: List[StepInterface]):
        self.steps = steps

    def run(self, container: SovereignContainer) -> SovereignContainer:
        """
        Executes the pipeline. 
        Validation is implicit: if a step violates the constitution, 
        it would have failed at import/definition time.
        """
        for step in self.steps:
            # Governance: Orchestrator passes container, does not modify it.
            step.execute(container)
            
        return container