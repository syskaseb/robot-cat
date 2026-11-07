import json,time,hashlib,os,zipfile
t201=time.monotonic();c201=time.process_time();assert first199 is None
srcdisp201=OUT/'day07-five-D-caseback-initial-order-source-disposition.json';sd201=json.loads(srcdisp201.read_bytes());assert sd201['status'].startswith('INITIAL_TOOL_RAW_INSTALLED_STRAP')
spec201={'UnderCaseDeck':[[33.75,-33.5,41],[60.5,0,44]],'PressureLoadBeam':[[57.75,-31.53051513099,43],[60.5,-1.25,46.4]],'CaseBackStop':[[37.25,-32.5,43.5],[38.5,0,54.25]],'CaseSouthWall':[[38.5,-32.5,43.5],[57.5,-31.25,54.25]],'CaseNorthWall':[[38.5,-1.25,43.5],[57.5,0,54.25]],'CaseSouthTopLip':[[38.5,-31.5,53],[57.5,-30,54.25]],'CaseNorthTopLip':[[38.5,-2.5,53],[57.5,-1,54.25]]}
upspec201={'RemovableSouthCaseFaceStop':[[57.5,-32.5,44],[58.75,-30,54.25]],'RemovableNorthCaseFaceStop':[[57.5,-2.5,44],[58.75,0,54.25]]}
planp201=OUT/'day07-five-D-caseback-minimal-carrier-material-and-initial-lay-plan.json';assert not planp201.exists();plan201=dict(id=planp201.stem,status='SAME_ONE_CASEBACK_WHOLE_LOAD_STRATEGY_MEMBER_PLAN_BEFORE_GEOMETRY',source_proposal=prp199.name,source_proposal_sha256=hashlib.sha256(prp199.read_bytes()).hexdigest(),permanent_member_bounds_mm=spec201,removable_member_bounds_mm=upspec201,retained_old_C1_whole_primary_upper=True,new_source_mount_members=['TopPad','Seat','Neck'],not_fusing_bought_nativeframe_or_case=True,actual_case_capture='Lowerdeck/bothsidewalls/toplips/closedbackstop receive wholecase by sliding it fromportside+X BEFOREremovableupper+twoface-stops. Same145loop retains upper; all5sourceports/channels stayopen. No caseforce carried by pullingwire.',loadpath='NativeP0->clamped65+65bearing->newneck/seat->undercase deck + source3mmseat -> loadbeam -> existingC1pressure+currentlegacyBankLedge path; retain currentF_R5bearing functions. This is not anotheroldVbar.',tool_and_wire_voids='ONLY explicitnewshaftR1.7 and originalaboveheadtoolR4.25 atNEWaxis + SAMEfiveC1allocatedexitfieldvoid; no outerBBoxaircuts or purchasedpartcuts.',initial_order='Clamp on completecurrentintegralprintedframe beforeBANK_F_R4OUT andbattery/adjustablestrap; slide connectedcase/leads into opencradle, lay fiveprofiles, close upper2stops+same145. Newcase-slide/access stillneedsnominalfeasibility, not fullN08trajectory.',stock_same_145_loop_head_tail=True,selected=False,N01_complete=False);planp201.write_bytes((json.dumps(plan201,indent=2)+'\n').encode())
shaftvoid201=Part.makeCylinder(1.7,30,A.Vector(33.75,-24.5,20));headvoid201=Part.makeCylinder(4.25,80,A.Vector(33.75,-24.5,42.72));cut201=shaftvoid201.fuse(headvoid201)
members201={'UNCHANGED_C1_WHOLE_PRIMARY':base193,**{'NewMount'+n:kit199[n] for n in ['TopPad','Seat','Neck']},**{n:box153(b) for n,b in spec201.items()}}
members201={n:(s if n.startswith('UNCHANGED') else s.cut(cut201).cut(void193)) for n,s in members201.items()}
uppermembers201={'UNCHANGED_C1_WHOLE_UPPER':up193,**{n:box153(b).cut(void193) for n,b in upspec201.items()}}
base201=fuse181(list(members201.values()));up201=fuse181(list(uppermembers201.values()));assert base201.isValid() and up201.isValid()
coverage201=[]
for half,mem,target in [('permanent',members201,base201),('upper',uppermembers201,up201)]:
    for n,s in mem.items():
        miss=s.cut(target);coverage201.append(dict(half=half,member=n,valid=s.isValid(),volume_mm3=s.Volume,intended_bounds_mm=saved_bounds(s),missing_valid=miss.isValid(),missing_mm3=miss.Volume if miss.isValid() else None))
