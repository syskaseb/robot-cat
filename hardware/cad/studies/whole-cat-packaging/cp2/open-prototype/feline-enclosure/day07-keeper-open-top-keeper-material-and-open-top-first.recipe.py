import time,json,hashlib,zipfile,os
t220=time.monotonic();c220=time.process_time();oldlower220=newframe209;oldupper220=up202
transfermembers220={}
for side in ['South','North']:
    wall=members201['Case'+side+'Wall'];lip=members201['Case'+side+'TopLip']
    wb=wall.BoundBox;top=wall.common(Part.makeBox(100,100,20,A.Vector(0,-70,51.75)))
    arm=top.fuse(lip);assert arm.isValid()
    # The connected tab is EXISTING removable stop material, not added world geometry.
    ab=arm.BoundBox;tab=oldupper220.common(Part.makeBox(.25,ab.YLength,ab.ZLength,A.Vector(57.5,ab.YMin,ab.ZMin)))
    transfermembers220[side+'_complete_lip_and_supported_arm']=arm
    transfermembers220[side+'_existing_upper_joint_tab']=tab
transfer220=fuse181([s for n,s in transfermembers220.items() if 'supported_arm' in n])
lower220=oldlower220.cut(transfer220).removeSplitter();upper220=oldupper220.fuse(transfer220).removeSplitter();assert lower220.isValid() and upper220.isValid()
oldunion220=oldlower220.fuse(oldupper220);newunion220=lower220.fuse(upper220)
lost220=oldunion220.cut(newunion220);added220=newunion220.cut(oldunion220);assert lost220.isValid() and added220.isValid()
members220=[];joints220=[]
for n,s in transfermembers220.items():
    mis=s.cut(upper220);members220.append(dict(member=n,volume_mm3=s.Volume,missing_valid=mis.isValid(),missing_mm3=mis.Volume,bounds_mm=saved_bounds(s)))
for side in ['South','North']:
    arm=transfermembers220[side+'_complete_lip_and_supported_arm'];tab=transfermembers220[side+'_existing_upper_joint_tab'];whole=arm.fuse(tab);co=whole.common(oldupper220);joints220.append(dict(side=side,arm_tab_union_valid=whole.isValid(),arm_tab_solids=len(whole.Solids),existing_upper_positive_joint_mm3=co.Volume,nominal_wall_support_section_mm2=3.125,lip_plus_wall_section_mm2=4.6875,not_strength_qualification=True))
remain220=oldlower220.cut(transfer220);misremain220=remain220.cut(lower220)
first220=None
if lost220.Volume>1e-7 or added220.Volume>1e-7 or misremain220.Volume>1e-7 or any(q['missing_mm3']>1e-7 or not q['missing_valid'] for q in members220) or any(q['existing_upper_positive_joint_mm3']<=1e-7 or q['arm_tab_solids']!=1 for q in joints220):first220=dict(stage='REAL_PARTITION_MEMBER_LOADPATH_OR_OPERATING_IDENTITY',lost_mm3=lost220.Volume,added_mm3=added220.Volume,joints=joints220)
# Actual nominal selected case is rectangular. The following prism is EXACT entire vertical case sweep, not an empty bbox proxy.
drop220=Part.makeBox(19,30,21,A.Vector(38.5,-31.25,44));caseco220=drop220.common(lower220);assert caseco220.isValid()
if first220 is None and caseco220.Volume>1e-7:first220=dict(stage='ACTUAL_OPEN_TOP_CONTINUOUS_CASE_LOWER_ENTRY',common_mm3=caseco220.Volume,vertical_translation_mm=[0,12],no_all_manual_path_impossibility=True)
ar220=OUT/'day07-D5-real-open-top-keeper-material-first-gate.breps.zip';assert not ar220.exists();ge220=[]
with zipfile.ZipFile(ar220,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('NEW_REAL_FIXED_LOWER_WITHOUT_TRANSFERRED_KEEPER',lower220),('NEW_REAL_REMOVABLE_CAPTURE_KEEPER_UPPER',upper220),('EXACT_TRANSFERRED_SUPPORT_AND_LIPS',transfer220),('ACTUAL_NOMINAL_CASE_FULL_VERTICAL_ENTRY12',drop220)]+list(transfermembers220.items())):
        f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat89-first-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();en=str(i)+'.brep';z.writestr(en,raw);ge220.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge220),indent=2)+'\n').encode())
p220=OUT/'day07-D5-real-open-top-keeper-material-first-gate.json';r220=dict(id=p220.stem,status='REAL_KEEPER_PARTITION_AND_OPEN_TOP_CASE_FIRST_HOLD' if first220 else 'REAL_KEEPER_PARTITION_LOAD_AND_OPEN_TOP_CASE_SCOPED_RECEIVED_UPPER_ASSEMBLY_PENDING',operating_union_lost_mm3=lost220.Volume,operating_union_added_mm3=added220.Volume,operating_bounds_before_mm=saved_bounds(oldunion220),operating_bounds_after_mm=saved_bounds(newunion220),retained_lower_material_missing_mm3=misremain220.Volume,member_coverage=members220,positive_actual_upper_joints=joints220,new_lower_solids=len(lower220.Solids),new_upper_solids=len(upper220.Solids),exact_case_vertical_sweep_common_mm3=caseco220.Volume,case_vertical_sweep_mm=[0,12],first_falsifier=first220,archive=ar220.name,archive_sha256=hashlib.sha256(ar220.read_bytes()).hexdigest(),geometry=ge220,selected=False,N01_complete=False,old_negative_counts_preserved=True,actualcut=None,actual_A_U_fit_slack=None,upper_changed_assembly_OPEN=True,operation_seconds=time.monotonic()-t220,process_cpu_seconds=time.process_time()-c220,pid=os.getpid(),session_id=46493);p220.write_bytes((json.dumps(r220,indent=2)+'\n').encode());print('KEEPER220_FIRST',r220['status'],first220,'identity',lost220.Volume,added220.Volume,'joints',joints220,'case',caseco220.Volume,'solids',len(lower220.Solids),len(upper220.Solids),'seconds',r220['operation_seconds'],r220['process_cpu_seconds'],'OWNER89_SAVED_IDLE',os.getpid(),flush=True)
