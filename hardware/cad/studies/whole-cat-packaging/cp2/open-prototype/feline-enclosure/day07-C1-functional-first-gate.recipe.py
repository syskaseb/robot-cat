import time,json,hashlib,zipfile,os
st135=time.monotonic();cpu135=time.process_time();p135=OUT/'day07-W068-inboard-overframe-C1-whole-interface-proposal.json';q135=json.loads(p135.read_bytes());fr135=ctx121[q135['root']['actor']];xx135=q135['root']['face_X_mm'];zz135=q135['root_loop']['plane_Z_mm']
def box135(bb):
 lo,hi=bb;return Part.makeBox(*[hi[j]-lo[j] for j in range(3)],A.Vector(*lo))
rect135=Part.Face(Part.Wire(Part.makePolygon([A.Vector(xx135,y,z) for y,z in [(-30,zz135-5),(-20,zz135-5),(-20,zz135+5),(-30,zz135+5),(-30,zz135-5)]]).Edges));contact135=fr135.Faces[99].common(rect135);pad135=contact135.extrude(A.Vector(3.5,0,0));probe135=box135([[xx135-.11,-30,zz135-5],[xx135-.01,-20,zz135+5]]);sub135=fr135.common(probe135);feed135=box135(q135['root_loop']['full_feed_field_mm']);up135=box135(q135['load_members']['upstand_mm']);bridge135=box135(q135['load_members']['overframe_bridge_mm']);rh135=box135([[v-3 for v in q135['root_loop']['root_head_centre_mm']],[v+3 for v in q135['root_loop']['root_head_centre_mm']]])
assert all(sh.isValid() and not sh.isNull() for sh in [contact135,pad135,sub135,feed135,up135,bridge135,rh135]);parts135=[('ROOT_SOURCE_CONFORMING_PAD',pad135),('ROOT_FULL_FEED_3_3_BY_2',feed135),('OVERFRAME_UPSTAND',up135),('OVERFRAME_BRIDGE',bridge135),('ROOT_FULL6_HEAD',rh135)];rows135=[];first135=None;lastco135=None
# Actual source-frame material contact is permitted; material intersection in a planned sleeve or bridge is not.
for n,sh in parts135:
 co=sh.common(fr135);gap,ww,_=sh.distToShape(fr135);row=dict(part=n,other=q135['root']['actor'],valid=sh.isValid(),source_valid=fr135.isValid(),gap_mm=gap,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,witnesses=[[list(a),list(b)] for a,b in ww[:1]],classification='ACTUAL_NAMED_MECHANICAL_BEARING_OR_ACCESS_NOT_FOREIGN_WAIVER')
 row['status']='SOURCE_FRAME_MATERIAL_CLEAR_OR_BOUNDARY_CONTACT' if co.isValid() and co.Volume<1e-7 else 'CURRENT_FRAME_MATERIAL_INTERFERENCE_HOLD';rows135.append(row)
 if row['status'].endswith('HOLD'):first135=row;lastco135=co;break
newtasks135=[]
if first135 is None:
 for n,sh in parts135:
  for k,v in ctx121.items():
   if k==q135['root']['actor'] or k in ['W068/single/end:0:saddle','W068/single/end:0:band_budget','W068/single/end:0:head_budget']:continue
   if bbox_lower_bound(sh.BoundBox,bounds126[k])<1.25:newtasks135.append((n,k))
 for n,k in newtasks135:
  sh=dict(parts135)[n];v=ctx121[k];row=dict(part=n,other=k,valid=sh.isValid(),source_valid=v.isValid())
  if not v.isValid():row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
  else:
   gap,ww,_=sh.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='FOREIGN_SEPARATED125' if gap>=1.25-1e-7 else 'FOREIGN_INTERFACE_HOLD')
   if gap<1e-7:
    co=sh.common(v);lastco135=co;row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  rows135.append(row)
  if row['status']!='FOREIGN_SEPARATED125':first135=row;break
  if time.monotonic()-st135>15:break
items135=[('ACTUAL_CURRENT_FRAME',fr135),('ACTUAL_FACE99_CONTACT_PATCH',contact135),('ACTUAL_SUBSTRATE',sub135)]+parts135
if first135 and lastco135 is not None:items135.append(('ACTUAL_FIRST_MATERIAL_INTERSECTION',lastco135))
ar135=OUT/'day07-W068-inboard-overframe-C1-first-functional-gate.breps.zip';assert not ar135.exists();ge135=[]
with zipfile.ZipFile(ar135,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items135):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge135.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,area_mm2=s.Area,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge135),indent=2)+'\n').encode())
r135=dict(id='day07-W068-inboard-overframe-C1-first-functional-gate',status='C1_FULL_LOADPATH_PREFLIGHT_HOLD_NO_THIRD_LOCAL_VARIANT' if first135 else 'C1_LOCAL_ROOT_ENVELOPE_RECEIVED_NOT_FULL_KIT',proposal=p135.name,proposal_sha256=hashlib.sha256(p135.read_bytes()).hexdigest(),face99_contact_area_mm2=contact135.Area,actual_substrate_mm3=sub135.Volume,root_pad_volume_mm3=pad135.Volume,rows=rows135,first_falsifier=first135,foreign_candidate_keys=len(newtasks135),foreign_rows_received=sum(x.get('classification') is None for x in rows135),all_pressure_tail_stock_installation_unreceived=True,scope='Planned FULL pad/upstand/bridge/feed/head functional envelopes before detailed production material. Actual frame boundary bearing allowed; positive retained-frame material penetration is not removed by shared ownership. No old pair/root/passage/motion replay.',selected=False,new_current_parent=False,N01_complete=False,archive=ar135.name,archive_sha256=hashlib.sha256(ar135.read_bytes()).hexdigest(),geometry=ge135,operation_seconds=time.monotonic()-st135,process_cpu_seconds=time.process_time()-cpu135,pid=os.getpid(),session_id=46493)
rp135=OUT/'day07-W068-inboard-overframe-C1-first-functional-gate.json';assert not rp135.exists();rp135.write_bytes((json.dumps(r135,indent=2)+'\n').encode());print('BODY135',r135['status'],'contact',contact135.Area,'substrate',sub135.Volume,'first',first135,'wall',r135['operation_seconds'],'CPU',r135['process_cpu_seconds'],flush=True);print('OWNER67_IDLE',os.getpid(),flush=True)
