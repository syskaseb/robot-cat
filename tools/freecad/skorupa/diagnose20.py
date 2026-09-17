from pathlib import Path
import FreeCAD as A
import Part,json
root=Path(__file__).resolve().parents[3]
out=root/'hardware/skorupa/v20'
d=A.openDocument(str(root/'hardware/skorupa/v19/Kot_v19_SKORUPA_PETG_256.FCStd'))
def shape(n):
    p=out/(n+'.brep')
    if p.exists():
        s=Part.Shape(); s.read(str(p)); return s
    o=d.getObject(n); s=o.Shape.copy(); s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement); return s
for a,b,v in json.loads((out/'validation.json').read_text())['collisions']:
    if a.endswith('R'): continue
    s=shape(a).common(shape(b)); bb=s.BoundBox
    print(a,b,'volume',s.Volume,'bounds',[bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax],flush=True)
