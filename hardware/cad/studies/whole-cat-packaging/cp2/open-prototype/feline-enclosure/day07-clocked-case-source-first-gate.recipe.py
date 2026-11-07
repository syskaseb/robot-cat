import time,json,hashlib,zipfile,os
st141=time.monotonic();cp141=time.process_time();pp141=OUT/'day07-FPI-W068-whole-clocked-case-layer-proposal.json';pr141=json.loads(pp141.read_bytes());old141=ctx121['F_PI:registered_casing_reservation'];oldcentre141=A.Vector(-52.95,0,41.1);target141=A.Vector(*pr141['case_pose']['centre_mm']);m141=A.Matrix();rotarr141=pr141['case_pose']['rotation_rows']
for i in range(3):
 for j in range(3):setattr(m141,'A'+str(i+1)+str(j+1),rotarr141[i][j])
rot141=A.Rotation(m141);tf141=A.Placement(target141-rot141.multVec(oldcentre141),rot141);case141=old141.copy();case141.Placement=tf141*case141.Placement;assert case141.isValid() and len(case141.Solids)==1 and abs(case141.Volume-old141.Volume)<1e-7;bounds141=saved_bounds(case141);assert max(abs(bounds141[i][j]-pr141['case_pose']['bounds_mm'][i][j]) for i in range(2) for j in range(3))<1e-6
lo,hi=pr141['case_pose']['routine_lid_access_box'];lid141=Part.makeBox(*[hi[i]-lo[i] for i in range(3)],A.Vector(*lo));assert lid141.isValid();parts141=[('NEW_WHOLE_FHAC_CASE_PROJECT_ENVELOPE',case141),('FULL_UPWARD_LID_OPERATION_RESERVATION',lid141)];tasks141=[];rows141=[];first141=None;common141=None
for n,s in parts141:
 for k,v in ctx121.items():
  if k=='F_PI:registered_casing_reservation':continue
  if bbox_lower_bound(s.BoundBox,bounds126[k])<1.25:tasks141.append((n,k))
# Entire bought/module/hardware neighbors are preflighted before prospective new printed detail.
tasks141.sort(key=lambda t:(0 if t[0]=='NEW_WHOLE_FHAC_CASE_PROJECT_ENVELOPE' else 1,0 if ('Station:' in t[1] and ':case' in t[1]) or 'Ref_Material' in t[1] else 1,t[1]))
for n,k in tasks141:
 s=dict(parts141)[n];v=ctx121[k];row=dict(part=n,other=k,field_valid=s.isValid(),source_valid=v.isValid(),field_kind='fullselectedcaseprototypebox' if n.startswith('NEW') else 'routineoperationreservation')
 if not v.isValid():
  row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 else:
  gap,ww,_=s.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='NEW_WHOLE_ALLOCATION_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_WHOLE_ALLOCATION_HOLD')
  if gap<1e-7:
   common141=s.common(v);row.update(common_valid=common141.isValid(),allocated_common_mm3=common141.Volume if common141.isValid() else None)
 rows141.append(row)
 if row['status']!='NEW_WHOLE_ALLOCATION_SEPARATED125':first141=row;break
 if time.monotonic()-st141>15:break
# Source/read-only cached bounds only: new case vs unchanged proposedcrown/stock/sourcefields and requiredS0operatorregion.
brows141=[];opbounds141=[[-75.70633586120518,-15,80.43543345605332],[-17.519879368482187,15,137.34029879589923]]
for n,s in parts141:
 for name,v in [('NEW_CROWN_CURRENT_PROPOSAL',union137),('NEW_ROOT145_CURRENT_PROPOSAL',bandphys137),('NEW_PRESSURE_HEAD_CURRENT_PROPOSAL',phead137),('SOURCE9_FIXED_PASSAGE',field114),('SOURCE_D3_ALLOCATED_FAN',assigned130)]:brows141.append(dict(part=n,other=name,lower_mm=bbox_lower_bound(s.BoundBox,v.BoundBox)))
 bb=A.BoundBox(*(opbounds141[0]+opbounds141[1]));brows141.append(dict(part=n,other='REQUIRED_S0_COMPLETE_OBLIQUE_OPERATOR_REGION',lower_mm=bbox_lower_bound(s.BoundBox,bb),bounds_source='day07-S0-complete-oblique-entry-profile.json',no_old_operator_test_replay=True))
items141=[('OLD_FPI_UNQUALIFIED_CASE_BOX',old141),('NEW_WHOLE_CASE',case141),('FULL_UPWARD_ROUTINE_LID_SPACE',lid141)]
if first141:items141.append(('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first141['other']]))
if common141 is not None and common141.isValid():items141.append(('FIRST_VALID_ALLOCATED_COMMON',common141))
ar141=OUT/'day07-FPI-whole-clocked-case-first-preflight.breps.zip';assert not ar141.exists();ge141=[]
with zipfile.ZipFile(ar141,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items141):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge141.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge141),indent=2)+'\n').encode())
r141=dict(id='day07-FPI-whole-clocked-case-first-preflight',status='WHOLE_CLOCKED_CASE_ALLOCATION_HOLD_BEFORE_NEW_SUPPORT' if first141 else 'BOUNDED_WHOLE_CASE_INITIAL_PREFLIGHT_ONLY_RECEIVED',proposal=pp141.name,proposal_sha256=hashlib.sha256(pp141.read_bytes()).hexdigest(),new_rigid_transform=dict(rotation=rotarr141,old_centre_mm=list(oldcentre141),new_centre_mm=list(target141),volume_same=True,new_valid=True,new_bounds=bounds141,world_placement_applied_ONCE=True,not_manufacturer_exact=True),rows=rows141,cursor=len(rows141),total=len(tasks141),unreceived=len(tasks141)-len(rows141),first_falsifier=first141,new_bounding_scope_only=brows141,old_3of4_source_tests_NOT_replayed=True,old_source_scans_not_replayed=True,case_cradle_or_new_clamps_material_built=False,currentcase_parent_replaced=False,affected_MTA_220_ends_moved=False,selected=False,N01_complete=False,archive=ar141.name,archive_sha256=hashlib.sha256(ar141.read_bytes()).hexdigest(),geometry=ge141,operation_seconds=time.monotonic()-st141,process_cpu_seconds=time.process_time()-cp141,pid=os.getpid(),session_id=46493)
p141=OUT/'day07-FPI-whole-clocked-case-first-preflight.json';assert not p141.exists();p141.write_bytes((json.dumps(r141,indent=2)+'\n').encode());print('BODY141',r141['status'],'rows',len(rows141),len(tasks141),'first',first141,'wall',r141['operation_seconds'],'CPU',r141['process_cpu_seconds'],flush=True);print('OWNER69_IDLE',os.getpid(),flush=True)
