#!/bin/bash
# Description: Automated forensic audit for unmatched single quote / unexpected EOF in CI/CD pipeline.
# Status: Active (Triggered upon CI failure)

echo "============================================================"
echo "🔍 STARTING DEEP FORENSIC AUDIT: Unmatched Quote / EOF Syntax Error"
echo "============================================================"

# 1. Diagnostic: Locate workflow files or test scripts running schema verification
echo "--- 1. Diagnostic: Locating workflow and test runner files ---"
WORKFLOW_FILE=$(grep -rl "Schema Verification" .github/workflows/ 2>/dev/null | head -n 1)
if [ -z "$WORKFLOW_FILE" ]; then
    WORKFLOW_FILE=$(find .github/workflows -type f | head -n 1)
fi

echo "Target workflow/script file identified: $WORKFLOW_FILE"

# 2. Smoking-gun source audit: cat -n on the identified file
if [ -n "$WORKFLOW_FILE" ] && [ -f "$WORKFLOW_FILE" ]; then
    echo "--- 2. Smoking-gun source audit: $WORKFLOW_FILE ---"
    cat -n "$WORKFLOW_FILE"
else
    echo "❌ Critical: No workflow or test script file found."
fi

# 3. Grep Diagnostic: Search for 'Schema Verification' or quote blocks
echo "--- 3. Grep Diagnostic: Searching for 'Schema Verification' or quote blocks ---"
grep -rn "Schema Verification" .github/workflows/ || echo "Workflow step not found via grep."

# 4. Suggested Automated Repairs (Commented out with # sed)
echo "============================================================"
echo "🛠️ SUGGESTED AUTO-REPAIR INJECTIONS:"
echo "============================================================"
echo "# To fix unclosed single quotes in workflow files, balance or escape the quotes:"
echo "# sed -i \"s/'/\\'/g\" $WORKFLOW_FILE"
echo "============================================================"

# exit 2