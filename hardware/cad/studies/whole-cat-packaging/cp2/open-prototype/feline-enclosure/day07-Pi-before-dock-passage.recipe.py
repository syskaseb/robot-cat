import time,json,hashlib,zipfile,os
t43=time.monotonic();c43=time.process_time();covers43={};tasks43=[]
# Complete enclosing profiles, not a claim that box overlap is actual component contact.
# Candidate path: lower bare board at left offset99 through open top, translate right99 atZ-5, raise5.
for n,s in poses42.items():
 b=s.BoundBox
 for stage,lo,hi in [('left_open_top_entry',[b.XMin-99,b.YMin,b.ZMin],[b.XMax-99,b.YMax,b.ZMax+35]),('right99_lower_entry',[b.XMin-99,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]),('raise5_into_source_mount',[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax+5])]:
  cover=Part.makeBox(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2],A.Vector(*lo));key=stage+'::'+n;covers43[key]=cover
  for other,q in fixed42.items():
   if bbox_lower_bound(cover.BoundBox,q.BoundBox)<=1.25:tasks43.append((key,other))
rows43=[];stop43=None
for key,other in tasks43:
 cover,q=covers43[key],fixed42[other]
 r=dict(stage_actor=key,fixed=other,cover_valid=cover.isValid(),fixed_valid=q.isValid())
 if not r['cover_valid'] or not r['fixed_valid']:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 else:
  try:
   gap,w,_=cover.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
   if gap<1e-7:
    co=cover.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
   own='raise5_into_source_mount' in key and ('NominalPCB' in key) and other in ['PAS:body','PAS:retained_upper']
   r['status']='CONSERVATIVE_OWN_MOUNT_BOUND_REQUIRES_EXACT_HOLE_NOT_NEW_FOREIGN' if own and gap<1.25 else 'FULL_PROFILE_PATH_SEPARATED125' if gap>=1.25-1e-7 else 'CONSERVATIVE_ENTRY_PATH_HOLD_NOT_ACTUAL_CONTACT'
  except Exception as ex:r.update(status='KERNEL_ERROR_OPEN_NOT_CONTACT',error=str(ex))
 rows43.append(r)
 if r['status']=='CONSERVATIVE_ENTRY_PATH_HOLD_NOT_ACTUAL_CONTACT':stop43=r;break
 if time.monotonic()-t43>45:break
ar43=OUT/'day07-Pi-before-dock-passage-cover-inputs.breps.zip';assert not ar43.exists();g43=[]
with zipfile.ZipFile(ar43,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate([(k,covers43[k]) for k in sorted({r['stage_actor'] for r in rows43})]+[(k,fixed42[k]) for k in sorted({r['fixed'] for r in rows43})]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);g43.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=g43,scope='Transient fullprofile assembly path bounds; no installed geometry'),indent=2)+'\n').encode())
result43=dict(id='day07-Pi-before-dock-full-profile-passage-gate',status='CONSERVATIVE_ENTRY_PATH_HOLD' if stop43 else 'ALL_PROPOSED_PATH_COVERS_RECEIVED_SCOPED' if len(rows43)==len(tasks43) else 'BOUNDED_CHUNK_PENDING',rows=rows43,cursor=len(rows43),total=len(tasks43),unreceived=len(tasks43)-len(rows43),stop=stop43,complete_fixed_count=len(fixed42),excluded=plan42['not_yet_installed']+plan42['not_yet_laid_flexible'],source_scope=pp42.name,source_scope_sha256=hashlib.sha256(pp42.read_bytes()).hexdigest(),archive=ar43.name,archive_sha256=hashlib.sha256(ar43.read_bytes()).hexdigest(),geometry=g43,operation_seconds=time.monotonic()-t43,process_cpu_seconds=time.process_time()-c43,not_actual_contact_from_cover_overlap=True,initial_assembly_NOT_accepted_until_functional_disposition=True,reverse_repair_NOT_received=True,selected=False,N01_complete=False)
p43=OUT/'day07-Pi-before-dock-full-profile-passage-gate.json';assert not p43.exists();p43.write_bytes((json.dumps(result43,ensure_ascii=False,indent=2)+'\n').encode());print('PI_BEFORE_DOCK_PATH',result43['status'],len(rows43),len(tasks43),stop43,result43['operation_seconds'],result43['process_cpu_seconds'],hashlib.sha256(p43.read_bytes()).hexdigest(),flush=True)
