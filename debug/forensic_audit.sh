#!/bin/bash
# ==============================================================================
# FORENSIC AUDIT: src/debug/forensic_audit.sh
# Purpose: Diagnose TypeError (Binary vs Text) and SystemExit(2) (CLI mismatch)
# ==============================================================================

echo "========================================================================"
echo "🔍 PHASE 1: IDENTIFYING FILE-MODE AND ARGUMENT MISMATCHES"
echo "========================================================================"

echo "[DIAGNOSTIC] Searching for 'wb' (binary) open modes that clash with JSON dumps:"
grep -rE "open\(.*,'wb'\)|open\(.*,\"wb\"\)" . || echo "✅ No binary open modes found."

echo -e "\n[DIAGNOSTIC] Checking CLI argument definitions in source vs test calls:"
grep -n "add_argument" src/pipeline/record_telemetry.py
grep -n "sys.argv" tests/test_main.py

echo -e "\n========================================================================"
echo "🔬 PHASE 2: SMOKING-GUN SOURCE AUDITS (CAT -N)"
echo "========================================================================"
echo "📄 Auditing src/pipeline/record_telemetry.py (JSON Write block):"
cat -n src/pipeline/record_telemetry.py | sed -n '65,75p'

echo -e "\n📄 Auditing tests/test_main.py (CLI patch block):"
cat -n tests/test_main.py | sed -n '1,30p'

echo -e "\n========================================================================"
echo "🛠️ PHASE 3: AUTOMATED REPAIR CANDIDATES (sed)"
echo "========================================================================"
echo "To fix TypeError (Binary/String mismatch), ensure files are opened as 'w' (text):"
echo "# sed -i 's/open(path, \"wb\")/open(path, \"w\")/g' tests/test_main.py"

echo -e "\nTo fix SystemExit(2), update test arguments to match the 3 required flags:"
echo "# sed -i 's/\[\"script\",/\[\"script\", \"--state-file\", \"dummy.json\", \"--exit-code\", \"0\", \"--log-file\", \"dummy.log\"\]/g' tests/test_main.py"

echo -e "\n========================================================================"
echo "🏁 Forensic audit complete."
EOF