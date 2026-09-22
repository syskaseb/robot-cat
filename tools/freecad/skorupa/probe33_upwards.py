"""Read-only upward screw and tool access study against actual v33 master."""
from pathlib import Path
import FreeCAD as A
import Part,json
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v33'
d=A.openDocument(str(OUT/'HeadDesign33.FCStd'));pcb=d.getObject('ReSpeaker33')
head=d.getObject('HeadFace33').Shape
shapes={'HeadFront':head,'Microphones':pcb.Shape}
for n in ['EarL','EarR','Camera','IrIlluminator','EyeRingL','EyeRingR','EyeLensL','EyeLensR','ToF','Nose','NeckColumn']:
    s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v32/shape-cache'/(n+'.brep')));shapes[n]=s
rows=[]
for i,p in enumerate([(100.44,-105.295,0),(42.73,-76.375,0)]):
    v=pcb.Placement.multVec(A.Vector(*p));x,y=v.x,v.y
    probes={
      'bottom_driver':Part.makeCylinder(3.25,6,A.Vector(x,y,124)).fuse(Part.makeBox(-120-x,6.5,6.5,A.Vector(x,y-3.25,123.5))),
      'top_wrench':Part.makeBox(-120-x,6,2,A.Vector(x,y-3,141.11)),
    }
    for name,z in [('BoltM2x12',132),('NutM2',141.11)]:
        s=d.getObject(name).Shape.copy();s.Placement=A.Placement(A.Vector(x,y,z),A.Rotation())*s.Placement;probes[name]=s
    for name,s in probes.items():
        hits=[]
        for n,b in shapes.items():
            if not s.BoundBox.intersect(b.BoundBox):continue
            volume=0
            for a in s.Solids:
                for q in b.Solids:
                    if not a.BoundBox.intersect(q.BoundBox):continue
                    c=a.common(q);assert c.isNull() or c.isValid()
                    assert abs(c.Volume)<=min(a.Volume,q.Volume)+.01,(name,n,'Impossible Boolean volume')
                    volume+=abs(c.Volume)
            if volume>.01:hits.append(dict(part=n,volume_mm3=volume))
        row=dict(index=i,probe=name,blockers=hits);rows.append(row);print(row,flush=True)
(OUT/'upwards-screw-study.json').write_text(json.dumps(rows,indent=2),encoding='utf8',newline='\n')
