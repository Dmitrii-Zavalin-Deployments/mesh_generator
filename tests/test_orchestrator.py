# tests/test_orchestrator.py

from interfaces.base_interface import StepInterface
from src.pipeline.orchestrator import Orchestrator
from src.state.mesh_generator_state import SovereignContainer
from tests.dummies.dummy_harness import dummy_in, get_mock_config


class DummyStep(StepInterface):
    """Mock processing step conforming to StepInterface for testing sequence execution."""
    def __init__(self, name: str, modifier_func=None):
        self.name = name
        self.modifier_func = modifier_func
        self.executed_count = 0

    def execute(self, container: SovereignContainer):
        self.executed_count += 1
        if self.modifier_func:
            self.modifier_func(container)


def test_orchestrator_initialization():
    """Verifies that the Orchestrator initializes correctly with an ordered sequence of steps."""
    step1 = DummyStep("step1")
    step2 = DummyStep("step2")
    orchestrator = Orchestrator([step1, step2])
    
    assert orchestrator.steps == [step1, step2]


def test_orchestrator_run_sequential_execution():
    """Verifies that Orchestrator runs steps in strict order and passes the SovereignContainer through."""
    d_in = dummy_in()
    config = get_mock_config()
    
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    execution_order = []

    def modify_1(c):
        execution_order.append("step1")
        c.bbox = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)

    def modify_2(c):
        execution_order.append("step2")
        c.mask = [1, 0, 1]

    step1 = DummyStep("step1", modify_1)
    step2 = DummyStep("step2", modify_2)

    orchestrator = Orchestrator([step1, step2])
    result_container = orchestrator.run(container)

    assert result_container is container
    assert step1.executed_count == 1
    assert step2.executed_count == 1
    assert execution_order == ["step1", "step2"]
    assert container.bbox == (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    assert container.mask == [1, 0, 1]


def test_orchestrator_empty_steps():
    """Verifies that Orchestrator safely executes with an empty step sequence."""
    d_in = dummy_in()
    config = get_mock_config()
    
    container = SovereignContainer(
        step_file=d_in["inputs"]["step_file"],
        max_element_size=config["max_element_size"],
        tolerance=config["tolerance"],
        min_element_size=config["min_element_size"]
    )

    orchestrator = Orchestrator([])
    result_container = orchestrator.run(container)

    assert result_container is container
