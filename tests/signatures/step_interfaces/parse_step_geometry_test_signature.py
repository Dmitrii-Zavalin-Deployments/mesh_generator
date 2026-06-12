class ParseStepGeometryTestSignature:
    """
    Contract‑level signature for validating ParseStepGeometryInterface (S1).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the geometry‑parsing step.

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the behaviour defined in
    ParseStepGeometryInterface:

        - Consumes: state.inputs_step_file
        - Produces: internal geometry object (NOT stored in the Sovereign Container)
        - Must NOT compute or mutate any schema‑level property

    These signatures define WHAT must be validated during Phase 6,
    not HOW validation is performed.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_input_file(self):
        """
        The step must detect when state.inputs_step_file is missing,
        empty, or undefined. Parsing must not proceed in this case.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_file_type(self):
        """
        The step must detect invalid file types.
        Only valid STEP files (.stp, .step) may be accepted.
        """
        raise NotImplementedError

    def test_sensitivity_file_not_found(self):
        """
        The step must detect when the referenced STEP file does not exist
        or cannot be accessed.
        """
        raise NotImplementedError

    def test_sensitivity_malformed_step_file(self):
        """
        The step must detect malformed or unreadable STEP files and fail
        gracefully without producing geometry.
        """
        raise NotImplementedError

    def test_sensitivity_schema_alignment(self):
        """
        The step must not read or write any schema‑level fields.
        It must only consume state.inputs_step_file.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Signatures
    # ----------------------------------------------------------------------

    def test_physics_geometry_validity(self):
        """
        The parsed geometry must be physically meaningful:
            - valid B‑Rep topology
            - valid surfaces and solids
            - no self‑intersections or invalid shapes

        Invalid geometry must be detected.
        """
        raise NotImplementedError

    def test_physics_empty_geometry(self):
        """
        The step must detect when the STEP file contains no usable geometry
        (empty shape, empty topology, etc.).
        """
        raise NotImplementedError

    def test_physics_geometry_normalization(self):
        """
        The step must ensure that the parsed geometry is normalized and
        suitable for downstream steps (S2–S12).
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_no_schema_mutation(self):
        """
        The step must NOT write or modify any schema‑level fields:
            - results_grid
            - results_mask
            - results_boundary_conditions

        Any mutation must be detected.
        """
        raise NotImplementedError

    def test_consistency_internal_geometry_storage(self):
        """
        The parsed geometry must be stored internally only.
        It must NOT be added to the Sovereign Container.
        """
        raise NotImplementedError

    def test_consistency_deterministic_parsing(self):
        """
        Parsing the same STEP file must always produce the same internal
        geometry representation (deterministic behaviour).
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        S1 must complete successfully before S2 begins.
        No downstream step may execute without valid parsed geometry.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2 — Global Step‑Level Validation Responsibilities
    # ----------------------------------------------------------------------

    def test_global_no_computation_before_validation(self):
        """
        The pipeline must refuse to run S1 if validation of the input file
        fails. No geometry parsing may occur before validation.
        """
        raise NotImplementedError

    def test_global_no_extra_fields(self):
        """
        ParseStepGeometryInterface must not define or use any fields beyond
        those declared in the interface. Extra fields must cause failure.
        """
        raise NotImplementedError