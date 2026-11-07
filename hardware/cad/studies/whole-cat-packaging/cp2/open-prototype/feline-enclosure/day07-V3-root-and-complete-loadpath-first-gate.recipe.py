import time,json,hashlib,zipfile,os
t70=time.monotonic();c70=time.process_time();proposal70=OUT/'day07-V3-outside-web-open-front-whole-proposal.json';pr70=json.loads(proposal70.read_bytes());dims70=pr70['dimensions'];bed70=Current35['CurrentFoundation:BankBedCurrent:1'];bedhash70=hashlib.sha256(bed70.exportBrepToString().encode()).hexdigest()
roots70=[];coupons70={};parts70={};prisms70={};fixed70={};upper70={};caplower70={};nylon70={};member70=[];guide70=[];foreign70=[];hold70=None;parent70=None
expected70='bf0311c029d0caa23b28387114a5b8f0621cfd0c79ec72a25074733e5c80ff99'
if bedhash70!=expected70:hold70=dict(status='CURRENT_BANKBED_BYTE_PIN_MISMATCH_NO_BUILD',actual=bedhash70,expected=expected70)
for i,(wire,x) in enumerate(zip(['W020','W022','W024'],[-40,-16,8]),1):
    if hold70:break
    pn='CurrentFoundation:BankPad:Ref_Material_F_L'+str(i)+'_CP2_Housing_0_0:0';pad=Current35[pn];roi=box49([x-3.5,39.25,52],[x-.5,43.25,54]);bco=bed70.common(roi);pco=pad.common(roi);coupons70[wire]=bco
    faces=[f for f in bco.Faces if type(f.Surface).__name__=='Plane' and abs(f.CenterOfMass.y-39.25)<1e-6 and f.normalAt(0,0).y<-.99];face=max(faces,key=lambda f:f.Area) if faces else None
    row=dict(wire=wire,parent='CurrentFoundation:BankBedCurrent:1',current_BankBed_sha256=bedhash70,named_pad=pn,bed_roi_valid=bco.isValid(),bed_roi_mm3=bco.Volume,pad_roi_valid=pco.isValid(),pad_roi_mm3=pco.Volume,real_front_face_area_mm2=face.Area if face else None,real_front_face_centre_mm=list(face.CenterOfMass) if face else None,inside_current_bed_behind_face=bed70.isInside(face.CenterOfMass+A.Vector(0,.05,0),1e-7,False) if face else False,outside_before_face=not bed70.isInside(face.CenterOfMass-A.Vector(0,.05,0),1e-7,False) if face else False)
    roots70.append(row);print('V3_ROOT70',row,flush=True)
    if not(bco.isValid() and bco.Volume>0 and pco.isValid() and pco.Volume>0 and face and row['inside_current_bed_behind_face'] and row['outside_before_face']):hold70=dict(status='ACTUAL_ROOT_FRONT_FACE_HOLD',row=row)
def join70(label,a,b):
    q=a.fuse(b);ma=a.cut(q);mb=b.cut(q);co=a.common(b);row=dict(label=label,valid=q.isValid(),solids=len(q.Solids),positive_joint_valid=co.isValid(),positive_joint_mm3=co.Volume,a_missing_valid=ma.isValid(),b_missing_valid=mb.isValid(),a_missing_mm3=ma.Volume,b_missing_mm3=mb.Volume)
    member70.append(row)
    assert q.isValid() and len(q.Solids)==1 and co.isValid() and co.Volume>1e-8 and ma.isValid() and mb.isValid() and ma.Volume<1e-5 and mb.Volume<1e-5,(label,row)
    return q
