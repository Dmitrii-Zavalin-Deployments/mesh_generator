class ParseStepGeometryTestSignature:
    """
    Contract-level signature for validating ParseStepGeometryInterface (S1).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the geometry-parsing step.

    This signature maps to the behaviour of the updated ParseStepGeometryStep:
        - Consumes: state.inputs_step_file (must be a valid .step file)
        - Produces: GeometryModel (containing TopoDS_Shape and spatial bounds)

    These signatures define WHAT must be validated during Phase 6.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_input_file(self):
        """
        The step must detect when state.inputs_step_file is missing,
        empty, or points to a non-existent path. Parsing must not proceed.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_file_type(self):
        """
        The step must detect invalid file types.
        Only valid STEP files (ISO 10303) may be accepted.
        """
        raise NotImplementedError

    def test_sensitivity_malformed_step_file(self):
        """
        The step must detect malformed STEP files that cannot be 
        interpreted by the OpenCASCADE reader and fail gracefully.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Signatures
    # ----------------------------------------------------------------------

    def test_physics_geometry_topology_validity(self):
        """
        The parsed geometry must be physically meaningful:
            - The TopoDS_Shape must be valid (not null).
            - The bounding box must be calculated correctly using Bnd_Box.
        """
        raise NotImplementedError

    def test_physics_geometry_non_empty(self):
        """
        The step must detect when the STEP file contains no geometry.
        An empty shape must be treated as a critical failure.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_geometry_model_returned(self):
        """
        The step must return an instance of GeometryModel.
        Verifying it is not a dictionary or a raw list.
        """
        raise NotImplementedError

    def test_consistency_no_schema_mutation(self):
        """
        The step must NOT write or modify any schema-level fields:
            - results_grid
            - results_mask
        It should only return the GeometryModel.
        """
        raise NotImplementedError

    def test_consistency_deterministic_parsing(self):
        """
        Parsing the same valid STEP file must always produce the same
        GeometryModel attributes (deterministic bounding box and shape).
        """
        raise NotImplementedError