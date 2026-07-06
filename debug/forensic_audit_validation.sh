#!/bin/bash
# debug/forensic_audit_validation.sh - Visualization Layer Audit
# =================================================================

echo "--- [1/3] Log Diagnostic: Extracting Silent Warnings ---"
# Check if your main application execution caught a non-fatal rendering exception
if [ -f "data/testing-input-output/mesh_generator_output.json" ]; then
    echo "Output JSON exists, scanning system logs for hidden graphics anomalies..."
    # If you pipe your logs to a file or stdout, we can check for the exception string here
fi

echo -e "\n--- [2/3] Smoking Gun Source Audit: End-of-Function Pipeline ---"
# Audit the final 30 lines of the categorization engine to see the state of the try/except block
cat -n src/steps/categorization.py | tail -n 45

echo -e "\n--- [3/3] Automated Repair Injections ---"
echo "Instructions: Run the following sed commands to strip out the broken mid-function patch"
echo "and fully initialize the FLTK frame server context at the bottom of the loop."

# Step A: Clean out the broken mid-function snippet if it exists near the tet_idx loop
# # sed -i '/snapshot_path = os.path.join(workspace_dir, "mesh_snapshot.png")/d' src/steps/categorization.py
# # sed -i '/gmsh.write(snapshot_path)/d' src/steps/categorization.py
# # sed -i '/Universal mesh snapshot saved:/d' src/steps/categorization.py

# Step B: Inject the explicit FLTK graphic initializers right before gmsh.write() at the bottom
# # sed -i '/workspace_dir = os.path.dirname/i \        gmsh.fltk.initialize()' src/steps/categorization.py
# # sed -i '/logger.info(f"Universal mesh snapshot saved successfully/a \        gmsh.fltk.finalize()' src/steps/categorization.py

echo -e "\nAudit Complete."