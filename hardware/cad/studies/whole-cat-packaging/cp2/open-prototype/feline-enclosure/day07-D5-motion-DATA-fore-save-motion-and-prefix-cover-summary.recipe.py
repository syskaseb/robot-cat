import json,time,hashlib,os
t189=time.monotonic();c189=time.process_time();assert r187['cursor']==27090 and r187['first_falsifier'] is None and len(r187['new_kernel_rows'])==0
summary189=[]
for fi,(fn,s) in enumerate(fixed187):
    mm=1e99;mk=None
    for pi in range(1,36):
        bs=posedbounds175[pi];fb=bounds187[fi];dd=np.maximum(np.maximum(fb[0]-bs[:,1,:],bs[:,0,:]-fb[1]),0);vals=np.linalg.norm(dd,axis=1);i=int(np.argmin(vals))
        if vals[i]<mm:mm=float(vals[i]);mk=[pi,fn,names175[i]]
    assert mm>=1.25-1e-7;summary189.append(dict(fixed_actor=fn,received_pairs=4515,all_full_cover_separated=True,minimum_certified_lower_mm=mm,minimum_key=mk))
prefix189=[]
for f in frames181:
    y=f['unchanged_actual_project_port_mm'][1];b=np.array([[57.5-1.55,y-3.12524153947005-1.55,48.5-1.55],[65.98036180850077+1.55,y+1.55,48.5+1.55]])
    outside=np.maximum(np.maximum(bounds187[0][0]-b[0],b[1]-bounds187[0][1]),0);assert outside.max()<1e-7
    prefix189.append(dict(port=f['port'],wire=f['wire'],complete9p25_analytic_profile_bounds=b.tolist(),contained_in_THISfreshmotion_field=bounds187[0].tolist(),outside_mm=outside.tolist(),scoped_motion_lower_mm=summary189[0]['minimum_certified_lower_mm'],no_extra_matrix_or_source_reopen=True,scope='Analyticper-ownportR12.4rolledXYarc+retained.25line/r1.55 fits conservativeNEWfirstfieldbbox acrosssame35R/T. DoesNOTqualifyfreeR35.1outsideSOURCEtransport.'))
floor189=min(s.BoundBox.ZMin for n,s in fixed187)-max(p['body_drop_mm'] for p in MotionSource31['poses'][:36])-MotionSource31['ground_rest_z_mm']
p189=OUT/'day07-five-D-south-new-motion-and-held-prefix-cover-summary.json';assert not p189.exists();r189=dict(id=p189.stem,status='NEW_FIVE_D_KIT_MOTION35_AND_FIVE_HELD9P25_PREFIX_COVERS_CLOSED_SCOPED',motion_cursor_receipt=p187.name,motion_cursor_sha256=hashlib.sha256(p187.read_bytes()).hexdigest(),required_newposes=list(range(1,36)),new_pairs=27090,exact_kernel_pairs=0,all_conservative_separated=True,per_fixed=summary189,minimum_certified_lower_mm=min(q['minimum_certified_lower_mm'] for q in summary189),five_complete_fixed9p25_prefix_analytic_containment=prefix189,new_fixed_material_floor_lower_over_required36_mm=floor189,oldG36120_155_4515_static_USB_not_replayed=True,selected=False,N01_complete=False,legacyPad_halfmm_OPEN=True,actual_SOURCE_outsideLi_motionstorage_whole850900_NOT_qualified=True,operation_seconds=time.monotonic()-t189,process_cpu_seconds=time.process_time()-c189,pid=os.getpid(),session_id=46493);p189.write_bytes((json.dumps(r189,indent=2)+'\n').encode());print('D5_MOTION_AND_PREFIX_COVER',r189['minimum_certified_lower_mm'],floor189,27090,len(prefix189),r189['operation_seconds'],r189['process_cpu_seconds'],hashlib.sha256(p189.read_bytes()).hexdigest(),'OWNER82_IDLE',os.getpid(),flush=True)
