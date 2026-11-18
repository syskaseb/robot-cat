import FreeCAD as A,Part,json,pathlib
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,x,y,z):return Part.makeCylinder(r,h,V(x,y,z),V(0,1,0))
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
o=D.getObject('F2_COMMON_PI_BUS_PCA_RECEIVER');before=o.Shape.copy()
# Replace the obsolete central AMP support by a short positive-side audio mount, preserving the BUS bearing plate and old Pi source material.
retired=box(12,-18,106.25,19,3,5.55).fuse(box(28,-18,100.5,6,40,3)).fuse(box(28,-18,100.5,6,3,9))
for x in [15.15,27.85]:retired=retired.fuse(cy(3,3,x,-15,109.015))
protected=D.getObject('D18C_COMMON_PI_OPEN_CARRIER').Shape.fuse(box(8,19,101,43,35,3))
cut=retired.cut(protected);s=before.cut(cut)
delta=V(-57,38.4,25.5);moves=[]
for q in D.Objects:
 if q.Name=='MAX98357A_amp' or q.Name.startswith('CB_AMP_') and q.ViewObject.Visibility:
  v=q.Shape.Volume;q.Placement=A.Placement(delta,A.Rotation()).multiply(q.Placement);moves.append(dict(name=q.Name,volume_before=v,volume_after=q.Shape.Volume,delta=list(delta)))
members=[box(-45,20.4,131.5,19,3,6),box(-37,20.4,124,6,12.1,4),box(-37,20.4,124,6,3,13.5)]
for x in [-41.85,-29.15]:members.append(cy(3,3,x,23.4,134.515))
s=s.multiFuse(members)
for x in [-41.85,-29.15]:s=s.cut(cy(1.1,7,x,19.9,134.515))
s=s.removeSplitter();o.Shape=s
cap=D.getObject('F3_E1_REMOVABLE_EDGE_KEEPER');cap.Shape=cap.Shape.fuse(box(52,20.45,158,53,5.1,1)).removeSplitter()
terminal_moves=[]
for q in D.Objects:
 if not q.Name.startswith('WAGO415_data') or not q.ViewObject.Visibility:continue
 b=q.Shape.BoundBox
 if b.XMin>60 and b.YMin>20:
  q.Placement=A.Placement(V(0,10,-6),A.Rotation()).multiply(q.Placement);terminal_moves.append(dict(name=q.Name,delta=[0,10,-6],reason='E1 cap/tool plane left clear; tilted full MTA below and actual rump ceiling bound common vertical terminal layer144..163'))
wr('whole-common-plane-completed-delta.json',dict(AMP_moves=moves,AMP_function='whole PCB+fulltwoM2 sets next to basket/BNO; MAIN5V1/I2S/speaker BTL affected, no end cut',planned_retired_support=cut.Volume,source_Pi_missing=D.getObject('D18C_COMMON_PI_OPEN_CARRIER').Shape.cut(s).Volume,receiver_valid=s.isValid(),receiver_solids=len(s.Solids),E1_cap_valid=cap.Shape.isValid(),E1_cap_solids=len(cap.Shape.Solids),E1_fixed_cap_common=cap.Shape.common(s).Volume,terminal_moves=terminal_moves,physical_PASS=False))
D.recompute();D.save();print('COMPLETED_COMMON_PLANE',s.isValid(),len(s.Solids),'cap',len(cap.Shape.Solids))
