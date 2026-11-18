import FreeCAD as A,Part,json,pathlib
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
data=json.loads((P/'occupied-DATA500-separated-static-bay.json').read_text());pts=data['centreline'];wire=Part.makePolygon([V(*x) for x in pts]);r=[]
for n in ['PCA9685_Adafruit815_PCB','E1_populated_prototype_board','ReSpeakerLite_on_REMOVABLE_back','TTP223_touch']:
 s=D.getObject(n).Shape;dd=wire.distToShape(s)[0];r.append(dict(name=n,centreline_to_actual_rigid=dd,capacity_radius=3.4,arc_sag_bound=.006,occupied_gap_lower=dd-3.4-.006,scope='CURRENT connected full500 static DATA bay; named PCB/E1 clearance, wire is not a rigid bought part'))
wr('DATA500-named-actual-neighbors.json',r)
o=D.addObject('PartDesign::Feature','D18C_DATA500_CONNECTED_STATIC_BAY');o.Shape=wire;o.ViewObject.LineColor=(.8,.32,.12);o.ViewObject.LineWidth=3
rs=[];families=json.loads((P/'occupied-FFC200-family.json').read_text())
for row in families:
 yaw,pitch=row['yaw'],row['pitch'];ry=A.Rotation(V(0,1,0),pitch);rz=A.Rotation(V(0,0,1),yaw)
 tp=A.Placement(V(-135,0,121)-ry.multVec(V(-135,0,121)),ry);ty=A.Placement(V(-106,0,127)-rz.multVec(V(-106,0,127)),rz);T=ty.multiply(tp)
 corners=row['corners'];count=6 if abs(pitch)>0 else 2
 ws=[Part.Wire(Part.makePolygon([V(*p) for p in q+[q[0]]]).Edges) for q in corners[:count]]
 field=Part.makeLoft(ws,True,True)
 for n,pose in [('D18C_TRUE_PITCH_OPTICAL_RECEIVER',T),('Pitch688',ty),('MG92B_Head_pitch',ty)]:
  s=D.getObject(n).Shape.copy();s.transformShape(pose.toMatrix());gap=field.distToShape(s)[0];rs.append(dict(yaw=yaw,pitch=pitch,rigid=n,valid=field.isValid(),gap=gap,common=field.common(s).Volume,scope='named full16.8x1.8 connector approach/688/true pitch receiving notch, NOT all free-span manufacturing proof'))
 if yaw==0 and pitch==0:
  for suffix,idx in [('LOWER',0),('UPPER',2)]:
   o=D.addObject('PartDesign::Feature','D18C_FFC200_OCCUPIED_EDGE_'+suffix);o.Shape=Part.makePolygon([V(*c[idx]) for c in row['corners']]);o.ViewObject.LineColor=(.1,.75,.85);o.ViewObject.LineWidth=3
wr('FFC200-named-moving-entry-check.json',rs)
print('DATA',json.dumps(r));print('FFC minimum',min(x['gap'] for x in rs),'positive commons',[x for x in rs if x['common']>1e-7])
