import json,time,hashlib,os,zipfile
t214=time.monotonic();c214=time.process_time();oldmotion214=json.loads(p187.read_bytes());assert oldmotion214['cursor']==oldmotion214['total']==27090 and not oldmotion214['first_falsifier']
sourceframe214=json.loads(p204.read_bytes());archpin214=sourceframe214['geometry'][0];actualsha214=hashlib.sha256(frame204.exportBrepToString().encode()).hexdigest()
parentbind214=dict(actual_variable='frame204',source_receipt=p204.name,source_receipt_sha256=hashlib.sha256(p204.read_bytes()).hexdigest(),source_archive=sourceframe214['archive'],source_archive_sha256=sourceframe214['archive_sha256'],source_entry=archpin214['entry'],source_member_sha256=archpin214['sha256'],current_native_serialization_sha256=actualsha214,byte_identity=actualsha214==archpin214['sha256'],construction='robot-cat85-shared-root-function-and-last-pairs.py: frame204=wholeframe203.multiFuse(actualcurrentSharedbase+FRG/P_AUXroots); wholeframe203=base201+currentRail+Flange; base201 containsNEWcasebackdeck/seat/neck/casecapture. NOTacceptedoldf08cover/sourcebase1292.',explicit_rootparent_casebacknewmaterial_motion_was_OPEN=True)
missing214=[('CURRENT_D5_CASEBACK_POSITIVE_CARRIER_MATERIAL',newdelta201.common(newframe209)),('CURRENT_D5_CASE_CAPTURE_ADDED_UPPER',up202.cut(up193)),('CURRENT_D5_RELOCATED_LOWER_JAW',kit199['LowerJaw']),*[(f'CURRENT_D5_RELOCATED_FULL_{n}',kit199['Hardware:'+n]) for n in ['Screw','Nut','TopWasher','BottomWasher']]]
oldcoverage214=[]
for label,s,fi in [('UNCHANGED_C1_BASE',base193,0),('UNCHANGED_C1_UPPER',up193,1)]:
    extra=s.cut(box153(bounds187[fi]));row=dict(current_part=label,accepted_cover_actor=fixed187[fi][0],source_current_oldgeometry_subset_receipt=p193.name,source_current_oldgeometry_subset_sha256=hashlib.sha256(p193.read_bytes()).hexdigest(),outside_accepted_BOX_valid=extra.isValid(),outside_accepted_BOX_mm3=extra.Volume if extra.isValid() else None,scope='StrictactualmaterialcontainedinALREADYaccepted27090conservativecover; no oldpairreplay');oldcoverage214.append(row)
    if not extra.isValid():raise RuntimeError('Coverageinput invalid')
    if extra.Volume>1e-7:missing214.append((label+'_ONLY_UNPROVEN_OUTSIDE_ACCEPTED_COVER',extra))
stockproof214=[]
for i,s in enumerate([band181,head181,neck181,tailfield181],2):
    b=np.array(saved_bounds(s));contained=bool(np.all(b[0]>=bounds187[i][0]-1e-7) and np.all(b[1]<=bounds187[i][1]+1e-7));stockproof214.append(dict(name=fixed187[i][0],same_native_shape=s.isSame(fixed187[i][1]),fullbounds_contained=contained,accepted_source_receipt=p187.name,accepted_source_sha256=hashlib.sha256(p187.read_bytes()).hexdigest(),no_pairreplay=True))
    assert stockproof214[-1]['same_native_shape'] and contained
partrows214=[]
for n,s in missing214:
    bb=np.array(saved_bounds(s));coveredby=[fixed187[i][0] for i,b in enumerate(bounds187) if np.all(bb[0]>=b[0]-1e-7) and np.all(bb[1]<=b[1]+1e-7)]
    partrows214.append(dict(name=n,valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=bb.tolist(),strict_whole_BBOX_covered_by_old_fields=coveredby,reason='EntirecurrentNEWcasebackload material/upper/jaw/selectedsteel wasabsentoldf08cover; notjustFRGnewdelta209 overunqualifiedframe204.'))
    assert s.isValid()
newrequired214=[(n,s) for (n,s),r in zip(missing214,partrows214) if not r['strict_whole_BBOX_covered_by_old_fields']]
ar214=OUT/'day07-current-caseback-complete-missing-motion-inputs.breps.zip';assert not ar214.exists();ge214=[]
with zipfile.ZipFile(ar214,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(newrequired214):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge214.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge214),indent=2))
p214=OUT/'day07-current-caseback-complete-motion-effectivity-guard.json';assert not p214.exists()
r214=dict(id=p214.stem,status='CURRENT_FRG_NOT_WHOLE_CASEBACK_GUARD_MISSING_FIELDS_EXPLICIT',frame204_binding=parentbind214,accepted_old_motion_receipt=p187.name,accepted_old_motion_sha256=hashlib.sha256(p187.read_bytes()).hexdigest(),accepted_old27090_not_replayed=True,current_C1_material_actual_strict_covered=oldcoverage214,unchanged_whole_D5_stock_identity_cover=stockproof214,ALL_newcaseback_effectivity_parts=partrows214,ONLY_missing_newfixed_actor_order=[n for n,s in newrequired214],missing_fixed_count=len(newrequired214),required_new_delta_pairs=len(newrequired214)*129*35,current_FRG22575_scope=p213.name,current_FRG22575_sha256=hashlib.sha256(p213.read_bytes()).hexdigest(),D5_case_and_five_ports_held9_and_all_steel_count_preserved=True,no_original_global_matrix_replay=True,assembly_static_lowerjaw_tool_case_pending=True,selected=False,N01_complete=False,actualcut=None,archive=ar214.name,archive_sha256=hashlib.sha256(ar214.read_bytes()).hexdigest(),geometry=ge214,operation_seconds=time.monotonic()-t214,process_cpu_seconds=time.process_time()-c214,pid=os.getpid(),session_id=46493)
p214.write_bytes((json.dumps(r214,indent=2)+'\n').encode());print('CURRENT_COMPLETE_EFFECTIVITY',parentbind214['byte_identity'],'strictold',oldcoverage214,'missing',len(newrequired214),[n for n,s in newrequired214],'pairs',r214['required_new_delta_pairs'],'wall',r214['operation_seconds'],'CPU',r214['process_cpu_seconds'],hashlib.sha256(p214.read_bytes()).hexdigest(),flush=True)
