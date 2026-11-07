import time,json,os,hashlib
t236=time.monotonic();c236=time.process_time()
rois236={'HIP_NORTH_UPPER_FIRST_TURN_AND_TRANSPORT':[[-137.45,34.45,45.35],[104,78.95,49.25]],'KNEE6_LOWER_SINGLE_LAYER_ROLL_BAY':[[-137.45,-44,-36.55],[-94,39.25,-32.65]]}
rs236=[]
for role,bb in rois236.items():
 b=box153(bb);parts=[]
 for n,s in context230.items():
  if bbox_lower_bound(b.BoundBox,s.BoundBox)>1e-8:continue
  parts.append(dict(actor=n,bounds_mm=saved_bounds(s),valid=s.isValid(),classification='CURRENT_ACTUAL_OR_FUNCTIONAL_STOCK_AABB_CANDIDATE_NOT_CONTACT_OR_FREEBAY'))
 rs236.append(dict(region=role,bounds_mm=bb,current_candidate_parts=parts))
p236=OUT/'day07-SPLIT3plus6-current-upper-north-and-lower-case-layer-read.json';assert not p236.exists();r236=dict(id=p236.stem,status='ACTUAL_CURRENT_SOURCE_LAYER_CANDIDATES_BEFORE_CHOSEN_SPLIT_PLAN',regions=rs236,context_count=len(context230),frame='Current baked world once/context230 disjoint frame and G4/D5 proposed aliases exactly as previous current1311 context; no restore or posechange.',operating_base_unchanged=True,no_bbox_free_space_claim=True,all9ports_and12physicalrows_preserved=True,operation_seconds=time.monotonic()-t236,process_cpu_seconds=time.process_time()-c236,pid=os.getpid(),session_id=46493);p236.write_bytes((json.dumps(r236,indent=2)+'\n').encode());print('SPLIT236_SAVED',[(q['region'],len(q['current_candidate_parts']),[v['actor'] for v in q['current_candidate_parts']]) for q in rs236],r236['operation_seconds'],r236['process_cpu_seconds'],'OWNER94_IDLE',os.getpid(),flush=True)
