#!/bin/bash
# forensic_audit.sh - Post-Test Diagnostic & Repair
# =================================================================

echo "--- [1/3] Artifact Diagnostic ---"
# Verify if the output directory exists
if [ -d "data/testing-input-output" ]; then
    echo "Directory 'data/testing-input-output' exists."
    ls -l data/testing-input-output/
else
    echo "Error: Directory 'data/testing-input-output' NOT found."
fi

echo -e "\n--- [2/3] Snapshot Existence Check ---"
if [ -f "data/testing-input-output/mesh_snapshot.png" ]; then
    echo "✅ Success: mesh_snapshot.png found."
else
    echo "❌ Missing: mesh_snapshot.png not found."
    echo "Checking for hidden or misnamed files..."
    find data/testing-input-output/ -maxdepth 1 -name "*.png"
fi

echo -e "\n--- [3/3] Repair Suggestions ---"
echo "Instructions: Check src/steps/categorization.py for the Gmsh snapshot call."
echo "Ensure that gmsh.fltk.initialize() or gmsh.write() is correctly invoked."
echo "If using a custom rendering pipeline, confirm the output path matches: "
echo "data/testing-input-output/mesh_snapshot.png"

# sed -i 's|old_path|new_path|g' src/steps/categorization.py

echo -e "\nAudit Complete."