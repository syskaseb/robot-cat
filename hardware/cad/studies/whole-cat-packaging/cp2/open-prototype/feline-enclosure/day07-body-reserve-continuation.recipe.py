import time,json,hashlib
t122=time.monotonic();c122=time.process_time();new122=[]
for n,k in tasks121[len(rows121):len(rows121)+3]:
 s=lookup121[n];v=ctx121[k];q=dict(region=n,other=k,source_valid=v.isValid(),field_valid=s.isValid())
 if q['source_valid']:
  g,w,_=s.distToShape(v);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='BODY_RESERVE_REGION_SEPARATED125' if g>=1.25-1e-7 else 'ALLOCATED_BODY_REGION_HOLD_NOT_DELIVEREDWIRECONTACT')
 else:q['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
 rows121.append(q);new122.append(q)
 if q['status']!='BODY_RESERVE_REGION_SEPARATED125':first121=q;break
 if time.monotonic()-t122>8:break
r122=dict(id='day07-SOURCE-FL2-body-reserve-continuation',previous_receipt=p121.name,previous_receipt_sha256=hashlib.sha256(p121.read_bytes()).hexdigest(),new_rows=new122,cursor=len(rows121),total=len(tasks121),unreceived=len(tasks121)-len(rows121),first_falsifier=first121,status='ALLOCATED_REGION_HOLD_NOT_WIRECONTACT' if first121 else 'BODY_RESERVE_REGION_PENDING',operation_seconds=time.monotonic()-t122,process_cpu_seconds=time.process_time()-c122,selected=False,N01_complete=False)
p122=OUT/'day07-SOURCE-FL2-body-reserve-continuation.json';assert not p122.exists();p122.write_bytes((json.dumps(r122,indent=2)+'\n').encode());print('BODY122',r122,flush=True);print('OWNER61_IDLE',os.getpid(),flush=True)
