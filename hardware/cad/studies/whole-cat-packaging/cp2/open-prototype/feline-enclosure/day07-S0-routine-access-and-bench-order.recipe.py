import time,json,hashlib,zipfile,os
t68=time.monotonic();c68=time.process_time()
# Source permits benchS0 before head/looms. Deferredactualheadassembly only; noP0/rail/integralprint disappears.
headlate68={n for n in context64 if n.startswith('Ref_Material_head_0_0_')};later68=[];benchrows68=[]
for n,k in case_tasks65[len(case_rows65):]:
    if k in headlate68:later68.append(dict(moving=n,other=k,classification='Actualselectedheadassemblyinstalledlater perselectedS0beforeheadsource; head-after-S0accessnotclaimedbythiscaseinsertionproof.'));continue
    q=context64[k];s=delta65[n];row=dict(moving=n,other=k,other_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=s.common(q);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        row['status']='SEPARATED125' if gap>=1.25-1e-7 else 'PREHEAD_CASE_APPROACH_HOLD'
    else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    benchrows68.append(row);print('CASE_ORDER68',row,flush=True)
    if row['status']!='SEPARATED125' or time.monotonic()-t68>12:break
caseprocessed68=len(case_rows65)+len(later68)+len(benchrows68)
tip68=max([f.CenterOfMass for f in key62.Faces if type(f.Surface).__name__=='Plane'],key=lambda p:(np.array(list(p))-C56)@out56)
top68=BodyOuter31.BoundBox.ZMax;access68=Part.makeCylinder(15,top68+3.25-tip68.z,A.Vector(tip68.x,tip68.y,tip68.z),A.Vector(0,0,1));assert access68.isValid()
accesscontext68={n:s for n,s in effective62.items() if n!='Ref_Material_S0_key_CP2_0_0'};tasks68=[n for n,s in accesscontext68.items() if bbox_lower_bound(access68.BoundBox,s.BoundBox)<=1.25];accessrows68=[]
for n in tasks68:
    q=accesscontext68[n];r=dict(other=n,other_valid=q.isValid())
    if q.isValid():
        gap,w,_=access68.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=access68.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        r['status']='PROPOSED_SOURCE_R15_ROUTINE_APPROACH_SEPARATED125' if gap>=1.25-1e-7 else 'ROUTINE_APPROACH_ALLOCATED_REGION_HOLD_NOT_KEY_OR_HAND_CONTACT'
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    accessrows68.append(r);print('KEY_OPERATION68',r,flush=True)
    if r['status']!='PROPOSED_SOURCE_R15_ROUTINE_APPROACH_SEPARATED125' or time.monotonic()-t68>20:break
ar68=OUT/'day07-S0-routine-access-and-prehead-case-order.breps.zip';assert not ar68.exists();ge68=[]
with zipfile.ZipFile(ar68,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('S0:proposed_source_R15_upper_operator_entry',access68)]+[(n,accesscontext68[n]) for n in sorted({r['other'] for r in accessrows68})]+[(k,context64[k]) for k in sorted({r['other'] for r in benchrows68})]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge68.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge68,scope='Oneconcreteoperatorentry hypothesis usingunchangedsourceR15 capacity atactualkeytip. Envelope not physicalfinger/toolmeasurement.'),indent=2)+'\n').encode())
r68=dict(id='day07-S0-routine-access-and-prehead-case-order',status='S0_ROUTINE_APPROACH_FIRST_FALSIFIER_HOLD' if any(r['status']!='PROPOSED_SOURCE_R15_ROUTINE_APPROACH_SEPARATED125' for r in accessrows68) else 'S0_PROPOSED_OPERATOR_APPROACH_LOCAL_SCOPE_RECEIVED_SHELL_INTERFACE_OPEN',case_order=dict(source='tools/cad/check_phase1_source_hardware.py selectedS0benchbeforehead/looms; source_switch_selected_interface beforeP0BUS/covers',deferred_actual_head_count=len(headlate68),deferred_names=sorted(headlate68),raw_received_bridge_family_common_mm3=122.21901388949941,raw_first2_reused_no_replay=True,remaining_rows=benchrows68,deferred_pair_dispositions=later68,cursor=caseprocessed68,total=len(case_tasks65),unreceived=len(case_tasks65)-caseprocessed68,head_install_afterS0_access_globalOPEN=True,integralrail_never_detached=True),routine_key_proposal=dict(source_key_tip_actual_mm=list(tip68),source_retained_key_and_tool_radius_mm=15,entry='Oneproposedverticaloperatoraccess fromactualkeytiptoopenupperBodyOuterplane112+3.25. Requires explicitE6upperopening/coverhandling, not inheritedloweraperture/inplacefeature. No newdoor/print built.',body_outer_top_z_mm=top68,entry_radius_mm=15,actual_hand_dimension_claim=False,full_source_key_region_kept=True,rows=accessrows68,cursor=len(accessrows68),total=len(tasks68),unreceived=len(tasks68)-len(accessrows68),scope='HOLDinvalidatesthisallocatedentryonly, notactualkeycontact or impossibilityallhandaccess. No thirdsupport/PCB/columnposeoffset. NeedcausalcombinedS0operatorportal/Picarrierassemblyinterface ifblocked; cancontinueindependentV3/R6scopewithoutwaiver.'),archive=ar68.name,archive_sha256=hashlib.sha256(ar68.read_bytes()).hexdigest(),geometry=ge68,operation_seconds=time.monotonic()-t68,process_cpu_seconds=time.process_time()-c68,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p68=OUT/'day07-S0-routine-access-and-prehead-case-order.json';assert not p68.exists();p68.write_bytes((json.dumps(r68,ensure_ascii=False,indent=2)+'\n').encode());print('S0_ROUTINE_FINAL68',r68['status'],r68['case_order']['cursor'],r68['case_order']['total'],accessrows68,r68['operation_seconds'],r68['process_cpu_seconds'],hashlib.sha256(p68.read_bytes()).hexdigest(),flush=True)
