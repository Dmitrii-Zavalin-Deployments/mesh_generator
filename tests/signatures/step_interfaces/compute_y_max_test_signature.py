class ComputeYMaxTestSignature:
    """
    Contract‑level signature for validating ComputeYMaxInterface (S5).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the step that computes:

        results.grid.y_max

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the behaviour defined in
    ComputeYMaxInterface:

        - Consumes: parsed geometry (internal, not stored in the Sovereign Container)
        - Produces: state.results_grid["y_max"]
        - Must compute exactly one schema‑level property
        - Must not mutate any other part of the Sovereign Container

    These signatures define WHAT must be validated during Phase 6,
    not HOW validation is performed.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_geometry(self):
        """
        The step must detect when the internal parsed geometry (from S1)
        is missing, invalid, or unavailable. It must not compute y_max
        without valid geometry.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_geometry_structure(self):
        """
        The step must detect malformed or incomplete geometry structures
        (e.g., missing surfaces, invalid topology).
        """
        raise NotImplementedError

    def test_sensitivity_schema_alignment(self):
        """
        The step must write exactly one field:
            results.grid.y_max

        It must not write:
            - y_min
            - x_min, x_max
            - z_min, z_max
            - nx, ny, nz
            - mask
            - boundary conditions
        """
        raise NotImplementedError

    def test_sensitivity_no_extra_fields(self):
        """
        The step must not introduce any fields beyond those declared in
        MeshGeneratorStateInterface. Extra fields must cause failure.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Signatures
    # ----------------------------------------------------------------------

    def test_physics_bounding_box_extraction(self):
        """
        The computed y_max must correspond to the maximum y‑coordinate
        of the parsed geometry's bounding box.
        Physically inconsistent values must be detected.
        """
        raise NotImplementedError

    def test_physics_invalid_numeric_value(self):
        """
        y_max must be a finite float.
        NaN, infinity, or malformed numeric values must be rejected.
        """
        raise NotImplementedError

    def test_physics_geometry_empty(self):
        """
        If the geometry contains no valid points or surfaces,
        the step must detect this and fail gracefully.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_single_responsibility(self):
        """
        The step must compute exactly one schema‑level property:
            results.grid.y_max

        No other field may be modified.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        The step must not corrupt or overwrite values computed by:
            - S1 (geometry)
            - S2 (x_min)
            - S3 (x_max)
            - S4 (y_min)
            - S6–S12 (other grid fields, mask, boundary conditions)
        """
        raise NotImplementedError

    def test_consistency_deterministic_output(self):
        """
        Given the same geometry input, the step must always compute the
        same y_max value (deterministic behaviour).
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        S5 must execute only after S4 has successfully computed y_min.
        No downstream step may execute until y_max is computed.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2 — Global Step‑Level Validation Responsibilities
    # ----------------------------------------------------------------------

    def test_global_no_computation_before_validation(self):
        """
        The pipeline must refuse to run S5 if validation of the geometry
        or state fails. No computation may occur before validation.
        """
        raise NotImplementedError

    def test_global_no_schema_mutation(self):
        """
        The step must not mutate any schema‑level property other than
        results.grid.y_max. Any additional mutation must cause failure.
        """
        raise NotImplementedError