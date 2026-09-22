"""Refine only the positive conservative-envelope contacts from Seeed study.

Zero envelope intersections are already a conservative exclusion. This
second pass avoids hundreds of slow empty shell vs electronics booleans.
No CAD document is edited. It is still not mounting/acoustic approval.
"""
from pathlib import Path
import hashlib,json
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/reference/head-electronics-2026-09-22'
CAD=ROOT/'hardware/skorupa/v32'
path=OUT/'measurements.json';report=json.loads(path.read_text())
source=OUT/'ReSpeakerLitev1.1.step'
assert hashlib.sha256(source.read_bytes()).hexdigest()==report['step_sha256']
assert hashlib.sha256((CAD/'Kot_v32_NOS_TOF.FCStd').read_bytes()).hexdigest()==report['cat_sha256']
assert json.loads((CAD/'shape-cache/index.json').read_text())['source_sha256']==report['cat_sha256']
s=Part.Shape();s.read(str(source));assert s.isValid()
cases=[]
for candidate in report['cases']:
    pose=A.Placement(A.Vector(*candidate['base_mm']),A.Rotation(A.Vector(0,0,1),candidate['rotation_z_deg']))
    moved=s.copy();moved.Placement=pose*moved.Placement;solids=moved.Solids
    contacts=[]
    for item in candidate['potential_interferences']:
        name=item['part'];other=Part.Shape();other.read(str(CAD/'shape-cache'/(name+'.brep')))
        total=0.;pairs=0;components=[]
        for i,left in enumerate(solids):
            if not left.BoundBox.intersect(other.BoundBox):continue
            volume=0.
            for right in other.Solids:
                if not left.BoundBox.intersect(right.BoundBox):continue
                common=left.common(right);assert common.isNull() or common.isValid(),(name,i)
                volume+=abs(common.Volume);pairs+=1
            if volume>.01:components.append(dict(step_solid_index=i,volume_mm3=volume))
            total+=volume
        contacts.append(dict(part=name,exact_solid_pairs=pairs,volume_mm3=total,
                             actual_material_collision=total>.01,colliding_step_solids=components))
        print(candidate['rotation_z_deg'],name,total,'pairs',pairs,flush=True)
    cases.append(dict(rotation_z_deg=candidate['rotation_z_deg'],contacts=contacts))
result=dict(step_sha256=report['step_sha256'],cat_sha256=report['cat_sha256'],
            envelope_report_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            integrated=False,mounts_approved=False,cases=cases,
            scope=__doc__)
(OUT/'detailed-contacts.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2),flush=True)