joins201=[];ns201=list(members201)
for i,n in enumerate(ns201):
    for m in ns201[i+1:]:
        a=members201[n];b=members201[m]
        if bbox_lower_bound(a.BoundBox,b.BoundBox)>1e-7:continue
        co=a.common(b)
        if co.isValid() and co.Volume>1e-7:joins201.append(dict(a=n,b=m,positive_common_mm3=co.Volume))
upjoins201=[]
for n,s in uppermembers201.items():
    if n.startswith('UNCHANGED'):continue
    co=s.common(up193);upjoins201.append(dict(member=n,common_valid=co.isValid(),positive_common_mm3=co.Volume if co.isValid() else None))
first201=None
if len(base201.Solids)!=1 or len(up201.Solids)!=1 or any(not q['valid'] or not q['missing_valid'] or q['missing_mm3']>1e-7 for q in coverage201):first201=dict(stage='FULL_INTENDED_MATERIAL_UNION_GUARD',primary_solids=len(base201.Solids),upper_solids=len(up201.Solids),coverage=coverage201)
newdelta201=base201.cut(base193);newupper201=up201.cut(up193)
case201=Current35['Station:D_FL:case'];casefit201=[]
for n,s in [('newwholeprimary',base201),('newwholeupper',up201)]:
    co=s.common(case201);casefit201.append(dict(part=n,common_valid=co.isValid(),case_material_common_mm3=co.Volume if co.isValid() else None,role='Actualcasecradle/capture ownnonpenetration, nototherwiremetalwaiver'))
    if first201 is None and (not co.isValid() or co.Volume>1e-7):first201=dict(stage='WHOLE_CASE_CAPTURE_NONPENETRATION',row=casefit201[-1])
wire201=[]
if first201 is None:
    for q,s in zip(routes193,nominal193):
        for n,b in [('NEW_PRIMARY_ADDED_MATERIAL',newdelta201),('NEW_UPPER_ADDED_MATERIAL',newupper201)]:
            co=s.common(b);row=dict(wire=q['wire'],part=n,common_valid=co.isValid(),nominal_common_mm3=co.Volume if co.isValid() else None);wire201.append(row)
            if not co.isValid() or co.Volume>1e-7:first201=dict(stage='UNCHANGED_CONTINUOUS_NOMINAL_EXIT_NEW_MATERIAL',row=row);break
        if first201:break
tasks201=[];sepbounds201=0;foreign201=[]
for kn,a in [('NEW_PRIMARY_DELTA',newdelta201),('NEW_UPPER_DELTA',newupper201)]:
    for n,b in neigh199.items():
        if n=='Station:D_FL:case':continue
        lo=bbox_lower_bound(a.BoundBox,bounds126[n] if n in bounds126 else b.BoundBox)
        req=0 if n in ['Ref_Material_P0_SideRight22_0_0','CurrentFoundation:FoundationRail:-1'] else 1.25
        if lo>=req+1e-7:sepbounds201+=1;continue
        priority=0 if ('Housing' in n or n.startswith('Ref_Material_P0_') or n.endswith(':case') or n.startswith('Battery')) else 1
        tasks201.append((priority,kn,n,a,b,lo,req))
