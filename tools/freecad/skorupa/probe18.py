from brep_inventory import read_shapes, OUT
import FreeCAD as A
import Part, json
shapes=read_shapes()
flip=A.Placement(A.Vector(42,0,0),A.Rotation(A.Vector(0,0,1),180))
s=shapes['BackCover'][0]
s.Placement=flip.multiply(s.Placement)
rows=[]
for x in (-60,-40,0,30,60,100,120):
    for z in (38,40,42,60,90,96,100,110):
        line=Part.makeLine(A.Vector(x,-100,z),A.Vector(x,100,z))
        cross=s.common(line)
        rows.append([x,z,[[round(e.BoundBox.YMin,2),round(e.BoundBox.YMax,2)] for e in cross.Edges]])
print(json.dumps(rows))
(OUT/'shell-sections.json').write_text(json.dumps(rows,indent=2))
