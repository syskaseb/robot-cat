"""Historical preflight on defective v32 head: diagnostic, NOT fit approval.

Use audit33.py and the independent mesh proof for the integrated mount. The
old head's Boolean classification is known unreliable; retained for comparison.
"""
from pathlib import Path
import json, hashlib
import FreeCAD as A
import Part

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / 'hardware/skorupa/v32'
OUT = ROOT / 'hardware/skorupa/v33/shape-cache/preflight-study'
OUT.mkdir(parents=True,exist_ok=True)
plan = json.loads((OLD/'assembly-plan.json').read_text())
assert hashlib.sha256((OLD/plan['cad_filename']).read_bytes()).hexdigest() == plan['source_sha256']
assert json.loads((OLD/'shape-cache/index.json').read_text())['source_sha256'] == plan['source_sha256']
source = ROOT/'hardware/reference/head-electronics-2026-09-22/ReSpeakerLitev1.1.step'
assert hashlib.sha256(source.read_bytes()).hexdigest() == '4a9585d0177dbcfc0efa7d740c8731d0848484c89ee47e4a0cc919afd65d1528'
pcb = Part.Shape(); pcb.read(str(source))
pose = A.Placement(A.Vector(-238.453487382385, -81.250000000129, 139.6), A.Rotation(A.Vector(0,0,1),90))
pcb.Placement = pose*pcb.Placement
bb = pcb.BoundBox
envelope = Part.makeBox(bb.XLength,bb.YLength,bb.ZLength,A.Vector(bb.XMin,bb.YMin,bb.ZMin))
def exact(a,b):
    common=a.common(b)
    assert common.isNull() or common.isValid()
    return abs(common.Volume)
shapes={}
for r in plan['components']:
    if r['name']=='Microphones':continue
    s=Part.Shape();s.read(str(OLD/'shape-cache'/(r['name']+'.brep')));shapes[r['name']]=s
hits=[]
for n,s in shapes.items():
    if not s.BoundBox.intersect(bb):continue
    v=exact(envelope,s)
    if v>.01:
        v=sum(exact(a,b) for a in pcb.Solids for b in s.Solids if a.BoundBox.intersect(b.BoundBox))
        hits.append(dict(part=n,actual_overlap_mm3=v))
    print('PCB broadphase',n,'overlap',v,flush=True)
supports=[]
holes=[pose.multVec(A.Vector(*p)) for p in [(100.44,-105.295,0),(42.73,-76.375,0)]]
for i,(point,outer) in enumerate(zip(holes,[54.5,-53])):
    x,y=point.x,point.y
    low,high=(y-2,outer) if y>0 else (outer,y+2)
    beam=Part.makeBox(8,high-low,4,A.Vector(x-4,low,132))
    post=Part.makeCylinder(2.5,3.6,A.Vector(x,y,136))
    s=beam.fuse(post).cut(Part.makeCylinder(1.2,8,A.Vector(x,y,132)))
    overlaps=[]
    for n,b in list(shapes.items())+[('Microphones',pcb)]:
        if not s.BoundBox.intersect(b.BoundBox):continue
        # Only the local support intersects a handful of STEP solids.
        v=sum(exact(a,q) for a in s.Solids for q in b.Solids if a.BoundBox.intersect(q.BoundBox))
        if v>.01:overlaps.append(dict(part=n,volume_mm3=v))
    end_inside=[shapes['HeadFront'].isInside(A.Vector(xx,outer,zz),1e-6,True)
                for xx in [x-3.9,x,x+3.9] for zz in [132.1,134,135.9]]
    supports.append(dict(index=i,hole=[x,y],beam_bounds=[x-4,low,132,8,high-low,4],overlaps=overlaps,end_points_inside_shell=end_inside))
    print('Support',supports[-1],flush=True)
result=dict(v32_sha256=plan['source_sha256'],pcb_pose_base=list(pose.Base),rotation_z_degrees=90,
            pcb_clearance_checks=hits,supports=supports,scope=__doc__,integrated=False)
(OUT/'microphone-study.json').write_text(json.dumps(result,indent=2),encoding='utf8',newline='\n')
print(json.dumps(result,indent=2),flush=True)
