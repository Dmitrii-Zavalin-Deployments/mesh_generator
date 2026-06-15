class StepInterfaceBase:
    """
    Base contract‑only interface for all Mesh Generator steps.
    Subclasses may only define the allowed method name.

    This interface enforces the Constitution by prohibiting subclasses
    from defining any methods or attributes not explicitly declared
    in the interface contract.
    """

    # Only one allowed member for all step interfaces
    ALLOWED_MEMBERS = {"run"}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Inspect subclass for Constitution violations
        for name in cls.__dict__:
            # Skip magic methods (e.g., __init__, __doc__)
            if name.startswith("__"):
                continue
            
            # Skip the meta-definition itself
            if name == "ALLOWED_MEMBERS":
                continue

            # Verify that the attribute is part of the allowed contract
            if name not in cls.ALLOWED_MEMBERS:
                raise TypeError(
                    f"CONSTITUTION VIOLATION: Subclass '{cls.__name__}' is strictly "
                    f"prohibited from defining custom member '{name}'. "
                    f"Allowed interface members are: {cls.ALLOWED_MEMBERS}"
                )

    def run(self, state, config):
        """
        Transform the Sovereign Container by computing exactly one
        schema‑level property. Must not perform any other computation
        or mutation.
        """
        raise NotImplementedError