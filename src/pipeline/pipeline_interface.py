class PipelineInterface:
    """
    The Global State View. 
    A composite interface that allows coherence signatures to access 
    all critical artifacts of the system at once.
    """
    @property
    def geometry(self): raise NotImplementedError

    @property
    def results_grid(self): raise NotImplementedError

    @property
    def mask(self): raise NotImplementedError

    @property
    def boundary_conditions(self): raise NotImplementedError