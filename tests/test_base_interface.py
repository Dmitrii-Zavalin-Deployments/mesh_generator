# tests/test_base_interface.py
import pytest

from interfaces.base_interface import StepInterface


def test_step_interface_valid_subclass():
    """Verifies that a subclass implementing only 'execute' passes structural validation."""
    class ValidStep(StepInterface):
        def execute(self, container):
            pass
    
    assert issubclass(ValidStep, StepInterface)


def test_step_interface_constitutional_violation_extra_method():
    """Verifies that introducing unauthorized helper methods raises a TypeError constitution violation."""
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
        class InvalidStep(StepInterface):
            def execute(self, container):
                pass
            
            def unauthorized_helper(self):
                return True


def test_step_interface_direct_invocation_not_implemented():
    """Verifies that direct execution on the abstract StepInterface base raises NotImplementedError."""
    step = StepInterface()
    with pytest.raises(NotImplementedError):
        step.execute(None)
