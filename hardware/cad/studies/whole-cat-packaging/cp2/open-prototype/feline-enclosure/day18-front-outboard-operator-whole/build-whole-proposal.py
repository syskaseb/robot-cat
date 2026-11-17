import FreeCAD as A,FreeCADGui as G,Part,json,pathlib,math
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
spec=json.loads((P/'whole-transform-spec.json').read_text());base={o['name']:o for o in json.loads((P/'source-current-metadata.json').read_text())};delta=[]
for s in spec:
 R=A.Rotation(V(1,0,0) if s['axis']=='X' else V(0,1,0) if s['axis']=='Y' else V(0,0,1),s['angle'])
 if s['pre']:
  ax,ang=s['pre'];rp=A.Rotation(V(1,0,0) if ax=='X' else V(0,0,1),ang);R=R.multiply(rp)
 T=A.Placement(V(*s['new'])-R.multVec(V(*s['old'])),R)
 for n in s['names']:
  o=D.getObject(n)
  if not o or not hasattr(o,'Shape'):continue
  o.Placement=T.multiply(o.Placement);b=o.Shape.BoundBox
  delta.append(dict(name=n,role=s['role'],bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],volume_before=base[n]['volume'],volume_after=o.Shape.Volume,world_rigid_transform=T.toMatrix().A))
# Withdraw obsolete OWN print concepts/analytical routes, not bought units.
withdraw=[]
for o in D.Objects:
 if o.Name.startswith(('D18_','TOUCH_M2x8_')):
  if hasattr(o,'ViewObject'):o.ViewObject.Visibility=False
  withdraw.append(o.Name)
GG=D.addObject('App::DocumentObjectGroup','D18B_FORM_NOT_PRINT_NOT_MASS')
def ob(n,s,c,alpha=0):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=n+' / PROPOSAL_NOT_PRINT_NOT_MASS';o.ViewObject.ShapeColor=c;o.ViewObject.Transparency=alpha;o.ViewObject.DisplayMode='Shaded';GG.addObject(o);return o
# Parts-backed bounded stations; functional low floor/F0 remain, no fictitious raised belly.
st=[(-147,28,145),(-126,77,166),(-92,102,176),(-25,102,178),(45,102,178),(112,102,175),(148,78,150),(178,25,96)]
w=[]
for x,ry,top in st:
 pts=[V(x,ry*math.copysign(abs(math.cos(math.pi*i/24))**.7,math.cos(math.pi*i/24)),48+(top-48)*math.sin(math.pi*i/24)**.7) for i in range(25)];pts.append(pts[0]);w.append(Part.Wire(Part.makePolygon(pts).Edges))
body=Part.makeLoft(w,True,True)
body=body.cut(Part.makeCylinder(23,95,V(90,-4,126),V(0,0,1)))
body=body.cut(Part.makeBox(20,18,80,V(20,-42,125)))
ob('D18B_BODY_FORM',body,(.13,.14,.16))
def ell(c,r):
 s=Part.makeSphere(1);m=A.Matrix();m.A11,m.A22,m.A33=r;s=s.transformGeometry(m);s.translate(V(*c));return s
head=ell((-181,0,136),(56,74,69))
for side in [-1,1]:head=head.fuse(ell((-231,side*20,116),(14,22,19)))
# Rectangular true H/V FOV frustum avoids the old circular cone/chassis opening.
for x,z,hy,hz,ah,av in [(-222,145,3.5,3.5,51,33.5),(-232,103,13,13,22.5,22.5)]:
 ws=[]
 for xx in [x-65,x+1]:
  d=max(0,x-xx);y=hy+d*math.tan(math.radians(ah));zz=hz+d*math.tan(math.radians(av));ps=[V(xx,-y,z-zz),V(xx,y,z-zz),V(xx,y,z+zz),V(xx,-y,z+zz),V(xx,-y,z-zz)];ws.append(Part.Wire(Part.makePolygon(ps).Edges))
 head=head.cut(Part.makeLoft(ws,True,True))
