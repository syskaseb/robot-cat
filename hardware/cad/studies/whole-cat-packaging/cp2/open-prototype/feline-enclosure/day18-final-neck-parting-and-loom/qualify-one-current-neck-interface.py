import FreeCAD as A,Part,json,ast,math,datetime
from pathlib import Path
D=A.ActiveDocument;P=Path(D.FileName).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def bounds(s):
 vs=[v.Point for v in s.Vertexes]
 return [[min(getattr(v,k) for v in vs) for k in ['x','y','z']],[max(getattr(v,k) for v in vs) for k in ['x','y','z']]] if vs else None
# Correct only temporary roof stock outside the actual parts-backed profiles, not a new silhouette family.
S=P.parent/'day18-closed-whole-common-assembly';tree=ast.parse((S/'whole-working-form.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='profile');ns={'Part':Part,'V':V};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<exact retained profile>','exec'),ns)
st=json.loads((S/'whole-working-form-effectivity.json').read_text())['stations'];out=Part.makeLoft([ns['profile'](s) for s in st],True,True)
ho=Part.makeSphere(1);m=A.Matrix();m.A11,m.A22,m.A33=64,77,64;ho=ho.transformGeometry(m);ho.translate(V(-134,0,150))
allowed=out.fuse(ho);roof=box(-140,-100,155.9,115,200,1.6);wing=roof.cut(allowed);partrows=[]
for n in ['F3_BODY_FORE_NEG','F3_BODY_FORE_POS']:
 o=D.getObject(n);before=o.Shape.copy();o.Shape=before.cut(wing).removeSplitter();s=o.Shape
 partrows.append({'name':n,'valid':s.isValid(),'solids':len(s.Solids),'removed_only_unbounded_roof_wing':before.cut(s).Volume,'components':[{'volume':q.Volume,'actual_vertex_bounds':bounds(q)} for q in s.Solids]})
wr('current-fixed-shoulder-material-read.json',partrows);D.recompute();D.save()
rows=[]
for yaw,pitch in [(0,0),(-20,-10),(-20,10),(20,-10),(20,10)]:
 R=A.Rotation(V(0,1,0),pitch);Z=A.Rotation(V(0,0,1),yaw);T=A.Placement(V(-106,0,127)-Z.multVec(V(-106,0,127)),Z).multiply(A.Placement(V(-135,0,121)-R.multVec(V(-135,0,121)),R))
 for n in ['F3_HEAD_FRONT','F3_HEAD_BACK']:
  h=D.getObject(n).Shape.copy();h.transformShape(T.toMatrix())
  for f in ['F3_BODY_FORE_NEG','F3_BODY_FORE_POS','YAW_FIXED_OUTER_RACE_CAP']:
   s=D.getObject(f).Shape;c=h.common(s);row={'yaw':yaw,'pitch':pitch,'moving':n,'fixed':f,'common':c.Volume,'valid':c.isValid()}
   if c.Volume>1e-6:row['actual_common_vertex_bounds']=bounds(c)
   rows.append(row)
  wr('current-head-neck-material-witness-gate.json',{'checks':rows,'cursor':[yaw,pitch,n],'scope':'ONLY this actual changed neck material; five correlated motion witnesses, analytic separation in checkpoint remains separate; no old global replay','accepted':False,'physical_PASS':False})
print('NEW_NECK_MATERIAL_GATE',len(rows),'positive',[r for r in rows if r['common']>1e-5])
