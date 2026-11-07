import time,json,hashlib,zipfile,os
t221=time.monotonic();c221=time.process_time()
diagnostic221=dict(source=p220.name,source_sha256=hashlib.sha256(p220.read_bytes()).hexdigest(),technical_only=True,not_design_failure=True,invalid_missing_result=not misremain220.isValid(),invalid_missing_result_reported_volume_mm3=misremain220.Volume,raw_cut_volume_mm3=remain220.Volume,removeSplitter_volume_mm3=lower220.Volume,explanation='The extra comparison rawCUT.cut(removeSplitter(CUT)) returned INVALID wholeoperand, not a valid material-loss witness. Do not count invalid result as loss/contact or strategyfailure. Keep raw valid CUT and raw FUSE for SAME intended real partition; no geometry offset/added material/new hypothesis.')
pd221=OUT/'day07-D5-keeper-partition-invalid-comparison-forensic.json';pd221.write_bytes((json.dumps(diagnostic221,indent=2)+'\n').encode())
lower221=remain220;upper221=oldupper220.fuse(transfer220);assert lower221.isValid() and upper221.isValid()
union221=lower221.fuse(upper221);lost221=oldunion220.cut(union221);added221=union221.cut(oldunion220);assert lost221.isValid() and added221.isValid()
first221=None
if lost221.Volume>1e-7 or added221.Volume>1e-7:first221=dict(stage='VALID_ACTUAL_UNION_IDENTITY',lost_mm3=lost221.Volume,added_mm3=added221.Volume)
caseown221=drop220.common(lower221);assert caseown221.isValid()
if first221 is None and caseown221.Volume>1e-7:first221=dict(stage='EXACT_CASE_OPEN_TOP_LOWER',common_mm3=caseown221.Volume)
rows221=[]
if first221 is None:
    # Actual integral bank material is retained throughout, not virtually detached.
    for n in ['Underdeck:RestoredBank','Ref_Material_F_R4_CP2_IN_0_0','Ref_Material_F_R5_CP2_OUT_0_0']:
        s=context210[n];co=drop220.common(s);ga,ww,_=drop220.distToShape(s);row=dict(actor=n,valid_common=co.isValid(),common_mm3=co.Volume,actual_gap_mm=ga,required_foreign_mm=1.25,status='CLEAR' if ga>=1.25-1e-7 else 'ASSEMBLY_DEPENDENCY_HOLD');rows221.append(row)
        if not co.isValid() or ga<1.25-1e-7:first221=dict(stage='OPEN_TOP_CASE_FULL_CURRENT_REQUIRED_NEIGHBOR_OR_LATE_INSTALL_DEPENDENCY',row=row,case_sweep_translation_mm=[0,12],not_all_paths_impossible=True);break
ar221=OUT/'day07-D5-raw-real-partition-current-open-top-first-neighbor.breps.zip';ge221=[];assert not ar221.exists()
with zipfile.ZipFile(ar221,'w',zipfile.ZIP_DEFLATED) as z:
    ss=[('RAW_VALID_NEW_FIXED_LOWER',lower221),('RAW_VALID_NEW_SEPARATE_UPPER',upper221),('EXACT_CASE_VERTICAL_ENTRY12',drop220)]
    if rows221:ss.append((rows221[-1]['actor'],context210[rows221[-1]['actor']]))
    for i,(n,s) in enumerate(ss):
        f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat89-raw-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();en=str(i)+'.brep';z.writestr(en,raw);ge221.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge221),indent=2)+'\n').encode())
p221=OUT/'day07-D5-raw-real-partition-current-open-top-first-neighbor.json';r221=dict(id=p221.stem,status='OPEN_TOP_REAL_PARTITION_FIRST_NEIGHBOR_HOLD' if first221 else 'OPEN_TOP_REAL_PARTITION_REQUIRED_NEIGHBORS_SCOPED_RECEIVED_MORE_ASSEMBLY_PENDING',same_partition_representation_repair=diagnostic221,valid_union_lost_mm3=lost221.Volume,valid_union_added_mm3=added221.Volume,nominal_case_continuous_lower_entry_common_mm3=caseown221.Volume,actual_new_lower_solids=len(lower221.Solids),actual_new_upper_solids=len(upper221.Solids),neighbor_rows=rows221,first_falsifier=first221,archive=ar221.name,archive_sha256=hashlib.sha256(ar221.read_bytes()).hexdigest(),geometry=ge221,new_upper_assembly_OPEN=True,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t221,process_cpu_seconds=time.process_time()-c221,pid=os.getpid(),session_id=46493);p221.write_bytes((json.dumps(r221,indent=2)+'\n').encode());print('KEEPER221_RAW_AND_ENTRY',r221['status'],first221,'union',lost221.Volume,added221.Volume,'caseown',caseown221.Volume,'rows',rows221,'seconds',r221['operation_seconds'],r221['process_cpu_seconds'],'OWNER89_SAVED_IDLE',os.getpid(),flush=True)