ob('D18B_HEAD_CHEEKS_FORM',head,(.14,.15,.17))
for side in [-1,1]:
 ob('D18B_GOLD_ORBIT_'+str(side).replace('-','m'),ell((-226.5,side*34,147),(5,16,18)),(.65,.43,.13))
 ob('D18B_DARK_EYE_'+str(side).replace('-','m'),ell((-229.8,side*34,147),(3.7,12.5,14.5)),(.015,.02,.025))
# Actual old ear/tail/source hardware all retained. No newly invented eye electronics.
for n in ['Ola_ear__1','Ola_ear_1']:D.getObject(n).ViewObject.Visibility=True
REF=D.addObject('App::DocumentObjectGroup','D18B_ASSEMBLY_RECEIVING_AND_LOOM_PLAN')
def line(n,ps,col):
 o=D.addObject('PartDesign::Feature',n);o.Shape=Part.makePolygon([V(*p) for p in ps]);o.Label='FUNCTIONAL_RECEIVING_PLAN_NOT_MATERIAL';o.ViewObject.LineColor=col;o.ViewObject.LineWidth=3;REF.addObject(o);o.ViewObject.Visibility=False;return o
line('D18B_CAMERA_LOAD_RECEIVER',[[-135,25,121],[-202,25,121],[-202,0,121],[-202,-.1,134.5],[-202,-.1,155.5]],(.1,.3,.8))
line('D18B_TOF_LOAD_BRANCH',[[-202,25,121],[-202,-8,100],[-224,-8,100],[-224,-3.81,96.54],[-224,-3.81,109.24]],(.1,.3,.8))
line('D18B_SHARED_FIXED_LOAD_CONCEPT',[[-80,-22.5,45.52],[-80,-22.5,52],[-70,22.5,52],[112,22.5,52],[122,-22.5,52]],(.25,.65,.2))
# Coupled source receiving profiles, full stock remains a proposal until all range radii clear.
for s in json.loads((P/'outboard-full200-analytic.json').read_text())['poses']:
 if (s['yaw'],s['pitch']) in [(0,0),(-20,10),(20,10)]:line('D18B_FFC_KEY_STATIONS_'+str(s['yaw']).replace('-','m'),[s['C'],s['A'],s['B'],[-62.5,31.1,113.5]],(.1,.65,.85))
for x in [18,78]:line('D18B_FULL200_TEXTILE_LOOP_FIELD',[[x,17.4,49],[x,57.6,49],[x,57.6,76.1],[x,17.4,76.1],[x,17.4,49]],(.55,.3,.1))
line('D18B_TOF4_R33_BIGHT_REFERENCE',[[ -180+33*math.cos(2*math.pi*i/48),-33+33*math.sin(2*math.pi*i/48),120] for i in range(49)],(.3,.7,.2))
# Cached rigid identity evidence, no source compound scan/BOP.
(P/'actual-whole-placement-delta.json').write_bytes((json.dumps(dict(changes=delta,withdrawn_own_unbuilt_roles=withdraw,new_print_material=False,station_bounds=st),indent=2)+'\n').encode('utf-8'))
r=[]
for n in ['Motor_ATO4A_1_5','Motor_ATO4A__1_5']:
 a=D.getObject('S0_key').Shape;b=D.getObject(n).Shape;r.append(dict(a='S0_key',b=n,distance=a.distToShape(b)[0],proof='actual affected pair distance, no world matrix'))
(P/'actual-operator-bank-delta.json').write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
D.recompute();D.Label='DAY18_OUTBOARD_OPERATOR_WHOLE_PROPOSAL';D.save()
v=V(-1.5,1,.65);v.normalize();rr=V(0,0,1).cross(v);rr.normalize();G.activeDocument().activeView().setCameraOrientation(A.Rotation(rr,v.cross(rr),v,'ZXY').Q);G.activeDocument().activeView().fitAll();G.activeDocument().activeView().redraw();print('WHOLE_MATERIAL_FREE_PROPOSAL_SAVED',len(delta),'rigid moves; source bank delta',r)