tasks201.sort(key=lambda q:(q[0],q[1],q[2]));wita201=None;witb201=None
if first201 is None:
    for _,kn,n,a,b,lo,req in tasks201:
        ga,ww,_=a.distToShape(b);row=dict(new_part=kn,actor=n,gap_mm=ga,required_mm=req,witnesses=[[list(x),list(y)] for x,y in ww[:1]],source_valid=b.isValid())
        if n=='CurrentFoundation:FoundationRail:-1':
            co=a.common(b);ex=co.cut(kit199['Neck']);row.update(actual_function='NewusefulNeck_root_ONLY_othermaterialnotwaived',common_valid=co.isValid(),common_mm3=co.Volume,new_neck_contact_outside_mm3=ex.Volume,pass_function=co.isValid() and ex.isValid() and ex.Volume<1e-7)
            fail=not row['pass_function']
        else:
            if ga<1e-7:
                co=a.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            fail=not row['source_valid'] or ga<req-1e-7 or (req==0 and ga<1e-7 and (not row.get('common_valid') or row.get('common_mm3',0)>1e-7))
        row['status']='NEW_CARRIER_ACTUAL_INTERFACE_HOLD' if fail else 'NEW_CARRIER_SEPARATED_OR_EXACT_FUNCTIONAL_ROOT';foreign201.append(row)
        if fail:first201=dict(stage='NEW_CASEBACK_CARRIER_CURRENT_NEIGHBOR',row=row);wita201=a;witb201=b;break
        if time.monotonic()-t201>12:break
ar201=OUT/'day07-five-D-caseback-minimal-carrier-first-gate.breps.zip';assert not ar201.exists();ge201=[]
exp201={'NEW_WHOLE_PERMANENT':base201,'NEW_WHOLE_REMOVABLE_UPPER':up201,'NEW_ADDED_PRIMARY_MATERIAL':newdelta201,'NEW_ADDED_UPPER_MATERIAL':newupper201,'ACTUAL_UNCHANGED_D5_CASE':case201}
if witb201 is not None:exp201['FIRST_CURRENT_NEIGHBOR_WITNESS']=witb201
with zipfile.ZipFile(ar201,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(exp201.items()):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge201.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge201),indent=2))
p201=OUT/'day07-five-D-caseback-minimal-carrier-first-gate.json';assert not p201.exists()
r201=dict(id=p201.stem,status='NEW_CASEBACK_CARRIER_FIRST_FALSIFIER_STOP' if first201 else 'NEW_CASEBACK_CARRIER_SCOPED_STAGE_PENDING_REMAINING',member_plan=planp201.name,member_plan_sha256=hashlib.sha256(planp201.read_bytes()).hexdigest(),full_intended_member_coverage=coverage201,primary_solids=len(base201.Solids),upper_solids=len(up201.Solids),actual_useful_positive_connections=joins201,upper_casecapture_connections=upjoins201,all_C1_material_retained_by_subset=all(q['missing_mm3']<1e-7 for q in coverage201 if q['member'].startswith('UNCHANGED')),whole_casefit=casefit201,new_material_nominal_exit_rows=wire201,foreign_rows=foreign201,foreign_cursor=len(foreign201),foreign_total=len(tasks201),foreign_unreceived=[[kn,n] for _,kn,n,a,b,lo,req in tasks201[len(foreign201):]],fullbounds_separated=sepbounds201,first_falsifier=first201,stock_and_motion_newdelta_NOT_qualified=True,old_C1_material_and_own5pressure_unchanged=True,whole_9_source_fans_Li_delta55_MAX3_OPEN=True,selected=False,N01_complete=False,actualcut=None,archive=ar201.name,archive_sha256=hashlib.sha256(ar201.read_bytes()).hexdigest(),geometry=ge201,operation_seconds=time.monotonic()-t201,process_cpu_seconds=time.process_time()-c201,pid=os.getpid(),session_id=46493)
p201.write_bytes((json.dumps(r201,indent=2)+'\n').encode());print('CASEBACK_CONSTRUCTIVE_FIRST',r201['status'],'solids',len(base201.Solids),len(up201.Solids),'members',len(coverage201),'joins',len(joins201),'wire',len(wire201),'foreign',len(foreign201),'of',len(tasks201),'first',first201,'wall',r201['operation_seconds'],'CPU',r201['process_cpu_seconds'],hashlib.sha256(p201.read_bytes()).hexdigest(),flush=True)
