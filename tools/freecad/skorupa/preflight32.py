"""Candidate geometry only: ToF mount / conservative optical clearance.

Production geometry is to be authored with native MCP PartDesign features.
"""
from pathlib import Path
import hashlib,json,math,itertools
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v32';OUT.mkdir(exist_ok=True)
CACHE=ROOT/'hardware/skorupa/v31/shape-cache'
plan=json.loads((CACHE.parent/'assembly-plan.json').read_text())
assert hashlib.sha256((CACHE.parent/plan['cad_filename']).read_bytes()).hexdigest()==plan['source_sha256']
assert json.loads((CACHE/'index.json').read_text())['source_sha256']==plan['source_sha256']
base=A.Vector(-200.2,-8.789181,106.932374)
pose=A.Placement(base,A.Rotation(A.Vector(0,1,0),-90))
old={}
for row in plan['components']:
    s=Part.Shape();s.read(str(CACHE/(row['name']+'.brep')))
    s.Placement=pose.inverse()*s.Placement;old[row['name']]=s
cx,cy=7.692626,8.789181
holes=[(10.16,2.54),(10.16,15.24)]
outline=Part.makeBox(17,26,2.5,A.Vector(cx-8.5,cy-13,3))
vertical=[e for e in outline.Edges if len(e.Vertexes)==2 and abs(e.Vertexes[0].Point.z-e.Vertexes[1].Point.z)>2.49]
nose=outline.makeFillet(4,vertical)
muzzle=old['Muzzle'].cut(Part.makeBox(17,26,15,A.Vector(cx-8.5,cy-13,3)))
# Two side bridges are integral with the muzzle; board-front datum z=1.016.
for y0,y1 in [(cy-15,2.54+3),(15.24-3,cy+15)]:
    muzzle=muzzle.fuse(Part.makeBox(6,y1-y0,1.984,A.Vector(7.16,y0,1.016)))
for x,y in holes:
    hole=Part.makeCylinder(1.2,15,A.Vector(x,y,-7))
    muzzle=muzzle.cut(hole);nose=nose.cut(hole)
window=Part.makeBox(10,6.5,20,A.Vector(cx-5,cy-3.25,1.016))
nose=nose.cut(window);muzzle=muzzle.cut(window)
pcb=Part.read(str(ROOT/'hardware/reference/component-selection-2026-09-22/vl53l5cx-pololu-3417.step'))
new=dict(Muzzle=muzzle,Nose=nose,ToF=pcb)
for i,(x,y) in enumerate(holes):
    new['ToFSpacer32_%d'%i]=Part.makeCylinder(2.5,4,A.Vector(x,y,-4)).cut(Part.makeCylinder(1.2,4,A.Vector(x,y,-4)))
    new['ToFBolt32_%d'%i]=Part.makeCylinder(1,12,A.Vector(x,y,-6.5)).fuse(Part.makeCylinder(2.1,2,A.Vector(x,y,5.5)))
    # Circumscribed nut envelope is conservative; native model will be hexagonal.
    new['ToFNut32_%d'%i]=Part.makeCylinder(2.309401,1.6,A.Vector(x,y,-5.6)).cut(Part.makeCylinder(1,1.6,A.Vector(x,y,-5.6)))
def rectangle(x0,x1,y0,y1,z):
    points=[A.Vector(x0,y0,z),A.Vector(x1,y0,z),A.Vector(x1,y1,z),A.Vector(x0,y1,z)]
    return Part.makePolygon(points+[points[0]])
def bounds(z):
    e=(z-2.566)*math.tan(math.radians(22.5))
    return [4.1-e,11.2+e,6.98-e,10.7+e]
optical=Part.makeLoft([rectangle(*bounds(z),z) for z in [2.566,60]],True,True)
combined={**old,**new};hits=[];pairs=0
for an,bn in itertools.combinations(sorted(combined),2):
    if not ({an,bn}&set(new)):continue
    a,b=combined[an],combined[bn]
    if not a.BoundBox.intersect(b.BoundBox):continue
    pairs+=1;v=abs(a.common(b).Volume)
    if v>.01:hits.append(dict(parts=[an,bn],volume_mm3=v))
    if pairs%10==0:print('pair',pairs,'hits',hits,flush=True)
optical_hits=[]
for n,s in combined.items():
    if n=='ToF' or not optical.BoundBox.intersect(s.BoundBox):continue
    v=abs(optical.common(s).Volume)
    if v>.01:optical_hits.append(dict(part=n,volume_mm3=v))
report=dict(source_sha256=plan['source_sha256'],pcb_base_CAD_mm=list(base),pcb_rotation='Ry(-90)',
    holes_local_xy_mm=holes,broadphase_pairs=pairs,rest_interferences=hits,optical_interferences=optical_hits,
    optical_assumption='Full package top bounding rectangle enlarged by about 0.3 mm on every side; 45 deg full FOV; 60 mm frontward probe. Geometry only, not crosstalk/range certification.',
    shapes=[dict(name=n,valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume) for n,s in new.items()],
    print_release=False,scope=__doc__)
(OUT/'preflight.json').write_text(json.dumps(report,indent=2),encoding='utf8')
for n,s in {**new,'OpticalReserve32':optical}.items():
    s.Placement=pose*s.Placement;s.exportBrep(str(OUT/(n+'-candidate.brep')))
print(json.dumps(report,indent=2))
