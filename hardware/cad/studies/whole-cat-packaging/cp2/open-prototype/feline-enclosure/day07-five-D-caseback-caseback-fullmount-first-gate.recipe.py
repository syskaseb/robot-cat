import json,time,hashlib,os,zipfile
t199=time.monotonic();c199=time.process_time();dx199=33.75-72.;prp199=OUT/'day07-five-D-caseback-frame-bearing-whole-load-proposal.json';pr199=json.loads(prp199.read_bytes())
src199={**{'Hardware:'+n:s for n,s in met197.items()},'LowerJaw':Current35['Station:Anchor:Rear:LowerClampJaw3'],'TopPad':Current35['Station:Anchor:Rear:TopClampPad3'],'Seat':Current35['CurrentFoundation:ClampSeat:3'],'Neck':Current35['CurrentFoundation:ClampNeck:3']}
kit199={};quality199=[]
for n,s in src199.items():
    a=s.copy();a.translate(A.Vector(dx199,0,0));row=dict(name=n,source_valid=s.isValid(),new_valid=a.isValid(),source_volume_mm3=s.Volume,new_volume_mm3=a.Volume,bounds_mm=saved_bounds(a),relative_change_mm=[dx199,0,0],datum='CURRENT bakedworld properrigidPlacement, noXML')
    assert row['source_valid'] and row['new_valid'] and abs(a.Volume-s.Volume)<1e-6,(n,row)
    quality199.append(row);kit199[n]=a
frame199=Current35['Ref_Material_P0_SideRight22_0_0'];bearing199=[]
for n,z in [('LowerJaw',37.02),('TopPad',38.52)]:
    a=kit199[n];co=a.common(frame199);area=0.
    for f in a.Faces:
        if abs(f.BoundBox.ZMin-z)<1e-6 and abs(f.BoundBox.ZMax-z)<1e-6:
            area+=sum(f.common(h).Area for h in frame199.Faces if abs(h.BoundBox.ZMin-z)<1e-5 and abs(h.BoundBox.ZMax-z)<1e-5)
    bearing199.append(dict(part=n,native_actor='Ref_Material_P0_SideRight22_0_0',actual_plane_z_mm=z,actual_common_valid=co.isValid(),actual_common_mm3=co.Volume if co.isValid() else None,actual_planar_bearing_mm2=area,required_source_bearing_mm2=60))
rootpart199=Current35['CurrentFoundation:FoundationRail:-1'];rootco199=kit199['Neck'].common(rootpart199)
root199=dict(name='NEW_NECK_to_ACTUAL_CURRENT_COMMON_FOUNDATION_RAIL',common_valid=rootco199.isValid(),common_mm3=rootco199.Volume if rootco199.isValid() else None,root_actor='CurrentFoundation:FoundationRail:-1',root_scope='Actualnewneck joint only, not wholecasecarrier loadproof or blindwholeprintOWN')
first199=None
if any(not q['actual_common_valid'] or q['actual_common_mm3']>1e-7 or q['actual_planar_bearing_mm2']<60-1e-5 for q in bearing199):first199=dict(stage='ACTUAL_NATIVE_NEW_BEARING',rows=bearing199)
elif not rootco199.isValid() or rootco199.Volume<=1e-7:first199=dict(stage='ACTUAL_NECK_TO_CURRENT_FRAME_ROOT',row=root199)
wirerows199=[];wirebbox199=0
if first199 is None:
    for q,a in zip(routes193,voids193):
        for n,b in kit199.items():
            if not n.startswith('Hardware:'):continue
            lo=bbox_lower_bound(a.BoundBox,b.BoundBox)
            if lo>=1.25-1e-7:ga=lo;kind='FULL_SHAPE_BBOX_LOWER'
            else:ga=a.distToShape(b)[0];kind='ACTUAL_FULL_PROFILE_DISTANCE'
            row=dict(wire=q['wire'],new_part=n,gap_or_lower_mm=ga,required_foreign_mm=1.25,evidence=kind,status='SEPARATED125' if ga>=1.25-1e-7 else 'ALLOCATED_PROFILE_MARGIN_HOLD_NOT_WIRECONTACT');wirerows199.append(row);wirebbox199+=int(kind=='FULL_SHAPE_BBOX_LOWER')
            if ga<1.25-1e-7:first199=dict(stage='WHOLE_METAL_ALL5_FULL_SOURCE_EXITS',row=row);break
        if first199:break
