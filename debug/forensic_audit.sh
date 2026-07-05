# --------------------------------------------------------------------------
# 4. TARGETED REPAIR: Short-circuit BC Validation
# --------------------------------------------------------------------------
echo ""
echo "=== 🔧 Applying Targeted Fix: BoundaryConditionsStep Logic ==="

# Strategy: Update the conditional check on line 30.
# If use_gmsh is True, we skip the 'grid'/'mask' validation entirely, 
# as those structures are specific to the legacy Voxelizer engine.

sed -i 's|if container.grid is None or container.mask is None:|if not container.use_gmsh and (container.grid is None or container.mask is None):|g' src/steps/boundary_conditions.py

echo "The 'if' statement on line 30 has been patched to allow bypass when 'use_gmsh' is active."