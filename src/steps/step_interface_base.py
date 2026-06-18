"""
src/steps/step_interface_base.py

Architectural enforcement base class.
This file is the root of the Step hierarchy and ensures all steps
strictly adhere to the "Single Responsibility" contract.
"""

class StepInterfaceBase:
    """
    Base class for all pipeline steps.
    
    Uses __init_subclass__ to enforce the 'ALLOWED_MEMBERS' contract.
    Any attempt to add unauthorized methods or logic to a subclass
    will trigger an immediate TypeError at runtime (startup).
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        # Retrieve the allowed members from the subclass (default to empty set)
        allowed = getattr(cls, "ALLOWED_MEMBERS", set())
        
        # Inspect the class namespace for methods
        for name, value in cls.__dict__.items():
            # Check if it's a method/function (excluding internal dunder methods)
            if callable(value) and not name.startswith("__"):
                if name not in allowed:
                    raise TypeError(
                        f"Architectural Violation in {cls.__name__}: "
                        f"Method '{name}' is not permitted. "
                        f"Allowed members: {allowed}"
                    )

    def run(self, *args, **kwargs) -> None:
        """
        The entry point for every step. 
        Implementations must override this method.
        """
        raise NotImplementedError("Each step implementation must provide its own 'run' method.")