class MeshGeneratorConfigTestSignature:
    """
    Contract‑level signature for validating MeshGeneratorConfigInterface.

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the runtime configuration
    injected into steps S8–S12.

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the fields declared in
    MeshGeneratorConfigInterface:

        solver_version: str
        tolerance: float
        max_element_size: float
        min_element_size: float

    These signatures define WHAT must be validated during Phase 6,
    not HOW validation is performed.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_fields(self):
        """
        All required configuration fields must be present:
            - solver_version
            - tolerance
            - max_element_size
            - min_element_size

        Missing fields must be detected before any step (S8–S12) executes.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_types(self):
        """
        All configuration fields must match the declared types:
            - solver_version: str
            - tolerance: float
            - max_element_size: float
            - min_element_size: float

        Invalid types must be rejected.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_numeric_ranges(self):
        """
        Numeric fields must be finite floats.
        NaN, infinity, or malformed numeric values must be rejected.
        """
        raise NotImplementedError

    def test_sensitivity_element_size_relationship(self):
        """
        max_element_size must be >= min_element_size.
        Invalid or inverted ranges must be detected.
        """
        raise NotImplementedError

    def test_sensitivity_schema_alignment(self):
        """
        The configuration structure must match the schema exactly.
        No extra fields, no missing fields, no schema drift.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Signatures
    # ----------------------------------------------------------------------

    def test_physics_tolerance_validity(self):
        """
        tolerance must be physically meaningful:
            - non‑negative
            - sufficiently small for geometric comparisons

        Physically impossible tolerance values must be detected.
        """
        raise NotImplementedError

    def test_physics_element_size_validity(self):
        """
        max_element_size and min_element_size must be physically meaningful:
            - strictly positive
            - consistent with solver stability limits

        Invalid element sizes must be detected.
        """
        raise NotImplementedError

    def test_physics_resolution_constraints(self):
        """
        Element sizes must be consistent with grid resolution constraints
        used in S8–S10. Physically impossible combinations must be detected.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_predictable_structure(self):
        """
        The configuration structure must remain stable and predictable across
        all steps. No step may mutate configuration fields.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        Configuration values must not be overwritten or corrupted by any step.
        They must remain constant throughout the pipeline.
        """
        raise NotImplementedError

    def test_consistency_no_uninitialized_fields(self):
        """
        All configuration fields must be explicitly initialized before use.
        No field may remain undefined at any stage of the pipeline.
        """
        raise NotImplementedError