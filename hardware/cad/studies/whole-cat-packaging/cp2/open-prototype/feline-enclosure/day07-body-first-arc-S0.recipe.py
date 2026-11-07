import time,json,hashlib,zipfile
t123=time.monotonic();c123=time.process_time();n,k=tasks121[len(rows121)];assert n=='BODY_FIRST_ARC_ALLPHI' and k=='Ref_Material_S0_body_CP2_0_0'
s=lookup121[n];v=ctx121[k];assert s.isValid() and v.isValid();gap,ww,_=s.distToShape(v);row123=dict(region=n,other=k,gap_mm=gap,source_valid=True,field_valid=True,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='BODY_RESERVE_REGION_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_BODY_REGION_HOLD_NOT_DELIVEREDWIRECONTACT');rows121.append(row123)
geo123=[];ap123=OUT/'day07-SOURCE-FL2-body-first-arc-S0.breps.zip';assert not ap123.exists()
items123=[('FULL_ADAPTIVE_FIRST_ARC_REGION',s),('ACTUAL_CURRENT_S0_BODY',v)]
if gap<1e-7:
 co123=s.common(v);row123.update(common_valid=co123.isValid(),allocated_common_mm3=co123.Volume if co123.isValid() else None);items123.append(('ALLOCATED_COMMON_NOT_WIRECONTACT',co123))
with zipfile.ZipFile(ap123,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(name,sh) in enumerate(items123):
  raw=sh.exportBrepToString().encode();entry=str(i)+'.brep';zz.writestr(entry,raw);geo123.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),valid=sh.isValid(),volume_mm3=sh.Volume))
 zz.writestr('manifest.json',json.dumps(dict(geometry=geo123),indent=2))
r123=dict(id='day07-SOURCE-FL2-body-first-arc-S0',new_row=row123,cursor=len(rows121),total=len(tasks121),unreceived=len(tasks121)-len(rows121),first_falsifier=row123 if gap<1.25-1e-7 else None,archive=ap123.name,archive_sha256=hashlib.sha256(ap123.read_bytes()).hexdigest(),geometry=geo123,operation_seconds=time.monotonic()-t123,process_cpu_seconds=time.process_time()-c123,selected=False,N01_complete=False)
p123=OUT/'day07-SOURCE-FL2-body-first-arc-S0.json';assert not p123.exists();p123.write_bytes((json.dumps(r123,indent=2)+'\n').encode());print('BODY123',r123,flush=True);print('OWNER61_IDLE',os.getpid(),flush=True)
