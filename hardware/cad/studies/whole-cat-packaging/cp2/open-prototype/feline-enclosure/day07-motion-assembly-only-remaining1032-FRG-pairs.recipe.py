import json,time,hashlib,os,zipfile
t213=time.monotonic();c213=time.process_time();assert row212['status']=='EXACT_NEW_POSE27_FULL_CAPACITY_SEPARATED125'
rows213=[];bounds213=0;cursor213=0;first213=None;posedlast213=None
for pose in range(28,36):
    bb=np.array(saved_bounds(tail208));mb=np.asarray(posedbounds175[pose]);los=np.linalg.norm(np.maximum(0,np.maximum(bb[0]-mb[:,1,:],mb[:,0,:]-bb[1])),axis=1)
    for ai,lo in enumerate(los):
        key=[pose,'FRG_FULL83p3_UNCUT_CAPACITY',names175[ai]]
        if lo>=1.25-1e-7:bounds213+=1
        else:
            n=names175[ai];code,si=owners115[n];rr,tt=transforms175[pose][code][si];s=moving115[n].copy();s.Placement=placement106(rr,tt)*s.Placement;v=moving115[n].Volume;row=dict(key=key,bounds_lower_mm=float(lo),source_volume_mm3=v,posed_volume_mm3=s.Volume,posed_valid=s.isValid())
            if not row['posed_valid'] or abs(v-s.Volume)>max(1e-6,abs(v)*1e-8):row['status']='PROPER_RIGID_INPUT_INTEGRITY_OPEN_NOT_CONTACT'
            else:
                ga,ww,_=tail208.distToShape(s);row.update(actual_gap_mm=ga,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='NEW_REMAINING_FRG_PAIR_SEPARATED125' if ga>=1.25-1e-7 else 'NEW_REMAINING_FRG_ALLOCATED_STOCK_HOLD_NOT_DELIVERED_CONTACT')
                if ga<1e-7:
                    co=tail208.common(s);row.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
            rows213.append(row);posedlast213=s
            if row['status']!='NEW_REMAINING_FRG_PAIR_SEPARATED125':first213=row
        cursor213+=1
        if first213 or time.monotonic()-t213>10:break
    if first213 or time.monotonic()-t213>10:break
ar213=OUT/'day07-FRG-only-remaining-motion-received-witness.breps.zip';assert not ar213.exists();ge213=[]
with zipfile.ZipFile(ar213,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('FULL83p3_CAPACITY',tail208)]+([('LAST_ACTUAL_PROPER_RIGID_TARGET',posedlast213)] if posedlast213 is not None else [])):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge213.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge213),indent=2))
p213=OUT/'day07-FRG-only-remaining1032-motion-receipt.json';assert not p213.exists();r213=dict(id=p213.stem,status='FRG_FIVE_CHANGED_FIELDS_MOTION35_CLOSED_SCOPED' if cursor213==1032 and not first213 else 'FRG_REMAINING_MOTION_FIRST_HOLD' if first213 else 'FRG_REMAINING_MOTION_SAVED_CURSOR_PENDING',previous_bounds_pairs_reused=21542,previous_one_exact_pair=p212.name,previous_one_exact_sha256=hashlib.sha256(p212.read_bytes()).hexdigest(),remaining_flat_definition='flat=(pose-28)*129+moving_index, expected0..1031; old21542+onepose27 notrerun',new_cursor=cursor213,new_total=1032,new_bounds_separated=bounds213,new_kernel_rows=rows213,new_unreceived=1032-cursor213,first_falsifier=first213,combined_total_qualified=21543+cursor213 if not first213 else None,caseback_complete_D5_effectivity_still_separate_OPEN=True,selected=False,N01_complete=False,actualcut=None,archive=ar213.name,archive_sha256=hashlib.sha256(ar213.read_bytes()).hexdigest(),geometry=ge213,operation_seconds=time.monotonic()-t213,process_cpu_seconds=time.process_time()-c213,pid=os.getpid(),session_id=46493);p213.write_bytes((json.dumps(r213,indent=2)+'\n').encode());print('FRG_ONLY_REMAINING',r213['status'],cursor213,'of1032','newexact',len(rows213),'first',first213,'combined',r213['combined_total_qualified'],'wall',r213['operation_seconds'],'CPU',r213['process_cpu_seconds'],hashlib.sha256(p213.read_bytes()).hexdigest(),flush=True)
