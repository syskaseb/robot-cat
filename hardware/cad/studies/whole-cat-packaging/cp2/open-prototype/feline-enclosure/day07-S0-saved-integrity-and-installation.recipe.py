import time,json,hashlib,zipfile,os
t60=time.monotonic();c60=time.process_time();reopens60=[]
with zipfile.ZipFile(ar59) as z:
    assert z.testzip() is None
    for g in geometry59:
        raw=z.read(g['entry']);assert hashlib.sha256(raw).hexdigest()==g['sha256']
        q=Part.Shape();q.importBrepFromString(raw.decode());reopens60.append(dict(name=g['name'],valid=q.isValid(),solids=len(q.Solids),volume_mm3=q.Volume,bounds_mm=saved_bounds(q),volume_difference_mm3=q.Volume-g['volume_mm3']))
    reopenedFull60=q
assert all(x['valid'] and x['solids']==1 and abs(x['volume_difference_mm3'])<1e-5 for x in reopens60)
parentcoverage60=[]
for n,s in [('complete_fixture',fixture59),('actual_current_parent',rail56)]:
    missing=s.cut(u59);parentcoverage60.append(dict(name=n,missing_valid=missing.isValid(),missing_mm3=missing.Volume))
insertion60={}
for i,v in enumerate([-19,19]):
    insertion60['M6_'+str(i)+'_20mm_insertion']=lcyl57(0,v,-15.4,3,40).fuse(lcyl57(0,v,4.6,5,26))
context60={n:s for n,s in Current35.items() if n not in excludedTools58};context60['complete_fixture']=fixture59
installrows60=[]
for n,s in insertion60.items():
    assert s.isValid()
    for k,q in context60.items():
        if bbox_lower_bound(s.BoundBox,q.BoundBox)>0:continue
        row=dict(moving=n,other=k,other_valid=q.isValid())
        if q.isValid():
            co=s.common(q);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            row['status']='NO_MATERIAL_INTRUSION' if co.isValid() and abs(co.Volume)<1e-7 else 'INITIAL_HARDWARE_INSERTION_HOLD'
        else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        installrows60.append(row)
toolsmetal60=[]
for n,s in tools57.items():
    for k,q in hardware57.items():
        if bbox_lower_bound(s.BoundBox,q.BoundBox)>0:continue
        co=s.common(q);toolsmetal60.append(dict(tool=n,metal=k,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None))
ar60=OUT/'day07-S0-C1-new-fixing-insertion.breps.zip';assert not ar60.exists();ge60=[]
with zipfile.ZipFile(ar60,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(insertion60.items()):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge60.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge60,scope='Named M6x20 straight insertion at bench before electricalrings/key. ShaftR3 travels20, headR5 travels20. Not fullN08.'),indent=2)+'\n').encode())
r60=dict(id='day07-S0-C1-save-integrity-and-initial-hardware',status='SAVED_FULL_FIXTURE_AND_INITIAL_FIXING_SCOPE_RECEIVED' if all(x['status']=='NO_MATERIAL_INTRUSION' for x in installrows60) and all(x['common_valid'] and abs(x['common_mm3'])<1e-7 for x in toolsmetal60) and all(x['missing_valid'] and abs(x['missing_mm3'])<1e-5 for x in parentcoverage60) else 'INITIAL_FIXING_OR_SAVE_HOLD',recovery_receipt=p59.name,recovery_receipt_sha256=hashlib.sha256(p59.read_bytes()).hexdigest(),new_geometry_reopen_only=reopens60,parent_union_material_coverage=parentcoverage60,initial_insertion=installrows60,tools_versus_full_new_metal=toolsmetal60,assembly_scope='Sourcebenchstage before rings/terminalwashers/nuts andkey. PermanentINOUTstuds andfullothercurrentparts included. Ownfilledbody/neck/recess sourceassumptions not a claim of supplierprecisevoid. Wholecaseinsert/terminalringtool/routinekeyaccess remain distinct globalassembly gates ifnot scoped elsewhere. No virtualdetachingintegralrail.',archive=ar60.name,archive_sha256=hashlib.sha256(ar60.read_bytes()).hexdigest(),geometry=ge60,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t60,process_cpu_seconds=time.process_time()-c60,pid=os.getpid(),session_id=46493)
p60=OUT/'day07-S0-C1-save-integrity-and-initial-hardware.json';assert not p60.exists();p60.write_bytes((json.dumps(r60,ensure_ascii=False,indent=2)+'\n').encode());print('S0_SAVED60',r60['status'],installrows60,toolsmetal60,r60['operation_seconds'],r60['process_cpu_seconds'],hashlib.sha256(p60.read_bytes()).hexdigest(),flush=True)
