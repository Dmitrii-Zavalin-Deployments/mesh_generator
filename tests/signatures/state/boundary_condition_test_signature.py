class BoundaryConditionTestSignature:
    """
    Contract‑level signature for validating BoundaryConditionInterface.

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for a single boundary condition
    entry inside results.boundary_conditions[i].

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the fields declared in
    BoundaryConditionInterface:

        location: str
            One of:
                "x_min", "x_max",
                "y_min", "y_max",
                "z_min", "z_max",
                "wall"

        type: str
            One of:
                "no-slip", "free-slip",
                "inflow", "outflow", "pressure"

        values: BoundaryConditionValuesInterface
            (u, v, w, p) — optional numeric fields

    These signatures define WHAT must be validated during Phase 6,
    not HOW validation is performed.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_fields(self):
        """
        Each boundary condition entry must contain:
            - location
            - type
            - values

        Missing fields must be detected before any computation begins.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_location_enum(self):
        """
        location must be one of:
            "x_min", "x_max",
            "y_min", "y_max",
            "z_min", "z_max",
            "wall"

        Any invalid or misspelled value must be rejected.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_type_enum(self):
        """
        type must be one of:
            "no-slip", "free-slip",
            "inflow", "outflow", "pressure"

        Any invalid or unsupported type must be rejected.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_values_structure(self):
        """
        values must match BoundaryConditionValuesInterface.
        Missing or malformed values must be detected.
        """
        raise NotImplementedError

    def test_sensitivity_schema_alignment(self):
        """
        The boundary condition structure must match the schema exactly.
        No extra fields, no missing fields, no schema drift.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Signatures
    # ----------------------------------------------------------------------

    def test_physics_location_consistency(self):
        """
        The location must be physically consistent with the geometry and
        grid extents computed in S2–S7.

        Physically impossible locations must be detected.
        """
        raise NotImplementedError

    def test_physics_type_consistency(self):
        """
        The type must be physically consistent with the location and solver
        conventions (e.g., inflow/outflow only on domain faces).
        """
        raise NotImplementedError

    def test_physics_values_numeric(self):
        """
        All provided values (u, v, w, p) must be numeric when present.
        Non‑numeric values must be rejected.
        """
        raise NotImplementedError

    def test_physics_values_required_for_type(self):
        """
        Certain boundary types require specific numeric fields:
            - inflow: u, v, w required
            - outflow: p required
            - pressure: p required
            - no-slip: u = v = w = 0
            - free-slip: p = 0 (or solver default)

        Missing required values must be detected.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_predictable_structure(self):
        """
        The boundary condition structure must remain stable and predictable
        across all steps. No step may mutate unrelated fields.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        Values written by S12.i.1 (location), S12.i.2 (type), and S12.i.3 (values)
        must not be overwritten or corrupted by unrelated steps.
        """
        raise NotImplementedError

    def test_consistency_no_uninitialized_fields(self):
        """
        All boundary condition fields must be explicitly initialized before use.
        No field may remain undefined at any stage of the pipeline.
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        Boundary condition fields must be computed in the correct order:
            S12.i.1 → S12.i.2 → S12.i.3

        No step may execute out of order or with incomplete prerequisites.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2 — Global Boundary‑Condition‑Level Validation Responsibilities
    # ----------------------------------------------------------------------

    def test_global_no_computation_before_validation(self):
        """
        The pipeline must refuse to run if any boundary condition entry
        fails validation. No computation may occur before validation.
        """
        raise NotImplementedError

    def test_global_no_extra_fields(self):
        """
        BoundaryConditionInterface must not contain any fields beyond:
            location, type, values

        Extra fields must cause immediate failure.
        """
        raise NotImplementedError