import FreeCAD as A,FreeCADGui as G,Part,json,pathlib,math,datetime
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
D.saveAs(str(P/'whole-module-loom-and-feline-closure.FCStd'))
spec=json.loads((P/'selected-whole-layer-spec.json').read_text());delta=[]
for s in spec:
 if 'S0' in s['role']:s['new'][2]=92
 if 'POST412' in s['role']:s['names']=['PBAY_POST_F0']
 if 'P_SYS_F_PI' in s['role']:s['new'][2]=-4
 if 'P_REAR_F_AUX' in s['role']:s['new']=[2,10,0]
 names=s.get('names',[])+[o.Name for o in D.Objects if any(o.Name.startswith(p) for p in s.get('prefixes',[])) and (o.ViewObject.Visibility or o.Name.startswith(('S0_','OP_S1_')))]
 R=A.Rotation(V(*s['axis']),s['angle']);T=A.Placement(V(*s['new'])-R.multVec(V(*s['old'])),R)
 for n in sorted(set(names)):
  o=D.getObject(n)
  if o is None:raise ValueError(n)
  vol=o.Shape.Volume;o.Placement=T.multiply(o.Placement);b=o.Shape.BoundBox;delta.append(dict(name=n,role=s['role'],volume_before=vol,volume_after=o.Shape.Volume,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],T=T.toMatrix().A))
# Two lower power415/615 roles remain distinct physical cases: use full narrow vertical cross-section below MTA.
for i in [0,1]:
 o=D.getObject('WAGO615_power_0_'+str(i));b=o.Shape.BoundBox;old=V((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2);new=V(old.x,-55.5,65);R=A.Rotation(V(1,0,0),-90);T=A.Placement(new-R.multVec(old),R);vol=o.Shape.Volume;o.Placement=T.multiply(o.Placement);b=o.Shape.BoundBox;delta.append(dict(name=o.Name,role='full615 vertical outer side levers, upward entry/openassembly',volume_before=vol,volume_after=o.Shape.Volume,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],T=T.toMatrix().A))
targets={'FL':(-104,-54,81),'FR':(-104,43,64),'RL':(58,-66,68),'RR':(58,60,64)}
for leg,(xx,yy,zz) in targets.items():
 objs=sorted([o for o in D.Objects if o.Name.startswith('NIGHT_INLINE_'+leg+'_')],key=lambda o:o.Shape.BoundBox.YMin)
 for i,o in enumerate(objs):
  b=o.Shape.BoundBox;T=A.Placement(V(xx-b.XMin,yy+10.1*i-b.YMin,zz-b.ZMin),A.Rotation());vol=o.Shape.Volume;o.Placement=T.multiply(o.Placement);b=o.Shape.BoundBox;delta.append(dict(name=o.Name,role='2 canonical inline couplers per real leg; same opposite-end source bodies, common trough after Pi-root tools',volume_before=vol,volume_after=o.Shape.Volume,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],T=T.toMatrix().A))
wr('selected-whole-layer-spec.json',spec);wr('actual-whole-rigid-delta.json',delta)
# Whole bought tail hardware gate, not a BBox declaration or a source-global scan.
r=[]
tailnames=['MG92B_Tail','Tail608','TAIL_HORN_ROOF_JOURNAL','TAIL_FIXED_BEARING_CARTRIDGE','TAIL_FIXED_OUTER_RACE_CAP','TAIL_REAL_REMOVABLE_SERVO_SADDLE']
for o in D.Objects:
 if not o.Name.startswith('S0_'):continue
 for n in tailnames:
  t=D.getObject(n).Shape;b=o.Shape.BoundBox;c=t.BoundBox;g=math.sqrt(sum(max(0,getattr(b,k+'Min')-getattr(c,k+'Max'),getattr(c,k+'Min')-getattr(b,k+'Max'))**2 for k in ['X','Y','Z']))
  if g<2:r.append(dict(a=o.Name,b=n,valid=t.isValid(),gap=o.Shape.distToShape(t)[0],common=o.Shape.common(t).Volume))
wr('S0-whole-tail-actual-gate.json',r)
# Current finite changed full-module screen before dependent supports or skins.
source=P.parent/'day18-connected-storage-pitch-frame/CURRENT-major-bounds.json';major=list(json.loads(source.read_text()));extra=['PBAY_POST_F0','Monitor_MOD05015','MG92B_Tail','Tail608','TAIL_FIXED_BEARING_CARTRIDGE','TAIL_FIXED_OUTER_RACE_CAP'];major=list(dict.fromkeys(major+extra));C={};changed={d['name'] for d in delta}
for n in major:
 o=D.getObject(n)
 if o:
  b=o.Shape.BoundBox;C[n]=dict(bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
candidates=[]
for i,n in enumerate(C):
 for m in list(C)[i+1:]:
  if n not in changed and m not in changed:continue
  if n.startswith('S0_') and m.startswith('S0_'):continue
  b=C[n]['bounds'];c=C[m]['bounds'];g=math.sqrt(sum(max(0,b[k]-c[k+3],c[k]-b[k+3])**2 for k in range(3)))
  if g<1.25-1e-6:candidates.append(dict(a=n,b=m,bbox_gap=g,status='CANDIDATE_ONLY, classify actual material/reserve before exact'))
wr('whole-current-major-bounds.json',C);wr('whole-before-material-cull.json',candidates)
D.Label='DAY18_WHOLE_MODULE_LAYER_WORKING';D.recompute();D.save();print('WHOLE_SAVED',len(delta),'tail',r,'finite candidates',candidates)