if not hold70:
    for i,(wire,x) in enumerate(zip(['W020','W022','W024'],[-40,-16,8]),1):
        blocks={}
        for label in ['heel','back_web','low_runner','front_riser','side_cap_link']:
            xx=dims70[label+'_relative_X_mm'];yy=dims70[label+'_Y_mm'];zz=dims70[label+'_Z_mm'];blocks[label]=box49([x+xx[0],yy[0],zz[0]],[x+xx[1],yy[1],zz[1]])
        ordered=list(blocks.items());s=ordered[0][1].copy()
        for label,q in ordered[1:]:s=join70(wire+':'+label,s,q)
        prisms70[wire]=s
        capname='Station:Bank:'+wire+'/body/end:split_cap_exterior';cap=Current35[capname];b=cap.BoundBox;lower=cap.common(box49([b.XMin-1,b.YMin-1,b.ZMin-1],[b.XMax+1,b.YMax+1,69]));upper=cap.cut(lower);union=lower.fuse(upper);missing=cap.cut(union)
        assert lower.isValid() and upper.isValid() and missing.isValid() and missing.Volume<1e-5
        caplower70[wire]=lower;upper70[wire]=upper;fixed70[wire]=join70(wire+':actual_source_lower9half',s,lower)
        newco=fixed70[wire].common(bed70);roots70[i-1]['new_actual_joint_valid']=newco.isValid();roots70[i-1]['new_actual_joint_mm3']=newco.Volume;roots70[i-1]['source_full9_cap_missing_mm3']=missing.Volume
        assert newco.isValid() and newco.Volume>0
        for label in ['band_budget','head_budget']:
            old=Current35['Station:Bank:'+wire+'/body/end:'+label];q=old.copy();q.translate(A.Vector(0,-2,0));nylon70[wire+':'+label]=q
        parts70.update({wire+':'+k:v for k,v in blocks.items()})
    # Completeallocatedcurrentfourregions, not the rejected oldcommonregion. Endcap9interfaces retainedseparately.
    for wire,s in prisms70.items():
        for n,q in new53.items():
            gap,w,_=s.distToShape(q);co=s.common(q) if gap<1e-7 else None;r=dict(root=wire,allocated_region=n,gap_mm=gap,required_own_guide_mm=.2,common_valid=co.isValid() if co is not None else None,common_mm3=co.Volume if co is not None and co.isValid() else 0 if co is None else None,status='FULL_FREE_REGION_GUIDE_CLEAR02' if gap>=.2-1e-7 else 'NEW_LOADPATH_OCCUPIED_REGION_HOLD_NOT_PHYSICAL_WIRECONTACT',witnesses=[[list(a),list(b)] for a,b in w[:1]])
            guide70.append(r);print('V3_GUIDE70',r,flush=True)
            if gap<.2-1e-7:hold70=r;break
        if hold70:break
if not hold70:
    retired70={'V:new_root_material','V:functional_pressure_support','V:common_region'}|{n for n in effective62 if any(n.startswith(w+':') for w in ['W020','W022','W024'])}
    for wire in ['W020','W022','W024']:
        for label in ['split_cap_exterior','band_budget','head_budget']:retired70.add('Station:Bank:'+wire+'/body/end:'+label)
    context70={n:s for n,s in effective62.items() if n not in retired70};context70['S0:required_operator_upper_entry_HOLD_preserved']=access68
    # Same3physicalgrips usefixedlower+removableupper, not duplicateclosedcaps. Wholeloops+headsmove2mmwithinfull9.
    context70.update({n+':relocated_full_source':s for n,s in nylon70.items()})
    moving70={**{w+':new_full_root':s for w,s in prisms70.items()},**{w+':relocated:'+n.split(':')[1]:s for n,s in nylon70.items() for w in [n.split(':')[0]]}}
    tasks70=[]
    for n,s in moving70.items():
        wire=n.split(':')[0];i=['W020','W022','W024'].index(wire)+1;pad='CurrentFoundation:BankPad:Ref_Material_F_L'+str(i)+'_CP2_Housing_0_0:0'
        for k,q in context70.items():
            if k in ['CurrentFoundation:BankBedCurrent:1',pad] or k.startswith(wire+':'):continue
            if bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25:tasks70.append((n,k))
    tasks70.sort(key=lambda p:(0 if 'CP2_IN_' in p[1] or 'CP2_OUT_' in p[1] else 1 if 'Housing' in p[1] else 2,p))
    for n,k in tasks70:
        s=moving70[n];q=context70[k];wire=n.split(':')[0];i=['W020','W022','W024'].index(wire)+1;owncase=k=='Ref_Material_F_L'+str(i)+'_CP2_Housing_0_0'
        r=dict(new=n,other=k,other_valid=q.isValid(),same_actual_pad_caseholder=owncase)
        if q.isValid():
            gap,w,_=s.distToShape(q);r.update(gap_mm=gap,required_foreign_mm=1.25,witnesses=[[list(a),list(b)] for a,b in w[:1]])
            co=s.common(q) if gap<1e-7 or owncase else None
            if co is not None:r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            r['status']='ACTUAL_PAIRED_CASEHOLDER_NO_INTRUSION' if owncase and co.isValid() and co.Volume<1e-7 else 'SEPARATED125' if gap>=1.25-1e-7 else 'NEW_WHOLE_LOADPATH_FOREIGN_HOLD'
            if owncase:r['function']='Samephysicalcase restsontheactualretainedBankPad; newCframeintegralextensionprotectsfullcasevolume. NoINPUT/OUTPUT/ATO orothercase exception.'
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        foreign70.append(r);print('V3_FOREIGN70',r,flush=True)
        if r['status'] not in ['SEPARATED125','ACTUAL_PAIRED_CASEHOLDER_NO_INTRUSION']:hold70=r;break
        if time.monotonic()-t70>18:break
