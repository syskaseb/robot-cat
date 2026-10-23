"""Record the authority of an existing S0 reservation and service cutset.

No selected geometry changes; no reservation overlap becomes a material verdict.
"""
import json
import math
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_source_restraint_plan import box


def record(scene):
    f=OUT/'n01-FPI-top-service-dependencies.json'
    prior=json.loads(f.read_text()); key=scene['Ref_Material_S0_key_CP2_0_0']
    assert len(key.Solids)==1 and len(key.Faces)==3 and key.isValid()
    assert abs(key.Volume-math.pi*15**2*63.5)<1e-5
    access=box(*prior['bounds_mm'])
    axis=Part.makeLine(key.Placement.multVec(A.Vector()),
                       key.Placement.multVec(A.Vector(0,0,63.5)))
    distance=axis.distToShape(access)[0]
    common=key.common(access); assert common.isValid()
    local=common.copy();local.Placement=key.Placement.inverse()*local.Placement
    sources=[f,ROOT/'tools/cad/whole_cat_interior.py',
        ROOT/'hardware/reference/hella-s0-primary-2026-10-16/HELLA-page259.png',
        OUT/'n01-USB-BUS-first-service-negative.json',
        OUT/'n01-BUS-module-service-retreat-sample.json',
        OUT/'n01-Pi-mated-USB-lift-service-sample.json']
    result=dict(status='SERVICE_DEPENDENCIES_RECORDED_NOT_ASSEMBLY_APPROVAL',
        S0=dict(actor='Ref_Material_S0_key_CP2_0_0',
            geometric_type='FULL_FAMILY_RESERVATION_NOT_EXACT_KEY_OR_OFF_POSE',
            radius_mm=15,height_mm=63.5,
            source_definition='whole_cat_interior.py: S0 family model includes stud space, NOT exact HELLA SKU casing',
            supplier_drawing_selected_part='002843002 on HELLA page259',
            confirmed_dimensions_mm={'panel_to_front_tip':66.5,'neck_diameter':22},
            exact_neck_axial_extent_and_key_shape_unknown=True,
            extraction25_is_project_assumption_not_measured_stroke=True,
            reservation_overlap_mm3=common.Volume,
            overlap_axial_interval_from_reservation_base_mm=[local.BoundBox.ZMin,local.BoundBox.ZMax],
            axis_to_FPI_access_mm=distance,
            sufficient_uniform_radius_with_half_mm_margin=distance-.5,
            radius_bound_is_NOT_supplier_dimension=True,
            actual_collision_proved=False,
            removing_key_does_not_remove_fixed_neck=True),
        routine_FPI=dict(prerequisites=['Isolate and physically disconnect source',
            'Release and park complete W027/W020/W031/W033/W035 groups with terminals unloaded',
            'Qualify actual fixed neck and key OFF position against F_PI access',
            'Only if key removal is necessary, qualify its actual withdrawal',
            'Open delivered cap, replace fuse, restore all restraints'],
            five_groups_are_NOT_five_WAGO_disconnects=True,
            fixed_boundaries_are_NOT_connectors=True,
            W027_known_terminal='FL_P.2',
            other_body_boundaries=['W020:FL1/fixed_boundary','W031:FR1/fixed_boundary',
                                   'W033:FR2/fixed_boundary','W035:FR3/fixed_boundary'],
            sequence_approved=False),
        rare_Pi_BUS=dict(separate_from_routine_fuse_service=True,
            Pi_first='USB gap0.430475 below project0.5; no material intersection claimed',
            BUS_plug_first='Fixed pad intersects plug withdrawal70.2mm3',
            BUS_module_retreat='Current TailCarrier witness68.382751mm3 suffices; secondary tail-mount witness ownership not requalified',
            Pi_lift_mated='Constant452mm jacket and R>=30 end pose; W009 clearance fails, continuous motion unqualified',
            sequence_approved=False),
        decision='Do not redesign Pi again solely to clear an inaccurately classified S0 key. Resolve fixed neck/key OFF geometry first; retain real cable/printed-support blockers.',
        required_measurements=['Panel to fixed neck tip',
            'Key handle thickness/width and installed OFF orientation',
            'Actual axial withdrawal needed to release the key'],
        exact_manufacturer_key_geometry_received=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sources},
        selected_geometry_changed=False,N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-service-dependency-decision-20261023.json',result)
    return result
