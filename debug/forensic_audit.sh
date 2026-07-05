#!/bin/bash
# ==============================================================================
# Forensic Audit: Deep Environment & Pipeline Root Cause Analysis
# Location: src/debug/forensic_audit.sh
# ==============================================================================

echo "🚨 [FORENSIC AUDIT] Analyzing test environment and binding anomalies..."

# 1. Root Cause & Binary Presence Diagnostics
echo "=== 🌐 Environment Diagnostics ==="
echo "Active Python: $(which python)"
echo "Python Version: $(python --version)"

echo "=== 📦 Conda Matrix Architecture Inspection ==="
if command -v conda &> /dev/null; then
    echo "Checking for binary vs wrapper packages..."
    conda list | grep -E "gmsh|pythonocc"
else
    echo "❌ Conda command not accessible in this subshell context."
fi

echo "=== 📁 Shared Library Linkage Diagnostics ==="
echo "Verifying if C++ Shared Objects exist without Python Wrappers:"
find /usr/share/miniconda/envs/test/ -type f \( -name "libgmsh.so*" -o -name "gmsh.py" -o -name "__init__.py" \) 2>/dev/null | grep -E "gmsh" || echo "No matching Gmsh files found."

# 2. Smoking-Gun Source Audits (Pinpointing the exact failing lines)
echo "=== 🚬 Smoking-Gun Source Audit: src/steps/categorization.py ==="
cat -n src/steps/categorization.py | grep -A 5 -B 5 "import gmsh"

echo "=== 🚬 Smoking-Gun Source Audit: tests/test_categorization.py ==="
cat -n tests/test_categorization.py | head -n 15

# 3. Interpreter Binding Probe
echo "=== 🧪 Live Path Mapping Probe ==="
python -c "import sys; print('Active sys.path Search Locations:'); [print(f' - {p}') for p in sys.path]"

# 4. Automated Repair Injections via Sed
# These commands are commented out with '#' per your instructions. 
# Depending on your strategy, uncomment the desired command to execute automated repairs in your workflow.

# Strategy A: Use sed to automatically patch your GitHub Actions YAML workflow files, 
# appending a pip force-install step directly underneath the conda install instruction.
# # sed -i '/conda install -y/a \          python -m pip install --no-cache-dir gmsh' .github/workflows/*.yml

# Strategy B: Use sed to inject a graceful runtime mock fallback into the step module,
# allowing test collection to pass natively even if the underlying binary bindings are missing.
# # sed -i '/import gmsh/c\try:\n    import gmsh\nexcept ImportError:\n    import unittest.mock as mock; gmsh = mock.MagicMock(); print("⚠️ MOCK APPLIED: gmsh binding bypassed for collection context")' src/steps/categorization.py

# Strategy C: Use sed to completely comment out the offending import lines in the test execution loop
# to isolate non-physics test routines.
# # sed -i 's/from src.steps.categorization import CategorizationStep/# from src.steps.categorization import CategorizationStep/g' tests/test_categorization.py

echo "=== 🛑 Forensic Audit Execution Completed ==="