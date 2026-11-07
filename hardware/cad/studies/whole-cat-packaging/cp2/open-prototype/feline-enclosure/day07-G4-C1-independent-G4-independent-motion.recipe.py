import json,time,hashlib,os
t175=time.monotonic();c175=time.process_time()
fixed175=list(parts173);names175=sorted(moving115);nf175=len(fixed175);na175=len(names175);assert (nf175,na175)==(8,129)
fixedbounds175=[]
for n,s in fixed175:
    bb=np.array(saved_bounds(s),dtype=float)
    if n=='PRESSURE_HEAD_NECK_CAPACITY':
        ab=np.array(r171['new_correct_local_stock_profile']['analytic_full_bounds_mm']);bb=np.array([np.minimum(bb[0],ab[0]),np.maximum(bb[1],ab[1])])
    fixedbounds175.append(bb)
transforms175={};posedbounds175={}
for pi in range(1,36):
    pose=MotionSource31['poses'][pi];tr={code:leg_transforms(axisgroups106[code],pose['legs'][code]['angles_delta_degrees']) for code in axisgroups106};transforms175[pi]=tr;arr=[]
    for n in names175:
        code,si=owners115[n];rr,tt=tr[code][si];pts=boxes115[n]@rr.T+tt;arr.append([pts.min(axis=0),pts.max(axis=0)])
    posedbounds175[pi]=np.array(arr)
p175=OUT/'day07-G4-C1-independent-new-motion-cursor.json';assert not p175.exists()
r175=dict(id=p175.stem,status='INDEPENDENT_EXACT_G4_CHANGED_MOTION_PENDING',selected=False,N01_complete=False,source_G4_static_receipt='day07-SOURCE-G4-common-closure-C1-bounded-disposition.json',source_G4_static_sha256=hashlib.sha256((OUT/'day07-SOURCE-G4-common-closure-C1-bounded-disposition.json').read_bytes()).hexdigest(),actor_effectivity='day07-SOURCE-G4-common-closure-C1-proposed-actor-effectivity.json',actor_effectivity_sha256=hashlib.sha256((OUT/'day07-SOURCE-G4-common-closure-C1-proposed-actor-effectivity.json').read_bytes()).hexdigest(),rejected_portal_receipt='day07-SOURCE-G4-C1-leading-and-motion-bounded-disposition.json',rejected_portal_SHA=hashlib.sha256((OUT/'day07-SOURCE-G4-C1-leading-and-motion-bounded-disposition.json').read_bytes()).hexdigest(),portal_retested=False,portal_gap_not_waived_mm=.8632644993806989,scope='INDEPENDENT exact G4 fixed delta versus actualposed108+21 ONLY. No neutral or oldmatrix/static replay. No selection/currenteffectivity. Frozen D leading allocation remains rejected.',fixed_operand_order=[n for n,s in fixed175],fixed_neutral_bounds_mm=[b.tolist() for b in fixedbounds175],moving_actor_order=names175,moving_owners={n:list(owners115[n]) for n in names175},moving_neutral_bounds_mm={n:[boxes115[n].min(axis=0).tolist(),boxes115[n].max(axis=0).tolist()] for n in names175},required_poses=list(range(1,36)),neutral_scope='C4ac exact static proofs reused only; neutral not called',key_definition='flat=(pose-1)*8*129+fixed_index*129+moving_index; exact key=[pose,fixed_operand_order[fixed_index],moving_actor_order[moving_index]]. Received conservative prefix [0,cursor), actualkernel keys separately. This explicitly defines EVERY received pair without listing unchanged old tests.',cursor=0,total=35*nf175*na175,checked_exact_key_ranges=[],new_kernel_rows=[],minimum_conservative_lower_mm=None,first_falsifier=None,pending_kernel_key=None,batches=[],cache_preparation_seconds=time.monotonic()-t175,cache_preparation_CPU_seconds=time.process_time()-c175,pid=os.getpid(),session_id=46493)
lastposed175=None;lastfixed175=None
def save175():
    r175['checked_exact_key_ranges']=[[0,r175['cursor']-1]] if r175['cursor'] else []
    tmp=p175.with_suffix('.tmp');tmp.write_bytes((json.dumps(r175,indent=2)+'\n').encode());os.replace(tmp,p175)
