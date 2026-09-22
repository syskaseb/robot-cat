"""Read-only servo/yoke interface dimensions to diagnose collision causes."""
from pathlib import Path
import json
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[3]
names=['Part__Feature030','Part__Feature031','Part__Feature032','Part__Feature036','Part__Feature037',
       'Part__Feature048','Part__Feature049','Part__Feature050','Part__Feature054','Part__Feature121']
rows=[]
for n in names:
    s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v26/shape-cache'/(n+'.brep')))
    b=s.BoundBox
    cylinders=[]
    for f in s.Faces:
        if isinstance(f.Surface,Part.Cylinder) and .7<f.Surface.Radius<1.7 and f.ParameterRange[1]-f.ParameterRange[0]>6.28:
            c=f.Surface
            cylinders.append(dict(radius_mm=c.Radius,center_mm=list(c.Center),axis=list(c.Axis)))
    row=dict(name=n,bbox_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],cylinders=cylinders)
    rows.append(row)
    print(n,[round(v,2) for v in row['bbox_mm']])
    print([(round(c['radius_mm'],2),[round(v,2) for v in c['center_mm']],[round(v,2) for v in c['axis']]) for c in cylinders])
(ROOT/'hardware/skorupa/v27/mount-axes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
