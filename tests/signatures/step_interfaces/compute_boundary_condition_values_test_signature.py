class ComputeBoundaryConditionValuesTestSignature:
    """
    Contract‑level signature for validating ComputeBoundaryConditionValuesInterface (S12.i.3).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the step that computes:

        results.boundary_conditions[i].values

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the behaviour defined in
    ComputeBoundaryConditionValuesInterface:

        Consumes:
            - results.boundary_conditions[i].type
            - configuration parameters (MeshGeneratorConfigInterface)
            - solver‑specific conventions (via config)
            - boundary‑condition index (int)

        Produces:
            - results.boundary_conditions[index].values

        Requirements:
            - compute exactly one schema‑level property
            - read only previously‑computed properties
            - write exactly one property
            - perform no other mutation
            - contain no implementation logic here
            - enforce the Single‑Responsibility Rule
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_inputs(self):
        """
        The step must detect when any required input is missing:
            - boundary_conditions[index].type
            - configuration parameters
            - solver‑specific conventions
            - boundary‑condition index

        The values must not be computed if any prerequisite is missing.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_index(self):
        """
        The step must detect invalid boundary‑condition indices:
            - negative indices
            - indices outside the valid range
            - non‑integer indices
        """
        raise NotImplementedError

    def test_sensitivity_invalid_types(self):
        """
        The step must detect invalid types for:
            - type (must be a valid solver‑defined BC type)
            - configuration parameters (must match declared types)
            - index (must be int)
        """
        raise NotImplementedError

    def test_sensitivity_invalid_type_values(self):
        """
        The step must detect invalid boundary‑condition types.
        Allowed types are defined by the solver conventions in config.
        Any other value must be rejected.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Signatures
    # ----------------------------------------------------------------------

    def test_physics_value_assignment_validity(self):
        """
        The computed values must be physically and mathematically consistent
        with:
            - the boundary condition type
            - solver conventions (e.g., inflow/outflow rules)
            - configuration parameters

        Physically inconsistent values must be detected.
        """
        raise NotImplementedError

    def test_physics_allowed_value_formats(self):
        """
        The output values must match the solver‑defined format:
            - scalar
            - vector
            - tuple
            - list
            - or other solver‑specific structure

        Any deviation must be rejected.
        """
        raise NotImplementedError

    def test_physics_invalid_numeric_values(self):
        """
        Values must not contain:
            - NaN
            - infinity
            - physically impossible magnitudes

        Such values must be rejected.
        """
        raise NotImplementedError

    def test_physics_solver_convention_enforcement(self):
        """
        The step must enforce solver‑specific conventions such as:
            - inflow velocity direction
            - pressure boundary rules
            - no‑slip wall conditions
            - symmetry plane constraints

        Violations must be detected.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_single_responsibility(self):
        """
        The step must compute exactly one schema‑level property:
            results.boundary_conditions[index].values

        No other field may be modified.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        The step must not corrupt or overwrite values computed by:
            - S1–S11 (geometry, grid, mask)
            - S12.i.1 (location)
            - S12.i.2 (type)
        """
        raise NotImplementedError

    def test_consistency_deterministic_output(self):
        """
        Given the same inputs (type, config, index),
        the step must always compute the same values
        (deterministic behaviour).
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        S12.i.3 must execute only after:
            - S12.i.2 (type)

        No downstream pipeline step may execute until the
        values are computed.
        """
        raise NotImplementedError