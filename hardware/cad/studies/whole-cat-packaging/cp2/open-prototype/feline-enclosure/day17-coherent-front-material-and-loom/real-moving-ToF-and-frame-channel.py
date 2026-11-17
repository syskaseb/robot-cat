import FreeCAD as A,FreeCADGui as G,Part,math,json,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;Z=V(0,0,1)
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def unit(v):v=V(v);v.normalize();return v
def pose(q,y,p):
 q=V(-135,0,121)+A.Rotation(V(0,1,0),p).multVec(V(q)-V(-135,0,121));return V(-106,0,127)+A.Rotation(Z,y).multVec(q-V(-106,0,127))
def hr(q,y,p):return A.Rotation(Z,y).multVec(A.Rotation(V(0,1,0),p).multVec(q))
def secwire(c,t,w,width):
 w=unit(w-t*w.dot(t));n=unit(t.cross(w));a=w*(width/2+.02);b=n*1.47
 return Part.Wire(Part.makePolygon([c-a-b,c+a-b,c+a+b,c-a+b,c-a-b]).Edges)
def curve(y,p):
 S=pose(V(-228.016,5.08,102.89),y,p);u=hr(V(1,0,0),y,p);C=S+u*8;G=V(-65,-22.6,184);ps=[C,C+70*u,G-V(70,0,0),G]
 def at(t):return ps[0]*(1-t)**3+ps[1]*3*t*(1-t)**2+ps[2]*3*t*t*(1-t)+ps[3]*t**3
 def vel(t):return 3*((ps[1]-ps[0])*(1-t)**2+(ps[2]-ps[1])*2*t*(1-t)+(ps[3]-ps[2])*t*t)
 def acc(t):return 6*((ps[2]-2*ps[1]+ps[0])*(1-t)+(ps[3]-2*ps[2]+ps[1])*t)
 lower=[]
 for i in range(64):
  a=i/64;b=(i+1)/64;e=unit(vel((a+b)/2));vs=[vel(a),vel(a)+acc(a)*(b-a)/2,vel(b)];mn=min(v.dot(e) for v in vs);mx=max(v.Length for v in vs);am=max(acc(a).Length,acc(b).Length);lower.append(mn**3/(mx*am)-9.42)
 wires=[secwire(S,u,hr(Z,y,p),18.8)]
 for i in range(65):
  t=i/64;v=unit(vel(t));w=hr(Z,y,p);wires.append(secwire(at(t),v,w,18.8-(18.8-10.4)*min(1,t*4)))
 # Both broad fixed returns retain whole4profile; no clamps at passive G.
 for i in range(1,25):
  a=math.pi/2*i/24;c=G+V(38*math.sin(a),0,-38*(1-math.cos(a)));t=V(math.cos(a),0,-math.sin(a));wires.append(secwire(c,t,V(0,1,0),10.4))
 B=G+V(38,0,-38)
 for i in range(1,25):
  a=math.pi/2*i/24;c=B+V(0,38*(1-math.cos(a)),-38*math.sin(a));t=V(0,math.sin(a),-math.cos(a));wires.append(secwire(c,t,V(1,0,0),10.4))
 # Independent real-net fanout stays on existing PCA/E1 endregions. These are passive seams NOT newterminals.
 up=8+sum((ps[i+1]-ps[i]).Length for i in range(3))+math.pi*38+9.4+20
 return Part.makeLoft(wires,True,True),{'yaw':y,'pitch':p,'ribbon_not_FFC':True,'innerR_certified_curve_parameter_lower':min(lower),'fixed_return_innerR':38-5.22,'routed_percore_upper_including_source_row_and20_end_work':up,'G_passive_not_grip':list(G),'fanout_to_existing_PCA_E1_region':list(G+V(38,38,-76))}
D.save();rr=[]
for y in [-20,0,20]:
 for p in [-10,0,10]:
  s,r=curve(y,p);rr.append(r)
  if (y,p) in [(0,0),(-20,10),(20,10)]:
   n='CF17_ToF4_OCCUPIED_'+str(y).replace('-','m')+'_'+str(p);o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.2,.7,.8);o.ViewObject.Transparency=55;o.ViewObject.Visibility=(y,p)==(0,0)
put('ToF4-actual-connected-profile-and-unit-upper.json',{'rows':rr,'profile_group':[10.4,2.9],'source_row_fanout_width':18.8,'real_rule_R':31.5,'project_blank_each_upper':math.ceil(max(r['routed_percore_upper_including_source_row_and20_end_work'] for r in rr)/5)*5,'nets':['EXT011 LOCAL.LOGIC3V3->VIN','EXT012 LOCAL.GND->GND','EXT013 PI.H3->SDA','EXT014 PI.H5->SCL'],'physical_material':'four HELU0.5mm2 OD2.1, selectedbulk bycolor; NOT fivePololu600 parents','source_fanout':'existing PCA.JP3.3/.4 aliases; precise suppliedheader/strain andwithinrowmappingphysicalFIT; no newsplice/freepins','continuous_head_motion_PASS':False,'samples_are_correlated_poses_not_allposes':True,'actualcuts':None,'physicalPASS':False})
# Actual useful functional channel in SOURCE moving sensorframe, not field-only clipping.
S=Part.Shape();S.read(str(P/'source-head-carrier.world.brep'));old=S.copy()
camcut=Part.makeBox(13.5,24,42,V(-212,-12,153))
tofcut=Part.makeBox(14,23,22.5,V(-212,-7,92))
cam_tie=Part.makeBox(1.9,28,8,V(-201.8,-14,151))
tof_tie=Part.makeBox(6.1,52,4,V(-204.6,-26,116.5))
q=S.cut(camcut).cut(tofcut).fuse(cam_tie).fuse(tof_tie).removeSplitter()
D.getObject('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE').Shape=q;D.getObject('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE').Placement=A.Placement()
# Topcamera lands below149.1 and source negativeY ToF brace(-12..-8) retained.
protected=[Part.makeBox(27,6,20,V(-224,-13,93)),Part.makeBox(7,64,8,V(-207,-32,141.1)),Part.makeBox(80,6,8,V(-205,22,117))]
put('moving-source-frame-functional-channel.json',{'sourceV':old.Volume,'newV':q.Volume,'new_valid':q.isValid(),'new_solids':len(q.Solids),'explicit_replaced_members':'central lowerbarY-7..16/Z94..98 andtopfrontcrossbar atZ153+; realouterties replace crossbarload; primarycamera uppermountlands/gimbal/pitcharm/ToFnegativeYbrace retained','source_outside_explicit_reliefs_missing':old.cut(camcut).cut(tofcut).cut(q).Volume,'new_tie_missing':[a.cut(q).Volume for a in [cam_tie,tof_tie]],'new_positive_tie_source_common':[a.common(old).Volume for a in [cam_tie,tof_tie]],'protected_source_ROI_missing':[old.common(a).cut(q).Volume for a in protected],'cutbounds':[str(camcut.BoundBox),str(tofcut.BoundBox)],'changed_mass_g_PETG1p27':(q.Volume-old.Volume)*.00127,'acceptance':'actualfullprofiles/localneighbors NEXT, notvalid1alone'})
D.recompute();D.save();print(json.dumps({'ToF_each_upper':max(r['routed_percore_upper_including_source_row_and20_end_work'] for r in rr),'innerRlower':min(r['innerR_certified_curve_parameter_lower'] for r in rr),'sourceframe':[q.isValid(),len(q.Solids),q.Volume]}))
