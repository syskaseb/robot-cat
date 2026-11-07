import time,json,hashlib,zipfile,os
t72=time.monotonic();c72=time.process_time();tightbox72=box49([opt72.XMin,opt72.YMin,opt72.ZMin],[opt72.XMax,opt72.YMax,opt72.ZMax]);tightvoid72=root71.common(tightbox72)
for existing in [portal71,bed70,Current35['V:new_root_material']]:
    if not tightvoid72.isNull() and tightvoid72.Solids:tightvoid72=tightvoid72.cut(existing)
# The looseBRepboxextended2.3377mmoutsideactualX-37surface. Proveaddedexteriorheel backsontoSOLIDwall, not portalentry.
backing72=box49([-37,39,52],[-36.95,39.25,54]);unbacked72=backing72.cut(portal71);outsideTight72=extra71.cut(tightbox72)
function72=dict(loose_bbox_void_guard_receipt=p71.name,loose_guard1p168_NOT_actual_channel=True,loose_Xmin=portal71.BoundBox.XMin,actual_optimal_Xmin=opt72.XMin,added_inside_tight_box_void_valid=tightvoid72.isNull() or tightvoid72.isValid(),added_inside_tight_box_void_mm3=0 if tightvoid72.isNull() else tightvoid72.Volume,exterior_newheel_backing_slab_mm3=backing72.Volume,backing_missing_valid=unbacked72.isNull() or unbacked72.isValid(),backing_missing_mm3=0 if unbacked72.isNull() else unbacked72.Volume,actual_existing_parent_joint_mm3=joint71.Volume,additional_own_print_joint_mm3=raw71.Volume,source_function='PermanentopenBankPortal2carrier+actualBankBed SAMEprintedloadframe; addedheelthickensoldSOLIDwestwall, not a channelmouth. Alltight-boxvoids andexterioroverlapbackingsurfaceprotected. No boughtpartmarginwaiver or sourcewirepath assumedfromname.')
ok72=function72['added_inside_tight_box_void_valid'] and function72['added_inside_tight_box_void_mm3']<1e-7 and function72['backing_missing_valid'] and function72['backing_missing_mm3']<1e-7 and joint71.Volume>0
remain72=[];stop72=None
if ok72:
    for n,k in tasks70[len(foreign70):]:
        s=moving70[n];q=context70[k];wire=n.split(':')[0];i=['W020','W022','W024'].index(wire)+1;owncase=k=='Ref_Material_F_L'+str(i)+'_CP2_Housing_0_0';r=dict(new=n,other=k,other_valid=q.isValid(),same_actual_pad_caseholder=owncase)
        if q.isValid():
            gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
            co=s.common(q) if gap<1e-7 or owncase else None
            if co is not None:r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            r['status']='ACTUAL_PAIRED_CASEHOLDER_NO_INTRUSION' if owncase and co.isValid() and co.Volume<1e-7 else 'SEPARATED125' if gap>=1.25-1e-7 else 'REMAINING_NEW_LOADPATH_FOREIGN_HOLD'
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        remain72.append(r)
        if r['status'] not in ['SEPARATED125','ACTUAL_PAIRED_CASEHOLDER_NO_INTRUSION']:stop72=r;break
        if time.monotonic()-t72>10:break
own72=[];outline72={};union72=None;unionProof72=[]
if ok72 and not stop72 and len(foreign70)+len(remain72)==len(tasks70):
    for wire,lower in fixed70.items():
        for label in ['band_budget','head_budget']:
            q=nylon70[wire+':'+label];co=lower.common(q);cu=upper70[wire].common(q);own72.append(dict(wire=wire,source_full_unit_part=label,lower_common_valid=co.isValid(),lower_intrusion_mm3=co.Volume,removable_upper_common_valid=cu.isValid(),upper_intrusion_mm3=cu.Volume))
        for label,s in [('fixedlower',lower),('removableupper',upper70[wire])]+[(n,nylon70[wire+':'+n]) for n in ['band_budget','head_budget']]:
            outside=s.cut(BodyOuter31);gap=s.distToShape(boundary56)[0];outline72[wire+':'+label]=dict(valid=s.isValid(),outside_valid=outside.isValid(),outside_mm3=outside.Volume,boundary_gap_mm=gap,required_mm=3.25)
    union72=bed70.copy()
    for wire,s in fixed70.items():
        old=union72.copy();q=old.fuse(s);a=old.cut(q);b=s.cut(q);assert q.isValid() and len(q.Solids)==len(bed70.Solids) and a.isValid() and a.Volume<1e-5 and b.isValid() and b.Volume<1e-5
        unionProof72.append(dict(added=wire,current_parent_missing_mm3=a.Volume,intended_lower_frame_missing_mm3=b.Volume,valid=q.isValid(),solids=len(q.Solids)));union72=q
ar72=OUT/'day07-V3-outside-web-current-material-and-functional-gate.breps.zip';assert not ar72.exists();ge72=[]
with zipfile.ZipFile(ar72,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('SOURCE:actualportal_solid_exterior_backing',backing72),('SOURCE:added_inside_tight_portal_voids',tightvoid72)]
    if union72 is not None:items+=[('CurrentBankBed_WITH_three_fixed_lower_C_frames',union72)]
    items +=[(r['other'],context70[r['other']]) for r in remain72 if r['status'] not in ['SEPARATED125','ACTUAL_PAIRED_CASEHOLDER_NO_INTRUSION']]
    for i,(n,s) in enumerate(items):
        if s.isNull():continue
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge72.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s) if not s.isNull() else None))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge72,scope='SameC0functionalprintclassification/remainingchangedinterfaces; no sourcecurrentreplacementselected yet.'),indent=2)+'\n').encode())
r72=dict(id='day07-V3-portal-tight-surface-and-remaining-foreign',status='SAME_C0_PORTAL_FUNCTION_AND_NEW_INTERFACES_RECEIVED' if ok72 and not stop72 and union72 is not None and all(x['lower_common_valid'] and x['removable_upper_common_valid'] and x['lower_intrusion_mm3']<1e-7 and x['upper_intrusion_mm3']<1e-7 for x in own72) else 'SAME_C0_FUNCTION_OR_FOREIGN_OR_PAIRED_RETENTION_HOLD',portal_function=function72,portal_function_scope_closed=ok72,remaining_foreign=remain72,cursor=len(foreign70)+len(remain72),total=len(tasks70),unreceived=len(tasks70)-len(foreign70)-len(remain72),stop=stop72,raw10foreign_and1p168_bbox_guard_preserved=True,no_first9accepted_replay=True,own_paired_full_stock_fit=own72,outline=outline72,new_whole_current_parent_union=unionProof72,archive=ar72.name,archive_sha256=hashlib.sha256(ar72.read_bytes()).hexdigest(),geometry=ge72,operation_seconds=time.monotonic()-t72,process_cpu_seconds=time.process_time()-c72,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p72=OUT/'day07-V3-portal-tight-surface-and-remaining-foreign.json';assert not p72.exists();p72.write_bytes((json.dumps(r72,ensure_ascii=False,indent=2)+'\n').encode());print('V3_TIGHT72',r72['status'],function72,'FOREIGN',r72['cursor'],r72['total'],stop72,'OWN',own72,r72['operation_seconds'],r72['process_cpu_seconds'],hashlib.sha256(p72.read_bytes()).hexdigest(),flush=True)
