import time,json,hashlib,zipfile,os,traceback
t59=time.monotonic();c59=time.process_time()
pieces59=[(n,globals()[n].copy()) for n in ['topfoot58','sidefoot58','bridge58','leg58','panel57']]
steps59=[];fixture59=pieces59[0][1].copy();build59=True
for n,s in pieces59[1:]:
    old=fixture59.copy();joined=old.fuse(s)
    lostold=old.cut(joined);lostnew=s.cut(joined)
    step=dict(added=n,valid=joined.isValid(),solids=len(joined.Solids),volume_mm3=joined.Volume,bounds_mm=saved_bounds(joined),old_missing_valid=lostold.isValid(),new_missing_valid=lostnew.isValid(),old_missing_mm3=lostold.Volume,new_missing_mm3=lostnew.Volume)
    steps59.append(step);print('S0_SEQUENTIAL_STEP',step,flush=True)
    if not(joined.isValid() and len(joined.Solids)==1 and lostold.isValid() and lostnew.isValid() and abs(lostold.Volume)<1e-5 and abs(lostnew.Volume)<1e-5):
        build59=False;break
    fixture59=joined
coverage59=[]
if build59:
    for n,s in pieces59:
        missing=s.cut(fixture59);coverage59.append(dict(member=n,source_volume_mm3=s.Volume,missing_valid=missing.isValid(),missing_mm3=missing.Volume))
    build59=all(x['missing_valid'] and abs(x['missing_mm3'])<1e-5 for x in coverage59)
result59=dict(id='day07-S0-C1-same-geometry-union-integrity-recovery',status='FULL_FIXTURE_BUILD_INTEGRITY_HOLD',supersedes_invalid_whole_mount_claim='day07-S0-current-mounted-case-correction1-receipt.json',invalid_receipt_sha256=hashlib.sha256(p58.read_bytes()).hexdigest(),invalid_archive_sha256=hashlib.sha256(ar58.read_bytes()).hexdigest(),defect='multiFuse returned only rootfoot82.87633661995892mm3, omitting intended bridge/leg/panel. isValid+1solid did not demonstrate member coverage. Prior wholeforeign/tool/outline conclusions invalid.',same_geometry_no_C2=True,steps=steps59,coverage=coverage59,complete_fixture_verified=build59,rows=[],tools=[],own_hardware=[],outline=None,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
if build59:
    root59=fixture59.common(rail56);u59=fixture59.fuse(rail56)
    result59['root']=dict(common_valid=root59.isValid(),common_mm3=root59.Volume,parent_union_valid=u59.isValid(),parent_union_solids=len(u59.Solids),source_parent_solids=len(rail56.Solids))
    tasks59=[n for n,q in foreign57.items() if bbox_lower_bound(fixture59.BoundBox,q.BoundBox)<=1.25]
    result59['foreign_total']=len(tasks59)
    for n in tasks59:
        q=foreign57[n];row=dict(other=n,other_valid=q.isValid())
        if q.isValid():
            gap,w,_=fixture59.distToShape(q);row.update(gap_mm=gap,required_mm=1.25,witnesses=[[list(a),list(b)] for a,b in w[:1]])
            if gap<1e-7:
                co=fixture59.common(q);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            row['status']='SEPARATED125' if gap>=1.25-1e-7 else 'FULL_CORRECTED_FIXTURE_FOREIGN_HOLD'
        else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        result59['rows'].append(row);print('S0_FULL_FOREIGN',row,flush=True)
        if row['status']!='SEPARATED125':break
    result59['foreign_unreceived']=len(tasks59)-len(result59['rows'])
    for n,s in hardware57.items():
        co=fixture59.common(s);result59['own_hardware'].append(dict(name=n,common_valid=co.isValid(),material_intrusion_mm3=co.Volume if co.isValid() else None))
    # Other unchanged1292/tool pairs retain the old complete-context screening; only the corrected newprint changed.
    for n,s in tools57.items():
        co=s.common(fixture59);result59['tools'].append(dict(tool=n,other='complete_corrected_fixture',common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None))
    outside=fixture59.cut(BodyOuter31);result59['outline']=dict(outside_valid=outside.isValid(),outside_mm3=outside.Volume,boundary_gap_mm=fixture59.distToShape(boundary56)[0],required_mm=3.25)
    result59['status']='FULL_FIXTURE_RECONSTRUCTED_LOCAL_GATES_RECEIVED' if (all(x['status']=='SEPARATED125' for x in result59['rows']) and result59['foreign_unreceived']==0 and all(x['common_valid'] and abs(x['material_intrusion_mm3'])<1e-7 for x in result59['own_hardware']) and all(x['common_valid'] and abs(x['common_mm3'])<1e-7 for x in result59['tools']) and outside.isValid() and outside.Volume<1e-7 and result59['outline']['boundary_gap_mm']>=3.25 and root59.isValid() and root59.Volume>0 and u59.isValid() and len(u59.Solids)==len(rail56.Solids)) else 'FULL_CORRECTED_FIXTURE_LOCAL_HOLD'
ar59=OUT/'day07-S0-C1-union-integrity-recovery.breps.zip';assert not ar59.exists()
geometry59=[]
with zipfile.ZipFile(ar59,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(pieces59+[('recovered_complete_fixture' if build59 else 'recovery_stopped_partial',fixture59)]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);geometry59.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=geometry59,same_candidate_geometry=True,complete_fixture_verified=build59),indent=2)+'\n').encode())
result59.update(archive=ar59.name,archive_sha256=hashlib.sha256(ar59.read_bytes()).hexdigest(),geometry=geometry59,operation_seconds=time.monotonic()-t59,process_cpu_seconds=time.process_time()-c59,source_reuse='11sourcecontours/frame/8unchangedmetalforeign+outline; no replay. C0W0775.280364 retained. C1 prior rootonly conclusions superseded. ActualCurrent1292 unchanged.',remaining='GlobalS0keyaccess/sourceleadlengthslack/changedmotion/wholeassembly plus V3/R6/invalid3/headNorth/123246 remain OPEN; no wholeN01 claim.')
p59=OUT/'day07-S0-C1-union-integrity-recovery-receipt.json';assert not p59.exists();p59.write_bytes((json.dumps(result59,ensure_ascii=False,indent=2)+'\n').encode())
print('S0_INTEGRITY_FINAL',result59['status'],result59['complete_fixture_verified'],result59['operation_seconds'],result59['process_cpu_seconds'],hashlib.sha256(p59.read_bytes()).hexdigest(),flush=True)