old199={n for n in ctx182 if n.startswith('Station:Anchor:Rear:RailClamp3') or n in ['Station:Anchor:Rear:TopClampPad3','Station:Anchor:Rear:LowerClampJaw3','CurrentFoundation:ClampSeat:3','CurrentFoundation:ClampNeck:3']}
neigh199={n:s for n,s in ctx182.items() if n not in old199};tasks199=[];boundssep199=0
for kn,a in kit199.items():
    if not kn.startswith('Hardware:'):continue
    for n,b in neigh199.items():
        lo=bbox_lower_bound(a.BoundBox,bounds126[n] if n in bounds126 else b.BoundBox)
        req=0 if n=='Ref_Material_P0_SideRight22_0_0' else 1.25
        if lo>=req+1e-7:boundssep199+=1;continue
        priority=0 if (n.startswith('Ref_Material_P0_') or n.endswith(':case') or 'Housing' in n or n.startswith('BatteryStrap')) else 1
        tasks199.append((priority,kn,n,a,b,lo,req))
tasks199.sort(key=lambda q:(q[0],q[1],q[2]));foreign199=[];wita199=None;witb199=None
if first199 is None:
    for _,kn,n,a,b,lo,req in tasks199:
        row=dict(new_part=kn,current_actor=n,required_mm=req,bbox_lower_mm=lo,source_valid=b.isValid(),function='MatchedsameP0railclamp metal/nativeframe sourceownnonpenetration ONLY' if req==0 else 'Otheractualcurrentfunction notOWNfromname')
        if not row['source_valid']:row['status']='SOURCE_INTEGRITY_OPEN'
        else:
            ga,ww,_=a.distToShape(b);row.update(actual_gap_mm=ga,witnesses=[[list(x),list(y)] for x,y in ww[:1]])
            if ga<1e-7:
                co=a.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            fail=(ga<req-1e-7) or (ga<1e-7 and (not row.get('common_valid',False) or row.get('common_mm3',0)>1e-7))
            row['status']='FULL_NEW_STACK_CURRENT_INTERFACE_HOLD' if fail else 'NEW_FULL_STACK_SEPARATED_OR_MATCHED_NATIVE_FIT'
        foreign199.append(row)
        if row['status'] not in ['NEW_FULL_STACK_SEPARATED_OR_MATCHED_NATIVE_FIT']:
            first199=dict(stage='FULL_CURRENT_STACK_NEIGHBOR',row=row);wita199=a;witb199=b;break
        if time.monotonic()-t199>10:break
ar199=OUT/'day07-five-D-caseback-frame-bearing-first-gate.breps.zip';assert not ar199.exists();ge199=[]
export199={**kit199,'ACTUAL_P0_SIDE':frame199,'ACTUAL_CURRENT_COMMON_RAIL_ROOT':rootpart199,**{'FROZEN_EXIT_'+q['wire']:s for q,s in zip(routes193,voids193)}}
if witb199 is not None:export199['FIRST_CURRENT_NEIGHBOR_WITNESS']=witb199
with zipfile.ZipFile(ar199,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(export199.items()):
        data=s.exportBrepToString().encode();en=f'{i:02d}.brep';z.writestr(en,data);ge199.append(dict(name=n,entry=en,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge199,current_world_no_XML=True,selected=False),indent=2))
p199=OUT/'day07-five-D-caseback-frame-bearing-first-gate.json';assert not p199.exists()
r199=dict(id=p199.stem,status='CASEBACK_WHOLE_MOUNT_FIRST_FALSIFIER_NO_NEW_CARRIER' if first199 else 'CASEBACK_BEARING_WHOLE_METAL_STAGE_RECEIVED_ACCESS_CARRIER_PENDING',proposal=prp199.name,proposal_sha256=hashlib.sha256(prp199.read_bytes()).hexdigest(),new_axis_mm=[33.75,-24.5],whole8_source_copies=quality199,actual_native_bearings=bearing199,actual_new_neck_current_printed_root=root199,all5_fullcapacity_vs_whole4metal=wirerows199,wire_bbox_separated=wirebbox199,new_actual_fullstack_neighbor_rows=foreign199,new_foreign_cursor=len(foreign199),new_foreign_total=len(tasks199),new_foreign_unreceived=[[kn,n] for _,kn,n,a,b,lo,req in tasks199[len(foreign199):]],whole_fullbounds_separated=boundssep199,first_falsifier=first199,old_wholeclamp_pose_candidate_exclusions=sorted(old199),actual_currentbase_unchanged=True,selected=False,N01_complete=False,new_casecarrier_not_built=True,initial_tool_access_NOT_yet_qualified=True,actualcut=None,archive=ar199.name,archive_sha256=hashlib.sha256(ar199.read_bytes()).hexdigest(),geometry=ge199,operation_seconds=time.monotonic()-t199,process_cpu_seconds=time.process_time()-c199,pid=os.getpid(),session_id=46493)
p199.write_bytes((json.dumps(r199,indent=2)+'\n').encode());print('DIFFERENT_CASEBACK_BEARING',r199['status'],'bearing',bearing199,'root',root199,'wire',len(wirerows199),'foreign',len(foreign199),'of',len(tasks199),'first',first199,'wall',r199['operation_seconds'],'CPU',r199['process_cpu_seconds'],hashlib.sha256(p199.read_bytes()).hexdigest(),flush=True)
