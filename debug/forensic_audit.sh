#!/bin/bash
# ==============================================================================
# Forensic Audit: CI Environment Integrity & Code State
# Triggered by: Pipeline Failure
# ==============================================================================

echo "🔎 [AUDIT] Starting forensic investigation..."

# 1. Environment Diagnostics
echo "--- Environment Diagnostics ---"
echo "Active Python: $(which python)"
python -c "import sys; print(sys.path)"
echo "--- Installed Packages (Conda) ---"
conda list | grep -E "gmsh|pythonocc" || echo "❌ ALERT: gmsh or pythonocc-core not found in conda list."

# 2. Source Code Audit (Smoking Gun)
echo "--- Smoking Gun: src/steps/categorization.py ---"
cat -n src/steps/categorization.py | grep -C 5 "import gmsh"

# 3. Verification Test
echo "--- Direct Import Attempt ---"
python -c "import gmsh; print('✅ gmsh is importable')" || echo "❌ FAILURE: gmsh is not importable from this python binary."

# 4. Automated Repair Suggestions
# These are commented-out 'sed' commands. If you identify a structural pattern 
# failure, uncomment these to patch the code or build during the pipeline.

# Scenario: Wrap problematic import in a Mock (if testing in restricted env)
# # sed -i '9i try:\n    import gmsh\nexcept ImportError:\n    import unittest.mock as mock; gmsh = mock.MagicMock()' src/steps/categorization.py

# Scenario: Ensure sys.path includes the conda site-packages explicitly
# # sed -i '1i import sys; sys.path.append("/usr/share/miniconda/envs/test/lib/python3.10/site-packages")' src/steps/categorization.py

echo "--- Forensic Audit Complete. ---"
exit 0