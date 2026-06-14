class ComputeBoundaryConditionLocationTestSignature:
    """
    Contract‑level signature for validating ComputeBoundaryConditionLocationInterface (S12.i.1).

    This signature defines all required Sensitivity, Physics & Math, and
    Consistency validation responsibilities for the step that computes:

        results.boundary_conditions[i].location

    No logic, no assertions, and no execution may appear in this file.
    All methods must raise NotImplementedError.

    This signature maps directly and exclusively to the behaviour defined in
    ComputeBoundaryConditionLocationInterface:

        Consumes:
            - parsed geometry (internal B‑Rep shape)
            - results.grid.x_min / x_max
            - results.grid.y_min / y_max
            - results.grid.z_min / z_max
            - runtime configuration parameters
            - boundary‑condition index (int)

        Produces:
            - results.boundary_conditions[index].location

        Allowed output values:
            "x_min", "x_max",
            "y_min", "y_max",
            "z_min", "z_max",
            "wall"

        Requirements:
            - compute exactly one schema‑level property
            - read only previously‑computed properties
            - write exactly one property
            - perform no other mutation
            - contain no implementation logic here
            - enforce the Single‑Responsibility Rule
    """

    # ----------------------------------------------------------------------
    # 3.2.1 — Sensitivity Gate Signatures
    # ----------------------------------------------------------------------

    def test_sensitivity_missing_required_inputs(self):
        """
        The step must detect when any required input is missing:
            - parsed geometry
            - grid extents (x_min, x_max, y_min, y_max, z_min, z_max)
            - configuration parameters
            - boundary‑condition index

        The location must not be computed if any prerequisite is missing.
        """
        raise NotImplementedError

    def test_sensitivity_invalid_index(self):
        """
        The step must detect invalid boundary‑condition indices:
            - negative indices
            - indices outside the valid range
            - non‑integer indices
        """
        raise NotImplementedError

    def test_sensitivity_invalid_types(self):
        """
        The step must detect invalid types for:
            - grid extents (must be floats)
            - geometry object (must be a valid B‑Rep shape)
            - configuration parameters (must match declared types)
            - index (must be int)
        """
        raise NotImplementedError

    def test_sensitivity_invalid_numeric_ranges(self):
        """
        The step must detect invalid numeric ranges such as:
            - x_min > x_max
            - y_min > y_max
            - z_min > z_max
            - degenerate bounding boxes
        """
        raise NotImplementedError

    def test_sensitivity_schema_alignment(self):
        """
        The step must write exactly one field:
            results.boundary_conditions[index].location

        It must not write:
            - type
            - values
            - any other boundary‑condition field
            - any grid field
            - mask
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

    def test_physics_location_classification_validity(self):
        """
        The computed location must correspond to the geometric surface’s
        actual position relative to the global bounding box.

        Physically inconsistent classifications must be detected.
        """
        raise NotImplementedError

    def test_physics_allowed_location_values(self):
        """
        The output must be one of:
            "x_min", "x_max",
            "y_min", "y_max",
            "z_min", "z_max",
            "wall"

        Any other value must be rejected.
        """
        raise NotImplementedError

    def test_physics_geometry_empty_or_degenerate(self):
        """
        If the geometry is empty, degenerate, or invalid,
        the step must detect this and fail gracefully.
        """
        raise NotImplementedError

    def test_physics_tolerance_usage(self):
        """
        The step must use configuration tolerance consistently when
        determining whether a surface lies on a domain face.
        """
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 3.2.3 — Consistency Gate Signatures
    # ----------------------------------------------------------------------

    def test_consistency_single_responsibility(self):
        """
        The step must compute exactly one schema‑level property:
            results.boundary_conditions[index].location

        No other field may be modified.
        """
        raise NotImplementedError

    def test_consistency_no_cross_step_corruption(self):
        """
        The step must not corrupt or overwrite values computed by:
            - S1–S11 (geometry, grid, mask)
            - S12.i.2 (type)
            - S12.i.3 (values)
        """
        raise NotImplementedError

    def test_consistency_deterministic_output(self):
        """
        Given the same inputs (geometry, grid extents, config, index),
        the step must always compute the same location value
        (deterministic behaviour).
        """
        raise NotImplementedError

    def test_consistency_pipeline_progression(self):
        """
        S12.i.1 must execute only after:
            - S1 (geometry)
            - S2–S7 (grid extents)
            - S8–S10 (nx, ny, nz)
            - S11 (mask)

        No downstream boundary‑condition step may execute until the
        location is computed.
        """
        raise NotImplementedError