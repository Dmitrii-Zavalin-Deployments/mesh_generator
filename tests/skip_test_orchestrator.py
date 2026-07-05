# tests/test_orchestrator.py
from unittest.mock import MagicMock, call
from src.pipeline.orchestrator import Orchestrator
from src.state.mesh_generator_state import SovereignContainer
from interfaces.base_interface import StepInterface

# --- LITERATE TEST SUITE ---

def test_orchestrator_initialization():
    """
    [INITIALIZATION PATH]
    Verify that the Orchestrator correctly registers the pipeline steps 
    upon instantiation, ensuring the sequencer state is set correctly.
    """
    # 1. Setup: Create a mock list of steps.
    mock_step_1 = MagicMock(spec=StepInterface)
    mock_step_2 = MagicMock(spec=StepInterface)
    steps = [mock_step_1, mock_step_2]
    
    # 2. Execution: Instantiate the Orchestrator.
    orchestrator = Orchestrator(steps)
    
    # 3. Verification: Ensure steps are stored and length is correct.
    assert len(orchestrator.steps) == 2
    assert orchestrator.steps[0] == mock_step_1

def test_orchestrator_execution_flow():
    """
    [EXECUTION PATH]
    Verify that the orchestrator executes steps in the defined order 
    and passes the SovereignContainer through the pipeline without mutation.
    """
    
    # 1. Setup: Define the SovereignContainer and two mock steps.
    container = SovereignContainer(
        step_file="test.step",
        max_element_size=0.5,
        solver_version="v1.0.0",
        tolerance=1e-6,
        min_element_size=0.1,
        boundary_map={}
    )
    
    # We use MagicMocks to track the order of calls.
    step_a = MagicMock(spec=StepInterface)
    step_b = MagicMock(spec=StepInterface)
    
    manager = MagicMock()
    manager.attach_mock(step_a.execute, 'step_a')
    manager.attach_mock(step_b.execute, 'step_b')
    
    # 2. Execution: Run the orchestrator.
    orchestrator = Orchestrator([step_a, step_b])
    result = orchestrator.run(container)
    
    # 3. Verification:
    # A. The Orchestrator returns the same container object.
    assert result is container
    
    # B. The execution order is preserved (Sequential Integrity).
    # We use a manager to record the calls to verify the sequence explicitly.
    
    # Re-run to verify sequence with manager (or just check the mock calls history)
    # Since we already ran it, we check the call history:
    expected_calls = [
        call.step_a(container),
        call.step_b(container)
    ]
    assert manager.mock_calls == expected_calls
    
    # Verify both steps were executed
    step_a.execute.assert_called_once_with(container)
    step_b.execute.assert_called_once_with(container)