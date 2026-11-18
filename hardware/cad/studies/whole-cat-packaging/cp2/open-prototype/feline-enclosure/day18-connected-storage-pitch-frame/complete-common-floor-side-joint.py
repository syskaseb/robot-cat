import FreeCAD as A,Part,json,pathlib,math
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def box(a,b):return Part.makeBox(b[0]-a[0],b[1]-a[1],b[2]-a[2],V(*a))
base=D.getObject('P02_front_deck').Shape.copy();floor=base;members={};roots=[-80,-38]
members['positive_side']=box([-110,19,90],[-36,30,95]);members['negative_side']=box([-110,-30,90],[-42.5,-19,95])
members['front_cross']=box([-110,-30,90],[-102,30,95]);members['rear_cross']=box([-50,-30,90],[-42.5,30,95])
for x in roots:
 lug=box([x-5,34,49.52],[x+5,38,70.52]);floor=floor.fuse(lug)
 members['foot_'+str(x)]=box([x-4,30,50.52],[x+4,34,56.52]).cut(base)
 members['flange_'+str(x)]=box([x-5,30,50.52],[x+5,34,70.52]).cut(base)
 members['dogleg_'+str(x)]=box([x-3,22,54.52],[x+3,34,70.52]).cut(base)
 members['column_'+str(x)]=box([x-3,22,54.52],[x+3,28,92])
for x in [-104.5,-46.5]:
 for y in [-24.5,24.5]:members['Pi3mm_post_'+str(x)+'_'+str(y)]=Part.makeCylinder(3,3,V(x,y,95))
s=list(members.values())[0]
for m in list(members.values())[1:]:s=s.fuse(m)
cuts=[box([-128.25,-7.25,49],[-93.75,7.25,90.25])]
for x in [-104.5,-46.5]:
 for y in [-24.5,24.5]:
  cuts.append(Part.makeCylinder(1.4,10,V(x,y,89)))
  cuts.append(box([x-2.8,21.2 if y>0 else -34,92.1],[x+2.8,34 if y>0 else -21.2,94.5]))
  cuts.append(box([x-3.1,21.2 if y>0 else -34,94.5],[x+3.1,34 if y>0 else -21.2,95]))
for x in roots:
 c=Part.makeCylinder(1.65,20,V(x,42,64.52),V(0,-1,0));floor=floor.cut(c);cuts.append(c)
 cuts.append(box([x-5,26.5,59.77],[x+9,30.01,69.27]))
for c in cuts:s=s.cut(c)
s=s.removeSplitter();floor=floor.removeSplitter();D.getObject('D18C_COMMON_PI_OPEN_CARRIER').Shape=s;D.getObject('D18C_P02_THREE_ROOT_THROUGH_VERSION').Shape=floor
D.getObject('D18C_P02_THREE_ROOT_THROUGH_VERSION').Label='P02_SOURCE_FLOOR_PLUS_TWO_SIDE_RECEIVING_LUGS / previous through-floor3root role withdrawn'
for o in list(D.Objects):
 if o.Name.startswith('D18C_ROOT_'):D.removeObject(o.Name)
def ob(n,shape):
 o=D.addObject('PartDesign::Feature',n);o.Shape=shape;o.ViewObject.ShapeColor=(.66,.67,.7)
def washer(x,y):return Part.makeCylinder(3.5,.5,V(x,y,64.52),V(0,-1,0)).cut(Part.makeCylinder(1.6,.5,V(x,y,64.52),V(0,-1,0)))
for i,x in enumerate(roots):
 ob('D18C_SIDE_ROOT_'+str(i)+'_M3x12_FULL',Part.makeCylinder(2.75,3,V(x,38.5,64.52),V(0,1,0)).fuse(Part.makeCylinder(1.5,12,V(x,38.5,64.52),V(0,-1,0))))
 ob('D18C_SIDE_ROOT_'+str(i)+'_HEAD_WASHER',washer(x,38.5));ob('D18C_SIDE_ROOT_'+str(i)+'_NUT_WASHER',washer(x,30))
 r=5.5/math.sqrt(3);p=[V(x+r*math.cos(k*math.pi/3),29.5,64.52+r*math.sin(k*math.pi/3)) for k in range(6)];p.append(p[0]);nut=Part.Face(Part.makePolygon(p)).extrude(V(0,-2.4,0)).cut(Part.makeCylinder(1.5,2.4,V(x,29.5,64.52),V(0,-1,0)));ob('D18C_SIDE_ROOT_'+str(i)+'_FULL_NUT',nut)
report=dict(cause='Underfloor full-bolt/tool operations meet retained source base; use actual own floor SIDE receiving faces above the bought base. Negative column omitted because S1 occupies it; whole Pi frame is supported by two positive-side finite orthogonal bearing faces and complete horizontal joints, not free gravity/friction.',source_floor_missing_mm3=base.cut(floor).Volume,carrier_floor_common_mm3=s.common(floor).Volume,carrier_valid=s.isValid(),carrier_solids=len(s.Solids),carrier_volume_mm3=s.Volume,carrier_PETG_g=s.Volume*.00127,new_floor_delta_mm3=floor.Volume-base.Volume,planned_member_missing={},full_root_joints='2 M3x12,4 washers7x3.2x0.5,2 fullAF5.5 nuts2.4; NEEDED_UNCONFIRMED. Underhead38.5 to26.5Y, nut27.1..29.5, full0.6 tip beyondnut. No bought drilling/cutting.',retired_UNBUILT_only=['3 downward M3x16 and three own floor holes','negative rear support column','square8 Pi posts replaced with standard Ø6 annular3mm bearing supports preserving all4 full M2.5 sets'],assembly='H01 source floor first; side-root screws/nuts before Pi/banks; full nut/spanner feed from side, source4 Pi nuts+washers preload then Pi4 source screws; two-person openhandlay; covers late',physical_strength='UNQUALIFIED benchload, no FEA/strength PASS',physical_PASS=False)
for n,m in members.items():
 t=m
 for c in cuts:t=t.cut(c)
 report['planned_member_missing'][n]=t.cut(s).Volume
(P/'completed-common-Pi-side-root.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());s.exportBrep(str(P/'common-Pi-carrier.brep'));floor.exportBrep(str(P/'P02-three-root-version.brep'))
# Complete the one common positive terminal rail using the actual source columns, not presumed identical old stations.
for o in D.Objects:
 if o.Name.startswith('WAGO415_data') and o.ViewObject.Visibility:
  b=o.Shape.BoundBox
  if b.XMin>80 and b.YMin>0:o.Placement.Base+=V(0,(25 if b.YMin<40 else 47)-b.YMin,0)
print('COMPLETED_SAME_SIDE_FLOOR_INTERFACE',s.isValid(),len(s.Solids),s.Volume,'sourcefloor missing',report['source_floor_missing_mm3'],'floor common',report['carrier_floor_common_mm3'])
