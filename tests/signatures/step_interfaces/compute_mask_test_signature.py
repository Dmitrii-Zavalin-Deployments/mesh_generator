class ComputeMaskTestSignature:
    """
    Contract‑level signature for validating ComputeMaskInterface (S11).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the step that computes:

        results.mask   (flattened 1D array of ints in {-1, 0, 1})

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the behaviour defined in
    ComputeMaskInterface:

        Consumes:
            - parsed geometry (internal B‑Rep shape from S1)
            - results.grid.nx
            - results.grid.ny
            - results.grid.nz

        Produces:
            - state.results_mask

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
            - parsed geometry (from S1)
            - results.grid.nx
            - results.grid.ny
            - results.grid.nz

        The mask must not be computed if any prerequisite is missing.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_types(self):
        """
        The step must detect invalid types for:
            - nx, ny, nz (must be positive integers)
            - geometry object (must be a valid B‑Rep shape)

        Invalid types must be rejected.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_numeric_ranges(self):
        """
        The step must detect invalid numeric ranges such as:
            - nx, ny, nz <= 0
            - extremely large grid sizes that exceed memory constraints

        Mask computation must not proceed in these cases.
        """
        raise NotImplementedError

    def test_sensitivity_schema_alignment(self):
        """
        The step must write exactly one field:
            results.mask

        It must not write:
            - grid bounding box values
            - nx, ny, nz
            - boundary conditions
            - any other schema‑level property
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

    def test_physics_mask_value_validity(self):
        """
        The mask must contain only values in {-1, 0, 1}:
            - -1 : solid
            -  0 : fluid interior
            -  1 : boundary‑adjacent

        Any other value must be rejected.
        """
        raise NotImplementedError

    def test_physics_geometry_classification_validity(self):
        """
        The step must classify each grid cell consistently with:
            - point‑in‑solid tests
            - distance‑to‑surface thresholds
            - geometric validity of the B‑Rep shape

        Physically inconsistent classifications must be detected.
        """
        raise NotImplementedError

    def test_physics_mask_length_correctness(self):
        """
        The mask length must equal:
            nx * ny * nz

        Any mismatch must be detected.
        """
        raise NotImplementedError

    def test_physics_empty_or_degenerate_geometry(self):
        """
        If the geometry is empty, degenerate, or invalid,
        the step must detect this and fail gracefully.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_single_responsibility(self):
        """
        The step must compute exactly one schema‑level property:
            results.mask

        No other field may be modified.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        The step must not corrupt or overwrite values computed by:
            - S1–S10 (geometry, bounding box, nx/ny/nz)
            - S12 (boundary conditions)
        """
        raise NotImplementedError

    def test_consistency_deterministic_output(self):
        """
        Given the same inputs (geometry, nx, ny, nz),
        the step must always compute the same mask array
        (deterministic behaviour).
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        S11 must execute only after S10 has successfully computed nz.
        No downstream step may execute until the mask is computed.
        """
        raise NotImplementedError
