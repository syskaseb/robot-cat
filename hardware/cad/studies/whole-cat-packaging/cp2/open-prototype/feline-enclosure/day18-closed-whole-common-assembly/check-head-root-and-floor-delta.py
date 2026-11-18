import FreeCAD as A,Part,json,math
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def bg(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
source=P.parent/'day18-connected-storage-pitch-frame'
family=json.loads((source/'occupied-FFC200-family.json').read_text());head=[]
for row in family:
 yaw,pitch=row['yaw'],row['pitch'];ry=A.Rotation(V(0,1,0),pitch);rz=A.Rotation(V(0,0,1),yaw)
 T=A.Placement(V(-106,0,127)-rz.multVec(V(-106,0,127)),rz).multiply(A.Placement(V(-135,0,121)-ry.multVec(V(-135,0,121)),ry));inv=T.inverse()
 # Local connector/root segment only; upstream free span has its own variable family.
 corners=[[inv.multVec(V(*p)) for p in c] for c in row['corners'][:8]]
 ws=[Part.Wire(Part.makePolygon(c+[c[0]]).Edges) for c in corners];field=Part.makeLoft(ws,True,True)
 for n in ['D18C_TRUE_PITCH_OPTICAL_RECEIVER']+[o.Name for o in D.Objects if o.Name.startswith('F3_HEAD_ROOT_')]:
  s=D.getObject(n).Shape
  if bg(field.BoundBox,s.BoundBox)>1.25:continue
  common=field.common(s);head.append({'yaw':yaw,'pitch':pitch,'object':n,'gap':field.distToShape(s)[0],'common':common.Volume,'valid':common.isValid(),'scope':'named new outer root full fasteners and camera-entry edge; eight local station sections only'})
wr('head-root-local-FFC-delta.json',head)
members=[]
for x in [-70,70,145]:
 for side in [-1,1]:
  members.append((str((x,side))+'column',box(x-6,84.5 if side>0 else -88.5,43.62,12,4,14.38)))
  if x==70 and side<0:add=[box(64,-88.5,55,34,4,3),box(89,-88.5,55,6,47.5,3)]
  elif x==145:add=[box(139,84.5 if side>0 else -88.5,55,15,4,3),box(148,84.5 if side>0 else -88.5,55,6,4,17),box(148,38 if side>0 else -88.5,68,6,50.5,4)]
  else:add=[box(x-5,43 if side>0 else -88.5,55,10,45.5,3)]
  members.extend((str((x,side))+'arm'+str(i),s) for i,s in enumerate(add))
targets=[o for o in D.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and o.ViewObject.Visibility and (o.Name.startswith(('P01','P05','H03','Motor_ATO','PBAY_','WAGO615','NIGHT_INLINE_')) or o.Name in ['Battery','S0_body','F0_FHAC0002_30A','MAIN_Pololu4853','AUX_FULL9p5_POPULATED_SCOPE'])]
rows=[]
for n,s in members:
 for o in targets:
  if bg(s.BoundBox,o.Shape.BoundBox)>1.25:continue
  c=s.common(o.Shape);rows.append({'member':n,'other':o.Name,'gap':s.distToShape(o.Shape)[0],'common':c.Volume,'valid':c.isValid()})
wr('cowl-new-arm-local-neighbors.json',{'scope':'ONLY current new columns/upper arms vs numerically culled retained foundation and visible bought modules, source lower receiver contacts reused by identity','checks':rows,'wholekit':False})
print('LOCAL_HEAD_AND_FLOOR_DELTA_SAVED',len(head),len(rows))
