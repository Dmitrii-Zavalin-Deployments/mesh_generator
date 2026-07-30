#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "          FORENSIC AUDIT: SIM117 NESTED 'WITH' DIAGNOSTICS"
echo "=========================================================="

echo "--- [1/3] Running Ruff Check to isolate violations ---"
# ruff check tests/test_categorization.py || true

echo ""
echo "--- [2/3] Grep diagnostic for nested 'with' patterns ---"
grep -n -C 2 "with " tests/test_categorization.py || true

echo ""
echo "--- [3/3] Smoking-gun source audit (cat -n tests/test_categorization.py) ---"
cat -n tests/test_categorization.py

echo ""
echo "=========================================================="
echo "          AUTOMATED REPAIR SCRIPTS (SED INJECTIONS)"
echo "=========================================================="
# To apply automated corrections for SIM117 multi-context combinations, uncomment below:
# sed -i 's/with patch("src.steps.categorization._run_gmsh_engine", return_value=None):/with patch("src.steps.categorization._run_gmsh_engine", return_value=None),/' tests/test_categorization.py
# sed -i 's/    with pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Categorization Engine failed to populate container.mask"):/    pytest.raises(RuntimeError, match="POST-CONDITION VIOLATION: Categorization Engine failed to populate container.mask"):' tests/test_categorization.py