"""Isolated, read-only candidate layout check using conservative PCB envelope.

Temporary probe solids, not a substitute for the native MCP model. Keeping
complex catalogue-PCB booleans out of the interactive GUI avoids blocking it.
"""
from pathlib import Path
import hashlib,json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
CACHE=ROOT/'hardware/skorupa/v29/shape-cache'
OUT=ROOT/'hardware/skorupa/v30';OUT.mkdir(exist_ok=True)
plan=json.loads((ROOT/'hardware/skorupa/v29/assembly-plan.json').read_text())
assert json.loads((CACHE/'index.json').read_text())['source_sha256']==plan['source_sha256']
holes=[(x,y) for x in [-35.68,-53.46] for y in [-22.86,-2.54]]
old={}
for row in plan['components']:
    if row['name']=='IMU':continue
    s=Part.Shape();s.read(str(CACHE/(row['name']+'.brep')));old[row['name']]=s
probes={'PCBEnvelope':Part.makeBox(22.86,25.4,4.53,A.Vector(-56,-25.4,45)),
        'STEMMAPlugKeepout':Part.makeBox(8,8,6.5,A.Vector(-48.57,-33.4,46)),
        'STEMMAWireRiseKeepout':Part.makeBox(8,10,6.5,A.Vector(-48.57,-43.4,50))}
for i,(x,y) in enumerate(holes):
    probes['Standoff_%d'%i]=Part.makeCylinder(3,6.48,A.Vector(x,y,38.52)).cut(Part.makeCylinder(1.2,6.48,A.Vector(x,y,38.52)))
    probes['M2ScrewEnvelope_%d'%i]=Part.makeCylinder(1,12,A.Vector(x,y,34.57)).fuse(Part.makeCylinder(2.1,2,A.Vector(x,y,46.57)))
    probes['M2NutEnvelope_%d'%i]=Part.makeCylinder(2.309401,1.6,A.Vector(x,y,35.42)).cut(Part.makeCylinder(1,1.6,A.Vector(x,y,35.42)))
cover=old['Part__Feature038'];full=[]
for x,y in holes:
    full.append(cover.common(Part.makeCylinder(1.2,2,A.Vector(x,y,37))).Volume)
    cover=cover.cut(Part.makeCylinder(1.2,2,A.Vector(x,y,37)))
old['Part__Feature038']=cover
old['ShellMounted20']=old['ShellMounted20'].cut(Part.makeCompound([Part.makeCylinder(3.4,8,A.Vector(x,y,37)) for x,y in holes]))
hits=[];pairs=0
for n,a in probes.items():
    for other,b in old.items():
        if not a.BoundBox.intersect(b.BoundBox):continue
        pairs+=1;v=abs(a.common(b).Volume)
        if v>.01:hits.append(dict(probe=n,part=other,volume_mm3=v))
    print(n,'done',flush=True)
result=dict(source_checkpoint='v29',source_sha256=plan['source_sha256'],
            scope='Conservative PCB and two cable/plug envelopes plus nominal hardware, against all retained parts. Proposed four cover holes and four clearance passages in shell floor; not yet native feature verification.',
            holes_CAD_xy_mm=holes,material_removed_per_hole_mm3=full,
            broadphase_pairs=pairs,hits=hits,print_release=False)
(OUT/'preflight.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
