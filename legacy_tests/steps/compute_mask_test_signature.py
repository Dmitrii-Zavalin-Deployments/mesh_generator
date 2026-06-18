class ComputeMaskTestSignature:
    """
    Contract-level signature for validating ComputeMaskInterface (S11).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the step that computes:
        results.mask (a contiguous numpy.ndarray of int8)

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the behaviour defined in
    ComputeMaskInterface:

        Consumes:
            - geometry_model: GeometryModel (containing TopoDS_Shape)
            - results.grid.nx, ny, nz

        Produces:
            - state.results_mask (numpy.ndarray)

    These signatures define WHAT must be validated during Phase 6.
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_inputs(self):
        """
        The step must detect when any required input is missing:
            - geometry_model (instance of GeometryModel)
            - results.grid.nx, ny, nz

        The mask must not be computed if any prerequisite is missing.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_types(self):
        """
        The step must detect invalid types for:
            - nx, ny, nz (must be positive integers)
            - geometry_model (must be a valid GeometryModel instance)

        Invalid types must be rejected.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.2 — Physics & Math Gate Signatures
    # ----------------------------------------------------------------------

    def test_physics_mask_type_and_length_correctness(self):
        """
        The result must be a numpy.ndarray:
            - Type: numpy.ndarray
            - Dtype: numpy.int8
            - Size: nx * ny * nz

        Any mismatch in type, dtype, or size must be detected.
        """
        raise NotImplementedError

    def test_physics_mask_value_validity(self):
        """
        The mask must contain only values in {-1, 0, 1}, representing 
        canonical physical regions for Navier-Stokes:
            - -1 : Wall (Boundary Condition)
             0 : Solid
             1 : Fluid (Interior)

        Any other value must be rejected.
        """
        raise NotImplementedError

    def test_physics_geometry_classification_validity(self):
        """
        The step must classify each grid cell consistently with 
        BRepClass3d_SolidClassifier ray-casting against the 
        geometry_model.cad_solid.

        Physically inconsistent classifications must be detected.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_single_responsibility(self):
        """
        The step must compute exactly one schema-level property:
            results.mask

        No other field may be modified in the state.
        """
        raise NotImplementedError

    def test_consistency_deterministic_output(self):
        """
        Given the same inputs (GeometryModel, nx, ny, nz),
        the step must always compute the same numpy array
        (deterministic behaviour).
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        S11 must execute only after resolution (nx, ny, nz) 
        and geometry parsing (S1) are complete.
        """
        raise NotImplementedError