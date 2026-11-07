import time,json,hashlib,zipfile,os
t62=time.monotonic();c62=time.process_time();restorepins62=[]
def pinned62(archive,g):
    ar=OUT/archive
    with zipfile.ZipFile(ar) as z:raw=z.read(g['entry'])
    assert hashlib.sha256(raw).hexdigest()==g['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());restorepins62.append(dict(archive=archive,archive_sha256=hashlib.sha256(ar.read_bytes()).hexdigest(),entry=g['entry'],sha256=g['sha256'],name=g['name']));return s
pi62=json.loads((OUT/'day07-removable-Pi-carrier-current-candidate-composition.json').read_bytes());mod62=json.loads((OUT/'day07-MODULE-V3-capacity-current-candidate-composition.json').read_bytes())
effective62=dict(Current35);effective62['CurrentFoundation:FoundationRail:-1']=u59
effective62['Flat:MODULE:5']=pinned62(mod62['scoped_region_override']['new_archive'],mod62['scoped_region_override']['new_geometry'])
for n in pi62['retained_source_cells']:effective62['CandidateWest:'+n]=W37parts[n]
for g in pi62['replacement_geometry']:effective62['CandidatePi:'+g['name']]=pinned62(pi62['replacement_archive'],g)
for g in pi62['selected_candidate_retention_geometry']:
    if g['name'].endswith(':head_budget'):continue
    effective62['CandidatePi:'+g['name']]=pinned62(pi62['replacement_archive'],g)
for g in mod62['new_structural_tie_binding']['head_overrides']:effective62['CandidatePi:'+g['name']]=pinned62(mod62['new_structural_tie_binding']['head_override_archive'],g)
effective62.update(hardware57)
key62=Current35['Ref_Material_S0_key_CP2_0_0'];keycontext62={n:s for n,s in effective62.items() if n not in s0names56}
task62=[n for n,s in keycontext62.items() if bbox_lower_bound(key62.BoundBox,s.BoundBox)<=1.25]
rows62=[]
for n in task62:
    s=keycontext62[n];row=dict(source='S0:key_family_and_tool_reservation',other=n,other_valid=s.isValid(),required_mm=1.25)
    if s.isValid():
        gap,w,_=key62.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=key62.common(s);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        row['status']='SOURCE_KEY_TOOL_REGION_SEPARATED125' if gap>=1.25-1e-7 else 'REQUIRED_KEY_TOOL_ALLOCATION_HOLD_NOT_EXACT_KEY_CONTACT'
    else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows62.append(row);print('S0_KEY_GATE62',row,flush=True)
    if row['status']!='SOURCE_KEY_TOOL_REGION_SEPARATED125':break
ar62=OUT/'day07-S0-key-actual-candidate-first-gate.breps.zip';assert not ar62.exists();ge62=[]
with zipfile.ZipFile(ar62,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('S0:key_family_and_tool_reservation',key62)]+[(r['other'],keycontext62[r['other']]) for r in rows62]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge62.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge62,scope='First missing S0 routine key source allocation against actualcandidate overlays. No newgeometry variant or oldproof replay.'),indent=2)+'\n').encode())
r62=dict(id='day07-S0-required-key-actual-candidate-first-gate',status='SOURCE_KEY_TOOL_REGION_STATIC_SCOPE_RECEIVED_ACCESS_PATH_OPEN' if all(r['status']=='SOURCE_KEY_TOOL_REGION_SEPARATED125' for r in rows62) else 'S0_REQUIRED_KEY_ALLOCATION_FIRST_FALSIFIER_HOLD',rows=rows62,total=len(task62),cursor=len(rows62),unreceived=len(task62)-len(rows62),effective_candidate_actor_count=len(effective62),source_current1292_unchanged=True,replaced_not_duplicate_parent=True,old_two_W37_cells_not_added=True,geometry_restoration_pins=restorepins62,source_function='Selected source source_switch_layout_r6.py: S0_key_family_tool_reserve cylinderR15x63.5. Requirement key operation retained; reserve overlap is NOT deliveredphysicalkeycontact proof. No keyretirement/shrink/poseoffset.',scope='Complete current1292 with currentS0parent replacement plus receivedMODULE5 override/retained5Westcells/removablePi2cells/bands2/heads2/8casefixings. Newretentionresidualcapacity not an extra installedunit; actual100 lifecycle in receivedsourcebinding. Body/neck/terminalownfamily excludedfromkeyforeignrule only, not unrelatedparts.',archive=ar62.name,archive_sha256=hashlib.sha256(ar62.read_bytes()).hexdigest(),geometry=ge62,operation_seconds=time.monotonic()-t62,process_cpu_seconds=time.process_time()-c62,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p62=OUT/'day07-S0-required-key-actual-candidate-first-gate.json';assert not p62.exists();p62.write_bytes((json.dumps(r62,ensure_ascii=False,indent=2)+'\n').encode());print('S0_KEY_FINAL62',r62['status'],r62['cursor'],r62['total'],r62['operation_seconds'],r62['process_cpu_seconds'],hashlib.sha256(p62.read_bytes()).hexdigest(),flush=True)
