#!/bin/bash
# Description: Forensic diagnostic for environment dependency resolution failures.
# Location: src/debug/forensic_audit.sh

echo "============================================================"
echo "🚨 FORENSIC AUDIT: Dependency Environment Check"
echo "============================================================"

# 1. Diagnostic: Check if 'requests' is installed in the current environment
echo "--- Environment Dependency Audit ---"
python -c "import requests; print('✅ requests found.')" 2>/dev/null || echo "❌ CRITICAL: 'requests' module NOT found in current environment."

echo "--- Current Python Path ---"
which python
python --version

echo "--- Pip List (Installed Packages) ---"
pip list | grep -E "requests|jsonschema|dropbox"

# 2. Smoking Gun: Inspect the source code import
echo "--- Source Code Import Audit (src/io/dropbox_utils.py) ---"
cat -n src/io/dropbox_utils.py | grep -C 5 "import requests"

# 3. Automated Repair (Commented out)
# If this script is called by the CI after a failure, we attempt a forced re-install 
# of the requirements to ensure the environment is correctly synchronized.

# sed -i 's/pip install/python -m pip install --upgrade/g' .github/workflows/main.yml
# echo "✅ Automated repair: Forcing pip to use current python interpreter."

# Uncomment the line below to force an immediate install repair if imports fail
# python -m pip install -r requirements.txt
# echo "✅ Repair attempt: Re-installed requirements."

echo "============================================================"
echo "Audit complete. If 'requests' is missing, ensure you use 'python -m pip' in your YAML."