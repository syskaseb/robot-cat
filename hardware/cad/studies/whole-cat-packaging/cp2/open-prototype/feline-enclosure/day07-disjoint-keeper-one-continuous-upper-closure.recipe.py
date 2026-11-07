import time,json,hashlib,zipfile,os
t228=time.monotonic();c228=time.process_time();assert first227 is None
source228=upper227;bb228=source228.BoundBox;startbox228=Part.makeBox(bb228.XLength+.02,bb228.YLength+.02,bb228.ZLength+.02,A.Vector(bb228.XMin-.01,bb228.YMin-.01,bb228.ZMin-.01));missing228=source228.cut(startbox228);assert missing228.isValid() and missing228.Volume<1e-7
sweepbox228=Part.makeBox(bb228.XLength+.02,bb228.YLength+.02,bb228.ZLength+4.02,A.Vector(bb228.XMin-.01,bb228.YMin-.01,bb228.ZMin-.01))
staged228=['PROPOSED_D5_WHOLE_UPPER','PROPOSED_D5_WHOLE145LOOP','PROPOSED_D5_FULLHEAD','PROPOSED_D5_FULLTAIL_CAPACITY'];context228={n:s for n,s in context210.items() if n not in staged228 and n!='Station:D_FL:case'}
candidate228=[(n,s) for n,s in context228.items() if bbox_lower_bound(sweepbox228.BoundBox,s.BoundBox)<1.25]
farcount228=len(context228)-len(candidate228)
ownrefs228={}
for i,y in enumerate([-25.75,-21,-16.25,-11.5,-6.75]):
    s=nom181[i].fuse(Part.makeCylinder(1.55,.25,A.Vector(57.5,y,48.5),A.Vector(1,0,0)));assert s.isValid();ownrefs228['OWN_D'+str(i+1)+'_FULL9_PLUS_EXISTING025']=s
for i,s in enumerate(nominal193):ownrefs228['OWN_MODELED_C1_LOCAL_CONTINUATION_'+str(i)]=s
rows228=[];faceguards228=[];skin228=[];first228=None;cursor228=0;p228=OUT/'day07-D5-exact-disjoint-upper-continuous-closure-cursor.json';assert not p228.exists()
def save228():
    r=dict(id=p228.stem,status='ACTUAL_CONTINUOUS_UPPER_CLOSURE_FIRST_HOLD' if first228 else ('ACTUAL_CONTINUOUS_UPPER_CLOSURE_RECEIVED_SCOPED' if cursor228==len(source228.Faces) else 'IN_PROGRESS_CONTINUOUS_UPPER_SKIN'),cursor=cursor228,total_faces=len(source228.Faces),analytic_bound_contains_actual_upper_missing_mm3=missing228.Volume,actual_lower_unchanged=True,exact_source_case_relative_sweep_already_received0=True,staged_initial_open_selected145_roles=staged228[1:],staging_reason='Initial closure is OPEN while upperplaced; same whole145loop/head/66.001640 remainder is closed onlyafterseat. No fakeunlock/trim/newstock; source unchanged operating stock proofs retained.',superseded_old_upper=staged228[0],far_current_context_count=farcount228,near_current_context_names=[n for n,s in candidate228],whole_current_context_count=len(context228),method='Whole actual source upper + boundary-face extrusions fromZ0to4 cover continuous translated solid: an entering point is either in initial solid or crosses its swept boundary. Plane faces parallel toZ and axialZcylinders have zero-volume sweeps; remaining actual face extrusions must be valid. Same global on-shape-guarded source AABB translated+4 supplies conservative all-pose broadphase; no new partial-torus defaultbbox used for rejection.',own_reference_roles=list(ownrefs228),own_reference_meaning='Full5held9+.25 already-existing and named actual modeled localC1post9 leading continuations only, r1.55 nominal. Need nonpenetration with this own functional pressure/leading material; no foreignwire exception or wholefreewire rigidmodel. Localhazard is closing keeper/pressurethroughthese source channels; regionbox cannot decide exact matched parting contact.',face_guards=faceguards228,rows=rows228,first_falsifier=first228,selected=False,N01_complete=False,whole_bank_retention_2stock_global_OPEN=True,no_old_motion_or_44_replay=True,operation_seconds=time.monotonic()-t228,process_cpu_seconds=time.process_time()-c228,pid=os.getpid(),session_id=46493)
    tmp=p228.with_suffix('.tmp');tmp.write_bytes((json.dumps(r,indent=2)+'\n').encode());os.replace(tmp,p228);return r
