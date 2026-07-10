#!/bin/bash
# src/debug/forensic_audit.sh
# Usage: Run this in GHA to diagnose import errors and pathing

echo "--- 🔍 FORENSIC AUDIT: ENVIRONMENT ---"
pwd
ls -R src/ | grep -v "__pycache__"

echo -e "\n--- 🔍 SMOKING GUN: SOURCE CODE AUDIT ---"
echo "Target: src/main.py"
cat -n src/main.py | sed -n '75,170p' # Look at GMSH block

echo -e "\n--- 🔍 TEST FILE AUDIT ---"
cat -n tests/test_main.py

echo -e "\n--- 🔍 DIAGNOSTICS: CHECKING GMSH IMPORT LOCATIONS ---"
grep -r "import gmsh" src/

echo -e "\n--- ⚙️ AUTOMATED REPAIR INJECTIONS (Commented) ---"
# If you find path issues, you can uncomment these:
# sed -i 's|import gmsh|import sys; from unittest.mock import MagicMock; sys.modules["gmsh"] = MagicMock()|g' src/main.py
# sed -i 's|sys.path.append|# sys.path.append|g' src/main.py

echo -e "\n--- 🏁 FORENSIC AUDIT COMPLETE ---"