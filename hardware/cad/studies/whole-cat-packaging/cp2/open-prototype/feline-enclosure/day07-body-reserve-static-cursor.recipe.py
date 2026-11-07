import time,json,hashlib,os,zipfile
t124=time.monotonic();c124=time.process_time();start124=len(rows121);new124=[];first124=None
out124=OUT/'day07-SOURCE-FL2-body-reserve-static-cursor5.json';assert not out124.exists()
def save124():
 global data124
 data124=dict(id=out124.stem,status='BODY_RESERVE_ALLOCATED_REGION_FIRST_FALSIFIER' if first124 else 'BODY_RESERVE_REGION_PENDING' if len(rows121)<len(tasks121) else 'BODY_RESERVE_STATIC_SCOPE_RECEIVED',previous_cursor=start124,new_rows=new124,cursor=len(rows121),total=len(tasks121),unreceived=len(tasks121)-len(rows121),first_falsifier=first124,operation_seconds=time.monotonic()-t124,process_cpu_seconds=time.process_time()-c124,all19_capacity_members_retained=len(whole121.Solids)==19,current_context_count=len(ctx121),selected=False,N01_complete=False,new_material=False,new_leg_geometry=False,pid=os.getpid(),session_id=46493)
 tmp=out124.with_suffix('.tmp');tmp.write_bytes((json.dumps(data124,indent=2)+'\n').encode());os.replace(tmp,out124)
save124()
for n,k in tasks121[start124:]:
 s=lookup121[n];v=ctx121[k];q=dict(region=n,other=k,field_valid=s.isValid(),source_valid=v.isValid())
 if q['source_valid']:
  gap,ww,_=s.distToShape(v);q.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:2]],status='BODY_RESERVE_REGION_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_BODY_REGION_HOLD_NOT_DELIVEREDWIRECONTACT')
 else:q['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
 rows121.append(q);new124.append(q)
 if q['status']!='BODY_RESERVE_REGION_SEPARATED125':first124=q
 save124()
 if first124 or time.monotonic()-t124>22:break
print('BODY124',data124,flush=True);print('OWNER62_IDLE',os.getpid(),flush=True)
