"""Make the 20H local S0 fitting panel and its exact printed witness."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile
from xml.etree import ElementTree
import json
import os
import math
import FreeCAD as App
import Part

here = Path(__file__).resolve().parent
old = here.parent / '20G/whole-cat20G.FCStd'
old_sha = '67b26e6038811cdd75d5f944776207a835fb15e82b19e62ed83044f0d0ec1b58'
assert sha256(old.read_bytes()).hexdigest() == old_sha
V = App.Vector
controls = run_path(str(here.parent / '20G/candidate.py'))
fixings = run_path(str(here.parent / '20G/hardware.py'))['load']()
bounds = controls['bounds']
contact = controls['solid_hit']

def saved_shapes(names):
    with ZipFile(old) as z:
        xml = ElementTree.fromstring(z.read('Document.xml'))
        shapes = {}
        for name in names:
            ref = xml.find(f"./ObjectData/Object[@name='{name}']/Properties/Property[@name='Shape']/Part")
            assert ref is not None, name
            shape = Part.Shape()
            shape.importBrepFromString(z.read(ref.attrib['file']).decode('ascii'))
            shapes[name] = shape
    return shapes

def bore(x, z, r, y0=98.89, y1=103.12):
    return Part.makeCylinder(r, y1-y0, V(x,y0,z), V(0,1,0))

def stable_brep(shape):
    """Round-trip the OCC representation before qualifying its geometry."""
    volume = shape.Volume
    saved = Part.Shape()
    saved.importBrepFromString(shape.exportBrepToString())
    fixed = not saved.isValid()
    if fixed:
        assert saved.fix(1e-7,1e-8,1e-5)
    raw = saved.exportBrepToString()
    readback = Part.Shape()
    readback.importBrepFromString(raw)
    assert readback.isValid() and len(readback.Solids)==1
    assert abs(readback.Volume-volume)<.001
    return readback, raw, fixed

x = 178.5
z = 104.5
hole_centers = [z-19, z+19]
watch = ['E19_RearBase','E19_RearLid','F19_RearCap','E1_populated_prototype_board',
         'E19_WagoRearPos','S0_body','S0_neck','S0_key',*controls['stack_names'],
         'G20_W066_Out_To_PSYS','C20_Protected_and_Return']
sh = saved_shapes(dict.fromkeys(watch))
base = sh['E19_RearBase']
key = sh['S0_key']
surface_types = [type(face.Surface).__name__ for face in key.Faces]
assert surface_types.count('Cylinder') == 1 and surface_types.count('Plane') == 2, surface_types
assert abs(key.Volume-math.pi*15**2*63.5)<1e-5
assert bounds(key)==[163.5,102.,89.5,193.5,165.5,119.5]

# Keep the switch pose and the Y99 body face. Restore two local flat
# printed bearing lands to Y102 (3 mm), matching the planned washer datum.
land_radius = 8.5
lands = [bore(x,c,land_radius,99.,102.) for c in hole_centers]
facing = [bore(x,c,land_radius,y0,y1) for c in hole_centers
          for y0,y1 in [(98.89,99.),(102.,103.12)]]
passages = [bore(x,z,12), *[bore(x,c,3.25) for c in hole_centers]]
with_lands = base
for land in lands:
    assert base.common(land).Volume>40
    with_lands = with_lands.fuse(land)
rear = with_lands.cut(Part.makeCompound(facing)).cut(Part.makeCompound(passages)).removeSplitter()
assert rear.isValid() and len(rear.Solids)==1
rear, rear_brep, rear_healed = stable_brep(rear)
assert all(contact(rear, h) is None for h in passages)
added = rear.cut(base).removeSplitter()
removed = base.cut(rear).removeSplitter()
assert added.Volume<1000 and removed.Volume<1000
assert all(not contact(added,sh[n]) for n in watch if n not in
           ('E19_RearBase','G20_W066_Out_To_PSYS','C20_Protected_and_Return'))

# The bench coupon shares the bolt and switch axes and the printed
# bearing planes. Its uniform surround is simple to print flat.
coupon = Part.makeBox(56,3,57,V(150.5,99,76)).cut(Part.makeCompound(passages)).removeSplitter()
assert len(coupon.Solids)==1 and coupon.isValid()
coupon, coupon_brep, coupon_healed = stable_brep(coupon)

mount = {}
for i, c in enumerate(hole_centers):
    inner = bore(x,c,6.,99.,99.02).cut(bore(x,c,3.25))
    outer = bore(x,c,6.,101.98,102.).cut(bore(x,c,3.25))
    expected = math.pi*(6**2-3.25**2)
    faces = []
    for section in (inner,outer):
        sa = rear.common(section).Volume/.02
        co = coupon.common(section).Volume/.02
        assert abs(sa-expected)<1e-4 and abs(co-sa)<1e-4,(i,sa,co,expected)
        faces.append(round(sa,5))
    mount[str(c)] = {'back_front_washer_annulus_bearing_area_mm2':faces,
                     'through_stack_panel_mm':3.0}
steel_hits = {n:h for n,s in fixings.items() if (h:=contact(rear,s))}
assert not steel_hits, steel_hits
assert all(not contact(coupon,sh[n]) for n in controls['stack_names'])
key_hits = {n:h for n,s in fixings.items() if (h:=contact(key,s))}
assert len(key_hits)==4
# The max certificate for the old installed 20G shapes continues to
# hold with the panel correction because those routes stay inboard.
for n in ('G20_W066_Out_To_PSYS','C20_Protected_and_Return'):
    assert sh[n].BoundBox.YMax+3.35 < added.BoundBox.YMin
assert coupon.common(key).Volume<1e-4
result = {
    'status':'CONDITIONAL_REAR_BASE__FIT_S0_FIRST',
    'input':'01a1f9e7-6080-7281-a490-efaf69fe6c59',
    'source_20G_native_sha256':old_sha,
    'key_model':{'constructor':'tools/electronics/source_switch_layout_r6.py:43',
       'name':'S0_key_family_tool_reserve','class':'APPROXIMATE_TOOL_AND_ACTUATION_RESERVE',
       'native_radius_mm':15,'native_length_mm':63.5,'current_bounds_mm':bounds(key),
       'valid_physical_key_shape_available':False,'actual_rotation_angle_and_axial_profile':None,
       'actual_contacts_with_key':None,'steel_contacts_with_conservative_reserve_mm3':
       {n:h[0] for n,h in key_hits.items()}},
    'supplier_nominal_pattern':{'document':'HELLA-46020100.pdf','central_through_mm':24,
      'mount_through_mm':6.5,'pitch_mm':38,'pitch_tolerance_mm':0.1,
      'center_x_z_mm':[x,z],'mount_centres_x_z_mm':[[x,c] for c in hole_centers],
      'orientation':'Vertical relative to the nominal lateral post pair per sourced project datum. Confirm on purchased specimen.'},
    'y_bearing_mm':{'inside':99.,'outside':102.},
    'mounting_bearings':mount,
    'retained_broad_case_contact_mm2':round(sh['S0_body'].translated(V(0,.02,0)).common(rear).Volume/.02,4),
    'fixing_to_corrected_base_interference_mm3':0,
    'rear_base_bounds_mm':bounds(rear),'coupon_bounds_mm':bounds(coupon),
    'rear_base_added_mm3':round(added.Volume,5), 'added_bounds_mm':bounds(added), 'removed_bounds_mm':bounds(removed),'rear_base_removed_mm3':round(removed.Volume,5),
    'rear_base_volume_mm3':rear.Volume,'coupon_volume_mm3':coupon.Volume,
    'native_reopen_ok':True,'kernel_topology_healed_on_reopen':{'rear_base':rear_healed,'coupon':coupon_healed},
    'coupon_qualification':'Flat bench coupon with exactly the holes of the candidate panel, two full annular washer seats, and 3 mm bearing stack. Exterior wall transitions and neighboring fittings remain in the full assembly CAD.',
    'required_M6_stock':{'DIN912_M6x20':2,'washer_6p4x12x1p6':4,'AF10_M6_nut_h5':2,'actual_owned':None},
    'conditional_wire_blanks_mm':{'W066':260,'W076/custom':389},
    'physicalPASS':False,'actualfit':None,'cut':None,'slack':None,
}
assert result['retained_broad_case_contact_mm2']>500
def atomic_json(path,data):
    tmp=path.with_suffix('.tmp')
    with tmp.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write('\n')
    os.replace(tmp,path)

if __name__=='__main__':
    atomic_json(here/'FIT_S0-gate.json',result)
    (here/'rear_base.brep').write_bytes(rear_brep.encode('ascii'))
    (here/'coupon.brep').write_bytes(coupon_brep.encode('ascii'))
    print(json.dumps(result,ensure_ascii=False),flush=True)
