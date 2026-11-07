import time,json,hashlib,zipfile,os
t133=time.monotonic();c133=time.process_time();face133=frame132.Faces[16];wire133=[]
for i,w in enumerate(face133.Wires):
 b=w.optimalBoundingBox(False,False);wire133.append(dict(index=i,length_mm=w.Length,bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],vertices_YZ_mm=[[v.Point.y,v.Point.z] for v in w.Vertexes]))
old_root_claim133='Raw100mm2rectangle isNOTstrengthcriterion. Actualsource-conforming88.771555contact ispositiveusablematerial/read only, not100 or mountPASS. Independentactualfeedcommon7.548396 remainsallocationHOLD. No pad/fieldcoordinates changed.'
tasks133=[k for k in ctx121 if k!='Ref_Material_P0_FrameFront20_0_0' and bbox_lower_bound(back132.BoundBox,bounds126[k])<1.25];tasks133.sort();rows133=[];first133=None;co133=None
for k in tasks133:
 sh=ctx121[k];q=dict(part='SAME_ROOT_BACKPAD_FUNCTIONAL_ENVELOPE',other=k,source_valid=sh.isValid(),field_valid=back132.isValid())
 if q['source_valid']:
  gap,ww,_=back132.distToShape(sh);q.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='ROOT_NEIGHBOR_SEPARATED125' if gap>=1.25-1e-7 else 'ROOT_NEIGHBOR_ACTUAL_ALLOCATION_HOLD')
  if gap<1e-7:
   co133=back132.common(sh);q.update(common_valid=co133.isValid(),new_common_mm3=co133.Volume if co133.isValid() else None)
 else:q['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 rows133.append(q)
 if q['status']!='ROOT_NEIGHBOR_SEPARATED125':first133=q;break
 if time.monotonic()-t133>12:break
sections133=[]
plane=Part.makePlane(160,120,A.Vector(x132, -60,0),A.Vector(1,0,0));section133=frame132.section(plane)
for e in section133.Edges:
 ps=e.discretize(Deflection=.1)
 if len(ps)>1:sections133.append([[p.y,p.z] for p in ps])
ar133=OUT/'day07-W068-root-independent-neighbor-proof.breps.zip';assert not ar133.exists();geo133=[];items=[('SAME_ROOT_BACKPAD',back132)]
if first133:items.append(('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first133['other']]))
if co133 is not None:items.append(('NEW_COMMON',co133))
with zipfile.ZipFile(ar133,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(n,sh) in enumerate(items):
  raw=sh.exportBrepToString().encode();en=str(i)+'.brep';zz.writestr(en,raw);geo133.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=sh.isValid(),volume_mm3=sh.Volume,bounds_mm=saved_bounds(sh)))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=geo133),indent=2)+'\n').encode())
r133=dict(id='day07-W068-root-independent-neighbor-and-window-read',status='W068_ROOT_NEIGHBOR_ACTUAL_HOLD' if first133 else 'W068_ROOT_NEIGHBORS_SCOPE_RECEIVED_FEED_STILL_HOLD',same_root_proposal_no_geometry_change=True,material_criterion_disposition=old_root_claim133,actual_frame_face_source_wires=wire133,frame_YZ_section_x_mm=x132,actual_frame_YZ_section_curves=sections133,rows=rows133,cursor=len(rows133),total=len(tasks133),unreceived=len(tasks133)-len(rows133),first_falsifier=first133,archive=ar133.name,archive_sha256=hashlib.sha256(ar133.read_bytes()).hexdigest(),geometry=geo133,new_arm_pressure_kit_NOT_built=True,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t133,process_cpu_seconds=time.process_time()-c133)
p133=OUT/'day07-W068-root-independent-neighbor-and-window-read.json';assert not p133.exists();p133.write_bytes((json.dumps(r133,indent=2)+'\n').encode());print('BODY133',r133['status'],len(rows133),len(tasks133),first133,'wires',len(wire133),'wall',r133['operation_seconds'],'CPU',r133['process_cpu_seconds'],flush=True);print('OWNER66_IDLE',os.getpid(),flush=True)
