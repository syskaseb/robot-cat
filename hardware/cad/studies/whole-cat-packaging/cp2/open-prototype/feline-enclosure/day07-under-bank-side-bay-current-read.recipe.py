import time,json,hashlib,os
st159=time.monotonic();cp159=time.process_time()
roi159=[[-137.45,35,-44.75],[110,82,51.0]];rbox159=box153(roi159);relevant159=[];sections159=[]
for n,s in ctx121.items():
 if bbox_lower_bound(s.BoundBox,rbox159.BoundBox)>1e-7:continue
 relevant159.append(dict(name=n,valid=s.isValid(),bounds_mm=saved_bounds(s),kind='SOURCE_ROLE_CLASSIFICATION_REQUIRED',material_source_same_current1292=n in Current35 and s.isSame(Current35[n])))
# Actual retained sections; no distance/common of old accepted pairs, no claim AABB is free space.
for yy in [40,55,75]:
 pl=Part.Face(Part.makePolygon([A.Vector(x,yy,z) for x,z in [(-138,-45),(111,-45),(111,52),(-138,52),(-138,-45)]]))
 for q in relevant159:
  n=q['name'];s=ctx121[n]
  if s.BoundBox.YMin>yy or s.BoundBox.YMax<yy:continue
  if not q['valid']:continue
  sec=s.section(pl)
  if sec.Edges:sections159.append(dict(name=n,Y_mm=yy,curves_xz=[[[v.x,v.z] for v in e.discretize(Deflection=.12)] for e in sec.Edges]))
  if time.monotonic()-st159>16:break
 if time.monotonic()-st159>16:break
rec159=[dict(name=n,bounds_mm=saved_bounds(s)) for n,s in ctx121.items() if n.startswith(('CurrentDFL:','CurrentFLG:','Station:Bank:W020/','Station:Bank:W022/','Station:Bank:W024/','Station:D_FL:','Station:FL_G:')) and any(w in n.lower() for w in ['cap','head','case','split','wire','band'])]
r159=dict(id='day07-SOURCE-under-bank-side-bay-actual-input-read',status='ACTUAL_FIXED_NEIGHBOR_BOUNDS_AND_SECTIONS_NOT_FREE_SPACE_ACCEPTANCE',roi_mm=roi159,fixed_candidates=relevant159,sections=sections159,receiver_source_parts=rec159,actual_context_count=len(ctx121),proposed_moving21_not_retired=True,rest108_not_retired=True,no_old_pairs_or_motion_replayed=True,operation_seconds=time.monotonic()-st159,process_cpu_seconds=time.process_time()-cp159,pid=os.getpid(),session_id=46493)
p159=OUT/(r159['id']+'.json');assert not p159.exists();p159.write_bytes((json.dumps(r159,indent=2)+'\n').encode());print('BODY159',len(relevant159),'candidates',len(sections159),'sections',r159['operation_seconds'],r159['process_cpu_seconds'],flush=True);print('OWNER74_IDLE',os.getpid(),flush=True)
