import time,json,hashlib,zipfile,os,math
t130=time.monotonic();c130=time.process_time();pp130=OUT/'day07-SOURCE-ninecore-left-entry-lane-roll-whole-proposal.json';pr130=json.loads(pp130.read_bytes());subset130=[];items130=[]
for q in pr130['rows']:
 x,z=q['centre_XZ_mm'];rr=q['margin_capacity_radius_mm'];sh=Part.makeCylinder(rr,37.75,A.Vector(x,39.25,z),A.Vector(0,1,0));outside=sh.cut(field114);assert sh.isValid() and outside.isValid();loss=outside.Volume;assert loss<1e-7
 subset130.append(dict(wire=q['wire'],physical_unit=q['physical_passage_unit'],centre_XZ_mm=[x,z],full_profile_radius_mm=q['profile_radius_mm'],margin_capacity_radius_mm=rr,capacity_outside_received_field_mm3=loss,valid=True));items130.append(('NEW_BODY_LANE:'+q['wire'],sh))
# Rigidcopy implements the complete physical lane assignment, not a purchased/source-point move.
dx130=-135.5-(-132.75);assigned130=drop128.copy();assigned130.Placement=A.Placement(A.Vector(dx130,0,0),A.Rotation())*drop128.Placement;assert assigned130.isValid() and abs(assigned130.Volume-drop128.Volume)<1e-6
minp130=[-135.5,float(p2[1]),42.05];endgap130=Part.Vertex(A.Vector(*minp130)).distToShape(assigned130)[0];assert endgap130<1e-6
ob130=assigned130.optimalBoundingBox(False,False);bb130=[[ob130.XMin,ob130.YMin,ob130.ZMin],[ob130.XMax,ob130.YMax,ob130.ZMax]];tasks130=[k for k in ctx121 if bbox_lower_bound(ob130,bounds126[k])<1.25];tasks130.sort(key=lambda k:(0 if k=='Ref_Material_current_S1_screw_5_0_0' else 1 if k=='Ref_Material_S0_body_CP2_0_0' else 2 if 'ring' in k.lower() else 3,k));rows130=[];first130=None;co130=None
for k in tasks130:
 s=ctx121[k];q=dict(other=k,field_valid=True,source_valid=s.isValid())
 if q['source_valid']:
  gap,ww,_=assigned130.distToShape(s);q.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='ASSIGNED_D_CAPACITY_SEPARATED125' if gap>=1.25-1e-7 else 'ASSIGNED_D_REGION_HOLD_FUNCTION_PENDING_NOT_WIRECONTACT')
  if gap<1e-7:
   co130=assigned130.common(s);q.update(common_valid=co130.isValid(),allocated_common_mm3=co130.Volume if co130.isValid() else None)
 else:q['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
 rows130.append(q)
 if q['status']!='ASSIGNED_D_CAPACITY_SEPARATED125':first130=q;break
 if time.monotonic()-t130>18:break
items130 += [('ASSIGNED_D_LEFT_ENTRY_FULL39_CAPACITY',assigned130)]
if first130:items130.append(('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first130['other']]))
if co130 is not None:items130.append(('ALLOCATED_COMMON_NOT_WIRECONTACT',co130))
sections130=[]
if first130 and first130.get('witnesses'):
 y=first130['witnesses'][0][0][1];plane=Part.makePlane(100,140,A.Vector(-160,y,0),A.Vector(0,1,0))
 for n,sh in items130[-3 if co130 is not None else -2:]:
  sec=sh.section(plane);curves=[]
  for e in sec.Edges:
   ps=e.discretize(Deflection=.08)
   if len(ps)>1:curves.append([[v.x,v.z] for v in ps])
  sections130.append(dict(Y_mm=y,name=n,curves_xz=curves))
ar130=OUT/'day07-SOURCE-ninecore-subset-and-assigned-D-gate.breps.zip';assert not ar130.exists();ge130=[]
with zipfile.ZipFile(ar130,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(n,sh) in enumerate(items130):
  raw=sh.exportBrepToString().encode();en=str(i)+'.brep';zz.writestr(en,raw);ge130.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=sh.isValid(),volume_mm3=sh.Volume,bounds_mm=saved_bounds(sh)))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=ge130),indent=2)+'\n').encode())
r130=dict(id='day07-SOURCE-ninecore-subset-and-assigned-D-gate',status='ALL9_FIXED_PASSAGE_SUBSETS_RECEIVED_ASSIGNED_D_LOCAL_HOLD' if first130 else 'ALL9_FIXED_PASSAGE_SUBSETS_RECEIVED_ASSIGNED_D_LOCAL_PENDING' if len(rows130)<len(tasks130) else 'ALL9_FIXED_PASSAGE_SUBSETS_AND_ASSIGNED_D_LOCAL_SCOPE_RECEIVED',proposal=pp130.name,proposal_sha256=hashlib.sha256(pp130.read_bytes()).hexdigest(),new_all9_subset_rows=subset130,minimum_profile_gap_analytic_mm=pr130['minimum_nominal_profile_gap_mm'],fixed_field_unchanged=True,old1443_4515_replay=False,assigned_D_quality=dict(valid=True,source_shape_volume_preserved=True,new_volume_mm3=assigned130.Volume,optimal_bounds_mm=bb130,analytic_Zmin_actual_BRep_gap_mm=endgap130,actual_source_ports_unchanged=True,capacity_free_lane_assignment_dx_mm=dx130,no_oldcurve_retest=True),new_local_rows=rows130,cursor=len(rows130),total=len(tasks130),unreceived=len(tasks130)-len(rows130),first_falsifier=first130,sections=sections130,archive=ar130.name,archive_sha256=hashlib.sha256(ar130.read_bytes()).hexdigest(),geometry=ge130,new_material=False,new_leg_geometry=False,all9_A_U_minfit_slack=None,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t130,process_cpu_seconds=time.process_time()-c130,pid=os.getpid(),session_id=46493)
rp130=OUT/'day07-SOURCE-ninecore-subset-and-assigned-D-gate.json';assert not rp130.exists();rp130.write_bytes((json.dumps(r130,indent=2)+'\n').encode());print('BODY130',r130['status'],'subsets',len(subset130),'local',len(rows130),len(tasks130),first130,'wall',r130['operation_seconds'],'CPU',r130['process_cpu_seconds'],flush=True);print('OWNER65_IDLE',os.getpid(),flush=True)
