#!/bin/bash
# src/debug/forensic_audit.sh
# Automated Deep Forensic Audit & Environment Verification Layer

set -u # Fail if undefined variables are used

log_banner() {
    echo "========================================================================"
    echo "🔍 FORENSIC AUDIT: $1"
    echo "========================================================================"
}

# ------------------------------------------------------------------------
# PHASE 1: ENVIRONMENT & RUNTIME DIAGNOSTICS (grep/cat diagnostics)
# ------------------------------------------------------------------------
log_banner "ENVIRONMENT PREFIX & RUNTIME STATE AUDIT"

echo "📍 Active Python Interpreter Path:"
which python
python --version

echo -e "\n📍 Inspecting Active Package Space for Matplotlib Matches:"
if command -v conda &> /dev/null; then
    conda list | grep -E "matplotlib|numpy|gmsh|pythonocc" || echo "⚠️ No matches found in Conda package space."
else
    pip list | grep -E "matplotlib|numpy|gmsh" || echo "⚠️ No matches found in Pip package space."
fi


# ------------------------------------------------------------------------
# PHASE 2: SMOKING-GUN SOURCE AUDIT (cat -n)
# ------------------------------------------------------------------------
log_banner "SMOKING-GUN SOURCE LINE AUDIT"

TARGET_FILE="src/utils/mask_visualizer.py"

if [ -f "$TARGET_FILE" ]; then
    echo "📄 Inspecting imports inside target module: $TARGET_FILE"
    # Capture the head of the file where imports typically live
    cat -n "$TARGET_FILE" | head -n 25
else
    echo "❌ Error: High-priority target $TARGET_FILE not found in workspace root."
fi

echo -e "\n📄 Cross-checking test entrypoints targeting collection crashes:"
for test_file in "tests/test_main.py" "tests/test_mask_visualizer.py"; do
    if [ -f "$test_file" ]; then
        echo -e "\n👉 Source Lines for $test_file:"
        cat -n "$test_file" | head -n 15
    fi
done


# ------------------------------------------------------------------------
# PHASE 3: GLOBAL DEPENDENCY DRIFT DETECTOR (grep tracking)
# ------------------------------------------------------------------------
log_banner "SCANNING CODESPACE FOR MATPLOTLIB IMPORTS"

echo "🔎 Locating all literal occurrences of matplotlib references across workspace..."
grep -rn "matplotlib" --include="*.py" --include="*.sh" --include="*.txt" src/ tests/ setup_scripts/ 2>/dev/null || echo "No occurrences traced."


# ------------------------------------------------------------------------
# PHASE 4: AUTOMATED INLINE REPAIRS (Commented-out Sed Injections)
# ------------------------------------------------------------------------
log_banner "AUTOMATED HOTFIX / REPAIR MATRIX (INACTIVE ENGINE)"
echo "ℹ️ The following sed injection mutations are prepared but safe-guarded."

# 1. Inject explicit matplotlib fallback into setup scripts right after jsonschema dependency
# # sed -i '/install_pkg "jsonschema>=4.23.0"/a \install_pkg "matplotlib>=3.7.0"' setup_scripts/mesh_gen_setup_21d2602.sh

# 2. Inject explicit matplotlib into native python setup script conda line if needed
# # sed -i 's/pythonocc-core gmsh numpy pip/pythonocc-core gmsh numpy pip matplotlib/g' .github/workflows/*.yml

# 3. Patch local workspace requirements definition matrix file
# # sed -i '/jsonschema>=/a matplotlib>=3.7.0' requirements.txt

# 4. Inline dynamic code recovery: Wrap mask_visualizer.py imports in a protective try-except block
# # sed -i 's/import matplotlib/try:\n    import matplotlib\nexcept ImportError:\n    import sys\n    print("🚨 Hot-patching environment at runtime")\n    import subprocess\n    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])\n    import matplotlib/' src/utils/mask_visualizer.py

echo "✅ Forensic deep audit pass completed successfully."