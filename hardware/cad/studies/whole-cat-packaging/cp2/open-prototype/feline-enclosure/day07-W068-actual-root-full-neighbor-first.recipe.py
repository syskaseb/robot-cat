import time,json,hashlib,zipfile,os
t132=time.monotonic();c132=time.process_time();pp132=OUT/'day07-W068-whole-rooted-pressure-leading-interface-proposal.json';pr132=json.loads(pp132.read_bytes());frame132=ctx121['Ref_Material_P0_FrameFront20_0_0'];x132=-85.4575664610479
# Actual chosen face patch and substrate; no fusion into retained source frame.
poly=Part.makePolygon([A.Vector(x132,y,z) for y,z in [(-30,18),(-20,18),(-20,28),(-30,28),(-30,18)]]);patch132=Part.Face(Part.Wire(poly.Edges));probe132=Part.makeBox(.1,10,10,A.Vector(x132+.01,-30,18));common132=frame132.common(probe132);contact132=frame132.Faces[16].common(patch132);assert common132.isValid() and contact132.isValid()
back132=Part.makeBox(x132+89,10,10,A.Vector(-89,-30,18));feed132=Part.makeBox(6,2,3.3,A.Vector(-88,-16,23));feedmaterial132=feed132.common(frame132);assert feedmaterial132.isValid();first132=None;rows132=[]
if abs(common132.Volume-10)>1e-6 or abs(contact132.Area-100)>1e-5:first132=dict(kind='ACTUAL_FRAME_PATCH_NOT_FULL_MATERIAL',substrate_common_mm3=common132.Volume,expected_mm3=10,contact_area_mm2=contact132.Area,required_mm2=100)
if first132 is None and feedmaterial132.Volume>1e-7:first132=dict(kind='ACTUAL_FRAME_FEED_WINDOW_OCCUPIED',common_mm3=feedmaterial132.Volume)
parts132=[('ROOT_BACKPAD_FUNCTIONAL_ENVELOPE',back132),('FULL_ROOT_TIE_FEED_FIELD',feed132)];tasks132=[]
if first132 is None:
 for n,sh in parts132:
  for k,v in ctx121.items():
   if k=='Ref_Material_P0_FrameFront20_0_0':continue
   if bbox_lower_bound(sh.BoundBox,bounds126[k])<1.25:tasks132.append((n,k))
 tasks132.sort(key=lambda q:(0 if q[0]=='ROOT_BACKPAD_FUNCTIONAL_ENVELOPE' else 1,q[1]));look132=dict(parts132)
 for n,k in tasks132:
  sh=look132[n];v=ctx121[k];row=dict(part=n,other=k,source_valid=v.isValid(),field_valid=sh.isValid())
  if row['source_valid']:
   gap,ww,_=sh.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='ROOT_INTERFACE_NEIGHBOR_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_ROOT_INTERFACE_HOLD_FUNCTION_PENDING')
   if gap<1e-7:
    co=sh.common(v);row.update(common_valid=co.isValid(),new_allocated_common_mm3=co.Volume if co.isValid() else None)
  else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
  rows132.append(row)
  if row['status']!='ROOT_INTERFACE_NEIGHBOR_SEPARATED125':first132=row;break
  if time.monotonic()-t132>15:break
oldroot132=[k for k in ctx121 if k!='W068/single/end:0:saddle' and bbox_lower_bound(ctx121['W068/single/end:0:saddle'].BoundBox,bounds126[k])<.05]
ar132=OUT/'day07-W068-actual-frame-root-first-gate.breps.zip';assert not ar132.exists();ge132=[];items132=[('ACTUAL_FRAME_FRONT20',frame132),('CHOSEN_FACE_PATCH',patch132),('ACTUAL_SUBSTRATE_PROBE',probe132),('ACTUAL_CONTACT_PATCH',contact132),('ROOT_BACKPAD_FUNCTIONAL_ENVELOPE',back132),('FULL_ROOT_TIE_FEED_FIELD',feed132)]
if first132 and first132.get('other'):items132.append(('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first132['other']]))
if first132 and first132.get('new_allocated_common_mm3') is not None:items132.append(('NEW_ALLOCATED_COMMON',co))
with zipfile.ZipFile(ar132,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(n,sh) in enumerate(items132):
  raw=sh.exportBrepToString().encode();en=str(i)+'.brep';zz.writestr(en,raw);ge132.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=sh.isValid(),volume_mm3=sh.Volume,area_mm2=sh.Area,bounds_mm=saved_bounds(sh) if not sh.isNull() else None))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=ge132),indent=2)+'\n').encode())
r132=dict(id='day07-W068-actual-frame-root-first-gate',status='W068_WHOLE_MECHANICAL_ROOT_FIRST_FALSIFIER_HOLD' if first132 else 'W068_FRAME_ROOT_LOCAL_PREFLIGHT_RECEIVED_WHOLE_KIT_NOT_BUILT',proposal=pp132.name,proposal_sha256=hashlib.sha256(pp132.read_bytes()).hexdigest(),old_W068_saddle_material_contact_bbox_candidates=oldroot132,old_saddle_rigid_root_NOT_proven=True,actual_frame_face=16,actual_patch_area_mm2=contact132.Area,actual_substrate_common_mm3=common132.Volume,full_frame_feed_material_common_mm3=feedmaterial132.Volume,rows=rows132,cursor=len(rows132),total=len(tasks132),unreceived=len(tasks132)-len(rows132),first_falsifier=first132,archive=ar132.name,archive_sha256=hashlib.sha256(ar132.read_bytes()).hexdigest(),geometry=ge132,scope='NewownFrameFront20bearingpatch mechanicalcontact onlymappedframe; allotherretainedgeometryforeign1.25. Thisisfirstroot/accessgate, notactualarm/pressure/fullstockinstall/wholemount acceptance.',new_pressure_clamp_or_arm_built=False,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t132,process_cpu_seconds=time.process_time()-c132,pid=os.getpid(),session_id=46493)
rp132=OUT/'day07-W068-actual-frame-root-first-gate.json';assert not rp132.exists();rp132.write_bytes((json.dumps(r132,indent=2)+'\n').encode());print('BODY132',r132['status'],'patch',contact132.Area,'substrate',common132.Volume,'feed',feedmaterial132.Volume,'rows',len(rows132),len(tasks132),'first',first132,'wall',r132['operation_seconds'],'CPU',r132['process_cpu_seconds'],flush=True);print('OWNER66_IDLE',os.getpid(),flush=True)
