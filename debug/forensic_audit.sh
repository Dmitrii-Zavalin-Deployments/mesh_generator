#!/bin/bash
# forensic_audit.sh - GitHub Actions Post-Test Diagnostic & Repair
# =================================================================

echo "--- [1/3] OS & GL Diagnostic ---"
cat /etc/os-release | grep PRETTY_NAME

# Check if the specific legacy OpenGL package exists in the current repo index
echo "Package availability check for libgl1-mesa-glx:"
if apt-cache search libgl1-mesa-glx | grep -q "libgl1-mesa-glx"; then
    echo "Status: Package found in repo index."
else
    echo "Status: Package 'libgl1-mesa-glx' NOT found (Expected on Ubuntu 24.04+)."
fi

echo -e "\n--- [2/3] Smoking Gun Audit ---"
# Locate all workflow files containing the deprecated dependency
FILES=$(grep -rl "libgl1-mesa-glx" .github/workflows/)

if [ -z "$FILES" ]; then
    echo "No files containing 'libgl1-mesa-glx' found in .github/workflows/."
else
    for file in $FILES; do
        echo "File: $file"
        # Print with line numbers to pinpoint exact locations
        cat -n "$file" | grep "libgl1-mesa-glx"
    done
fi

echo -e "\n--- [3/3] Automated Repair Injection ---"
echo "Instructions: To apply the fix automatically, uncomment the sed line below and re-run."
echo "This will replace the deprecated 'libgl1-mesa-glx' with the modern 'libgl1'."

# sed -i 's/libgl1-mesa-glx/libgl1/g' .github/workflows/*.yml

echo -e "\nAudit Complete."