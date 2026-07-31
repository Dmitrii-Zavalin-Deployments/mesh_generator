#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "=== 1. DIAGNOSTICS: RUFF & DUPLICATE SYM AUDIT ==="
echo "=================================================="
echo "[+] Locating all definitions of test_voxelization_invalid_tolerance:"
grep -n "def test_voxelization_invalid_tolerance" tests/test_voxelization.py || true

# echo -e "\n[+] Capturing Ruff F811 lint diagnostic output:"
# ruff check tests/test_voxelization.py --select F811 || true


echo -e "\n=================================================="
echo "=== 2. SMOKING-GUN SOURCE AUDIT (cat -n)       ==="
echo "=================================================="
echo "[+] Target File: tests/test_voxelization.py"
echo "--- Section A: Existing Parameterized Test (around line 41) ---"
cat -n tests/test_voxelization.py | sed -n '38,48p'

echo -e "\n--- Section B: Duplicate Definition (around line 101) ---"
cat -n tests/test_voxelization.py | sed -n '98,110p'


echo -e "\n=================================================="
echo "=== 3. AUTOMATED REPAIR INJECTIONS (PRESERVED) ==="
echo "=================================================="
echo "[!] Un-comment the sed injections below to auto-repair the collision."

# Renames the line 101 duplicate function to avoid colliding with line 41
# sed -i 's/def test_voxelization_invalid_tolerance():/def test_voxelization_invalid_tolerance_execution():/' tests/test_voxelization.py

# Auto-resolves lingering lint/formatting issues post-rename
# ruff check src tests --fix