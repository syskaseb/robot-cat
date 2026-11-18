import FreeCAD as A,Part,json,pathlib,math
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def box(a,b):return Part.makeBox(b[0]-a[0],b[1]-a[1],b[2]-a[2],V(*a))
def obj(n,s,col=(.24,.48,.38)):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;return o
base=D.getObject('P02_front_deck').Shape.copy();members={};roots=[(-80,34,25.5),(-38,-34,-25.5),(-38,34,25.5)]
for sign in [-1,1]:members['Pi_side_'+str(sign)]=box([-110,sign*24.5-5.5,90],[-36,sign*24.5+5.5,95])
for x in [-110,-47]:members['Pi_cross_'+str(x)]=box([x,-30,90],[x+8,30,95])
for i,(x,y,coly) in enumerate(roots):
 members['root_foot_'+str(i)]=box([x-4,y-4,50.52],[x+4,y+4,56.52]).cut(base)
 members['low_dogleg_'+str(i)]=box([x-3,min(y,coly)-3,50.52],[x+3,max(y,coly)+3,56.52]).cut(base)
 members['column_'+str(i)]=box([x-3,coly-3,54.52],[x+3,coly+3,92])
for x in [-104.5,-46.5]:
 for y in [-24.5,24.5]:members['Pi_post_'+str(x)+'_'+str(y)]=box([x-4,y-4,95],[x+4,y+4,98])
s=list(members.values())[0]
for m in list(members.values())[1:]:s=s.fuse(m)
cuts=[]
for x in [-104.5,-46.5]:
 for y in [-24.5,24.5]:
  cuts.append(Part.makeCylinder(1.4,10,V(x,y,89),V(0,0,1)))
  cuts.append(box([x-3.3,21.2 if y>0 else -34,92.1],[x+3.3,34 if y>0 else -21.2,95]))
for x,y,cy in roots:cuts.append(Part.makeCylinder(1.65,25,V(x,y,40),V(0,0,1)))
for c in cuts:s=s.cut(c)
s=s.removeSplitter();receiver=obj('D18C_COMMON_PI_OPEN_CARRIER',s)
floor=base
for x,y,cy in roots:floor=floor.cut(Part.makeCylinder(1.65,30,V(x,y,35),V(0,0,1)))
f=obj('D18C_P02_THREE_ROOT_THROUGH_VERSION',floor,(.35,.35,.39));D.getObject('P02_front_deck').ViewObject.Visibility=False
report=dict(source_floor='P02_front_deck actual BRep; boughtP01 and8H01 unchanged',carrier_valid=s.isValid(),carrier_solids=len(s.Solids),carrier_volume_mm3=s.Volume,carrier_PETG_g=s.Volume*.00127,floor_removed_only_planned_3holes_mm3=base.Volume-floor.Volume,source_floor_missing_unplanned_volume=base.cut(floor).cut(Part.makeCompound([c for c in cuts[-3:]])).Volume,member_coverage={},roots=[],steel_demand='3x M3x16 socket,6x washer7x3.2x0.5,3x fullAF5.5 nut2.4; NEEDED_UNCONFIRMED, NOT purchased inventory',Pi_existing_sets='4 FULL M2.5x8 +2washers+nut each retained by identity; 3mm printed posts, no second spacer',assembly='H01/P02 floor FIRST; 3 full M3 throughsets from below before Pi/banks; 4 Pi nut+washer sidefeeds before board; existing4 M2.5 from above; open power/data/FFC handlay then covers',physical_PASS=False)
for n,m in members.items():
 t=m
 for c in cuts:t=t.cut(c)
 report['member_coverage'][n]=dict(planned_volume=t.Volume,missing_volume=t.cut(s).Volume)
def washer(z,x,y):return Part.makeCylinder(3.5,.5,V(x,y,z)).cut(Part.makeCylinder(1.6,.5,V(x,y,z)))
for i,(x,y,cy) in enumerate(roots):
 # Root floor bottom45.52, top50.52 (+local retained key fits matching underside). Full16 includes tip beyond nut.
 screw=Part.makeCylinder(2.75,3,V(x,y,42.02)).fuse(Part.makeCylinder(1.5,16,V(x,y,45.02)))
 obj('D18C_ROOT_'+str(i)+'_M3x16_FULL',screw,(.65,.66,.7));obj('D18C_ROOT_'+str(i)+'_BOTTOM_WASHER',washer(45.02,x,y),(.65,.66,.7));obj('D18C_ROOT_'+str(i)+'_TOP_WASHER',washer(56.52,x,y),(.65,.66,.7))
 r=5.5/math.sqrt(3);pp=[V(x+r*math.cos(k*math.pi/3),y+r*math.sin(k*math.pi/3),57.02) for k in range(6)];pp.append(pp[0]);nut=Part.Face(Part.makePolygon(pp)).extrude(V(0,0,2.4)).cut(Part.makeCylinder(1.25,2.4,V(x,y,57.02)));obj('D18C_ROOT_'+str(i)+'_FULL_NUT',nut,(.65,.66,.7))
 contact=s.common(base).Volume
 # Nominal matched surfaces can touch with zero common material; a thin receiving slice gives finite bearing footprint.
 sl=box([x-4,y-4,50.519],[x+4,y+4,50.521]);face_area=base.common(sl).Volume/.002
 report['roots'].append(dict(x=x,y=y,bearing_slice_equivalent_area_mm2=face_area,screw_underhead=45.02,tip=61.02,nut_top=59.42,full_tip_beyond_nut=1.60))
report['separate_carrier_floor_common_mm3']=s.common(floor).Volume
report['intended_extent']=[-110,-38,50.52,-34,38,98]
(P/'common-Pi-floor-interface.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
s.exportBrep(str(P/'common-Pi-carrier.brep'));floor.exportBrep(str(P/'P02-three-root-version.brep'))
print('COMMON_PI',report['carrier_valid'],report['carrier_solids'],report['carrier_volume_mm3'],'floor_common',report['separate_carrier_floor_common_mm3'],'missing',max(x['missing_volume'] for x in report['member_coverage'].values()))
