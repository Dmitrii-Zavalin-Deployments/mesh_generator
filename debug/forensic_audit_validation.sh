#!/bin/bash
# Description: Automated forensic audit for AttributeError: 'SovereignContainer' object has no attribute 'use_gmsh'.
# Status: Active (Triggered upon CI failure)

echo "============================================================"
echo "🔍 STARTING DEEP FORENSIC AUDIT: Missing 'use_gmsh' Attribute"
echo "============================================================"

# 1. Diagnostic: Inspect src/steps/voxelization.py around the error line
if [ -f "src/steps/voxelization.py" ]; then
    echo "--- 1. Smoking-gun source audit: src/steps/voxelization.py ---"
    cat -n src/steps/voxelization.py
fi

# 2. Diagnostic: Locate and inspect SovereignContainer definition file
CONTAINER_MATCH=$(grep -rn "class SovereignContainer" src/ || echo "")
echo "--- 2. SovereignContainer Definition Location ---"
echo "$CONTAINER_MATCH"

CONTAINER_PATH=$(echo "$CONTAINER_MATCH" | cut -d: -f1)
if [ -n "$CONTAINER_PATH" ] && [ -f "$CONTAINER_PATH" ]; then
    echo "--- 3. Smoking-gun source audit: $CONTAINER_PATH ---"
    cat -n "$CONTAINER_PATH"
fi

# 3. Grep Diagnostic: Search for 'use_gmsh' across the codebase
echo "--- 4. Grep Diagnostic: Searching for 'use_gmsh' references ---"
grep -rn "use_gmsh" src/ || echo "No further references found."

# 4. Suggested Automated Repairs (Commented out with # sed)
echo "============================================================"
echo "🛠️ SUGGESTED AUTO-REPAIR INJECTIONS:"
echo "============================================================"
echo "# To make the check robust using getattr in src/steps/voxelization.py:"
echo "# sed -i \"s/container.use_gmsh/getattr(container, 'use_gmsh', True)/g\" src/steps/voxelization.py"
echo ""
echo "# Or to inject self.use_gmsh = True into SovereignContainer's __init__:"
echo "# sed -i '/def __init__(/a \\        self.use_gmsh = True' $CONTAINER_PATH"
echo "============================================================"

# exit 1