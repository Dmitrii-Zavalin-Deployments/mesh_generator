class BoundaryConditionValuesTestSignature:
    """
    Contract‑level signature for validating BoundaryConditionValuesInterface.

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the numeric boundary‑condition
    values object inside results.boundary_conditions[i].values.

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the fields declared in
    BoundaryConditionValuesInterface:

        u: float   (optional velocity component)
        v: float   (optional velocity component)
        w: float   (optional velocity component)
        p: float   (optional pressure value)

    These signatures define WHAT must be validated during Phase 6,
    not HOW validation is performed.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_invalid_types(self):
        """
        All provided values (u, v, w, p) must be floats.
        Non‑numeric or incompatible types must be rejected.
        """
        raise NotImplementedError

    def test_sensitivity_missing_required_fields_for_type(self):
        """
        Depending on the boundary condition type (validated elsewhere),
        certain fields may be required:

            - inflow: u, v, w required
            - outflow: p required
            - pressure: p required
            - no-slip: u = v = w = 0
            - free-slip: p = 0 (or solver default)

        Missing required values must be detected.
        """
        raise NotImplementedError

    def test_sensitivity_schema_alignment(self):
        """
        The values object must match the schema exactly.
        No extra fields, no missing fields, no schema drift.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_numeric_ranges(self):
        """
        Values must be finite floats.
        NaN, infinity, or malformed numeric values must be rejected.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Signatures
    # ----------------------------------------------------------------------

    def test_physics_velocity_vector_validity(self):
        """
        The velocity components (u, v, w), when present, must form a
        physically meaningful vector. Physically impossible values must
        be detected.
        """
        raise NotImplementedError

    def test_physics_pressure_validity(self):
        """
        Pressure value p, when present, must be physically meaningful.
        Negative or non‑physical pressure values must be detected.
        """
        raise NotImplementedError

    def test_physics_consistency_with_boundary_type(self):
        """
        The values must be physically consistent with the boundary type:
            - no-slip: u = v = w = 0
            - free-slip: p = 0 (or solver default)
            - inflow: velocity components required
            - outflow: pressure required
            - pressure: pressure required
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_predictable_structure(self):
        """
        The values object must maintain a predictable structure across all steps.
        No step may mutate unrelated fields.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        Values written by S12.i.3 must not be overwritten or corrupted by
        unrelated steps.
        """
        raise NotImplementedError

    def test_consistency_no_uninitialized_fields(self):
        """
        All fields must be explicitly initialized before use.
        No field may remain undefined at any stage of the pipeline.
        """
        raise NotImplementedError