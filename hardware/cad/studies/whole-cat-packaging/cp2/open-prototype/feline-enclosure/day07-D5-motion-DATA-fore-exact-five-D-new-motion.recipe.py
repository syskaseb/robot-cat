import json,time,hashlib,os
t187=time.monotonic();c187=time.process_time()
fixed187=[('NEW_D5_POSITIVE_PRIMARY_DELTA',newdelta184),('NEW_D5_REMOVABLE_UPPER',up181),('NEW_D5_FULL_PRESSURE_LOOP',band181),('NEW_D5_FULL_PRESSURE_HEAD',head181),('NEW_D5_WHOLE_UNCUT_NECK_CAPACITY',neck181),('NEW_D5_WHOLE_REMAINING_TAIL_CAPACITY',tailfield181)];nf187=len(fixed187);na187=len(names175);assert (nf187,na187)==(6,129)
bounds187=[]
for fi,(n,s) in enumerate(fixed187):
    b=np.array(saved_bounds(s))
    if fi in [0,1]:
        extra=np.array([[57.75-3.55,-25.75-3.12524153947005-3.55,48.5-3.55],[65.98036180850077+3.55,-6.75+3.55,48.5+3.55]])
        if fi==0:wb=np.array(saved_bounds(base181));extra=np.array([np.minimum(extra[0],wb[0]),np.maximum(extra[1],wb[1])])
        b=np.array([np.minimum(b[0],extra[0]),np.maximum(b[1],extra[1])])
    if fi==4:
        P=np.array(neckP181);extra=np.array([[P[0]-1,P[1],P[2]-1.65],[P[0]+3,P[1]+4,P[2]+1.65]]);b=np.array([np.minimum(b[0],extra[0]),np.maximum(b[1],extra[1])])
    bounds187.append(b)
p187=OUT/'day07-five-D-south-exact-new-motion-cursor.json';assert not p187.exists()
r187=dict(id=p187.stem,status='EXACT_FIVE_D_NEW_MOTION_PENDING',source_static='day07-five-D-south-launch-common-load-and-stock-bounded-disposition.json',source_static_sha256=hashlib.sha256((OUT/'day07-five-D-south-launch-common-load-and-stock-bounded-disposition.json').read_bytes()).hexdigest(),effectivity='day07-five-D-south-launch-proposed-actor-effectivity.json',effectivity_sha256=hashlib.sha256((OUT/'day07-five-D-south-launch-proposed-actor-effectivity.json').read_bytes()).hexdigest(),scope='ONLYnewDpositiveprimary/upper/wholeloop-head/fulltail-neck versusSAMEfrozenposed108+21 poses1..35. Reusepreviousnumericproperrigidtransform cache ONLY, notanyGmotionpairs/neutralstatic. No currentactorselection/oldparentduplication.',fixed_actor_order=[n for n,s in fixed187],fixed_conservative_bounds_mm=[b.tolist() for b in bounds187],moving_actor_order=names175,moving_owners={n:list(owners115[n]) for n in names175},key_definition='flat=(pose-1)*6*129+fixed_index*129+moving_index; key=[pose,fixed_actor_order[fixed_index],moving_actor_order[moving_index]]. Exactreceivedprefix[0,cursor), newkernelkeys explicitlystored.',required_pose_indices=list(range(1,36)),cursor=0,total=35*6*129,checked_exact_key_ranges=[],new_kernel_rows=[],pending_kernel_key=None,first_falsifier=None,batches=[],selected=False,N01_complete=False,legacyPad_halfmm_GLOBAL_OPEN=True,whole_SOURCE_freefan_NOT_qualified=True,pid=os.getpid(),session_id=46493)
def save187():
    r187['checked_exact_key_ranges']=[[0,r187['cursor']-1]] if r187['cursor'] else [];q=p187.with_suffix('.tmp');q.write_bytes((json.dumps(r187,indent=2)+'\n').encode());os.replace(q,p187)
save187()
def chunk187(seconds=12):
    global last187,lastfixed187
    assert not r187['first_falsifier'];st=time.monotonic();cp=time.process_time();start=r187['cursor'];last187=None;lastfixed187=None
    while r187['cursor']<r187['total']:
        k=r187['cursor'];pi=k//(nf187*na187)+1;fi=(k//na187)%nf187;ai=k%na187;n=names175[ai];fn,fs=fixed187[fi];fb=bounds187[fi];mb=posedbounds175[pi][ai];lo=float(np.linalg.norm(np.maximum(np.maximum(fb[0]-mb[1],mb[0]-fb[1]),0)));key=[pi,fn,n]
        if lo<1.25-1e-7:
            r187['pending_kernel_key']=key;save187();code,si=owners115[n];rr,tt=transforms175[pi][code][si];s=moving115[n].copy();s.Placement=placement106(rr,tt)*s.Placement;v0=moving115[n].Volume;row=dict(flat_key=k,key=key,bbox_lower_mm=lo,posed_valid=s.isValid(),source_volume_mm3=v0,posed_volume_mm3=s.Volume)
            if not row['posed_valid'] or abs(v0-s.Volume)>max(1e-6,abs(v0)*1e-8):row['status']='NEW_POSED_INPUT_INTEGRITY_OPEN_NOT_CONTACT'
            else:
                ga,ww,_=fs.distToShape(s);row.update(gap_mm=ga,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='NEW_D_MOVING_INTERFACE_SEPARATED125' if ga>=1.25-1e-7 else 'NEW_D_ALLOCATED_OR_PRINT_MOVING_INTERFACE_HOLD_NOT_DELIVERED_CONTACT')
                if ga<1e-7:
                    co=fs.common(s);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            r187['new_kernel_rows'].append(row);r187['pending_kernel_key']=None
            if row['status']!='NEW_D_MOVING_INTERFACE_SEPARATED125':r187['first_falsifier']=row;last187=s;lastfixed187=fs
        r187['cursor']+=1
        if r187['first_falsifier'] or time.monotonic()-st>=seconds:break
    r187['batches'].append(dict(start_cursor=start,end_cursor=r187['cursor'],operation_seconds=time.monotonic()-st,process_cpu_seconds=time.process_time()-cp));r187['status']='EXACT_FIVE_D_NEW_MOTION_FIRST_HOLD' if r187['first_falsifier'] else ('EXACT_FIVE_D_NEW_MOTION_35_CLOSED_SCOPED' if r187['cursor']==r187['total'] else 'EXACT_FIVE_D_NEW_MOTION_PENDING');save187();print('EXACT_FIVE_D_MOTION',r187['status'],r187['cursor'],'of',r187['total'],'exact',len(r187['new_kernel_rows']),r187['first_falsifier'],r187['batches'][-1],flush=True)
print('EXACT_FIVE_D_MOTION_READY',r187['total'],time.monotonic()-t187,time.process_time()-c187,flush=True)
chunk187(12)
