import FreeCAD as A,Part,json
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;rows=[]
for tag,x,names in [('PSYS_P11',111,['PBAY_P_SYS','P11_rear_gate','AUX_FULL9p5_POPULATED_SCOPE','CLOSED_BODY_rear_positive']),('PREAR_P11',136,['PBAY_P_REAR','P11_rear_gate','CLOSED_BODY_rear_positive']),('POWER_BOTH_SIDES',65,['PBAY_F_PI','PBAY_F_HY','P11_rear_gate','P12_common_deck_speaker','P19_shared_lower_carrier','Battery_GEA223S30X6GT','CLOSED_BODY_rear_positive','CLOSED_BODY_rear_negative'])]:
 pts=[A.Vector(x,y,z) for y,z in [(-120,0),(120,0),(120,200),(-120,200),(-120,0)]];plane=Part.Face(Part.makePolygon(pts))
 for n in names:
  o=D.getObject(n)
  if not o:continue
  s=o.Shape.section(plane);lines=[]
  for e in s.Edges:lines.append([[q.y,q.z] for q in e.discretize(Number=18)])
  rows.append(dict(section=tag,planeX=x,name=n,edge_count=len(s.Edges),lines=lines))
(P/'actual-power-layer-sections.json').write_text(json.dumps(rows,indent=2)+'\n');print({'sections':len(rows),'nonempty':sum(bool(q['lines']) for q in rows)})
