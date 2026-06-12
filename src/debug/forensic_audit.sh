#!/usr/bin/env bash
# ==============================================================================
# Path: src/debug/forensic_audit.sh
# Purpose: Post-mortem diagnostic tool for CGAL linking failures (-lCGAL not found)
# ==============================================================================
set -uo pipefail

echo "=========================================================================="
echo "🔍 STARTING FORENSIC AUDIT: /usr/bin/ld: cannot find -lCGAL"
echo "=========================================================================="

# ------------------------------------------------------------------------------
# 1. DIAGNOSTICS: Inspect Conda prefix for CGAL library assets
# ------------------------------------------------------------------------------
echo -e "\n--- [1/3] CGAL Library and Path Diagnostics ---"

echo "[INFO] CGAL Package Version installed by Conda:"
if command -v conda &> /dev/null; then
    conda list cgal || echo "[WARN] CGAL package statement not found in active env."
else
    echo "[WARN] Conda package manager is inaccessible in this shell context."
fi

echo -e "\n[INFO] Inspecting \$CONDA_PREFIX/lib for compiled CGAL binaries:"
if [ -n "${CONDA_PREFIX:-}" ]; then
    echo "Current CONDA_PREFIX path evaluation: $CONDA_PREFIX"
    # Search for any legacy or helper compiled binaries (like libCGAL_Core)
    find "$CONDA_PREFIX/lib" -maxdepth 2 -name "*CGAL*" 2>/dev/null || echo "[NOTE] No files matching *CGAL* found. Confirms header-only structure."
else
    echo "[ERROR] \$CONDA_PREFIX environment variable is empty or unset!"
fi

# ------------------------------------------------------------------------------
# 2. SMOKING-GUN SOURCE AUDIT: Locate the compilation coordinates
# ------------------------------------------------------------------------------
echo -e "\n--- [2/3] Source Code / Workflow Step Inspection ---"

WORKFLOW_FILE=".github/workflows/test_external_tools.yml"

if [ -f "$WORKFLOW_FILE" ]; then
    echo "[INFO] Printing workflow compilation step with line numbers:"
    cat -n "$WORKFLOW_FILE" | grep -A 10 -B 2 "test_cgal.cpp" || cat -n "$WORKFLOW_FILE" | head -n 120
else
    echo "[WARN] Target workflow file not found at $WORKFLOW_FILE. Searching directory for references..."
    grep -rn "test_cgal.cpp" . | cat -n
fi

# ------------------------------------------------------------------------------
# 3. AUTOMATED REPAIRS: Commented-out sed interventions
# ------------------------------------------------------------------------------
echo -e "\n--- [3/3] Prescribed Automated Repairs ---"
echo "[INFO] Review the suggested fixes below. Uncomment to inject into your pipeline."
echo "[NOTE] Modern CGAL (5.0+) is header-only. Stripping the '-lCGAL' linker flag resolves this immediately."

# Fix Strategy A: Strip the redundant -lCGAL flag from the inline compilation line
# # sed -i 's/-lCGAL//g' "$WORKFLOW_FILE"

# Fix Strategy B: If your kernel strictly requires the algebraic core component (rare for standard cartesian)
# # sed -i 's/-lCGAL/-lCGAL_Core/g' "$WORKFLOW_FILE"

echo "=========================================================================="
echo "🎉 FORENSIC AUDIT COMPLETE"
echo "=========================================================================="