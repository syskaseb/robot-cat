"""Search a rear-exit flat-wrench corridor; read-only tool envelopes."""
from pathlib import Path
import math,json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v33'
d=A.openDocument(str(OUT/'HeadDesign33.FCStd'));pcb=d.getObject('ReSpeaker33');shapes={'HeadFront':d.getObject('HeadFace33').Shape,'Microphones':pcb.Shape}
for n in ['EarL','EarR','Camera','IrIlluminator','EyeRingL','EyeRingR','ToF','Nose']:
    s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v32/shape-cache'/(n+'.brep')));shapes[n]=s
v=pcb.Placement.multVec(A.Vector(42.73,-76.375,0));x,y=v.x,v.y;rows=[]
for angle in [-45,-30,-15,15,30,45]:
    length=(-120-x)/math.cos(math.radians(angle));s=Part.makeBox(length,6,2,A.Vector(0,-3,0))
    s.Placement=A.Placement(A.Vector(x,y,141.11),A.Rotation(A.Vector(0,0,1),angle));hits=[]
    for n,b in shapes.items():
        if not s.BoundBox.intersect(b.BoundBox):continue
        volume=sum(abs(a.common(q).Volume) for a in s.Solids for q in b.Solids if a.BoundBox.intersect(q.BoundBox))
        if volume>.01:hits.append(dict(part=n,volume_mm3=volume))
    r=dict(angle_deg=angle,blockers=hits);rows.append(r);print(r,flush=True)
(OUT/'wrench-study.json').write_text(json.dumps(rows,indent=2),encoding='utf8',newline='\n')
