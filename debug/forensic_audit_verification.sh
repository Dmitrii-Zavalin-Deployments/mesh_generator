#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "         COMMENCING FORENSIC AUDIT TRACE          "
echo "=================================================="

# echo "--- 1. Environment & Workspace Diagnostics ---"
# pwd
# python3 --version
# pip list | grep -E "pytest|ruff|jsonschema|gmsh" || true

# echo "--- 2. Linter Execution Status ---"
# python3 -m ruff check src tests || ruff check src tests || echo "Linter failures detected."

echo "--- 3. Smoking-Gun Source Audit: tests/test_main_2.py ---"
if [ -f "tests/test_main_2.py" ]; then
    echo "=== Line-numbered source listing ==="
    cat -n tests/test_main_2.py
    echo "=== Grep diagnostics for ValidationError ==="
    grep -n "ValidationError" tests/test_main_2.py || echo "No references to ValidationError found."
else
    echo "Notice: tests/test_main_2.py not present in workspace."
fi

echo "--- 4. Automated Repair Injections (Commented Sed Operations) ---"
# Fix F821: Inject missing jsonschema import right after the pytest import in tests/test_main_2.py
# sed -i '/import pytest/a from jsonschema import ValidationError' tests/test_main_2.py

# Alternative fallback repair: prepend missing import to top of tests/test_main_2.py
# sed -i '1i from jsonschema import ValidationError' tests/test_main_2.py

echo "=================================================="
echo "           FORENSIC AUDIT COMPLETED               "
echo "=================================================="