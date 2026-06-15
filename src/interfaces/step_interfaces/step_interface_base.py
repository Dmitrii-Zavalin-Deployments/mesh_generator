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

        # 1. Read the configuration
        allowed = getattr(cls, 'ALLOWED_MEMBERS', {"run"})

        # 2. Validate all members
        for name, value in cls.__dict__.items():
            if name.startswith("__"):
                continue
            
            # Now we don't have to skip "ALLOWED_MEMBERS" because 
            # we aren't checking the dict keys directly for configuration
            if name not in allowed and name != "ALLOWED_MEMBERS":
                raise TypeError(
                    f"CONSTITUTION VIOLATION: Subclass '{cls.__name__}' is strictly "
                    f"prohibited from defining custom member '{name}'."
                )

    def run(self, state, config):
        """
        Transform the Sovereign Container by computing exactly one
        schema‑level property. Must not perform any other computation
        or mutation.
        """
        raise NotImplementedError