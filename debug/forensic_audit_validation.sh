#!/bin/bash
# Description: Automated forensic audit for KeyError: 'boundary_map'.
# Status: Active (Triggered upon CI failure)

echo "============================================================"
echo "🔍 STARTING DEEP FORENSIC AUDIT: Missing 'boundary_map' Configuration"
echo "============================================================"

# 1. Diagnostic: Check config.json contents
if [ -f "config/config.json" ]; then
    echo "--- 1. Smoking-gun source audit: config/config.json ---"
    cat -n config/config.json
elif [ -f "config.json" ]; then
    echo "--- 1. Smoking-gun source audit: config.json ---"
    cat -n config.json
else
    echo "❌ Critical: config.json not found."
fi

# 2. Diagnostic: Check config schema definition
if [ -f "schema/mesh_generator_config_schema.json" ]; then
    echo "--- 2. Smoking-gun source audit: schema/mesh_generator_config_schema.json ---"
    cat -n schema/mesh_generator_config_schema.json
fi

# 3. Diagnostic: Check src/main.py around SovereignContainer initialization
if [ -f "src/main.py" ]; then
    echo "--- 3. Smoking-gun source audit: src/main.py (lines 80-105) ---"
    sed -n '80,105p' src/main.py
fi

# 4. Grep Diagnostic: Search for boundary_map across the codebase
echo "--- 4. Grep Diagnostic: Searching for 'boundary_map' references ---"
grep -rn "boundary_map" src/ config/ schema/ || echo "No further references found."

# 5. Suggested Automated Repairs (Commented out with # sed)
echo "============================================================"
echo "🛠️ SUGGESTED AUTO-REPAIR INJECTIONS:"
echo "============================================================"
echo "# To handle missing boundary_map gracefully in src/main.py using .get():"
echo "# sed -i \"s/boundary_map=config\['boundary_map'\]/boundary_map=config.get('boundary_map', {})/g\" src/main.py"
echo ""
echo "# Or to completely remove boundary_map from SovereignContainer call in src/main.py:"
echo "# sed -i '/boundary_map=/d' src/main.py"
echo "============================================================"

# exit 1