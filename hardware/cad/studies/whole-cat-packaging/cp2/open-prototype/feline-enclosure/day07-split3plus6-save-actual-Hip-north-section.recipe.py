import time,json,os
t239=time.monotonic();c239=time.process_time();assert first237['other']=='Ref_Material_U1_R4_0_0';pl239=Part.makePlane(100,110,A.Vector(-70.55,-30,-45),A.Vector(1,0,0),A.Vector(0,1,0));secs239=[]
for n,s in [('HIP_W019_ALLOCATED',fields237['W019']),('ACTUAL_RETAINED_U1_R4',context230[first237['other']])]:
 sec=s.section(pl239);lines=[]
 for e in sec.Edges:lines.append([[p.y,p.z] for p in e.discretize(Deflection=.025)])
 assert lines
 secs239.append(dict(actor=n,X_mm=-70.55,curves_YZ=lines))
f239=context230[first237['other']];p239=OUT/'day07-SPLIT3plus6-current-U1-R4-local-actual-section.json';r239=dict(id=p239.stem,status='ACTUAL_CURRENT_HIP_NORTH_FIRST_HAZARD_SECTION_NO_NEW_TEST',actual_source_actor=first237['other'],actual_current_bounds_mm=saved_bounds(f239),actual_shape_volume_mm3=f239.Volume,source_function='Retained native U1 component; no deletion, purchased/material subtype NOT inferred from name. Foreign1.25 remains. No print-only own classification.',sections=secs239,actual_witnesses=first237['witnesses'],gap_mm=first237['gap_mm'],valid_common_mm3=first237['allocated_common_mm3'],no_physical_contact_claim=True,no_secondfamily_or_source_pose_change=True,operation_seconds=time.monotonic()-t239,process_cpu_seconds=time.process_time()-c239,pid=os.getpid(),session_id=46493);p239.write_bytes((json.dumps(r239,indent=2)+'\n').encode());print('SPLIT239_SAVED',r239['actual_current_bounds_mm'],len(secs239),r239['operation_seconds'],r239['process_cpu_seconds'],'OWNER94_NATIVE_IDLE26064',flush=True)
