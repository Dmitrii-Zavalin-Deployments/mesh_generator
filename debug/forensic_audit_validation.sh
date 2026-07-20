#!/bin/bash
# src/debug/forensic_audit.sh
# Forensic diagnostic for GMSH memory pointer collisions in CI

echo "========================================================================"
echo "🔍 STEP 1: PIPELINE CRASH ANALYSIS"
echo "========================================================================"
# Look for the crash pattern in your runner logs
LOG_FILE=$(find . -name "*.log" | head -n 1) # Auto-detect log file
if [ -f "$LOG_FILE" ]; then
    echo "Found log: $LOG_FILE"
    grep -C 5 "Segmentation fault" "$LOG_FILE" || echo "No explicit Segfault found in logs."
else
    echo "No log files found in current directory."
fi

echo -e "\n========================================================================"
echo "📋 STEP 2: AUDITING SMOKING-GUN SOURCE CODE (categorization.py)"
echo "========================================================================"
# Display lines around the initialization logic
cat -n src/steps/categorization.py | sed -n '30,60p'

echo -e "\n========================================================================"
echo "🛠️ STEP 3: AUTOMATED REPAIR CANDIDATES (sed injections)"
echo "========================================================================"
echo "Use these commands to harden the initialization sequence against stale states:"
echo ""

# REPAIR 1: Replace simple clear() with a try/except block to catch C++ exceptions
# This prevents a hard crash if the memory address is already dangling
echo "# sed -i 's/gmsh.clear()/try:\n            gmsh.clear()\n        except Exception:\n            gmsh.finalize()\n            gmsh.initialize()/' src/steps/categorization.py"

# REPAIR 2: Forcing a hard re-init if the clear() is risky
# This forces the engine to start fresh if it's already active, rather than clearing
echo "# sed -i 's/gmsh.clear()/gmsh.finalize()\n        gmsh.initialize()/' src/steps/categorization.py"

echo -e "\n========================================================================"
echo "FORENSIC AUDIT COMPLETE"
echo "========================================================================"