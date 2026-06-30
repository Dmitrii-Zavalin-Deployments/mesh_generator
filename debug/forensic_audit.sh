#!/bin/bash
# ==============================================================================
# FORENSIC AUDIT: debug/forensic_audit.sh
# Repo: Mesh Generator (Core Engine)
# ==============================================================================

echo "========================================================================"
echo "🔍 PHASE 1: CLI ARGUMENT & FILE OPEN AUDIT"
echo "========================================================================"
echo "--- Argument Parsing & sys.argv usage in Entry Point ---"
grep -n -E "argparse|add_argument|sys.argv" src/main.py || echo "⚠️ No direct argparse patterns matched in src/main.py"

echo -e "\n--- File Open Modes across Source Tree (Checking for binary/text mismatches) ---"
grep -n "open(" src/main.py src/steps/*.py src/pipeline/*.py src/state/*.py 2>/dev/null || echo "⚠️ No explicit open() statements matched."

echo -e "\n========================================================================"
echo "🔬 PHASE 2: SMOKING GUN SOURCE AUDITS (cat -n)"
echo "========================================================================"
echo "--- Complete tests/test_main.py Execution Context ---"
cat -n tests/test_main.py

echo -e "\n--- Complete src/main.py Code Layers ---"
cat -n src/main.py

echo -e "\n========================================================================"
echo "🛠️ PHASE 3: AUTOMATED REPAIR CANDIDATES (sed)"
echo "========================================================================"
echo "# Fix CLI error assertion (argparse naturally throws code 2 on syntax failures, not 1):"
echo "# sed -i 's/assert exc.value.code == 1/assert exc.value.code == 2/g' tests/test_main.py"
echo "# sed -i 's/assert e.code == 1/assert e.code == 2/g' tests/test_main.py"
echo ""
echo "# Fix uncaught SystemExit in file-not-found test:"
echo "# sed -i '/def test_main_file_not_found/a \    with pytest.raises(SystemExit):' tests/test_main.py"

echo -e "\n========================================================================"
echo "🏁 Forensic scan generation complete."
