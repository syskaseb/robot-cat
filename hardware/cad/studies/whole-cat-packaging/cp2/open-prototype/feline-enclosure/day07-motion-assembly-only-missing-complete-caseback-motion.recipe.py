import json,time,hashlib,os,zipfile
t215=time.monotonic();c215=time.process_time();assert r213['new_cursor']==1032 and not first213
fixed215=list(newrequired214);nf215=len(fixed215);bounds215=[np.array(saved_bounds(s)) for n,s in fixed215];p215=OUT/'day07-only-missing-complete-caseback-motion-cursor.json';assert not p215.exists()
r215=dict(id=p215.stem,status='ONLY_MISSING_COMPLETE_CASEBACK_MOTION_PENDING',source_effectivity=p214.name,source_effectivity_sha256=hashlib.sha256(p214.read_bytes()).hexdigest(),scope='ONLYwholeNEWuncoveredcurrentcasebackcarrier/upper/lowerjaw/4completeM3metal andanystrictcoveroutside residue. NoFRG22575/oldD27090/G36120/155451548replay.',fixed_actor_order=[n for n,s in fixed215],fixed_complete_bounds_mm=[b.tolist() for b in bounds215],target_actor_order=names175,key_definition='flat=(pose-1)*fixedcount*129+fixedindex*129+targetindex; exactprefix[0,cursor), cursor excludespending untilactuallyreceived.',cursor=0,total=35*nf215*129,conservative_bounds_count=0,new_kernel_rows=[],pending_kernel_key=None,first_falsifier=None,batches=[],selected=False,N01_complete=False,initialassembly_still_OPEN=True,pid=os.getpid(),session_id=46493)
def save215():
    q=p215.with_suffix('.tmp');q.write_bytes((json.dumps(r215,indent=2)+'\n').encode());os.replace(q,p215)
save215()
def chunk215(seconds=10):
    global last215,lastfixed215
    start=r215['cursor'];st=time.monotonic();cp=time.process_time();last215=None;lastfixed215=None
    while r215['cursor']<r215['total'] and not r215['first_falsifier']:
        k=r215['cursor'];pose=k//(nf215*129)+1;fi=(k//129)%nf215;ai=k%129;n=names175[ai];fn,a=fixed215[fi];bb=bounds215[fi];mb=posedbounds175[pose][ai];lo=float(np.linalg.norm(np.maximum(0,np.maximum(bb[0]-mb[1],mb[0]-bb[1]))));key=[pose,fn,n]
        if lo>=1.25-1e-7:r215['conservative_bounds_count']+=1
        else:
            r215['pending_kernel_key']=key;save215();code,si=owners115[n];rr,tt=transforms175[pose][code][si];b=moving115[n].copy();b.Placement=placement106(rr,tt)*b.Placement;v=moving115[n].Volume;row=dict(flat=k,key=key,bounds_lower_mm=lo,posed_valid=b.isValid(),source_volume_mm3=v,posed_volume_mm3=b.Volume)
            if not row['posed_valid'] or abs(v-b.Volume)>max(1e-6,abs(v)*1e-8):row['status']='PROPER_RIGID_SOURCE_INTEGRITY_OPEN_NOT_CONTACT'
            else:
                ga,ww,_=a.distToShape(b);row.update(actual_gap_mm=ga,witnesses=[[list(x),list(y)] for x,y in ww[:1]],status='ONLY_MISSING_CASEBACK_PAIR_SEPARATED125' if ga>=1.25-1e-7 else 'ONLY_MISSING_CASEBACK_ACTUAL_OR_ALLOCATED_HOLD_NOT_DELIVERED_CONTACT')
                if ga<1e-7:
                    co=a.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            r215['new_kernel_rows'].append(row);r215['pending_kernel_key']=None
            if row['status']!='ONLY_MISSING_CASEBACK_PAIR_SEPARATED125':r215['first_falsifier']=row;last215=b;lastfixed215=a
        r215['cursor']+=1
        if r215['first_falsifier'] or time.monotonic()-st>seconds:break
    r215['batches'].append(dict(start_cursor=start,end_cursor=r215['cursor'],operation_seconds=time.monotonic()-st,process_cpu_seconds=time.process_time()-cp));r215['status']='CURRENT_COMPLETE_CASEBACK_MISSING_DELTA_FIRST_FALSIFIER' if r215['first_falsifier'] else ('CURRENT_COMPLETE_CASEBACK_MISSING_DELTA35_CLOSED_SCOPED' if r215['cursor']==r215['total'] else 'CURRENT_COMPLETE_CASEBACK_MISSING_DELTA_SAVED_CURSOR_PENDING');save215();print('CURRENT_COMPLETE_CASEBACK_MISSING_MOTION',r215['status'],r215['cursor'],'of',r215['total'],'exact',len(r215['new_kernel_rows']),'first',r215['first_falsifier'],r215['batches'][-1],flush=True)
chunk215(10)
