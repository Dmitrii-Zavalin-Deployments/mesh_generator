class ComputeXMaxTestSignature:
    """
    Contract‑level signature for validating ComputeXMaxInterface (S3).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the step that computes:

        results.grid.x_max

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the behaviour defined in
    ComputeXMaxInterface:

        - Consumes: parsed geometry (internal, not stored in the Sovereign Container)
        - Produces: state.results_grid["x_max"]
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
        is missing, invalid, or unavailable. It must not compute x_max
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
            results.grid.x_max

        It must not write:
            - x_min
            - y_min
            - y_max
            - z_min
            - z_max
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
        The computed x_max must correspond to the maximum x‑coordinate
        of the parsed geometry's bounding box.
        Physically inconsistent values must be detected.
        """
        raise NotImplementedError

    def test_physics_invalid_numeric_value(self):
        """
        x_max must be a finite float.
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
            results.grid.x_max

        No other field may be modified.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        The step must not corrupt or overwrite values computed by:
            - S1 (geometry)
            - S2 (x_min)
            - S4–S12 (other grid fields, mask, boundary conditions)
        """
        raise NotImplementedError

    def test_consistency_deterministic_output(self):
        """
        Given the same geometry input, the step must always compute the
        same x_max value (deterministic behaviour).
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        S3 must execute only after S2 has successfully computed x_min.
        No downstream step may execute until x_max is computed.
        """
        raise NotImplementedError