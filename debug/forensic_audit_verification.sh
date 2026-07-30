#!/bin/bash
# src/debug/forensic_audit.sh

echo "=================================================="
echo "1. DIAGNOSTICS: Python Environment & OCC Packages"
echo "=================================================="
# python -m pip list || true
# conda list || true

echo "=================================================="
echo "2. DIAGNOSTICS: OCC references across test suite"
echo "=================================================="
grep -rn "OCC.Core" tests/ || true

echo "=================================================="
echo "3. SMOKING-GUN SOURCE AUDIT (cat -n)"
echo "=================================================="
cat -n tests/test_resolution.py || true

echo "=================================================="
echo "4. AUTOMATED REPAIR INJECTIONS (Commented)"
echo "=================================================="
# sed -i 's/from OCC.Core/try:\n    from OCC.Core\nexcept ImportError:\n    pass #/g' tests/test_resolution.py
# sed -i '/from OCC.Core/d' tests/test_resolution.py