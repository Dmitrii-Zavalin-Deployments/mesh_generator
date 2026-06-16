#!/bin/bash
# ==============================================================================
# src/debug/forensic_audit.sh
# Deep Forensic Audit & Automated Repairs for Config Signatures & Serialization
# ==============================================================================

echo "============================================================"
echo "1. GREP/CAT DIAGNOSTICS FOR CODE/OUTPUT ROOT CAUSES"
echo "============================================================"

echo "[DIAGNOSTIC] Checking for json serialization usage in pipeline or test files..."
grep -rn "json\." src/ tests/ || echo "No explicit json calls found via quick search."

echo -e "\n[DIAGNOSTIC] Checking how MeshGeneratorConfig is instantiated in config tests..."
grep -n "MeshGeneratorConfig(" tests/config/test_mesh_generator_config.py || echo "No direct instantiations found in test file."

echo "============================================================"
echo "2. SMOKING-GUN SOURCE AUDITS (cat -n)"
echo "============================================================"

echo "[AUDIT] Examining current constructor signature in mesh_generator_config.py:"
cat -n src/implementation/config/mesh_generator_config.py | head -n 45

echo -e "\n[AUDIT] Examining current loading strategy in config_loader.py:"
cat -n src/implementation/config/config_loader.py

echo "============================================================"
echo "3. AUTOMATED REPAIR INJECTIONS (Commented out with # sed)"
echo "============================================================"

# # Fix 1: Equip MeshGeneratorConfig constructor with a default value to prevent unit test breaks
# sed -i 's/min_element_size: float/min_element_size: float, boundary_conditions: dict = None/g' src/implementation/config/mesh_generator_config.py

# # Fix 2: Inject the property assignment inside the MeshGeneratorConfig initialization block
# sed -i "s/super().__setattr__('min_element_size', min_element_size)/super().__setattr__('min_element_size', min_element_size)\n        super().__setattr__('boundary_conditions', boundary_conditions if boundary_conditions is not None else {})/g" src/implementation/config/mesh_generator_config.py

# # Fix 3: Update get_values_for_type to dynamically pull from the boundary_conditions attribute
# sed -i 's/return {/if hasattr(self, "boundary_conditions") and bc_type in self.boundary_conditions:\n            return self.boundary_conditions[bc_type]\n        return {/g' src/implementation/config/mesh_generator_config.py

# # Fix 4: Enforce No-Defaults Policy at the gateway while supporting incoming dictionary values
# sed -i "s/'min_element_size'/'min_element_size',\n            'boundary_conditions'/g" src/implementation/config/config_loader.py
# sed -i "s/min_element_size=data\['min_element_size'\]/min_element_size=data\['min_element_size'\],\n            boundary_conditions=data.get\('boundary_conditions', {}\)/g" src/implementation/config/config_loader.py

# # Fix 5: Monkeypatch json.JSONEncoder globally to transparently support MeshGeneratorConfig serialization
# sed -i '$a \\nimport json\n_old_json_default = json.JSONEncoder.default\ndef _custom_json_default(self, obj):\n    from src.implementation.config.mesh_generator_config import MeshGeneratorConfig\n    if isinstance(obj, MeshGeneratorConfig):\n        return {"solver_version": obj.solver_version, "tolerance": obj.tolerance, "max_element_size": obj.max_element_size, "min_element_size": obj.min_element_size, "boundary_conditions": getattr(obj, "boundary_conditions", {})}\n    return _old_json_default(self, obj)\njson.JSONEncoder.default = _custom_json_default' src/implementation/config/mesh_generator_config.py

echo "============================================================"
echo "Forensic Audit Script Complete."
echo "============================================================"