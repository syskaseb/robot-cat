import FreeCAD as A,FreeCADGui as G,Part,json
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
rows=[]
for tag,x,prefix in [('BANK_LEFT_X',-81.8819,('BANK_PANEL_','Motor_ATO4A__1_0','Motor_ATO4A_1_0')),('REAR_FHAC_X',105,('P11_rear_gate','P19_','P12_common_deck_speaker','FHAC0001_Yaw'))]:
 # Explicit worldYZ rectangle; prior makePlane had its intrinsic U/V axes
 # outside the assembly. This is view-data repair, no shape change.
 face=Part.Face(Part.makePolygon([V(x,-120,0),V(x,120,0),V(x,120,180),V(x,-120,180),V(x,-120,0)]))
 for o in D.Objects:
  if not o.Name.startswith(prefix) or not hasattr(o,'Shape'):continue
  s=o.Shape.section(face);lines=[]
  for e in s.Edges:lines.append([[p.y,p.z] for p in e.discretize(Number=20)])
  if lines:rows.append(dict(section=tag,x=x,name=o.Name,lines=lines))
(P/'actual-interface-sections.json').write_text(json.dumps(rows,indent=2)+'\n')
D.Label='DAY16 COMMON PROTECTION / NOMINAL CONNECTED PRINTS / OPEN FIT3+INLINE'
D.recompute();D.save();G.getDocument(D.Name).Modified=False
print(json.dumps(dict(section_counts=[(q['section'],q['name'],len(q['lines'])) for q in rows],objects=len(D.Objects),saved_path=D.FileName)))
