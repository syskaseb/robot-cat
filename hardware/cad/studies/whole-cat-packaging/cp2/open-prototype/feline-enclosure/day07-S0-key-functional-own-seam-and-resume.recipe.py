import time,json,hashlib,zipfile,os
t63=time.monotonic();c63=time.process_time()
panelcontact63=key62.common(panel57);restprint63=u59.cut(panel57);restgap63=key62.distToShape(restprint63)[0]
contact63=key62.common(u59);ncoords63=[(np.array(list(v.Point))-C56)@out56 for v in contact63.Vertexes]
ownseam63=dict(raw_receipt=p62.name,raw_sha256=hashlib.sha256(p62.read_bytes()).hexdigest(),raw_HOLD_preserved=True,whole_mount_common_valid=contact63.isValid(),whole_mount_common_mm3=contact63.Volume,panel_contact_valid=panelcontact63.isValid(),panel_contact_mm3=panelcontact63.Volume,contact_local_n_extent_mm=[min(ncoords63),max(ncoords63)] if ncoords63 else None,panel_outer_plane_n_mm=3,rest_rail_and_strut_valid=restprint63.isValid(),rest_rail_and_strut_gap_mm=restgap63,classification='NamedownS0mount/key-base plane n3, zeromaterialintrusion; panelendsat3/keyfamilybeginsat3. Actualremainingfullrail/strut separated>=1.25. Not blanketwholeframeownership. Exactkeyrecess/handle geometry remainsphase2sourceassumption.')
assert contact63.isValid() and abs(contact63.Volume)<1e-7 and panelcontact63.isValid() and abs(panelcontact63.Volume)<1e-7 and restprint63.isValid() and restgap63>=1.25 and (not ncoords63 or max(abs(n-3) for n in ncoords63)<1e-5)
continuation63=[];ownhardwarekey63=[]
for n in task62[len(rows62):]:
    s=keycontext62[n];row=dict(other=n,other_valid=s.isValid())
    if s.isValid():
        gap,w,_=key62.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=key62.common(s);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        if n in hardware57:
            row['classification']='OwnpublishedS0casefixing vs filledkey/toolfamily; materialtypeactualbolt vsconservativekeyreserve. Rawoverlap notactualdeliveredkeycontact; exactkeyshape/casefixingrecess phase2fitcondition, not foreign1.25waiver.';ownhardwarekey63.append(row);continue
        row['status']='SEPARATED125' if gap>=1.25-1e-7 else 'FOREIGN_KEY_TOOL_ALLOCATION_HOLD_NOT_EXACT_KEY_CONTACT'
    else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    continuation63.append(row);print('KEY_REMAIN63',row,flush=True)
    if row['status']!='SEPARATED125':break
processed63=len(rows62)+len(continuation63)+len(ownhardwarekey63)
r63=dict(id='day07-S0-key-functional-own-seam-and-continuation',status='KEY_FAMILY_LOCAL_FOREIGN_SCOPE_RECEIVED_OPERATOR_APPROACH_OPEN' if processed63==len(task62) and all(x['status']=='SEPARATED125' for x in continuation63) else 'KEY_FOREIGN_ALLOCATION_HOLD',own_panel_base=ownseam63,own_new_case_fixing_family=ownhardwarekey63,continuation=continuation63,cursor=processed63,total=len(task62),unreceived=len(task62)-processed63,prior7foreign_reused_no_replay=True,completekeysourceR15preserved=True,actualroutinekeyoperation_NOT_yet_proven=True,operation_seconds=time.monotonic()-t63,process_cpu_seconds=time.process_time()-c63,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p63=OUT/'day07-S0-key-functional-own-seam-and-continuation.json';assert not p63.exists();p63.write_bytes((json.dumps(r63,ensure_ascii=False,indent=2)+'\n').encode());print('S0_KEY_FINAL63',r63['status'],r63['cursor'],r63['total'],ownseam63,ownhardwarekey63,r63['operation_seconds'],r63['process_cpu_seconds'],hashlib.sha256(p63.read_bytes()).hexdigest(),flush=True)
