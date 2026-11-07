import time,json,hashlib,zipfile,os
t64=time.monotonic();c64=time.process_time();moving64=['Ref_Material_S0_body_CP2_0_0','Ref_Material_S0_neck_CP2_0_0','Ref_Material_S0_stud_IN_0_0','Ref_Material_S0_stud_OUT_0_0'];travel64=4.0
context64={n:s for n,s in effective62.items() if n not in s0names56 and n not in hardware57};covers64={};descriptions64=[]
for n in moving64:
    source=Current35[n];cy=next(f for f in source.Faces if type(f.Surface).__name__=='Cylinder');planes=[f.CenterOfMass for f in source.Faces if type(f.Surface).__name__=='Plane'];assert len(planes)==2
    low,high=sorted(planes,key=lambda p:(np.array(list(p))-C56)@out56);h=(high-low).Length
    cover=Part.makeCylinder(cy.Surface.Radius,h+travel64,low-A.Vector(*out56)*travel64,A.Vector(*out56));missing=source.cut(cover);assert cover.isValid() and missing.isValid() and missing.Volume<1e-6
    covers64[n]=cover;descriptions64.append(dict(name=n,radius_mm=cy.Surface.Radius,source_length_mm=h,axial_insertion_mm=travel64,cover_bounds_mm=saved_bounds(cover),original_missing_mm3=missing.Volume,operation='Rigidcase approaches currentneckhole alongactualN, from4mmback tofinal. Neck3mm initially0.999999mmclear ofpanel. Keyremoved; washers/rings/nuts andnewM6installedlater perselectedsource.'))
tasks64=[(n,k) for n,s in covers64.items() for k,q in context64.items() if bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25];rows64=[]
for n,k in tasks64:
    s=covers64[n];q=context64[k];row=dict(moving=n,other=k,other_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=s.common(q);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        ownpanel=k=='CurrentFoundation:FoundationRail:-1' and gap<1e-7 and row.get('common_valid') and abs(row.get('common_mm3',1))<1e-7
        row['status']='OWN_CASE_SEATING_PLANE_NO_MATERIAL_INTRUSION' if ownpanel else 'SEPARATED125' if gap>=1.25-1e-7 else 'INITIAL_CASE_FAMILY_ALLOCATION_HOLD_NOT_DELIVERED_CONTACT'
        if ownpanel:
            rest=s.distToShape(restprint63)[0];row['actual_remaining_rail_strut_gap_mm']=rest
            if rest<1.25:row['status']='INITIAL_CASE_REST_PRINT_HOLD'
    else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows64.append(row);print('S0_CASE_INSERT64',row,flush=True)
    if row['status'] not in ['SEPARATED125','OWN_CASE_SEATING_PLANE_NO_MATERIAL_INTRUSION']:break
    if time.monotonic()-t64>15:break
ar64=OUT/'day07-S0-initial-case-insertion-first-gate.breps.zip';assert not ar64.exists();ge64=[]
with zipfile.ZipFile(ar64,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(list(covers64.items())+[(k,context64[k]) for k in sorted({r['other'] for r in rows64})]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge64.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge64,scope='Actualsourcecylinders extendedby4mm alongactualaxis, wholecase/neck/permanentstuds. No finepathsolver, no newmountvariant.'),indent=2)+'\n').encode())
r64=dict(id='day07-S0-initial-case-insertion-first-gate',status='INITIAL_CASE_4MM_AXIAL_SEATING_SCOPE_RECEIVED' if len(rows64)==len(tasks64) and all(x['status'] in ['SEPARATED125','OWN_CASE_SEATING_PLANE_NO_MATERIAL_INTRUSION'] for x in rows64) else 'INITIAL_CASE_SEATING_PENDING_OR_HOLD',moving_case_source_roles=moving64,not_yet_installed=[n for n in s0names56 if n not in moving64]+list(hardware57),full_effective_fixed_count=len(context64),covers=descriptions64,rows=rows64,total=len(tasks64),cursor=len(rows64),unreceived=len(tasks64)-len(rows64),sourcebenchorder='Casebeforekey/rings/washer/nut/M6parts; completeintegralrailpresent, noprintvirtualdetach. FullothercurrentPi/head/looms testedconservatively; anyneedtodefermustbesourceclassifiedexplicitly.',not_whole_freehandplacement_from_externalbench=True,source_current1292_unchanged=True,archive=ar64.name,archive_sha256=hashlib.sha256(ar64.read_bytes()).hexdigest(),geometry=ge64,operation_seconds=time.monotonic()-t64,process_cpu_seconds=time.process_time()-c64,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p64=OUT/'day07-S0-initial-case-insertion-first-gate.json';assert not p64.exists();p64.write_bytes((json.dumps(r64,ensure_ascii=False,indent=2)+'\n').encode());print('S0_CASE_FINAL64',r64['status'],r64['cursor'],r64['total'],r64['operation_seconds'],r64['process_cpu_seconds'],hashlib.sha256(p64.read_bytes()).hexdigest(),flush=True)
