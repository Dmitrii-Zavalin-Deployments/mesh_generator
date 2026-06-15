#!/bin/bash
# ==============================================================================
# Forensic Audit: Validating Dummy File Geometric Content
# ==============================================================================

echo "--- 1. GEOMETRY DIAGNOSTICS (Does it contain solid topology?) ---"
# Check if the file contains BREP or SHELL keywords needed for 3D shapes
if grep -qE "(CLOSED_SHELL|MANIFOLD_SOLID_BREP)" tests/dummies/dummy_model.stp; then
    echo "[OK] Valid 3D topology definitions found."
else
    echo "[!] ALERT: No 3D topology (CLOSED_SHELL/BREP) found in tests/dummies/dummy_model.stp"
fi
echo ""

echo "--- 2. SMOKING-GUN SOURCE AUDIT ---"
# Show the DATA section of the dummy file to prove it only contains a LINE
cat -n tests/dummies/dummy_model.stp | grep -A 10 "DATA;"
echo ""

echo "--- 3. REPAIR INJECTION ---"
# Overwrite the dummy file with a valid 1mm Sphere MANIFOLD_SOLID_BREP.
# (Note: Overwriting via cat is much safer here than 30 lines of sed injections).
cat << 'EOF' > tests/dummies/dummy_model.stp
ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('OpenCASCADE Model'),'2;1');
FILE_NAME('sphere.stp','2024-01-01',(''),(''),'','','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#1 = APPLICATION_CONTEXT('core data for automotive mechanical design processes');
#2 = APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#1);
#3 = PRODUCT_CONTEXT('',#1,'mechanical');
#4 = PRODUCT('Sphere','Sphere','',(#3));
#5 = PRODUCT_DEFINITION_FORMATION('','',#4);
#6 = PRODUCT_DEFINITION_CONTEXT('part definition',#1,'design');
#7 = PRODUCT_DEFINITION('design','',#5,#6);
#8 = PRODUCT_DEFINITION_SHAPE('','',#7);
#9 = ADVANCED_BREP_SHAPE_REPRESENTATION('',(#10),#24);
#10 = MANIFOLD_SOLID_BREP('',#11);
#11 = CLOSED_SHELL('',(#12));
#12 = ADVANCED_FACE('',(#13),#18,.T.);
#13 = FACE_BOUND('',#14,.T.);
#14 = VERTEX_LOOP('',#15);
#15 = VERTEX_POINT('',#16);
#16 = CARTESIAN_POINT('',(0.0,0.0,1.0));
#17 = CARTESIAN_POINT('',(0.0,0.0,0.0));
#18 = SPHERICAL_SURFACE('',#19,1.0);
#19 = AXIS2_PLACEMENT_3D('',#17,#20,#21);
#20 = DIRECTION('',(0.0,0.0,1.0));
#21 = DIRECTION('',(1.0,0.0,0.0));
#22 = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );
#23 = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );
#24 = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNIT_ASSIGNED_CONTEXT((#22,#23)) REPRESENTATION_CONTEXT('Context #1','3D Context') );
#25 = SHAPE_DEFINITION_REPRESENTATION(#8,#9);
ENDSEC;
END-ISO-10303-21;
EOF

echo "--- Forensic Audit Complete. Review the logs above. ---"