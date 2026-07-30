#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "1. DIAGNOSTICS: Ruff SIM117 Context Violations"
echo "=================================================="
# ruff check tests/ --select SIM117 || true

echo ""
echo "=================================================="
echo "2. SMOKING-GUN SOURCE AUDIT (cat -n)"
echo "=================================================="

echo "--- tests/skip_test_categorization.py (lines 98-135, 248-255) ---"
if [ -f "tests/skip_test_categorization.py" ]; then
    sed -n '98,105p;128,135p;248,255p' tests/skip_test_categorization.py | cat -n
fi

echo "--- tests/skip_test_main.py (lines 68-81, 180-196) ---"
if [ -f "tests/skip_test_main.py" ]; then
    sed -n '68,81p;180,196p' tests/skip_test_main.py | cat -n
fi

echo "--- tests/skip_test_resolution.py (lines 95-128) ---"
if [ -f "tests/skip_test_resolution.py" ]; then
    sed -n '95,128p' tests/skip_test_resolution.py | cat -n
fi

echo ""
echo "=================================================="
echo "3. AUTOMATED REPAIR INJECTIONS (Commented)"
echo "=================================================="

# --- SIM117 REPAIRS: tests/skip_test_categorization.py ---
# sed -i '100,101s/with patch.dict("sys.modules", {"gmsh": None}):/with patch.dict("sys.modules", {"gmsh": None}), pytest.raises(RuntimeError, match="Gmsh Python bindings missing"):/' tests/skip_test_categorization.py
# sed -i '101d' tests/skip_test_categorization.py

# sed -i '131,132s/with patch.dict("sys.modules", {"gmsh": mock_gmsh}):/with patch.dict("sys.modules", {"gmsh": mock_gmsh}), pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Gmsh failed to generate 3D tetrahedral elements"):/' tests/skip_test_categorization.py
# sed -i '132d' tests/skip_test_categorization.py

# sed -i '251,252s/with patch.dict("sys.modules", {"gmsh": mock_gmsh}):/with patch.dict("sys.modules", {"gmsh": mock_gmsh}), pytest.raises(Exception, match="Xvfb frame buffer allocation timeout"):/' tests/skip_test_categorization.py
# sed -i '252d' tests/skip_test_categorization.py


# --- SIM117 REPAIRS: tests/skip_test_main.py ---
# sed -i '77s/patch("os.path.isfile", return_value=False):/patch("os.path.isfile", return_value=False), pytest.raises(FileNotFoundError, match="CONSTITUTION VIOLATION"):/' tests/skip_test_main.py
# sed -i '78d' tests/skip_test_main.py

# sed -i '192s/patch("src.main.validate", side_effect=ValidationError("Invalid Schema")):/patch("src.main.validate", side_effect=ValidationError("Invalid Schema")), pytest.raises(ValidationError):/' tests/skip_test_main.py
# sed -i '194d' tests/skip_test_main.py


# --- SIM117 REPAIRS: tests/skip_test_resolution.py ---
# sed -i '98,99s/with patch("src.steps.resolution.get_min_feature_size", return_value=1.0):/with patch("src.steps.resolution.get_min_feature_size", return_value=1.0), caplog.at_level(logging.INFO):/' tests/skip_test_resolution.py
# sed -i '99d' tests/skip_test_resolution.py

# sed -i '111,112s/with caplog.at_level(logging.ERROR):/with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError, match="CONSTITUTION VIOLATION"):/' tests/skip_test_resolution.py
# sed -i '112d' tests/skip_test_resolution.py

# sed -i '122,124s/with patch("src.steps.resolution.get_min_feature_size", return_value=0.1):/with patch("src.steps.resolution.get_min_feature_size", return_value=0.1), caplog.at_level(logging.ERROR), pytest.raises(RuntimeError, match="GEOMETRY VIOLATION"):/' tests/skip_test_resolution.py
# sed -i '123,124d' tests/skip_test_resolution.py


# --- NATIVE RUFF AUTOMATED FIX ---
# sed -i 's/# ruff/ruff/' <<< "ruff check tests --select SIM117 --fix"