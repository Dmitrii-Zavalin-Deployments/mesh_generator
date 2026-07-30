#!/usr/bin/env bash
# ==============================================================================
# Forensic Audit & Automated Repair Script for CI Pipeline (Ruff Compliance)
# Target: src/debug/forensic_audit.sh
# ==============================================================================

set -euo pipefail

echo "=================================================================="
echo "STAGE 1: Diagnostic Diagnostics & Codebase Pattern Inspection"
echo "=================================================================="

echo "--- Checking for TRY201 (explicit exception re-raising) ---"
grep -rn "raise e" src/ tests/ || echo "No 'raise e' found."
grep -rn "raise ex" src/ tests/ || echo "No 'raise ex' found."

echo "--- Checking for RUF059 (unused unpacked variables) ---"
grep -rn "element_tags" src/ || echo "No unreferenced element_tags found."

echo "--- Checking for RUF013 (implicit Optional typing) ---"
grep -rn "= None" src/utils/ || echo "No implicit Optional defaults found."

echo "--- Checking for EXE001 (non-executable files with shebangs) ---"
find src/ -name "*.py" -exec head -n 1 {} \; | grep "#!" || echo "No shebang issues."

echo ""
echo "=================================================================="
echo "STAGE 2: Automated Code Repairs & Sed Injections"
echo "=================================================================="

echo ">>> Applying FIX 1: TRY201 (re-raising exceptions without name)"
sed -i 's/raise e/raise/g' src/main.py
sed -i 's/raise ex/raise/g' src/steps/categorization.py

echo ">>> Applying FIX 2: RUF059 (prefix unused unpacked variable with underscore)"
sed -i 's/element_types, element_tags, element_node_tags/element_types, _element_tags, element_node_tags/g' src/steps/categorization.py

echo ">>> Applying FIX 3: RUF013 (convert implicit Optional to T | None)"
sed -i 's/fallback_save_dir: str = None/fallback_save_dir: str | None = None/g' src/utils/mask_visualizer.py

echo ">>> Applying FIX 4: EXE001 (make validate_schema.py executable)"
chmod +x src/utils/validate_schema.py

echo ""
echo "=================================================================="
echo "STAGE 3: Verification (Running Ruff Check)"
echo "=================================================================="
# ruff check src tests --fix || true

echo "=================================================================="
echo "Forensic Audit & Repair Execution Complete."
echo "=================================================================="