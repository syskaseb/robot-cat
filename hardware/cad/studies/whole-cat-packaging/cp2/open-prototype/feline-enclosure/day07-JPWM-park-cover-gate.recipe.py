import time,json,hashlib,os
t41=time.monotonic();c41=time.process_time();rr41=[];cand41=[n for n,s in context40.items() if bbox_lower_bound(park40.BoundBox,s.BoundBox)<=1.25]
for n in cand41:
 b=context40[n]
 if n.startswith('Flat:MODULE:') or n=='V:common_region' or n.startswith('Underdeck:SOURCE:'):
  rr41.append(dict(other=n,status='FLEXIBLE_SERVICE_REGION_CAPACITY_OPEN_NOT_RIGIDCONTACT',bounds_mm=saved_bounds(b)));continue
 if n.startswith('Ref_Material_BUSsupplier') or n=='SharedBUS:TailCarrier':
  rr41.append(dict(other=n,status='INVALID_SOURCE_HISTORY_COVER_OPEN_NOT_CONTACT'));continue
 va,vb=park40.isValid(),b.isValid();r=dict(other=n,park_cover_valid=va,other_valid=vb)
 if va and vb:
  try:
   gap,w,_=park40.distToShape(b);co=park40.common(b) if gap<1e-7 else None;cv=co.isValid() if co is not None else None;v=co.Volume if cv else (0 if co is None else None)
   r.update(gap_mm=gap,common_valid=cv,common_mm3=v,witnesses=[[list(x),list(y)] for x,y in w[:1]],status='PARK_COVER_SEPARATED125' if gap>=1.25-1e-7 else 'PARK_COVER_ALLOCATION_HOLD_NOT_DELIVEREDCONTACT')
  except Exception as ex:r.update(status='KERNEL_ERROR_NOT_CONTACT',error=str(ex))
 else:r['status']='INVALID_SOURCE_NOT_CONTACT'
 rr41.append(r)
r=dict(id='day07-JPWM-module-temporary-park-full-cover-gate',scope='Conservative fullmated26x12x12 sourcebody encloses any individualhousing; do notinvent splitplane/half geometry. Pose[-35,53.5,90.5] is SOURCE MATED-PAIRFRAME datum, not a claimed halfcentreofmass.',source13_proposal_sha256=hashlib.sha256(propP40.read_bytes()).hexdigest(),park_cover_bounds_mm=saved_bounds(park40),rows=rr41,cursor=len(rr41),total=len(cand41),support='proposed twofreshselected100ties as linkedtemporarysling at existingC1westcolumn junction, nominalstock only; slinggeometry/heads/anchorhandling and wirecapacitynotaccepted by thiscover test',source_pigtail_bench='only aftercurrentcompletepigtailendpointrelease; notclaimedexecuted/received',factory_stock='all4independentmin220 unchanged; temporaryMODULEdebits/R/connectedserviceloopcapacitystillOPEN, no pooling and no obsolete150',operation_seconds=time.monotonic()-t41,process_cpu_seconds=time.process_time()-c41,N01_complete=False,selected=False)
p=OUT/'day07-JPWM-module-temporary-park-full-cover-gate.json';assert not p.exists();p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));print('JPWM41_PARK_COVER',rr41,r['operation_seconds'],r['process_cpu_seconds'],hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
