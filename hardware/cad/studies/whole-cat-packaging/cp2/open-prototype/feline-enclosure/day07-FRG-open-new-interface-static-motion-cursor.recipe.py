import json,time,hashlib,os
t210=time.monotonic();c210=time.process_time();assert first209 is None
excluded210={'CurrentFoundation:FoundationRail:-1','CurrentFoundation:FoundationFlange:-1','SharedRetention:lower_common_flange_base','Station:FR_G:shared_near_root','Station:FR_G:split_common_comb','Station:P_AUX:shared_near_root','PROPOSED_D5_C1_WHOLE_CASE_CARRIER'}
context210={n:s for n,s in context208.items() if n not in excluded210}
newfixed210={'NEW_POSITIVE_PERMANENT_MATERIAL':newdelta209,'NEW_SEPARATE_PRESSURE_UPPER':newup209}
tasks210=[];bounds210=0;rows210=[];first210=None
for an,a in newfixed210.items():
    for n,b in context210.items():
        req=0 if n=='Station:FR_G:case' else 1.25;lo=bbox_lower_bound(a.BoundBox,bounds126[n] if n in bounds126 else b.BoundBox)
        if lo>=req+1e-7:bounds210+=1;continue
        priority=0 if n.endswith(':case') or n.startswith('Ref_Material_P0_') or 'Housing' in n else 1;tasks210.append((priority,an,n,a,b,lo,req))
tasks210.sort(key=lambda q:(q[0],q[1],q[2]))
for _,an,n,a,b,lo,req in tasks210:
    ga,ww,_=a.distToShape(b);row=dict(new_part=an,actor=n,actual_gap_mm=ga,required_mm=req,source_valid=b.isValid(),witnesses=[[list(x),list(y)] for x,y in ww[:1]])
    if ga<1e-7:
        co=a.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
    fail=not row['source_valid'] or ga<req-1e-7 or (req==0 and ga<1e-7 and (not row.get('common_valid') or row.get('common_mm3',0)>1e-7));row['status']='NEW_PRINT_FOREIGN_OR_OWNCASE_HOLD' if fail else 'NEW_PRINT_SEPARATED_OR_ACTUAL_CASE_BEARING_FIT';rows210.append(row)
    if fail:first210=dict(stage='NEW_MATERIAL_FIRST_CURRENT_FOREIGN',row=row);break
    if time.monotonic()-t210>8:break
case210=Current35['Station:FR_G:case'];area210=0
for f in shim209.Faces:
    if abs(f.BoundBox.ZMin-40.76)<1e-6 and abs(f.BoundBox.ZMax-40.76)<1e-6:
        area210+=sum(f.common(g).Area for g in case210.Faces if abs(g.BoundBox.ZMin-40.76)<1e-6 and abs(g.BoundBox.ZMax-40.76)<1e-6)
bodybb210=BodyOuter31.BoundBox;bbbody210=np.array(saved_bounds(BodyOuter31));out210=[]
for n,s in {**newfixed210,**stock208}.items():
    bb=np.array(saved_bounds(s));margin=float(np.min(np.r_[bb[0]-bbbody210[0],bbbody210[1]-bb[1]]));out210.append(dict(part=n,actual_bodyouter_margin_box_mm=margin,required_mm=3.25,status='INSIDE_SELECTED_ENVELOPE325' if margin>=3.25-1e-7 else 'OUTLINE_OPEN'))
motion210=[];mpending210=[];minmotion210=1e9
if first210 is None and len(rows210)==len(tasks210):
    for an,a in {**newfixed210,**stock208}.items():
        bb=np.array(saved_bounds(a))
        for pose in range(1,36):
            mb=np.asarray(posedbounds175[pose]);lower=np.linalg.norm(np.maximum(0,np.maximum(bb[0]-mb[:,1,:],mb[:,0,:]-bb[1])),axis=1);minmotion210=min(minmotion210,float(lower.min()));todo=np.where(lower<1.25-1e-7)[0]
            motion210.append(dict(part=an,pose=pose,actual_current_target_count=len(lower),full_bounds_separated=int(len(lower)-len(todo)),minimum_lower_mm=float(lower.min())))
            if len(todo):mpending210.extend([dict(part=an,pose=pose,index=int(i),bounds_lower_mm=float(lower[i]),status='NEEDS_ACTUAL_PAIR_NOT_CONTACT_NOT_PROVEN_HOLD') for i in todo]);break
        if mpending210:break
p210=OUT/'day07-FRG-open-front-new-interface-static-motion-cursor.json';assert not p210.exists()
r210=dict(id=p210.stem,status='NEW_OPEN_INTERFACE_FIRST_FOREIGN_HOLD' if first210 else ('NEW_OPEN_INTERFACE_STATIC_RECEIVED_MOTION_BOUNDS_SCOPED' if len(rows210)==len(tasks210) else 'NEW_OPEN_INTERFACE_STATIC_SAVED_CURSOR_PENDING'),source_constructive=p209.name,source_constructive_sha256=hashlib.sha256(p209.read_bytes()).hexdigest(),actual_new_static_rows=rows210,static_cursor=len(rows210),static_total=len(tasks210),static_unreceived=[[an,n] for _,an,n,a,b,lo,req in tasks210[len(rows210):]],static_fullbounds_separated=bounds210,first_falsifier=first210,source_alias_decompositions_not_physicalforeign=sorted(excluded210),actual_nominal_case_bearing_area_mm2=area210,outline_new5_fields_only=out210,bodyouter_source_bounds_mm=bbbody210.tolist(),bodyouter_volume_mm3=BodyOuter31.Volume,new5_fields_motion_rows=motion210,new_motion_conservative_pairs=sum(q['full_bounds_separated'] for q in motion210),new_motion_minimum_lower_mm=minmotion210 if motion210 else None,new_motion_pending_actual_pairs=mpending210,motion_qualified=bool(len(motion210)==5*35 and not mpending210),oldmotion27k36k155451548NOTreplayed=True,initialcase_slide_and_upper_keys_wholeassembly_OPEN=True,selected=False,N01_complete=False,actualcut=None,operation_seconds=time.monotonic()-t210,process_cpu_seconds=time.process_time()-c210,pid=os.getpid(),session_id=46493)
p210.write_bytes((json.dumps(r210,indent=2)+'\n').encode());print('OPEN_INTERFACE_STATIC_MOTION',r210['status'],'static',len(rows210),'of',len(tasks210),'first',first210,'bearing',area210,'newmotion',r210['new_motion_conservative_pairs'],'qualified',r210['motion_qualified'],'pending',len(mpending210),'wall',r210['operation_seconds'],'CPU',r210['process_cpu_seconds'],hashlib.sha256(p210.read_bytes()).hexdigest(),flush=True)
