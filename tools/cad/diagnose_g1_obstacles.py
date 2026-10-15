"""Map ALL eight received G1 conflicts to their actual printed subparts.

Pinned nominal snapshot, not a full motion/material acceptance gate. This is
the whole-layout diagnosis after two failures, not another scalar offset.
"""
import json,time,zipfile
import FreeCAD as A
import Part
from plan_g1_rooted_carrier import geometry
from plan_body36_receiver_space import P
from plan_axial_source_supports import arm_box
from loom_land_port import box
from build_front_fixed_port_clearance import placement

WANTED={'W4_OutputJointSleeve','W4_XB32','W3Ref_YawSource_Band','MTA/FR',
        'wire/head-supply-checkpoint/XB12','wire/head-supply-checkpoint/XB13',
        'wire/head-supply-checkpoint/XS13','wire/tail-wiring-checkpoint/XB32'}

def run():
    tick=time.monotonic();_,_,recipe=geometry()
    pieces={r['name']:box(r['bounds_mm']) for r in recipe['pads']}
    pieces.update({'Root'+str(i):arm_box(a,b,[2,2,2]) for i,(a,b) in enumerate(zip(recipe['root_path_mm'],recipe['root_path_mm'][1:]))})
    for r in recipe['lands']:
        s=box(r['seat']).fuse(box(r['foot'])).cut(box(r['ring_cut']['outer']).cut(box(r['ring_cut']['inner']))).removeSplitter()
        s.Placement=placement(r['local_to_world'])*s.Placement
        pieces[r['wire']+'Seat']=s;pieces[r['wire']+'Bridge']=box(r['bridge_mm'])
    archive=P.OUT.parent/'current-view-60-20261012.zip';records=[]
    with zipfile.ZipFile(archive) as z:
        rows=json.loads(z.read('index.json'))['entries'];selected=[r for r in rows if r['label'] in WANTED]
        assert len(selected)==len(WANTED)
        for row in selected:
            s=Part.Shape();s.importBrepFromString(z.read(row['file']).decode());assert s.isValid()
            radius=row.get('radius_mm',0);b=s.BoundBox
            record=dict(name=row['label'],bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],radius_mm=radius,subparts=[])
            for n,p in pieces.items():
                bb=p.BoundBox;bb.enlarge(radius+.25 if radius else 1e-4)
                if not bb.intersect(s.BoundBox):continue
                if radius:
                    gap=min(p.distToShape(e)[0] for e in s.Edges)
                    if gap<radius+.25:record['subparts'].append(dict(name=n,gap_mm=gap,required_mm=radius+.25))
                else:
                    volume=p.common(s).Volume
                    if volume>1e-5:record['subparts'].append(dict(name=n,volume_mm3=volume))
            records.append(record);print(json.dumps(record),flush=True)
    result=dict(status='ALL_EIGHT_KNOWN_G1_OBSTACLES_MAPPED_NOT_NEW_LAYOUT_ACCEPTANCE',obstacles=records,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (archive,P.OUT/'g1-rooted-carrier-plan.json',P.ROOT/'tools/cad/plan_g1_rooted_carrier.py',P.ROOT/'tools/cad/diagnose_g1_obstacles.py')},
        worker_seconds=round(time.monotonic()-tick,3),physical_pass=False)
    (P.OUT/'g1-whole-obstacles.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':run()