for i,f in enumerate(source228.Faces):
    kind=type(f.Surface).__name__;parallel=False
    if kind=='Plane':
        u,U,v,V=f.ParameterRange;parallel=abs(f.normalAt((u+U)/2,(v+V)/2).z)<1e-9
    elif kind=='Cylinder':parallel=abs(abs(f.Surface.Axis.z)-1)<1e-9
    if parallel:faceguards228.append(dict(face=i,kind=kind,parallel_zero_volume_sweep=True));cursor228=i+1;continue
    ex=f.extrude(A.Vector(0,0,4));guard=dict(face=i,kind=kind,valid=ex.isValid(),solids=len(ex.Solids),volume_mm3=ex.Volume);faceguards228.append(guard)
    if not ex.isValid() or (not ex.Solids and abs(ex.Volume)>1e-9) or ex.Volume<-1e-7:first228=dict(stage='NEW_ACTUAL_FACE_EXTRUSION_VALIDITY_INPUT_HOLD_NOT_CONTACT',guard=guard);break
    if not ex.Solids:cursor228=i+1;continue
    skin228.append((i,ex));co=ex.common(lower227)
    row=dict(face=i,actor='ACTUAL_FIXED_LOWER',required='VALID_NO_INTERPRINT_PENETRATION_MATCHED_OWN_CONTACT_ALLOWED',valid_common=co.isValid(),common_mm3=co.Volume);rows228.append(row)
    if not co.isValid() or co.Volume>1e-7:first228=dict(stage='CONTINUOUS_UPPER_VS_FIXED_LOWER_MATERIAL',row=row);break
    for n,s in ownrefs228.items():
        co=ex.common(s);row=dict(face=i,actor=n,required='VALID_NOMINAL_JACKET_NONPENETRATION_OWN_MODELED_CHANNEL',valid_common=co.isValid(),common_mm3=co.Volume);rows228.append(row)
        if not co.isValid() or co.Volume>1e-7:first228=dict(stage='CONTINUOUS_UPPER_LOCAL_SOURCE_CHANNEL_JACKET',row=row);break
    if first228:break
    for n,s in candidate228:
        ga=ex.distToShape(s)[0];row=dict(face=i,actor=n,actual_valid_skin_gap_mm=ga,required_foreign_mm=1.25);rows228.append(row)
        if ga<1.25-1e-7:first228=dict(stage='CONTINUOUS_UPPER_RETAINED_CURRENT_FOREIGN',row=row);break
    if first228:break
    cursor228=i+1
    if i%8==0:save228()
r228=save228()
ar228=OUT/'day07-D5-disjoint-upper-continuous-initial-closure-witness.breps.zip';assert not ar228.exists();ge228=[]
with zipfile.ZipFile(ar228,'w',zipfile.ZIP_DEFLATED) as z:
    ss=[('ACTUAL_DISJOINT_UPPER_AT_CLOSED_POSITION',source228),('ON_SHAPE_GUARDED_CONTINUOUS_UPPER_GLOBAL_COVER',sweepbox228)]
    if skin228:ss.append(('LAST_RECEIVED_ACTUAL_FACE_SWEEP_'+str(skin228[-1][0]),skin228[-1][1]))
    if first228 and 'row' in first228:
        n=first228['row']['actor'];s=lower227 if n=='ACTUAL_FIXED_LOWER' else ownrefs228[n] if n in ownrefs228 else context228[n];ss.append((n,s))
    for i,(n,s) in enumerate(ss):
        f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat91-closure-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();en=str(i)+'.brep';z.writestr(en,raw);ge228.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge228),indent=2)+'\n').encode())
r228.update(archive=ar228.name,archive_sha256=hashlib.sha256(ar228.read_bytes()).hexdigest(),geometry=ge228);p228.write_bytes((json.dumps(r228,indent=2)+'\n').encode());print('PARTITION228_CONTINUOUS_CLOSURE',r228['status'],first228,'cursor',cursor228,'of',len(source228.Faces),'rows',len(rows228),'foreignnear',r228['near_current_context_names'],'seconds',r228['operation_seconds'],r228['process_cpu_seconds'],'OWNER91_SAVED_IDLE',os.getpid(),flush=True)
