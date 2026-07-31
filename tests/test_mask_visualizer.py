from unittest.mock import patch

from src.utils.mask_visualizer import generate_mask_snapshot


def test_generate_mask_snapshot_missing_grid_or_mask(caplog):
    """Verifies early return and warning logs when grid or mask data is missing."""
    # Missing grid
    generate_mask_snapshot({"results": {"mask": [1, 0]}})
    assert "Voxel visualizer skipped" in caplog.text

    # Missing mask
    grid = {"nx": 1, "ny": 1, "nz": 1, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1}
    generate_mask_snapshot({"results": {"grid": grid}})

    # Empty dictionary
    generate_mask_snapshot({})


def test_generate_mask_snapshot_path_resolutions(tmp_path):
    """Verifies dynamic path resolution branches: mesh_snapshot_path, fallback_save_dir, and default cwd."""
    grid = {"nx": 1, "ny": 1, "nz": 1, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1}
    mask = [1]

    # 1. mesh_snapshot_path provided
    custom_snap = tmp_path / "custom_sub" / "mesh_snap.png"
    data1 = {"results": {"grid": grid, "mask": mask, "mesh_snapshot_path": str(custom_snap)}}
    generate_mask_snapshot(data1)
    assert (tmp_path / "custom_sub").exists()

    # 2. fallback_save_dir provided
    fallback_dir = tmp_path / "fallback_folder"
    data2 = {"results": {"grid": grid, "mask": mask}}
    generate_mask_snapshot(data2, fallback_save_dir=str(fallback_dir))
    assert fallback_dir.exists()

    # 3. Neither provided (defaults to cwd)
    cwd_dir = tmp_path / "cwd_folder"
    cwd_dir.mkdir(exist_ok=True)
    with patch("os.getcwd", return_value=str(cwd_dir)):
        generate_mask_snapshot(data2)
        assert cwd_dir.exists()


def test_generate_mask_snapshot_striding_large_voxels(tmp_path):
    """Verifies striding branch when total voxels exceed 1,000,000 (stride = 4)."""
    # 101 * 100 * 100 = 1,010,000 > 1,000,000
    grid = {"nx": 101, "ny": 100, "nz": 100, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1}
    mask = [1] * (101 * 100 * 100)
    generate_mask_snapshot({"results": {"grid": grid, "mask": mask}}, fallback_save_dir=str(tmp_path))


def test_generate_mask_snapshot_striding_axis_ceiling(tmp_path):
    """Verifies striding branch when an axis exceeds MAX_AXIS_CEILING (stride = 2)."""
    # nx = 160 > 150, total voxels < 1,000,000 (160 * 10 * 10 = 16,000)
    grid = {"nx": 160, "ny": 10, "nz": 10, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1}
    mask = [1] * (160 * 10 * 10)
    generate_mask_snapshot({"results": {"grid": grid, "mask": mask}}, fallback_save_dir=str(tmp_path))


def test_generate_mask_snapshot_color_mapping_and_success(tmp_path):
    """Verifies successful rendering covering fluid (1), solid (0), wall (-1), and ignored (999) values."""
    grid = {"nx": 2, "ny": 2, "nz": 1, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1}
    # 2 * 2 * 1 = 4 voxels containing values 1, 0, -1, 999
    mask = [1, 0, -1, 999]
    data = {"results": {"grid": grid, "mask": mask}}
    generate_mask_snapshot(data, fallback_save_dir=str(tmp_path))
    assert (tmp_path / "voxel_mask_verification.png").exists()


def test_generate_mask_snapshot_reshape_error(tmp_path, caplog):
    """Verifies exception handling for lattice dimension mismatch (reshape error)."""
    grid = {"nx": 2, "ny": 2, "nz": 2, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1}
    # Expected 8 elements, but providing 3
    bad_mask = [1, 2, 3]
    generate_mask_snapshot({"results": {"grid": grid, "mask": bad_mask}}, fallback_save_dir=str(tmp_path))
    assert "Lattice dimension mismatch" in caplog.text


def test_generate_mask_snapshot_timeout_error(tmp_path, caplog):
    """Verifies exception handling for timeout errors."""
    grid = {"nx": 2, "ny": 2, "nz": 2, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1}
    with patch("numpy.array", side_effect=RuntimeError("Operation timeout occurred in background routine")):
        generate_mask_snapshot({"results": {"grid": grid, "mask": [1]*8}}, fallback_save_dir=str(tmp_path))
        assert "Non-blocking visualization capture routine failure" in caplog.text


def test_generate_mask_snapshot_general_error(tmp_path, caplog):
    """Verifies exception handling for general unexpected errors."""
    grid = {"nx": 2, "ny": 2, "nz": 2, "x_min": 0, "x_max": 1, "y_min": 0, "y_max": 1, "z_min": 0, "z_max": 1}
    with patch("numpy.array", side_effect=TypeError("Unexpected type error occurred")):
        generate_mask_snapshot({"results": {"grid": grid, "mask": [1]*8}}, fallback_save_dir=str(tmp_path))
        assert "Visualization failure" in caplog.text
