import FreeCAD as A,FreeCADGui as G,Part,json,pathlib,math
D=A.ActiveDocument; P=pathlib.Path(__file__).parent; V=A.Vector
def box(a,b): return Part.makeBox(b[0]-a[0],b[1]-a[1],b[2]-a[2],V(*a))
members={
 'CAM_plate':box([-159.6,-22,138.5],[-156.6,22,158]),
 'journal_boss':box([-142,22,114],[-128,30,128]),
 'main_arm':box([-159.6,22,114],[-135,28,128]),
 'front_crossmember':box([-159.6,-22,114],[-153.6,28,128]),
 'negative_upright':box([-159.6,-22,121],[-153.6,-17,158]),
 'upper_negative':box([-159.6,-22,152.5],[-153.6,-10,158]),
 'upper_positive':box([-159.6,10,152.5],[-153.6,22,158]),
 'upper_central_rear':box([-157,-11,152.5],[-153.6,11,158]),
 'ToF_plate':box([-179,-20,92],[-176,2,114]),
 'ToF_beam':box([-179,-20,96],[-153.6,-15,104]),
 'ToF_branch':box([-159.6,-20,100],[-153.6,-15,125])}
cuts=[Part.makeCylinder(4.2,12,V(-135,20,121),V(0,1,0)),Part.makeCylinder(1.1,25,V(-150,25,121),V(1,0,0)),box([-144.2,22.3,118.3],[-142,38,123.7])]
for y in [-10.5,10.5]: cuts.append(Part.makeCylinder(1.1,8,V(-162,y,144.9),V(1,0,0)))
for z in [96.54,109.24]: cuts.append(Part.makeCylinder(1.1,8,V(-182,-3.81,z),V(1,0,0)))
# Through-to-front notch is intentional, not a wire exception through the CAM plate.
cuts.append(box([-162,-10,151.8],[-157,10,160]))
s=list(members.values())[0]
for q in list(members.values())[1:]:s=s.fuse(q)
for q in cuts:s=s.cut(q)
s=s.removeSplitter()
o=D.addObject('PartDesign::Feature','D18C_TRUE_PITCH_OPTICAL_RECEIVER');o.Shape=s;o.ViewObject.ShapeColor=(.22,.42,.64)
o.addProperty('App::PropertyLink','RotatingLoadOwner');o.RotatingLoadOwner=D.getObject('PITCH_HORN_ROOF_JOURNAL')
o.addProperty('App::PropertyString','Assembly');o.Assembly='TRUE_PITCH journal bore + complete reversed M2x20 crosspin; side-load full nut/washer BEFORE Pi/banks; CAM2+ToF2 source full sets; no attachment to fixed 688 outercap'
report=dict(valid=s.isValid(),solid_count=len(s.Solids),volume_mm3=s.Volume,PETG_g=s.Volume*.00127,bounds=[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax],members={},positive_junctions=[],assembly_status='NOMINAL_RECEIVER; source horn/bearing fit and safe mounting annuli require physical dryfit; neighbors pending')
for n,m in members.items():
 t=m
 for c in cuts:t=t.cut(c)
 report['members'][n]=dict(planned_retained_volume=t.Volume,missing_volume=t.cut(s).Volume)
for na,nb in [('CAM_plate','negative_upright'),('CAM_plate','upper_positive'),('main_arm','journal_boss'),('main_arm','front_crossmember'),('front_crossmember','negative_upright'),('negative_upright','upper_negative'),('upper_negative','upper_central_rear'),('upper_central_rear','upper_positive'),('ToF_plate','ToF_beam'),('ToF_beam','ToF_branch'),('ToF_branch','front_crossmember')]:
 report['positive_junctions'].append(dict(a=na,b=nb,common_before_planned_cuts=members[na].common(members[nb]).Volume))
for n in ['HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','D18B_CAMERA_LOAD_RECEIVER','D18B_TOF_LOAD_BRANCH']:
 z=D.getObject(n)
 if z:z.ViewObject.Visibility=False
# Model-linked FOV frame: camera clock180, optical model lensface X=-177, not a supplier nodal claim.
fov=dict(camera=dict(clock_about_optical_axis_deg=180,optical_axis_world=[-1,0,0],horizontal_world=[0,-1,0],vertical_world=[0,0,-1],nominal_model_lens_face=[-177,0,145],H_deg=102,V_deg=67,apex_status='MODEL_FACE_REFERENCE_NOT_MANUFACTURER_NODAL_POINT'),tof=dict(model_front_X=-187,centre_Z=103,H_deg=45,V_deg=45,both_TX_RX_open=True),moving_owner='PITCH_HORN_ROOF_JOURNAL; pitch Y through (-135,0,121), carried by yaw Z(-106,0,127)')
for n,x,z,hy,hz,ah,av in [('CAM',-177,145,3.5,3.5,51,33.5),('TOF',-187,103,13,13,22.5,22.5)]:
 ws=[]
 for xx in [x-70,x+.05]:
  d=max(0,x-xx);yy=hy+d*math.tan(math.radians(ah));zz=hz+d*math.tan(math.radians(av));p=[V(xx,-yy,z-zz),V(xx,yy,z-zz),V(xx,yy,z+zz),V(xx,-yy,z+zz),V(xx,-yy,z-zz)];ws.append(Part.Wire(Part.makePolygon(p).Edges))
 f=D.addObject('PartDesign::Feature','D18C_'+n+'_MODEL_CLOCK_BOUND_FOV');f.Shape=Part.makeLoft(ws,True,True);f.ViewObject.Visibility=False
 fov[n+'_FOV_object']=f.Name
(P/'true-pitch-material-coverage.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
(P/'actual-clock-FOV-and-load-binding.json').write_bytes((json.dumps(fov,indent=2)+'\n').encode())
s.exportBrep(str(P/'true-pitch-receiver.brep'))
print('TRUE_PITCH_RECEIVER',report['valid'],report['solid_count'],report['volume_mm3'],max(x['missing_volume'] for x in report['members'].values()))
