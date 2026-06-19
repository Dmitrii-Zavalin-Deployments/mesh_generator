#!/bin/bash
# Description: Forensic diagnostic for KeyError in configuration loading.
# Location: src/debug/forensic_audit.sh

INPUT_FILE="./data/testing-input-output/mesh_generator_input.json"

echo "============================================================"
echo "🚨 FORENSIC AUDIT: KeyError (Missing 'boundary_map')"
echo "============================================================"

# 1. Diagnostic: Check if the key exists in the input JSON
# echo "--- Checking Input JSON for 'boundary_map' ---"
# if grep -q "boundary_map" "$INPUT_FILE"; then
#     echo "✅ 'boundary_map' found in $INPUT_FILE."
# else
#     echo "❌ CRITICAL: 'boundary_map' missing from $INPUT_FILE."
# fi

# 2. Smoking Gun: Audit the loading logic in main.py
echo "--- Source Context (src/main.py around line 33) ---"
cat -n src/main.py | sed -n '30,40p'

# 3. Automated Repair (Commented out)
# If the key is missing, this sed command injects a default empty dictionary
# into the JSON right before the closing brace '}'.
# sed -i '$s/}/, "boundary_map": {} }/' "$INPUT_FILE"
# echo "✅ Automated repair: Injected default 'boundary_map' into JSON."

echo "============================================================"
echo "Audit complete. Update your JSON input or use defensive coding (.get()) in main.py."