save175()
def chunk175(seconds=12):
    global lastposed175,lastfixed175
    assert not r175['first_falsifier'];st=time.monotonic();cp=time.process_time();start=r175['cursor'];pending=False
    while r175['cursor']<r175['total']:
        k=r175['cursor'];pi=k//(nf175*na175)+1;fi=(k//na175)%nf175;ai=k%na175;n=names175[ai];fn,fs=fixed175[fi];mb=posedbounds175[pi][ai];fb=fixedbounds175[fi];g=np.maximum(np.maximum(fb[0]-mb[1],mb[0]-fb[1]),0);lower=float(np.linalg.norm(g));key=[pi,fn,n]
        if r175['minimum_conservative_lower_mm'] is None or lower<r175['minimum_conservative_lower_mm']:r175['minimum_conservative_lower_mm']=lower
        if lower<1.25-1e-7:
            r175['pending_kernel_key']=key;save175();code,si=owners115[n];rr,tt=transforms175[pi][code][si];s=moving115[n].copy();s.Placement=placement106(rr,tt)*s.Placement
            row=dict(flat_key=k,key=key,bbox_lower_mm=lower,posed_copy_valid=s.isValid(),neutral_volume_mm3=moving115[n].Volume,posed_volume_mm3=s.Volume)
            if not row['posed_copy_valid'] or abs(row['neutral_volume_mm3']-row['posed_volume_mm3'])>max(1e-6,abs(row['neutral_volume_mm3'])*1e-8):row['status']='NEW_RIGID_COPY_INPUT_INTEGRITY_OPEN_NOT_CONTACT'
            else:
                gap,ww,_=fs.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='NEW_G4_MOVING_INTERFACE_SEPARATED125' if gap>=1.25-1e-7 else ('ALLOCATED_STOCK_CAPACITY_MOTION_HOLD_NOT_DELIVERED_CONTACT' if fi>=4 else 'NEW_G4_ACTUAL_MATERIAL_MOVING_INTERFACE_CLEARANCE_HOLD'))
                if gap<1e-7:
                    cc=fs.common(s);row.update(common_valid=cc.isValid(),common_mm3=cc.Volume if cc.isValid() else None)
            r175['new_kernel_rows'].append(row);r175['pending_kernel_key']=None
            if row['status']!='NEW_G4_MOVING_INTERFACE_SEPARATED125':r175['first_falsifier']=row;lastposed175=s;lastfixed175=fs
        r175['cursor']+=1
        if r175['first_falsifier'] or time.monotonic()-st>=seconds:break
    r175['batches'].append(dict(start_cursor=start,end_cursor=r175['cursor'],operation_seconds=time.monotonic()-st,process_cpu_seconds=time.process_time()-cp))
    r175['status']='INDEPENDENT_EXACT_G4_MOTION_FIRST_HOLD' if r175['first_falsifier'] else ('INDEPENDENT_EXACT_G4_MOTION_35_POSES_CLOSED_SCOPED' if r175['cursor']==r175['total'] else 'INDEPENDENT_EXACT_G4_CHANGED_MOTION_PENDING')
    save175();print('INDEPENDENT_G4_MOTION',r175['status'],r175['cursor'],'of',r175['total'],'actual',len(r175['new_kernel_rows']),r175['first_falsifier'],'batch',r175['batches'][-1],flush=True)
print('INDEPENDENT_G4_MOTION_READY',r175['total'],r175['cache_preparation_seconds'],r175['cache_preparation_CPU_seconds'],flush=True)
chunk175(12)
