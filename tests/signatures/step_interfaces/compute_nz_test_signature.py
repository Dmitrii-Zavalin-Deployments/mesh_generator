class ComputeNzTestSignature:
    """
    Contract‑level signature for validating ComputeNzInterface (S10).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the step that computes:

        results.grid.nz

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the behaviour defined in
    ComputeNzInterface:

        Consumes:
            - results.grid.z_min
            - results.grid.z_max
            - runtime configuration parameters (MeshGeneratorConfigInterface)

        Produces:
            - state.results_grid["nz"]

        Requirements:
            - compute exactly one schema‑level property
            - read only previously‑computed properties
            - write exactly one property
            - perform no other mutation
            - contain no implementation logic here

    These signatures define WHAT must be validated during Phase 6,
    not HOW validation is performed.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_inputs(self):
        """
        The step must detect when any required input is missing:
            - results.grid.z_min
            - results.grid.z_max
            - configuration parameters (tolerance, min/max element size)

        nz must not be computed if any prerequisite is missing.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_types(self):
        """
        The step must detect invalid types for:
            - z_min, z_max (must be floats)
            - configuration parameters (must be floats or strings as defined)

        Invalid types must be rejected.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_numeric_ranges(self):
        """
        The step must detect invalid numeric ranges such as:
            - z_min > z_max
            - negative or zero element sizes
            - invalid tolerance values

        nz must not be computed in these cases.
        """
        raise NotImplementedError

    def test_sensitivity_schema_alignment(self):
        """
        The step must write exactly one field:
            results.grid.nz

        It must not write:
            - nx, ny
            - x_min, x_max
            - y_min, y_max
            - z_min, z_max
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

    def test_physics_resolution_computation_validity(self):
        """
        The computed nz must be physically meaningful and consistent with:
            - bounding box size (z_max - z_min)
            - configuration parameters (min/max element size)
            - solver stability constraints

        Physically impossible nz values must be detected.
        """
        raise NotImplementedError

    def test_physics_invalid_numeric_value(self):
        """
        nz must be a positive integer.
        NaN, infinity, zero, negative, or non‑integer values must be rejected.
        """
        raise NotImplementedError

    def test_physics_geometry_empty(self):
        """
        If z_min == z_max (zero‑thickness geometry), the step must detect
        this and fail gracefully.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_single_responsibility(self):
        """
        The step must compute exactly one schema‑level property:
            results.grid.nz

        No other field may be modified.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        The step must not corrupt or overwrite values computed by:
            - S1–S7 (geometry and bounding box)
            - S8 (nx)
            - S9 (ny)
            - S11–S12 (mask, boundary conditions)
        """
        raise NotImplementedError

    def test_consistency_deterministic_output(self):
        """
        Given the same inputs (z_min, z_max, config), the step must always
        compute the same nz value (deterministic behaviour).
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        S10 must execute only after S9 has successfully computed ny.
        No downstream step may execute until nz is computed.
        """
        raise NotImplementedError