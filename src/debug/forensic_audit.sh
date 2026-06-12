#!/usr/bin/env bash
# ==============================================================================
# Path: src/debug/forensic_audit.sh
# Purpose: Post-mortem diagnostic tool for FreeCAD import failures in CI/CD
# ==============================================================================
set -uo pipefail

echo "=========================================================================="
echo "🔍 STARTING FORENSIC AUDIT: ModuleNotFoundError: No module named 'FreeCAD'"
echo "=========================================================================="

# ------------------------------------------------------------------------------
# 1. DIAGNOSTICS: Verify installation and locate hidden shared objects
# ------------------------------------------------------------------------------
echo -e "\n--- [1/3] Conda Package and System Path Diagnostics ---"

if command -v conda &> /dev/null; then
    echo "[INFO] Active Conda Environment Packages:"
    conda list | grep -iE "freecad|occt|pythonocc" || echo "[WARN] FreeCAD package not detected via conda list!"
    
    echo -e "\n[INFO] Locating FreeCAD binaries within \$CONDA_PREFIX:"
    find "$CONDA_PREFIX" -name "FreeCAD.so" -o -name "FreeCADCmd" -o -name "FreeCAD.pyd" 2>/dev/null || echo "[ERROR] No FreeCAD binaries found in Conda tree."
else
    echo "[ERROR] Conda package manager is inaccessible in this shell context."
fi

echo -e "\n[INFO] Current Python Search Paths (sys.path):"
python -c "import sys; print('\n'.join(sys.path))"

# ------------------------------------------------------------------------------
# 2. SMOKING-GUN SOURCE AUDIT: Check the source file or workflow configuration
# ------------------------------------------------------------------------------
echo -e "\n--- [2/3] Source Code / Workflow Step Inspection ---"

# Target the workflow file or the pipeline configuration that triggered the failure
WORKFLOW_FILE=".github/workflows/mesh_generator_experiment.yml"

if [ -f "$WORKFLOW_FILE" ]; then
    echo "[INFO] Printing workflow configuration with line numbers to trace the execution context:"
    cat -n "$WORKFLOW_FILE" | grep -A 10 -B 2 "import FreeCAD" || cat -n "$WORKFLOW_FILE" | head -n 100
else
    echo "[WARN] Target workflow file not found at $WORKFLOW_FILE. Auditing local directory structure:"
    find . -maxdepth 3 -name "*.yml" -o -name "*.py" | cat -n
fi

# ------------------------------------------------------------------------------
# 3. AUTOMATED REPAIRS: Commented-out sed interventions
# ------------------------------------------------------------------------------
echo -e "\n--- [3/3] Prescribed Automated Repairs ---"
echo "[INFO] Review the suggested fixes below. Uncomment to inject into your pipeline."

# Fix Strategy A: Dynamically append FreeCAD's shared object path inside the inline script before importing
# # sed -i '/import FreeCAD/i \          import sys, os; sys.path.append(os.path.join(os.environ["CONDA_PREFIX"], "lib")); sys.path.append(os.path.join(os.environ["CONDA_PREFIX"], "lib", "freecad", "lib"))' "$WORKFLOW_FILE"

# Fix Strategy B: Prepend a global PYTHONPATH export into the runner shell sequence right before the python execution
# # sed -i '/Test FreeCAD Reference/a \        env:\n          PYTHONPATH: ${{ env.CONDA_PREFIX }}/lib:${{ env.CONDA_PREFIX }}/lib/freecad/lib' "$WORKFLOW_FILE"

echo "=========================================================================="
echo "🎉 FORENSIC AUDIT COMPLETE"
echo "=========================================================================="