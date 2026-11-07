import time,json,hashlib,zipfile,os,math
t75=time.monotonic();c75=time.process_time();az75=axis74.z;extra75=(15*math.sqrt(1-az75*az75)+3.25)/az75
fullop75=Part.makeCylinder(15,length74+extra75,start74,axis74);missing75=op74.cut(fullop75);assert fullop75.isValid() and missing75.isValid() and missing75.Volume<1e-5;delta75=fullop75.cut(op74);assert delta75.isValid()
tasks75=[n for n,s in ctx74.items() if bbox_lower_bound(delta75.BoundBox,s.BoundBox)<=1.25];rr75=[]
for n in tasks75:
    s=ctx74[n];r=dict(other=n,other_valid=s.isValid())
    if s.isValid():
        gap,w,_=delta75.distToShape(s);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=delta75.common(s);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        r['status']='ADDITIONAL_FULL_ENTRY_PROFILE_SEPARATED125' if gap>=1.25-1e-7 else 'FULL_OBLIQUE_ENTRY_ALLOCATION_HOLD'
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rr75.append(r)
    if r['status']!='ADDITIONAL_FULL_ENTRY_PROFILE_SEPARATED125':break
ar75=OUT/'day07-S0-complete-oblique-entry-profile.breps.zip';assert not ar75.exists();ge75=[]
with zipfile.ZipFile(ar75,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('S0:full_oblique_R15_profile_outside_body',fullop75),('S0:additional_entry_profile_only',delta75)]+[(r['other'],ctx74[r['other']]) for r in rr75]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge75.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge75,role='SAMEobliqueaxis/R15/sourcekey/cowlhypothesis. Extendonlyoutside-entry soENTIRElastcircularprofileisaboveE6top+3.25; oldlocalfieldcontained. Not ascalarclearancefix/newpose orhandshape.'),indent=2)+'\n').encode())
last75=start74+axis74*(length74+extra75);lowest75=last75.z-15*math.sqrt(1-az75*az75)
r75=dict(id='day07-S0-complete-oblique-entry-profile',status='SAME_OBLIQUE_FULL_ENTRY_PROFILE_SCOPE_RECEIVED_COWL_E6_OPEN' if len(rr75)==len(tasks75) and all(r['status']=='ADDITIONAL_FULL_ENTRY_PROFILE_SEPARATED125' for r in rr75) else 'FULL_OBLIQUE_ENTRY_PROFILE_HOLD',local_receipt=p74.name,local_receipt_sha256=hashlib.sha256(p74.read_bytes()).hexdigest(),same_axis_and_radius_and_key_and_anchors=True,source_R_mm=15,extension_axial_beyond_top_centre_mm=extra75,formula='(R*sqrt(1-axisZ^2)+3.25)/axisZ: fullfinalcirclelowestZ>=BodyOuterZmax112+3.25',actual_lowest_final_cross_section_z_mm=lowest75,old_local_profile_missing_valid=missing75.isValid(),old_local_profile_missing_mm3=missing75.Volume,new_additional_rows=rr75,cursor=len(rr75),total=len(tasks75),unreceived=len(tasks75)-len(rr75),old2pairs_not_replayed=True,remaining='No cowl/ribs/hinge/guard/covermaterialbuilt. ActualE6skin/rimstructuralopening/fullguardtool/terminalprotection/root/operationaloutline/motionstillrequired; sourcekeyfamilyactualfitphase2. Operatorallocationisnotactualhandgeometry orassembledroutinePASS.',archive=ar75.name,archive_sha256=hashlib.sha256(ar75.read_bytes()).hexdigest(),geometry=ge75,operation_seconds=time.monotonic()-t75,process_cpu_seconds=time.process_time()-c75,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p75=OUT/'day07-S0-complete-oblique-entry-profile.json';assert not p75.exists();p75.write_bytes((json.dumps(r75,ensure_ascii=False,indent=2)+'\n').encode());print('S0_COMPLETE75',r75['status'],extra75,lowest75,rr75,r75['operation_seconds'],r75['process_cpu_seconds'],hashlib.sha256(p75.read_bytes()).hexdigest(),flush=True)
