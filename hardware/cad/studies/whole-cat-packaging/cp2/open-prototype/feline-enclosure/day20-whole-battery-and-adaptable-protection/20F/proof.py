"""Bound every fixed-S0-tangent HELU bend at the retained RR holder."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree
import hashlib
import json
import math
import os
import FreeCAD as App
import Part

folder=Path(__file__).resolve().parent
study=folder.parent.parent
hardware=next(p for p in folder.parents if p.name=='hardware')
D=folder.parent/'20D'
E=folder.parent/'20E'
V=App.Vector

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

native=D/'whole-cat20D.FCStd'
history=E/'20E-RR-S0.json'
guide=hardware/'electronics/power-platform/POWER-WIRE-P0.md'
bearing_source=study/'day19-simple-box-common-core/module-bearings.py'
assert digest(native)=='b1549964028b289ccc9b27adb023ed804f331b8f4fa23159c00a072975a750e9'
assert digest(history)=='d4a1b9b97eaada69bebca2a1979ee5c772c8ff5cee011b7cd63ca9ca3fd058f6'
assert '6 × Ø = 25,2 mm' in guide.read_text(encoding='utf-8')
assert 'b.ZMin-1.45,6,2.75,1.35' in bearing_source.read_text(encoding='utf-8')

def box(a,b):
    return Part.makeBox(*(y-x for x,y in zip(a,b)),V(*a))

def intersect(a,b):
    c=a.common(b)
    assert c.isNull() or c.isValid()
    return float(c.Volume)

names=('E19_RearLid','Speaker','C20_MTA_RR','S0_ring_IN_0_0',
       'NIGHT_MTA0100335_UNKNOWN_3','F19_RearCap','E19_RearBase')
with ZipFile(native) as z:
    tree=ElementTree.fromstring(z.read('Document.xml'))
    source={}
    native_pins={}
    for n in names:
        p=tree.find(f"./ObjectData/Object[@name='{n}']/Properties/Property[@name='Shape']/Part")
        raw=z.read(p.get('file'))
        native_pins[n]=hashlib.sha256(raw).hexdigest()
        shape=Part.Shape()
        shape.importBrepFromString(raw.decode('ascii'))
        assert shape.isValid()
        source[n]=shape

# Reuse exactly the received 20E clearance gauge solely to identify its contact
# on the cover. Execute its immutable geometry declarations only.
e_recipe=E/'region.py'
assert digest(e_recipe)=='af59542460866df4ddbeb195cf7b28fdbe83dc067799a0baf36bdcaea69dc591'
scope={'__file__':str(folder/'proof.py')}
exec(compile(e_recipe.read_text(encoding='utf-8').split('results={}')[0],
             'received 20E geometry declarations','exec'),scope)
old_gauge=scope['gauge']
lid=source['E19_RearLid']
hit=lid.common(old_gauge)
assert hit.isValid() and hit.Volume>11
bb=source['Speaker'].BoundBox
x=bb.XMax-8
y=bb.YMin
z=bb.ZMin
foot=box([x,y-1.55,z-1.45],[x+6,y+1.2,z-.1])
web=box([x,y-1.55,z-1.45],[x+6,y-.17,171.55])
functional_member=foot.fuse(web)
assert abs(intersect(lid,foot)-foot.Volume)<1e-4
assert abs(intersect(lid,web)-web.Volume)<1e-4
assert hit.cut(functional_member).Volume<1e-4

# Distal plane centre and outbound axis from the actual modeled S0 barrel.
# The plane is one of the distal semicircular faces, so the two halves share its
# X and Z centre. Their common axis is the barrel cylinder's 3.2 mm radius axis.
ring=source['S0_ring_IN_0_0']
expected=V(-.5,0,math.sqrt(3)/2)
barrel=[f for f in ring.Faces if isinstance(f.Surface,Part.Cylinder)
        and abs(f.Surface.Radius-3.2)<1e-7 and f.Surface.Axis.dot(expected)>.99999]
assert len(barrel)==2
out=barrel[0].Surface.Axis
out.normalize()
distal=[f for f in ring.Faces if isinstance(f.Surface,Part.Plane)
        and abs(f.Surface.Axis.dot(out))>.99999 and 126<f.CenterOfMass.z<129
        and 152<f.CenterOfMass.x<154]
assert len(distal)>=2
recon=V(sum(f.CenterOfMass.x for f in distal)/len(distal),
        74.,
        sum(f.CenterOfMass.z for f in distal)/len(distal))
mouth=V(153.05,74,127.79608338621)
assert recon.distanceToPoint(mouth)<1e-4
assert all(abs((f.CenterOfMass-mouth).dot(out))<1e-4 for f in distal)

# For a unit-speed path c(s), ||c''|| <= 1/R gives
# ||c(s) - (c(0) + s*c'(0))|| <= integral_0^s (s-t)/R dt = s^2/(2R).
# Use the permissive interpretation R=25.2 on the centreline. Reading the
# 25.2 mm as an inside-jacket radius increases the centreline bound to 27.3 mm.
radius=25.2
physical_radius=2.1
clearance_required=1.25
s=11.5
witness=mouth+out*s
delta=s*s/(2*radius)
tile=box([147.15,73.8,137.65],[147.45,74.2,137.9])
assert tile.isInside(witness,.001,False)
rr=source['C20_MTA_RR']
assert rr.isInside(witness,.001,False)
volume_checked=intersect(rr,tile)
assert abs(volume_checked-tile.Volume)<1e-6
assert delta<physical_radius+clearance_required
assert (V(*[147.3,74,137.7554])-witness).Length<1e-3

old_budget=json.loads((D/'20D-final-gate.json').read_bytes())['wire_budgets']
w076=old_budget['W076_custom']
raw_ends=[V(*w076['allocated_waypoints'][i]) for i in (0,-1)]
assert raw_ends[1].distanceToPoint(mouth)<.001
ends=w076['terminal_debits_mm']
dressing=w076['one_laying_allowance_mm']
direct=(raw_ends[1]-raw_ends[0]).Length
end_distances=[(a-witness).Length for a in raw_ends]
assert min(end_distances)>delta+1.0

def xyz(v):
    return [round(x,6) for x in (v.x,v.y,v.z)]

def pin(q):
    return {'path':q.relative_to(hardware).as_posix(),'sha256':digest(q)}

result={
    'status':'HOLD_FIXED_RR_TO_S0_INTERFACE_COVER_ONLY_FALSIFIED',
    'actual_input':'01a1f9b0-fcf3-7ef1-b684-2a4247814e1c',
    'source_commits':{'20D':'9e358f17c79ac9bbf75e51762c9f8a48f05f8940',
                      '20E':'4443b0d60fa9326a2cde74c3f8aa2632aa6d4565'},
    'sources':{'native':pin(native),'20E_evidence':pin(history),'20D_manifest':pin(D/'20D-manifest.json'),
               'HELU23802_fixed_R':pin(guide),'speaker_hanger_constructor':pin(bearing_source),
               'native_shape_sha256':native_pins},
    'identified_cover_member':{
        'function':'Inboard aft loudspeaker suspension. Lower toe bears beneath the speaker and a 6 x 1.38 mm stem carries it up to the rear cover.',
        'foot_bounds_mm':[128,52.45,148.95,134,55.2,150.3],
        'stem_bounds_read_mm':[128,52.45,148.95,134,53.83,171.55],
        'foot_installed_mm3':round(foot.Volume,6),'stem_installed_in_checked_span_mm3':round(web.Volume,6),
        '20E_gauge_vs_lid_mm3':round(float(hit.Volume),6),
        '20E_overlap_outside_this_member_mm3':round(float(hit.cut(functional_member).Volume),6)
    },
    'independent_lower_interface_bound':{
        'basis':'Current S0 distal barrel mouth and rigid inboard plate floor in the retained C20_MTA_RR. Both are independent of E19_RearLid.',
        'actual_modeled_barrel_mouth_mm':xyz(mouth),'outbound_tangent':xyz(out),
        'minimum_HELU23802_fixed_bend_mm':radius,'minimum_proof_axis_radius_mm':radius,
        'inside_radius_interpretation_implies_axis_mm':radius+physical_radius,
        'outer_wire_OD_mm':2*physical_radius,'required_jacket_clearance_mm':clearance_required,
        'distance_along_any_compliant_path_mm':s,
        'straight_tangent_point_inside_print_mm':xyz(witness),
        'verified_solid_tile_mm3':round(volume_checked,6),
        'all_compliant_centres_within_mm_of_material':round(delta,6),
        'required_centre_to_rigid_mm':physical_radius+clearance_required,
        'upper_bound_jacket_clearance_at_this_station_mm':round(delta-physical_radius,6),
        'clearance_deficit_at_least_mm':round(clearance_required-(delta-physical_radius),6),
        'distance_to_wire_endpoint_centres_mm':{'POST':round(end_distances[0],3),'S0':round(end_distances[1],3)},
        'method':'The ideal tangent point is inside a volume-verified tile of the retained RR print. Bounded curvature keeps every candidate centre within s squared over 2R of this point. Both wire tips are farther away. A closest point on a differentiable candidate is interior, where the offset to material is normal to the wire. The radial clearance requirement therefore applies.'
    },
    'decision':'A cover-only relief cannot meet the selected wire bend radius together with the required 1.25 mm clearance. Preserve the intact functional speaker suspension and the received prints. This conditional result is for the currently modeled fixed S0 outlet axis and RR position. Validating a changed terminal or RR relationship requires a new decision.',
    'full_unit_budget':{
        'POST_to_S0_direct_distance_lower_bound_mm':round(direct,3),
        'end_allowances_once_mm':ends,'laying_allowance_once_mm':dressing,
        'direct_plus_end_and_laying_lower_bound_mm':math.ceil(direct+ends+dressing),
        '20D_reference_blank_mm':w076['project_blank_mm'],'20E_rejected_reference_blank_mm':385,
        'accepted_W076_custom_cut_budget_mm':None,'stock_nominal_HELU_mm':9000,
        'stock_nominal_LAPP_mm':3000,'stock_actual_mm':None,
        'W001_reference_blank_mm':old_budget['W001']['project_blank_mm'],
        'W075_project_total_mm':old_budget['W075']['project_total_mm'],
        'full_factory_F0_output_project_range_mm':old_budget['W076_complete_FHAC_out']['project_port_choices_plus_end_mm']
    },
    'physical_unknowns':['actual pack exits and full connector handling','delivered cap, factory F0 leads and WAGO pitch',
                         'four MTA body/lid/factory-end shapes','actual S0 crimp/barrel engagement',
                         'actual stock, length, bend and closure'],
    'new_prints':0,'native_changed':False,'physicalPASS':False,'actualfit':None,'cut':None,'slack':None
}
out_path=folder/'20F-interface-gate.json'
old=out_path.read_bytes() if out_path.is_file() else None
temp=out_path.with_suffix('.tmp')
with temp.open('x',encoding='utf-8',newline='\n') as f:
    json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
assert (out_path.read_bytes() if out_path.is_file() else None)==old
os.replace(temp,out_path)
print(result['status'],xyz(witness),volume_checked,delta,result['full_unit_budget'],flush=True)
