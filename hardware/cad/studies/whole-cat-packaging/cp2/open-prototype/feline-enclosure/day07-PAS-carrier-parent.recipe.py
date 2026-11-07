import time,json,hashlib,zipfile,os
t46=time.monotonic();c46=time.process_time();pas46=['PAS:retained_upper','PAS:body']
exclude46=pi36|set(pas46)|{'PAS:band','PAS:head'}
fixed46={n:s for n,s in Current35.items() if n not in exclude46};tasks46=[]
for p in pas46:
 for n,s in fixed46.items():
  if bbox_lower_bound(Current35[p].BoundBox,s.BoundBox)<=1.25:tasks46.append((p,n))
rows46=[]
for p,n in tasks46:
 a,b=Current35[p],fixed46[n];r=dict(a=p,b=n,a_valid=a.isValid(),b_valid=b.isValid())
 if r['a_valid'] and r['b_valid']:
  gap,w,_=a.distToShape(b);r.update(gap_mm=gap,witnesses=[[list(x),list(y)] for x,y in w[:1]])
  if gap<1e-7:
   co=a.common(b);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  r['status']='SEPARATED125' if gap>=1.25-1e-7 else 'ACTUAL_PARENT_OR_FOREIGN_INTERFACE_REQUIRES_SOURCE_DISPOSITION'
 else:r['status']='INVALID_SOURCE_NOT_CONTACT'
 rows46.append(r)
ab=Current35[pas46[0]].common(Current35[pas46[1]])
ar46=OUT/'day07-PAS-upper-carrier-fixed-interface-inputs.breps.zip';assert not ar46.exists();geo46=[]
with zipfile.ZipFile(ar46,'w',zipfile.ZIP_DEFLATED) as z:
 for i,n in enumerate(pas46+sorted({n for _,n in tasks46})):
  s=Current35[n];raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);geo46.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=geo46,scope='One actual current PAS parent-interface inventory, no sourcepose motion'),indent=2)+'\n').encode())
rr46=dict(id='day07-PAS-upper-carrier-current-fixed-interface-gate',rows=rows46,cursor=len(rows46),total=len(tasks46),full_neighborhood_count=len(fixed46),excluded_source_Pi=sorted(pi36),excluded_source_stock=dict(actors=['PAS:band','PAS:head'],physical_units=1,reason='Source plan_feline_power_axial_saddle generates complete power grip kit; one-way tie is not yet closed for initial assembly and must be renewed if disturbed in rare repair, not a permanent structural parent.'),PAS_body_retainedupper_actual_join=dict(valid=ab.isValid(),common_mm3=ab.Volume if ab.isValid() else None),archive=ar46.name,archive_sha256=hashlib.sha256(ar46.read_bytes()).hexdigest(),geometry=geo46,operation_seconds=time.monotonic()-t46,process_cpu_seconds=time.process_time()-c46,selected=False,N01_complete=False)
p46=OUT/'day07-PAS-upper-carrier-current-fixed-interface-gate.json';assert not p46.exists();p46.write_bytes((json.dumps(rr46,ensure_ascii=False,indent=2)+'\n').encode());print('PAS46_CURRENT_PARENTS',rows46,rr46['PAS_body_retainedupper_actual_join'],rr46['operation_seconds'],rr46['process_cpu_seconds'],hashlib.sha256(p46.read_bytes()).hexdigest(),flush=True)
