import FreeCAD as A,Part,json,pathlib,math
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
s=D.getObject('F2_COMMON_PI_BUS_PCA_RECEIVER').Shape;board=D.getObject('N17_PRIMARY_BUS_BOARD_NO_EXTRA_BOM').Shape
# Primary Board is valid. Its real bottom face supplies nominal finite annular contact; source submicron import offset is recorded.
face=max([f for f in board.Faces if abs(f.CenterOfMass.z-107.00000066)<1e-4],key=lambda f:f.Area)
pads=[]
for x in [10.5,47.5]:
 for y in [22.5,50.5]:
  disk=Part.Face(Part.Wire(Part.makeCircle(2,V(x,y,face.CenterOfMass.z),V(0,0,1))))
  pads.append(dict(axis=[x,y],finite_primary_annulus_area=disk.common(face).Area,nominal_post_to_primary_plane_gap=face.CenterOfMass.z-107,primary_pcb_common=s.common(board).Volume))
agg=Part.Shape();agg.read(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/electronics/full-cat/pi-bus-primary-r1/PCB.brep')
near=[]
for i,q0 in enumerate(agg.Solids):
 q=q0.copy();q.translate(V(8,20,108.6));b=q.BoundBox
 if b.ZMin>107.00001 or b.ZMax<100 or b.XMax<8 or b.XMin>51 or b.YMax<19 or b.YMin>54:continue
 if abs(q.Volume-board.Volume)<1e-3 and abs(b.ZLength-1.6)<1e-4:continue
 if not q.isValid():near.append(dict(index=i,status='INVALID_MEMBER_NO_BOP'));continue
 near.append(dict(index=i,gap=s.distToShape(q)[0],common=s.common(q).Volume,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]))
wr('BUS-primary-actual-members-and-contact.json',dict(method='only actual member solids of cached PCB.brep assembly; no full aggregate BOP/healing and no unplaced library shapes',pads=pads,underboard_member_pairs=near,raw126='retained original; lower bridge removed by replacement load rib, full installation capacity common0',physical_PASS=False))
data=D.getObject('F3_DATA500_HORIZONTAL_COMPLETE_UNIT').Shape
checks=[]
names=['PCA9685_Adafruit815_PCB','E1_populated_prototype_board','MAX98357A_amp','BNO085','F0_FHAC0002_30A','ReSpeakerLite_on_REMOVABLE_back','TTP223_touch','F2_COMMON_PI_BUS_PCA_RECEIVER']
for n in names:
 q=D.getObject(n);gap=data.distToShape(q.Shape)[0];checks.append(dict(name=n,DATA_axis_distance=gap,DATA_OD_capacity=6.8,occupied_lower_gap=gap-3.4,named_risk='new horizontal full500/port approaches versus actual common occupied layer',scope='exact analytic DATA axis + conservative circular profile bound; no free cable made into a rigid part'))
wr('DATA500-current-named-hazards.json',checks)
t=json.loads((P/'ToF4-full-connected-family-and-unit-plan.json').read_text())
for q in t['poses']:
 if q['yaw']==0 and q['pitch']==0:
  o=D.addObject('PartDesign::Feature','F3_ToF4_MOVING_U_NEUTRAL_GROUP');o.Shape=Part.makePolygon([V(*p) for p in q['centreline']]);o.ViewObject.LineColor=(.55,.2,.8);o.ViewObject.LineWidth=3
for q in t['fixed_fans']:
 o=D.addObject('PartDesign::Feature','F3_ToF_FIXED_'+q['wire']);o.Shape=Part.makePolygon([V(*p) for p in q['centreline']]);o.ViewObject.LineColor=(.55,.2,.8)
meta=[dict(name=q.Name,label=q.Label) for q in D.Objects if any(k in q.Name.lower() for k in ['c_hy','c_hp','jr_','tail_hollow','hollow_tail','body_m3','hex_m3'])]
wr('current-existing-JR-tail-body-interface-identities.json',meta)
wr('checkpoint-0525-real-functions.json',dict(fact='Common controls real single print plus removable E1cap; sourcePrimaryBUS4 finite contact faces and real cached assembly members now separated from installed field; current DATA named hazard results saved',consequence='Continue same coherent material/closure, do not claim whole-kit from fields or valid1solid',ToF_full_plan='full source-header fan + movingU + true PCAJP3 stationary fanout, one proper bulk ledger per core',physical_PASS=False))
D.recompute();D.save();print('LOCAL_AND_CONNECTED_GROUP_RESULTS_SAVED',checks)
