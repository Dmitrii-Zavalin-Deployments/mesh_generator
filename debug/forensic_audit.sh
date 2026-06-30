#!/bin/bash
# src/debug/forensic_audit.sh

# Disable exit-on-error to ensure a thorough diagnostic sweep completes
set +e

echo "========================================================================"
echo "🔍 PHASE 1: GREP DIAGNOSTICS FOR CLI & I/O ROOT CAUSES"
echo "========================================================================"
echo "[TEST RUNNER] System Timestamp: $(date +'%Y-%m-%d %H:%M:%S')"

TARGET_SRC="src/main.py"
TARGET_TEST="tests/test_main.py"

echo -e "\n🔍 Scanning for argument parsing configurations and custom exit calls:"
grep -n -E "ArgumentParser|sys.exit|exit\(" "$TARGET_SRC" || echo "⚠️ No explicit argparse or exit symbols found."

echo -e "\n🔍 Scanning for binary or write file handle allocations ('wb', 'rb'):"
grep -n -E "open\(.*,.*b.*\)|.write\(|.read\(" "$TARGET_SRC" || echo "⚠️ No explicit binary file operations found."

echo -e "\n🔍 Scanning test assertions for exit code expectations:"
grep -n -A 3 -B 3 "SystemExit" "$TARGET_TEST" || echo "⚠️ No SystemExit hooks located in test suite."

echo "========================================================================"
echo "🔬 PHASE 2: SMOKING-GUN SOURCE AUDITS (CAT -N MATRIX)"
echo "========================================================================"
if [ -f "$TARGET_SRC" ]; then
    echo "📄 Line Audit: $TARGET_SRC (Main Entrypoint Engine Structure)"
    cat -n "$TARGET_SRC" | head -n 120
else
    echo "❌ CRITICAL: Source file $TARGET_SRC not found."
fi

if [ -f "$TARGET_TEST" ]; then
    echo -e "\n📄 Line Audit: $TARGET_TEST (Failing Assertion Target Windows)"
    cat -n "$TARGET_TEST" | grep -n -C 5 -E "test_main_cli_argument_error|test_main_happy_path" || cat -n "$TARGET_TEST" | head -n 100
else
    echo "❌ CRITICAL: Test file $TARGET_TEST not found."
fi

echo "========================================================================"
echo "🛠️ PHASE 3: AUTOMATED IN-ENVIRONMENT REPAIRS (SED INJECTIONS)"
echo "========================================================================"
echo "The following sed routines repair CLI structural exits and I/O typing issues."
echo "Uncomment these steps within your GHA step execution context to clear the gate."

# --- Repair Track A: Re-align Argparse Exit Status or Override Default Behavior ---
# Force argparse to bubble up custom exit status code 1 or catch SystemExit(2) to normalize it
# sed -i 's/sys.exit(2)/sys.exit(1)/g' "$TARGET_SRC"
# If overriding standard argparse error handler is needed within src/main.py:
# sed -i '/parser = argparse.ArgumentParser/a \    parser.error = lambda message: sys.exit(1)' "$TARGET_SRC"

# --- Repair Track B: Correct Test Expectations to Match Standard CLI Conventions ---
# Adjust test assertions if the testing framework must adapt to standard argparse exit codes (2)
# sed -i 's/assert e.value.code == 1/assert e.value.code == 2/g' "$TARGET_TEST"

# --- Repair Track C: Resolve String-to-Bytes Conversion Failures ---
# Option 1: Convert file handle generation mode from binary write ('wb') to text write ('w')
# sed -i "s/open(\(.*\), *['\"]wb['\"])/open(\1, 'w', encoding='utf-8')/g" "$TARGET_SRC"

# Option 2: Explicitly encode input string strings to bytes if binary streams are non-negotiable
# sed -i 's/\.write(payload)/\.write(payload.encode("utf-8"))/g' "$TARGET_SRC"

echo "========================================================================"
echo "🎉 Forensic diagnostic audit process terminated cleanly."
echo "========================================================================"