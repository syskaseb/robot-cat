import json,time,hashlib,zipfile,os
t176=time.monotonic();c176=time.process_time();assert r175['cursor']==36120 and r175['first_falsifier'] is None
actual176={q['flat_key']:q for q in r175['new_kernel_rows']};summ176=[];min176=1e99
for fi,(fn,fs) in enumerate(fixed175):
    mm=1e99;mk=None;broad=0;exact=0
    for pi in range(1,36):
        bs=posedbounds175[pi];fb=fixedbounds175[fi];dd=np.maximum(np.maximum(fb[0]-bs[:,1,:],bs[:,0,:]-fb[1]),0);vals=np.linalg.norm(dd,axis=1)
        for ai,lo in enumerate(vals):
            k=(pi-1)*nf175*na175+fi*na175+ai
            if k in actual176:v=actual176[k]['gap_mm'];exact+=1
            else:v=float(lo);broad+=1;assert lo>=1.25-1e-7
            if v<mm:mm=v;mk=[pi,fn,names175[ai]]
    summ176.append(dict(fixed_actor=fn,received_pairs=35*na175,broadphase_full_cover_separated=broad,new_exact_pairs=exact,minimum_certified_lower_mm=mm,minimum_key=mk,allocated_stock_field=fi>=4));min176=min(min176,mm)
closest176=min(r175['new_kernel_rows'],key=lambda q:q['gap_mm']);pi,fn,mn=closest176['key'];fi=[n for n,s in fixed175].index(fn);code,si=owners115[mn];rr,tt=transforms175[pi][code][si];posed176=moving115[mn].copy();posed176.Placement=placement106(rr,tt)*posed176.Placement;assert posed176.isValid() and abs(posed176.Volume-closest176['posed_volume_mm3'])<1e-6
ar176=OUT/'day07-G4-C1-independent-motion-closest-received-pair.breps.zip';assert not ar176.exists();ge176=[]
with zipfile.ZipFile(ar176,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([(fn,fixed175[fi][1]),(mn,posed176)]):
        f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat79-motion-witness-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();en=str(i)+'.brep';z.writestr(en,raw);ge176.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),valid=s.isValid(),volume_mm3=s.Volume,pose=pi if i==1 else None))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge176,received_exact_row=closest176,no_new_distance_or_motion_tests=True),indent=2)+'\n').encode())
q176=OUT/'day07-G4-C1-independent-motion-aggregation-and-witness.json';assert not q176.exists();result176=dict(id=q176.stem,status='ONLY_EXACT_G4_NEW_FIXED_MOVING_DELTA_35_POSES_CLOSED_SCOPED',cursor_receipt=p175.name,cursor_sha256=hashlib.sha256(p175.read_bytes()).hexdigest(),received=36120,conservative_separated=36120-len(actual176),exact_new_pairs=len(actual176),per_fixed_actor=summ176,minimum_certified_lower_mm=min176,closest_new_exact_gap_mm=closest176['gap_mm'],closest_new_exact_row=closest176,required_pose_indices=[1,35],neutral_exact_static_reuse_only=True,source_order_and_flat_keys=r175['key_definition'],archive=ar176.name,archive_sha256=hashlib.sha256(ar176.read_bytes()).hexdigest(),geometry=ge176,no_new_distance_calls_in_aggregation=True,frozen_D_portal_gap_mm=.8632644993806989,frozen_D_portal_remains_REJECTED=True,selected=False,N01_complete=False,current_parent_unchanged=True,operation_seconds=time.monotonic()-t176,process_cpu_seconds=time.process_time()-c176,pid=os.getpid(),session_id=46493)
q176.write_bytes((json.dumps(result176,indent=2)+'\n').encode());print('G4_MOTION_RECEIVED',36120,len(actual176),'mincert',min176,'minexact',closest176['gap_mm'],result176['operation_seconds'],result176['process_cpu_seconds'],hashlib.sha256(q176.read_bytes()).hexdigest(),'OWNER79_IDLE',os.getpid(),flush=True)