else:tasks70=[]
ar70=OUT/'day07-V3-outside-web-open-front-first-gate.breps.zip';assert not ar70.exists();ge70=[]
with zipfile.ZipFile(ar70,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('SOURCE:actual_current_BankBed',bed70)]+[(w+':actual_root_coupon',s) for w,s in coupons70.items()]+[(w+':new_complete_lower_frame',s) for w,s in fixed70.items()]+[(w+':new_material_prisms',s) for w,s in prisms70.items()]+[(w+':removable_full9_upper',s) for w,s in upper70.items()]+[(w+':relocated_full_source',s) for w,s in nylon70.items()]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge70.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge70,role='Newcausal3sideCframes actualroot/materialcoverage/newwholeguide+foreign; oldV3C0/C1frozen'),indent=2)+'\n').encode())
r70=dict(id='day07-V3-outside-web-open-front-first-gate',status='NEW_CAUSAL_V3_FIRST_FALSIFIER_HOLD' if hold70 else 'NEW_CAUSAL_V3_BOUNDED_PREFLIGHT_PENDING' if len(foreign70)<len(tasks70) else 'NEW_CAUSAL_V3_LOCAL_LOADPATH_PREFLIGHT_RECEIVED',proposal=proposal70.name,proposal_sha256=hashlib.sha256(proposal70.read_bytes()).hexdigest(),source_current_BankBed_actual_sha256=bedhash70,actual_roots=roots70,material_union_member_coverage=member70,region_interfaces=guide70,foreign=foreign70,cursor=len(foreign70),total=len(tasks70),unreceived=len(tasks70)-len(foreign70),stop=hold70,old_frozen_negative_counts_not_resumed=True,scope='Samewholecase/metal/ATO/real3caps/fullbandsheads/currentS0key+operatorHOLD/Pi/MODULEsourceparts preserved. Matchingcaseholderfunctionalfitrequiresnointrusion; allactualINOUT/ATO/otherpartsforeign1.25. Ownfreeoccupiedregionguide.2 asprevioussourcefunction; no profile/Rreduction.',archive=ar70.name,archive_sha256=hashlib.sha256(ar70.read_bytes()).hexdigest(),geometry=ge70,operation_seconds=time.monotonic()-t70,process_cpu_seconds=time.process_time()-c70,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p70=OUT/'day07-V3-outside-web-open-front-first-gate.json';assert not p70.exists();p70.write_bytes((json.dumps(r70,ensure_ascii=False,indent=2)+'\n').encode());print('V3_FINAL70',r70['status'],r70['cursor'],r70['total'],hold70,r70['operation_seconds'],r70['process_cpu_seconds'],hashlib.sha256(p70.read_bytes()).hexdigest(),flush=True)
