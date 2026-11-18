import FreeCAD as A,Part,json,pathlib,math
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cy(r,h,x,y,z,axis=V(0,1,0)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def ob(n,s,c=(.18,.24,.28)):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=c;return o
def nut(x,y,z):
 ps=[V(x+4/math.sqrt(3)*math.cos(math.pi*i/3),y,z+4/math.sqrt(3)*math.sin(math.pi*i/3)) for i in range(6)];return Part.Face(Part.Wire(Part.makePolygon(ps+[ps[0]]).Edges)).extrude(V(0,1.6,0)).cut(cy(1,1.6,x,y,z))
def bolt(n,x,y,z,L):return ob(n,cy(1,L,x,y,z).fuse(cy(1.9,2,x,y-2,z)),(.67,.68,.7))
def washer(n,x,y,z):return ob(n,cy(2.5,.5,x,y,z).cut(cy(1.1,.5,x,y,z)),(.67,.68,.7))
changes=[]
def shift(names,v,reason):
 for n in names:
  o=D.getObject(n)
  if o is None:continue
  vol=o.Shape.Volume;o.Placement=A.Placement(v,A.Rotation()).multiply(o.Placement);changes.append(dict(name=n,reason=reason,delta=list(v),volume_before=vol,volume_after=o.Shape.Volume))
shift(['MAIN_Pololu4853']+[q.Name for q in D.Objects if q.Name.startswith('CB_MAIN_') and q.ViewObject.Visibility],V(0,4,16),'one common negative control plane above complete615 cases, full16mm stock and ports inward; W078/79/80 affected')
shift(['AUX_Pololu4092','AUX_FULL9p5_POPULATED_SCOPE']+[q.Name for q in D.Objects if q.Name.startswith('CB_AUX_') and q.ViewObject.Visibility],V(0,0,16),'same useful negative common control plane and full16mm stock; XA02/03 affected')
shift(['PBAY_P_SYS','PBAY_F_PI'],V(-8,0,2),'whole short factory pair on continuous floor; same relative port/R16 unit, avoiding S0 and leaving real base pads')
shift([q.Name for q in D.Objects if q.Name.startswith('NIGHT_INLINE_RL_') and q.ViewObject.Visibility],V(0,0,-34.5),'two full RL inline units below reoriented rear terminal row; actual MTA0100335 lead reach still UNBOUND')
base=D.getObject('F2_COMMON_PI_BUS_PCA_RECEIVER');old=base.Shape.copy();s=old.copy();planned=[]
# Actual source M2 post diameter4, not arbitrary8: primary pads and source underside pins are co-allocated.
for x in [10.5,47.5]:
 for y in [22.5,50.5]:
  cut=Part.makeCylinder(4,3.01,V(x,y,104)).cut(Part.makeCylinder(2,3.01,V(x,y,104)));s=s.cut(cut);planned.append(cut)
cut=box(13,19,103.5,31,35,.501);s=s.cut(cut);planned.append(cut)
members=[box(-49,-54.5,84,6,87,6),box(-49,26,84,18,6.5,6),box(-49,-54.5,88,55,3,10),box(6,-54.5,88,6,8,10),box(6,-49.5,88,77,3,10),box(42,-49.5,88,6,3,40),box(71,-49.5,88,6,3,40),box(42,-49.5,125,38,3,3),box(45,-49.5,100,32,3,5)]
for kind,indices in [('MAIN',[0,1]),('AUX',[0,1,2])]:
 for i in indices:
  w=D.getObject('CB_'+kind+'_'+str(i)+'_PCBwasher');b=w.Shape.BoundBox;x=(b.XMin+b.XMax)/2;z=(b.ZMin+b.ZMax)/2;pcbfront=b.YMin;pcbback=pcbfront-(1.5748 if kind=='MAIN' else 1.57)
  members.append(cy(3,pcbback+46.5,x,-46.5,z))
  bw=D.getObject('CB_'+kind+'_'+str(i)+'_basewasher');bb=bw.Shape.BoundBox;bw.Placement.Base+=V(0,-50-bb.YMin,0)
  oldbolt=[q for q in D.Objects if q.Name.startswith('CB_'+kind+'_'+str(i)+'_M2x') and q.ViewObject.Visibility]
  for q in oldbolt:q.Label='RETIRED_UNBUILT_DEMAND_'+q.Name;q.ViewObject.Visibility=False
  bolt('F3_'+kind+'_'+str(i)+'_FULL_M2x16',x,-50,z,16)
  members.append(cy(3,3,x,-49.5,z))
# Two opposed BNO holes, full source bolts/washers/nuts unchanged. Nominal post annulus is the only contact.
members += [box(-23,34,122.5,30,3,6),box(-28,25.55,127,6,11.45,7)]
for x in [-17.36,2.96]:members.append(cy(2.75,3,x,31,125.24))
# AMP uses its two manufacturer holes on one open arm, not the installation-box edge.
members += [box(12,-18,106.25,19,3,5.55),box(28,-18,100.5,6,40,3),box(28,-18,100.5,6,3,9)]
for x in [15.15,27.85]:members.append(cy(3,3,x,-15,109.015))
# E1 lower edge shelf and removable top edge cap. Backside PCB plane and safe edge remain one actual sample condition.
members += [box(51,20.95,126.4,58,7.6,1.6),box(51,25.55,126.4,6,3,6.6),box(103,25.55,126.4,6,3,6.6)]
for x in [56,101]:members.append(cy(3,3,x,25.55,162))
s=s.multiFuse(members).removeSplitter()
holes=[]
for kind,indices in [('MAIN',[0,1]),('AUX',[0,1,2])]:
 for i in indices:
  b=D.getObject('CB_'+kind+'_'+str(i)+'_PCBwasher').Shape.BoundBox;holes.append(cy(1.1,18,(b.XMin+b.XMax)/2,-50,(b.ZMin+b.ZMax)/2))
for x in [-17.36,2.96]:holes.append(cy(1.1,7,x,30.5,125.24))
for x in [15.15,27.85]:holes.append(cy(1.1,7,x,-18.5,109.015))
for x in [56,101]:holes.append(cy(1.1,4,x,25.05,162))
for q in holes:s=s.cut(q)
s=s.removeSplitter();base.Shape=s
cap=box(52,22.55,158,53,3,3).fuse(box(52,20.45,157.5,53,.5,1))
for x in [56,101]:
 cap=cap.fuse(cy(3,3,x,22.55,162));cap=cap.cut(cy(1.1,3,x,22.55,162));bolt('F3_E1_CAP_'+str(x)+'_FULL_M2x10',x,22.05,162,10);washer('F3_E1_CAP_'+str(x)+'_HEAD_WASHER',x,22.05,162);washer('F3_E1_CAP_'+str(x)+'_NUT_WASHER',x,28.55,162);ob('F3_E1_CAP_'+str(x)+'_FULL_NUT',nut(x,29.05,162),(.67,.68,.7))
cap=cap.removeSplitter();ob('F3_E1_REMOVABLE_EDGE_KEEPER',cap)
wr('common-controls-material-and-effectivity.json',dict(valid=s.isValid(),solids=len(s.Solids),new_receiver_volume=s.Volume,PETG_g=s.Volume*.00127,members=len(members),source_Pi_carrier_missing_mm3=D.getObject('D18C_COMMON_PI_OPEN_CARRIER').Shape.cut(s).Volume,declared_replacements=['BUS fourpost OD8 replaced by source-hole-bound OD4 and actual under-component relief; full chosen metal unchanged','PCA lower bridge replaced by upper rib','MAIN2xM2x10/AUX3xM2x12 UNBUILT screw demand replaced by5fullM2x16; no bought cut'],changes=changes,keeper=dict(valid=cap.isValid(),solids=len(cap.Solids),volume=cap.Volume,parting_common=cap.common(s).Volume,safe_contact='nominal E1 barePCB top/lower edge only; one actual populated-board sample must provide these safe lands, not pressure on unseen IC'),needed_standard_demand={'M2x16_socket_full':5,'M2x10_socket_full_new_E1':2,'M2_washer_new_E1':4,'M2_nut_new_E1':2,'inventory':'NEEDED_UNCONFIRMED'},assembly='Two floor-side sourceM3 joints first; BUS four fullCSK before PCA/E1 whole solderedkit, BNO/AMP, MAIN/AUX; E1 cap late, no virtual solder disconnect',unreceived=['named new material/fullmetal neighbors and toolfeed','ToF/JR/POWER complete connected groups','other body/skin roots'],physical_PASS=False))
D.recompute();D.save();print('COMMON_CONTROLS_REALIZED',s.isValid(),len(s.Solids),s.Volume,'cap common',cap.common(s).Volume)
