import time,json,hashlib,zipfile,os
t99=time.monotonic();cpu99=time.process_time();parentname99='CurrentFoundation:BankBedCurrent:1';parent99=ctx83[parentname99];assert parent99.isValid()
patch99=Part.Face(Part.makePolygon([A.Vector(x,y,52) for x,y in [(-53,68),(-45,68),(-45,76),(-53,76),(-53,68)]]));foot99=Part.makeBox(8,8,.75,A.Vector(-53,68,51.5));co99=parent99.common(foot99);surface99=parent99.common(patch99);missingface99=patch99.cut(surface99);assert co99.isValid() and surface99.isValid() and missingface99.isValid()
faceinfo99=[]
for i,f in enumerate(parent99.Faces):
    if f.BoundBox.ZLength<1e-6 and abs(f.CenterOfMass.z-52)<1e-6:
        faceinfo99.append(dict(index=i,area_mm2=f.Area,centre_mm=list(f.CenterOfMass),bounds_mm=saved_bounds(f),normal=list(f.normalAt(0,0))))
rootok99=abs(co99.Volume-16)<1e-5 and abs(surface99.Area-64)<1e-5 and missingface99.Area<1e-5
proposed99={'PROPOSED_SOURCE_KNEE:lower':local83(frame98.copy()),'PROPOSED_SOURCE_KNEE:upper':local83(cap96.copy())}
for n,s in {**{'LOOP:'+n:s for n,s in loops94.items()},**{'HEAD:'+n:s for n,s in heads94.items()},**{'PULL_TEMP:'+n:s for n,s in pulls94.items()},**{'TAIL_PARK:'+n:s for n,s in tails94.items()},**{'TAIL_TRANSPORT:'+n:s for n,s in transport95.items()},**{'FIXED_LOCAL_PROFILE:'+n:s for n,s in profiles93.items()}}.items():proposed99['PROPOSED_SOURCE_KNEE:'+n]=local83(s.copy())
ctx99={**ctx83,**proposed99};tasks99=[k for k,s in ctx99.items() if k!=parentname99 and bbox_lower_bound(foot99.BoundBox,s.BoundBox)<1.25];rows99=[]
if rootok99:
    for k in tasks99:
        q=ctx99[k];r=dict(other=k,source_valid=q.isValid())
        if q.isValid():
            gap,w,_=foot99.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='ACTUAL_ROOT_NEIGHBOR_SEPARATED125' if gap>=1.25-1e-7 else 'ACTUAL_ROOT_NEIGHBOR_HOLD')
            if gap<1e-7:
                c=foot99.common(q);r.update(common_valid=c.isValid(),common_mm3=c.Volume if c.isValid() else None)
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        rows99.append(r);print('BODY99_NEIGHBOR',r,flush=True)
        if r['status']!='ACTUAL_ROOT_NEIGHBOR_SEPARATED125':break
ar99=OUT/'day07-SOURCE-current-bankbed-root-first-gate.breps.zip';assert not ar99.exists();ge99=[]
with zipfile.ZipFile(ar99,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('ACTUAL_CURRENT:'+parentname99,parent99),('PROPOSED_ROOT:8x8foot',foot99),('ACTUAL:foot_parent_common',co99),('ACTUAL:contact_surface',surface99),('ACTUAL:missing_contact_surface',missingface99)]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge99.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s) if not s.isNull() else None,volume_mm3=s.Volume,area_mm2=s.Area,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge99,scope='Actualbf0311currentBankOpenSpineparent/rootcandidate ONLY; NOTbaseActor0497, no newselectedmaterial'),indent=2)+'\n').encode())
r99=dict(id='day07-SOURCE-current-bankbed-root-first-gate',proposal='day07-SOURCE-bodylanding-and-whole-approach-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-bodylanding-and-whole-approach-proposal.json').read_bytes()).hexdigest(),status='ACTUAL_BANKBED_UNDERSIDE_ROOT_SCOPE_RECEIVED' if rootok99 and len(rows99)==len(tasks99) and all(r['status']=='ACTUAL_ROOT_NEIGHBOR_SEPARATED125' for r in rows99) else 'ACTUAL_BANKBED_ROOT_OR_NEIGHBOR_FALSIFIED',
 source_parent=parentname99,source_current_pin='bf0311c029d0caa23b28387114a5b8f0621cfd0c79ec72a25074733e5c80ff99',source_role='CurrentloadedBankOpenSpine+2cuts; sourceframealreadyworld/noXML, notbaseActor0497.',actual_valid=parent99.isValid(),actual_bounds_mm=saved_bounds(parent99),actual_parent_native_export_sha256=ge99[0]['sha256'],actual_parent_volume_mm3=parent99.Volume,source_bottom_faces=faceinfo99,
 root=dict(foot_bounds_mm=saved_bounds(foot99),source_common_valid=co99.isValid(),source_common_mm3=co99.Volume,expected_full_embed_mm3=16,source_contact_area_mm2=surface99.Area,required_full_contact_area_mm2=64,missing_contact_area_mm2=missingface99.Area,full_material_contact=rootok99,no_bbox_root_claim=True),
 current_context_base=1419,proposed_moving_Knee_attachments_included=len(proposed99),proposed_attachment_owner='Motion_RL_Knee',oldrejectedholders_excluded=True,rows=rows99,cursor=len(rows99),total=len(tasks99),unreceived=len(tasks99)-len(rows99),
 group_R_lengths_motion='NOT_RUN_BEFORE_ROOT_ACCEPTANCE' if not rootok99 else 'NEXT_NEW_GROUP_SOURCE_APPROACH_ONLY',all_actual_A_U_minimumfit_slack=None,no_new_landing_support_detail=True,selected=False,N01_complete=False,current1292_effective1311_rest108_unchanged=True,
 archive=ar99.name,archive_sha256=hashlib.sha256(ar99.read_bytes()).hexdigest(),geometry=ge99,operation_seconds=time.monotonic()-t99,process_cpu_seconds=time.process_time()-cpu99,pid=os.getpid(),session_id=46493)
p99=OUT/'day07-SOURCE-current-bankbed-root-first-gate.json';assert not p99.exists();p99.write_bytes((json.dumps(r99,ensure_ascii=False,indent=2)+'\n').encode());print('BODY99_FINAL',r99['status'],r99['root'],len(rows99),len(tasks99),r99['operation_seconds'],r99['process_cpu_seconds'],hashlib.sha256(p99.read_bytes()).hexdigest(),flush=True)
