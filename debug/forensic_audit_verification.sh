#!/usr/bin/env bash
set -euo pipefail

echo "======================================================================"
echo "         FORENSIC AUDIT: RUFF LINT VIOLATIONS DIAGNOSTICS            "
echo "======================================================================"

TARGET_FILE="tests/test_main.py"

# --- 1. RUFF DIAGNOSTIC REPORT ---
echo -e "\n--- [1/3] RUFF ERROR DETAILED BREAKDOWN ---"
if command -v ruff &> /dev/null; then
    ruff check "$TARGET_FILE" --select SIM117,SIM210,F841 || true
else
    echo "Ruff binary not found in current PATH. Skipping direct binary check."
fi

# --- 2. SMOKING-GUN SOURCE AUDIT (cat -n) ---
echo -e "\n--- [2/3] CODE INSPECTION: TARGET LOCATIONS ---"

echo -e "\n>>> Inspecting SIM117 Violation #1 (Lines 45-55):"
cat -n "$TARGET_FILE" | sed -n '45,55p'

echo -e "\n>>> Inspecting SIM117 Violation #2 (Lines 68-75):"
cat -n "$TARGET_FILE" | sed -n '68,75p'

echo -e "\n>>> Inspecting SIM210 Violation (Lines 120-128):"
cat -n "$TARGET_FILE" | sed -n '120,128p'

echo -e "\n>>> Inspecting F841 Violation (Lines 172-182):"
cat -n "$TARGET_FILE" | sed -n '172,182p'


# --- 3. AUTOMATED REPAIR INJECTIONS ---
# To apply these automated fixes, uncomment the 'sed' lines below and execute this script.

echo -e "\n--- [3/3] AUTOMATED SED REPAIR RECIPES (INACTIVE BY DEFAULT) ---"

# Fix SIM117 (#1): Combine nested `with` statements into single line
# sed -i '50,51c\    with patch.object(sys, "argv", test_args), pytest.raises(FileNotFoundError, match="CONSTITUTION VIOLATION: STEP file not found"):' "$TARGET_FILE"

# Fix SIM117 (#2): Combine nested `with` statement with multi-context parent
# sed -i '70,72c\    with patch.object(sys, "argv", test_args), \\\n         patch("os.path.exists", side_effect=lambda p: False if "config" in str(p) else os.path.exists(p)), \\\n         pytest.raises(FileNotFoundError, match="CONSTITUTION VIOLATION: Configuration file not found"):' "$TARGET_FILE"

# Fix SIM210: Replace `True if <expr> else False` with `bool(<expr>)`
# sed -i 's/side_effect=lambda p: True if "config.json" in str(p) or "schema" in str(p) or os.path.exists(p) else False/side_effect=lambda p: bool("config.json" in str(p) or "schema" in str(p) or os.path.exists(p))/' "$TARGET_FILE"

# Fix F841: Remove unused variable assignment `as mock_orch`
# sed -i 's/patch("src.main.Orchestrator") as mock_orch,/patch("src.main.Orchestrator"),/' "$TARGET_FILE"

echo "Forensic audit complete. Uncomment 'sed' lines above in this script to execute automated repairs."