import time,json,hashlib,zipfile,os
t47=time.monotonic();c47=time.process_time()
moving47={n:Current35[n] for n in moving42+[n for n in pi36 if n.startswith('Ref_Material_Pi4') and 'NominalPCB' not in n]+['PAS:retained_upper','PAS:body']}
assert len(moving47)==26
moving47.update({'Carrier:'+n:W37parts[n] for n in ['outside_PCB_west_return','actual_stem_END']})
excluded47=pi36|{'PAS:retained_upper','PAS:body','PAS:band','PAS:head'}
fixed47={n:s for n,s in Current35.items() if n not in excluded47}
fixed47.update({'C1:'+n:s for n,s in W37parts.items() if n not in ['outside_PCB_west_return','actual_stem_END']})
reuse47={}
for fn in ['day06-retained-Pi-complete-current-neighbor-gate.json','day07-PAS-upper-carrier-current-fixed-interface-gate.json']:
 for r in json.loads((OUT/fn).read_bytes())['rows']:
  if r.get('status')=='SEPARATED125':reuse47[(r['a'],r['b'])]=(r['gap_mm'],fn)
tasks47=[];covers47={}
for n,s in moving47.items():
 b=s.BoundBox;cover=Part.makeBox(b.XLength,b.YLength,b.ZLength+35,A.Vector(b.XMin,b.YMin,b.ZMin));covers47[n]=cover
 for k,q in fixed47.items():
  if bbox_lower_bound(cover.BoundBox,q.BoundBox)<=1.25:tasks47.append((n,k))
rows47=[];stop47=None;exactnew47=0
for n,k in tasks47:
 s,q=moving47[n],fixed47[k];r=dict(moving=n,fixed=k)
 if n.startswith('Carrier:') and k=='C1:west_bank_gap_column':
  r.update(status='ONLY_NAMED_NEW_REMOVABLE_SEAM_PENDING_SEPARATE_MATERIAL_PROOF',scope='Original positive C1 union is deliberately replaced by the proposed bearing/retention; not waived as existing foreign clearance.');rows47.append(r);continue
 if k.startswith(('Flat:MODULE:','Underdeck:SOURCE:')) or k=='V:common_region':
  r.update(status='FLEXIBLE_CONNECTED_OCCUPANCY_DEPENDENCY_OPEN_NOT_RIGIDCONTACT');rows47.append(r);continue
 if not s.isValid() or not q.isValid():
  r.update(status='INVALID_SOURCE_COVER_OPEN_NOT_CONTACT');rows47.append(r);continue
 if (n,k) in reuse47:g,fn=reuse47[(n,k)];r['current_gap_reused_from']=fn
 else:g=s.distToShape(q)[0];r['new_current_operand_distance']=True;exactnew47+=1
 H=max(0.,q.BoundBox.ZMax-s.BoundBox.ZMin)
 lb=g-min(35.,H)
 r.update(current_gap_mm=g,max_vertical_gap_reduction_upper_mm=min(35.,H),continuous_upward_gap_lower_mm=lb)
 if lb>=1.25-1e-7:r['status']='CONTINUOUS_TOP_ENTRY_SEPARATED125_BY_CURRENT_GAP_HEIGHT_BOUND'
 else:
  cg,w,_=covers47[n].distToShape(q);r.update(full_profile_sweep_cover_gap_mm=cg,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  r['status']='CONTINUOUS_TOP_ENTRY_SEPARATED125_BY_FULL_COVER' if cg>=1.25-1e-7 else 'TOP_ENTRY_PROFILE_ALLOCATION_HOLD_NOT_ACTUAL_CONTACT'
  if r['status'].startswith('TOP_ENTRY_PROFILE'):stop47=r
 rows47.append(r)
 if stop47 or time.monotonic()-t47>45:break
ar47=OUT/'day07-removable-Pi-carrier-top-entry-inputs.breps.zip';assert not ar47.exists();geo47=[]
with zipfile.ZipFile(ar47,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(list(moving47.items())+[(n,fixed47[n]) for n in sorted({r['fixed'] for r in rows47})]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);geo47.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=geo47,scope='Unchanged actual source kit plus two retained C1 upper cells; proposed new removable seam not fabricated by this gate'),indent=2)+'\n').encode())
r47=dict(id='day07-removable-Pi-carrier-top-entry-first-gate',status='TOP_ENTRY_PROFILE_HOLD' if stop47 else 'TOP_ENTRY_CORE_REGION_RECEIVED_SCOPED' if len(rows47)==len(tasks47) else 'BOUNDED_ENTRY_GATE_PENDING',rows=rows47,cursor=len(rows47),total=len(tasks47),unreceived=len(tasks47)-len(rows47),stop=stop47,moving_source_actors=26,retained_upper_cells=2,fixed_count=len(fixed47),current1292_unchanged=True,new_current_distance_queries=exactnew47,
 mathematical_scope='For +Z translation0..35, exact current gap g can decrease by at most min(35,max(0,B.Zmax-A.Zmin)); after that height all points of A are above B and distance is nondecreasing. Thus g-H>=1.25 proves the whole segment. Otherwise use full enclosing swept profile; its overlap is only allocationHOLD.',
 assembly='Initial complete SOURCE/U1-MODULE/JPWM stay installed. Bench Pi/card/4M2 own rails carrier lowers from open top. Four real Pi mates and source tie closures not yet connected; no virtual solder or integral U1 removal.',
 additional_source_retention=dict(actors=['PAS:band','PAS:head'],physical_units=1,constructor='plan_feline_power_axial_saddle.py -> saddle full power2 grip kit',handling='Retained full source grip function/stock; closure after mating, renew if disturbed. In addition to the four previously counted Pi stock units, not a hidden fixed parent.'),
 remaining=['new mechanical bearing/root/2full100T18I/heads/tails/ownseam and installedoutline','Pi-mate source access and full connected flexible capacity2/R6/invalid3','S0 currentcase retention remains globallyOPEN despite keeping its pose; no fictitious late-mount proof','whole123246/head/4MTA unchanged portions not retested'],
 archive=ar47.name,archive_sha256=hashlib.sha256(ar47.read_bytes()).hexdigest(),geometry=geo47,operation_seconds=time.monotonic()-t47,process_cpu_seconds=time.process_time()-c47,pid=os.getpid(),session_id=46493,selected=False,N01_complete=False)
p47=OUT/'day07-removable-Pi-carrier-top-entry-first-gate.json';assert not p47.exists();p47.write_bytes((json.dumps(r47,ensure_ascii=False,indent=2)+'\n').encode());print('REMOVABLE47_TOP',r47['status'],len(rows47),len(tasks47),stop47,r47['operation_seconds'],r47['process_cpu_seconds'],hashlib.sha256(p47.read_bytes()).hexdigest(),flush=True)
