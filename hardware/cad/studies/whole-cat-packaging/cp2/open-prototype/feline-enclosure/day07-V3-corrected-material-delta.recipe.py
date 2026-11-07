import time,json,hashlib,zipfile,os
t55=time.monotonic();c55=time.process_time();delta55=add54.cut(oldsupport54);assert delta55.isValid() and delta55.Volume>0
rawWitness55=A.Vector(-41,16,66.2);inOld55=oldsupport54.isInside(rawWitness55,1e-7,True)
rows55=[];hold55=None;tasks55=[n for n,q in Current35.items() if n not in ['V:new_root_material','V:functional_pressure_support','V:common_region'] and not any(n.startswith(w+':') for w in ['W020','W022','W024']) and bbox_lower_bound(delta55.BoundBox,q.BoundBox)<=1.25]
for n in tasks55:
 q=Current35[n];r=dict(other=n,changed_delta_valid=delta55.isValid(),other_valid=q.isValid())
 if q.isValid():
  gap,w,_=delta55.distToShape(q);r.update(gap_mm=gap,required_foreign_mm=1.25,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  if gap<1e-7:
   co=delta55.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  r['status']='ONLY_NEW_MATERIAL_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_MATERIAL_FOREIGN_HOLD'
 else:r['status']='INVALID_SOURCE_UNRESOLVED_NOT_CONTACT'
 rows55.append(r)
 if 'HOLD' in r['status']:hold55=r;break
columngap55=commonshape53.distToShape(W37parts['west_bank_gap_column'])[0]
ar55=OUT/'day07-V3-shared-support-changed-material.breps.zip';assert not ar55.exists();ge55=[]
with zipfile.ZipFile(ar55,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate([('V:actual_added_material_excluding_old_retained_source',delta55),('REFERENCE:existing_source_support',oldsupport54)]+[(r['other'],Current35[r['other']]) for r in rows55]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge55.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge55,scope='Correct changed-only interface scope for SAME sharedsupport geometry; NOT a thirdvariant or clearance waiver'),indent=2)+'\n').encode())
r55=dict(id='day07-V3-shared-support-changed-material-disposition',status='SAME_SUPPORT_CHANGED_ONLY_FOREIGN_RECEIVED' if hold55 is None else 'SAME_SUPPORT_CHANGED_ONLY_FOREIGN_HOLD',rows=rows55,cursor=len(rows55),total=len(tasks55),unreceived=len(tasks55)-len(rows55),stop=hold55,
 raw_C1_TE_gap=dict(file='day07-V3-source-clamp-shared-support-correction.json',gap_mm=1.152,required_foreign=1.25,witness_world_mm=list(rawWitness55),witness_in_actual_old_accepted_support=inOld55,scope='The fullnewbar/finger included4.3330409mm3 of unchanged source tabs. Its closestmetal point is original material. Keep rawresult; test delta=add minus oldfullsupport instead of replaying accepted material. No limit reduction/metalownership waiver/no new geometry.'),
 added_volume_mm3=delta55.Volume,full_add_volume_mm3=add54.Volume,excluded_actual_old_material_mm3=add54.Volume-delta55.Volume,
 original_removed_material_mm3=removed54.Volume,valid_common_with_declared_cut_mm3=insideDeclared54.Volume,outside_declared_removed_upper_mm3=outside_volume54,protected_caps_lost_mm3=lostcap54.Volume,
 corrected_V3_common_vs_unchanged_column_gap_mm=columngap55,required_foreign_column_mm=1.25,original_V_column_obstruction_eliminated_in_this_candidate=columngap55>=1.25,
 whole_V3_status='NOT_ACCEPTED: originalC0region1/239 left238unreceived; correctedsupport4regional root clearances received, but allremainingchangedregionalforeign, mutuallocaloccupancy/guide/root and perphysical900nominalwholebudgets remainOPEN. No pooling of independentMODULE/SOURCE220, no source9 change.',
 same_support_correction_geometry=True,no_third_geometry_variant=True,no_old_accepted_pairs_repeated=True,archive=ar55.name,archive_sha256=hashlib.sha256(ar55.read_bytes()).hexdigest(),geometry=ge55,operation_seconds=time.monotonic()-t55,process_cpu_seconds=time.process_time()-c55,selected=False,N01_complete=False)
p55=OUT/'day07-V3-shared-support-changed-material-disposition.json';assert not p55.exists();p55.write_bytes((json.dumps(r55,ensure_ascii=False,indent=2)+'\n').encode());print('V55_CHANGED_ONLY',r55['status'],rows55,columngap55,r55['operation_seconds'],r55['process_cpu_seconds'],hashlib.sha256(p55.read_bytes()).hexdigest(),flush=True)
