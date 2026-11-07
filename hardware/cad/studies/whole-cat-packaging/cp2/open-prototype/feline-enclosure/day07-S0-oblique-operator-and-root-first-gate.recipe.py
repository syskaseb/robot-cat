import time,json,hashlib,zipfile,os
t74=time.monotonic();c74=time.process_time();prop74=OUT/'day07-S0-oblique-portal-whole-first-gate-proposal.json';pd74=json.loads(prop74.read_bytes());start74=tip68;top74=A.Vector(-50,0,112);axis74=top74-start74;length74=axis74.Length;axis74.normalize();op74=Part.makeCylinder(15,length74+3.25,start74,axis74);assert op74.isValid()
roots74=[];coupons74={}
for label,urange in [('left',[-13,-11]),('right',[11,13])]:
    localroi=Part.makeBox(urange[1]-urange[0],2,2.5,A.Vector(urange[0],18,.5));roi=loc57(localroi);coupon=u59.common(roi);fpoint=place57.multVec(A.Vector(sum(urange)/2,19,3));inside=u59.isInside(fpoint-A.Vector(*out56)*.05,1e-7,False);outside=not u59.isInside(fpoint+A.Vector(*out56)*.05,1e-7,False)
    roots74.append(dict(name=label,actual_current_parent='CurrentFoundation:FoundationRail:-1_WITH_integralS0C1/fullpanel',coupon_valid=coupon.isValid(),actual_material_mm3=coupon.Volume,actual_surface_point_mm=list(fpoint),source_inside_behind=inside,source_outside_ahead=outside,nominal_useful_source_patch_area_mm2=4,actual_new_guard_or_brace_built=False));coupons74[label]=coupon
ctx74={n:s for n,s in effective62.items() if n!='Ref_Material_S0_key_CP2_0_0'};tasks74=[n for n,s in ctx74.items() if bbox_lower_bound(op74.BoundBox,s.BoundBox)<=1.25];rr74=[]
for n in tasks74:
    q=ctx74[n];r=dict(other=n,other_valid=q.isValid())
    if q.isValid():
        gap,w,_=op74.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=op74.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        r['status']='OBLIQUE_SOURCE_R15_OPERATOR_REGION_SEPARATED125' if gap>=1.25-1e-7 else 'OBLIQUE_OPERATOR_ALLOCATION_HOLD_NOT_HAND_CONTACT'
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rr74.append(r);print('S0_OBLIQUE74',r,flush=True)
    if r['status']!='OBLIQUE_SOURCE_R15_OPERATOR_REGION_SEPARATED125' or time.monotonic()-t74>10:break
ar74=OUT/'day07-S0-oblique-operator-and-real-root-first-gate.breps.zip';assert not ar74.exists();ge74=[]
with zipfile.ZipFile(ar74,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('S0:oblique_R15_operator_capacity',op74)]+[(n+':actual_panel_root_coupon',s) for n,s in coupons74.items()]+[(r['other'],ctx74[r['other']]) for r in rr74]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge74.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge74,scope='OnewholeS0operatorportalhypothesis: actualrootREAD andallocatedsourceR15entry preflightONLY; no cowl/braces/E6materialbuilt or selected.'),indent=2)+'\n').encode())
r74=dict(id='day07-S0-oblique-operator-and-real-root-first-gate',status='OBLIQUE_OPERATOR_REGION_AND_ACTUAL_PANEL_ROOTS_SCOPE_RECEIVED_COWL_E6_INTERFACE_OPEN' if len(rr74)==len(tasks74) and all(r['status']=='OBLIQUE_SOURCE_R15_OPERATOR_REGION_SEPARATED125' for r in rr74) and all(r['coupon_valid'] and r['actual_material_mm3']>0 and r['source_inside_behind'] and r['source_outside_ahead'] for r in roots74) else 'OBLIQUE_PORTAL_FIRST_GATE_HOLD_OR_PENDING',proposal=prop74.name,proposal_sha256=hashlib.sha256(prop74.read_bytes()).hexdigest(),source_key_tip_actual_mm=list(start74),entry_axis=list(axis74),entry_R_mm=15,operator_region_not_actual_hand=True,actual_current_source_key_kept=True,root_interfaces=roots74,rows=rr74,cursor=len(rr74),total=len(tasks74),unreceived=len(tasks74)-len(rr74),retired_old_vertical_operator_only_as_rejected_hypothesis_not_physicalpart=True,prior_vertical_gap339_negative_kept=True,no_routine_Pi_removal=True,full_effective_current1311_unchanged=True,remaining='Fullguard2braces/materialcoverage/root/M6M10tool/ring/sourceends/bodyoutline andactualE6skinopening/rimloadpath/terminalcowl/closure/motionremainOPEN. Thisread doesNOTallowclaim an unqualifiedE6coverisnonstructural or oldControl_S0preserved. Actualkey/toolfit remains phase2assumption; noanthropometry/physicalhandcontactclaim.',archive=ar74.name,archive_sha256=hashlib.sha256(ar74.read_bytes()).hexdigest(),geometry=ge74,operation_seconds=time.monotonic()-t74,process_cpu_seconds=time.process_time()-c74,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p74=OUT/'day07-S0-oblique-operator-and-real-root-first-gate.json';assert not p74.exists();p74.write_bytes((json.dumps(r74,ensure_ascii=False,indent=2)+'\n').encode());print('S0_OBLIQUE_FINAL74',r74['status'],roots74,r74['cursor'],r74['total'],r74['operation_seconds'],r74['process_cpu_seconds'],hashlib.sha256(p74.read_bytes()).hexdigest(),flush=True)
