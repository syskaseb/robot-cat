import time,json,os,zipfile,hashlib
t238=time.monotonic();c238=time.process_time();start238=len(rows237);assert start238==36 and first237 is None
for n,k in tasks237[start238:]:
 s=fields237[n];v=context230[k];q=dict(field=n,other=k,source_valid=v.isValid(),required_mm=1.25)
 if not q['source_valid']:q.update(status='SOURCE_INVALID_UNRESOLVED_NOT_CONTACT');rows237.append(q);first237=q;break
 g,ws,_=s.distToShape(v);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in ws[:1]],status='NEW_HIP_NORTH_CAPACITY_CLEAR' if g>=1.25-1e-7 else 'NEW_HIP_NORTH_ALLOCATED_HOLD')
 if g<1.25-1e-7:
  co=s.common(v);assert co.isValid();q.update(common_valid=True,allocated_common_mm3=co.Volume,meaning='Actualcapacity/currentfunctionalpartclearanceHOLD notdeliveredcontact/all3Dlayouts/stockshortage. Stopwholehypothesis/no secondfamily.');first237=q
 rows237.append(q);cursor.write_bytes((json.dumps(dict(rows=rows237,received=len(rows237),total=len(tasks237),first=first237,pending=None if first237 else (tasks237[len(rows237)] if len(rows237)<len(tasks237) else None)),indent=2)+'\n').encode())
 if first237 or time.monotonic()-t238>65:break
if first237:
 with zipfile.ZipFile(ar237,'a',zipfile.ZIP_DEFLATED) as z:
  # Manifest rewritten once below without duplicate ZIPmember names.
  pass
 oldentries={}
 with zipfile.ZipFile(ar237) as z:oldentries={n:z.read(n) for n in z.namelist() if n!='manifest.json'}
 ss=[('FIRST_CURRENT_ACTUAL:'+first237['other'],context230[first237['other']])]
 for n,s in ss:
  i=len(gg);f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat94-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();e=str(i)+'.brep';oldentries[e]=raw;gg.append(dict(actor=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 with zipfile.ZipFile(ar237,'w',zipfile.ZIP_DEFLATED) as z:
  for n,raw in oldentries.items():z.writestr(n,raw)
  z.writestr('manifest.json',(json.dumps(dict(geometry=gg),indent=2)+'\n').encode())
r237.update(status='WHOLE3PLUS6_FIRST_HIP_NORTH_FALSIFIER_STOP' if first237 else 'HIP_LOCAL_NORTH_BOUNDED_CURSOR_NOT_WHOLE_TRANSPORT',rows=rows237,received=len(rows237),unreceived=len(tasks237)-len(rows237),first_falsifier=first237,archive_sha256=hashlib.sha256(ar237.read_bytes()).hexdigest(),geometry=gg,operation_seconds=r237['operation_seconds']+time.monotonic()-t238,process_cpu_seconds=r237['process_cpu_seconds']+time.process_time()-c238,receive_blocks=[dict(first=0,last=start238-1),dict(first=start238,last=len(rows237)-1)],prior_36_keys_not_replayed=True);p237.write_bytes((json.dumps(r237,indent=2)+'\n').encode());print('SPLIT238_SAVED',first237,'received',len(rows237),'total',len(tasks237),'wallCPU',r237['operation_seconds'],r237['process_cpu_seconds'],'OWNER94_NATIVE_IDLE26064',flush=True)
