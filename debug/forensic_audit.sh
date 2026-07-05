#!/bin/bash
# src/debug/forensic_audit.sh
# 🔍 Post-Test Automated Forensic Audit & Diagnostic Suite

echo "=========================================================================="
echo " 🕵️‍♂️ RUNNING AUTOMATED PIPELINE FORENSIC AUDIT"
echo "=========================================================================="

# --------------------------------------------------------------------------
# 1. GREP/CAT DIAGNOSTICS FOR CODE/OUTPUT ROOT CAUSES
# --------------------------------------------------------------------------
echo ""
echo "=== 🔬 Section 1: Grep Diagnostics for Code/Output Root Causes ==="

echo "[Diagnostic A] Inspecting SovereignContainer constructor signature:"
grep -A 12 "class SovereignContainer" src/state/mesh_generator_state.py || echo "⚠️ Could not locate SovereignContainer class definition."

echo ""
echo "[Diagnostic B] Locating all occurrences of 'engine_type' across code and tests:"
grep -rn "engine_type" src/ tests/ || echo "⚠️ No active references to 'engine_type' found."

# --------------------------------------------------------------------------
# 2. CAT -N FOR SMOKING-GUN SOURCE AUDITS
# --------------------------------------------------------------------------
echo ""
echo "=== 🚬 Section 2: 'cat -n' Smoking-Gun Source Audits ==="

echo "[Audit A] Line-numbered view of SovereignContainer constructor context:"
if [ -f src/state/mesh_generator_state.py ]; then
    cat -n src/state/mesh_generator_state.py | grep -A 15 -B 2 "def __init__"
else
    echo "❌ System Error: src/state/mesh_generator_state.py does not exist."
fi

echo ""
echo "[Audit B] Line-numbered view of main orchestrator logic regarding engines:"
if [ -f src/main.py ]; then
    cat -n src/main.py | grep -C 5 "engine_type" || echo "ℹ️ No instances of 'engine_type' inside src/main.py"
fi

echo ""
echo "[Audit C] Line-numbered view of the failing test_main happy path:"
if [ -f tests/test_main.py ]; then
    cat -n tests/test_main.py | grep -C 8 "test_main_happy_path" || echo "ℹ️ Could not isolate test_main_happy_path block."
fi

# --------------------------------------------------------------------------
# 3. AUTOMATED REPAIR INJECTIONS VIA SED (SAFE-MODE WITH '#')
# --------------------------------------------------------------------------
echo ""
echo "=== 🔧 Section 3: Automated Repair Injections via Sed ==="
echo "The following repair actions are safely deactivated with leading comments."
echo "Uncomment the strategy matching your architectural preferences to auto-patch."

# Strategy A: Fix the 20+ test breaks by giving 'use_gmsh' a backwards-compatible default value.
# This prevents constructor failures when old tests instantiate the container using 6 parameters instead of 7.
# # sed -i 's/use_gmsh: bool/use_gmsh: bool = True/g' src/state/mesh_generator_state.py

# Strategy B: Resolve KeyError by changing strict dictionary access to a safe .get() fallback method in main.py.
# # sed -i "s/config\['engine_type'\]/config.get('engine_type', 'gmsh')/g" src/main.py
# # sed -i "s/data\['engine_type'\]/data.get('engine_type', 'gmsh')/g" src/main.py

# Strategy C: Alternative patch to inject the required parameter into the dynamic test setups or mock data structures.
# # sed -i "s/\"inputs\": {/\"inputs\": {\n            \"engine_type\": \"gmsh\",/g" tests/test_main.py

echo "=========================================================================="
echo " 🛑 FORENSIC AUDIT SUITE EXECUTION COMPLETE"
echo "=========================================================================="