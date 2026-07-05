# --------------------------------------------------------------------------
# 4. TARGETED REPAIR: CategorizationStep Constructor
# --------------------------------------------------------------------------
echo ""
echo "=== 🔧 Applying Targeted Fix: CategorizationStep __init__ ==="

# Strategy: 
# 1. Update __slots__ to allow the new attribute.
# 2. Inject the __init__ constructor to accept use_gmsh.

sed -i "s|__slots__ = ()|__slots__ = ('use_gmsh',)|g" src/steps/categorization.py
sed -i "/__slots__ = ('use_gmsh',)/a \    def __init__(self, use_gmsh: bool):\n        self.use_gmsh = use_gmsh" src/steps/categorization.py

echo "Use the commands above to enable state-passing in the CategorizationStep."