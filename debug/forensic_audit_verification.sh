#!/bin/bash
# src/debug/forensic_audit.sh
# Automated forensic audit for SovereignContainer initialization failures.

echo "🔍 [FORENSIC AUDIT] Analyzing SovereignContainer Type Error..."
echo "============================================================"

# 1. Locate the Class Definition
echo "📋 Searching for SovereignContainer definition..."
CONTAINER_DEF=$(grep -r "class SovereignContainer" src/ | head -n 1 | cut -d: -f1)
echo "   ↳ Found definition in: $CONTAINER_DEF"

# 2. Grep Diagnostics: Show the mismatching constructor signatures
echo -e "\n📋 Grep Diagnostic: Identifying mismatch between calls and definition..."
grep -A 2 "def __init__" "$CONTAINER_DEF"
grep -n "SovereignContainer(" tests/test_base_interface.py

# 3. Smoking Gun Audit: Show lines with line numbers for manual verification
echo -e "\n📜 Smoking Gun Audit: tests/test_base_interface.py (Source Code)"
cat -n tests/test_base_interface.py

# 4. Automated Repair Suggestions
# These sed commands are commented out. To apply the fix, remove the '#' and run the script.
echo -e "\n🛠️ Automated Repair Injection (Sed templates):"
echo "   To fix the TypeError, we must inject 'use_gmsh=True' (or False) into the constructor calls."
echo ""
echo "# sed -i 's/SovereignContainer(/SovereignContainer(use_gmsh=True, /g' tests/test_base_interface.py"
echo ""

# 5. Summary
echo "============================================================"
echo "Audit complete. The tests failed because the class API changed."
echo "Uncomment the sed command above if you wish to apply the fix automatically."