import time,json,hashlib,zipfile,os
t51=time.monotonic();c51=time.process_time()
newhead51={}
for i,Y in enumerate([36.5,41.5]):newhead51['joint_tie'+str(i)+':T18R100_head_width_bound']=box49([-23.5,Y-2.225,102.1],[-18.2,Y+2.225,107.1])
context51=dict(Current35);context51.update({'new_receiver':receiver49,'new_foot_return':footbar49,'newEND':W37parts['actual_stem_END']})
headrows51=[]
for n,s in newhead51.items():
 for k,q in context51.items():
  lb=bbox_lower_bound(s.BoundBox,q.BoundBox)
  if lb<1.25:
   own=k in ['new_receiver','new_foot_return','newEND'];g=s.distToShape(q)[0];co=s.common(q) if g<1e-7 else None
   headrows51.append(dict(head=n,other=k,bbox_lower_mm=lb,gap_mm=g,required_mm=0 if own else 1.25,common_valid=co.isValid() if co is not None else None,common_mm3=co.Volume if co is not None and co.isValid() else 0 if co is None else None,status='NAMED_STRUCTURAL_HEAD_OWNMOUNT_NO_INTRUSION' if own and (co is None or co.isValid() and co.Volume<1e-7) else 'SEPARATED125' if not own and g>=1.25 else 'CHANGED_HEAD_INTERFACE_HOLD'))
headoutline51={n:dict(previous_outline_lower_mm=4.9,added_extent_each_side_mm=.075,new_outline_lower_mm=4.825,required_mm=3.25,method='Distance-to-boundary is1-Lipschitz under Hausdorff .075mm width enlargement; no oldoutlineBOP replay') for n in newhead51}
section51=box49([-19.4,45,41.66],[-16.6,49,48.86])
sectionrows51=[]
sectioncontext51=dict(Current35);sectioncontext51.update({'C1:'+n:s for n,s in W37parts.items()})
for n,q in sectioncontext51.items():
 if bbox_lower_bound(section51.BoundBox,q.BoundBox)>1.25:continue
 rr=dict(other=n,section_valid=section51.isValid(),other_valid=q.isValid())
 if n.startswith(('Flat:MODULE:','Underdeck:SOURCE:')) or n=='V:common_region':rr['status']='FLEXIBLE_REGION_OTHER_LAYER_NOT_RIGIDCONTACT'
 elif rr['other_valid']:
  g,w,_=section51.distToShape(q);rr.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  if g<1e-7:
   co=section51.common(q);rr.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  rr['status']='WEST_INTERDECK_FULL_SECTION_SEPARATED125' if g>=1.25-1e-7 else 'WEST_INTERDECK_ALLOCATED_SECTION_HOLD_NOT_PHYSICAL_WIRECONTACT'
 else:rr['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 sectionrows51.append(rr)
 if rr['status'].startswith('WEST_INTERDECK_ALLOCATED'):break
ar51=OUT/'day07-carrier-T18R100-heads-and-V3-section.breps.zip';assert not ar51.exists();geo51=[]
with zipfile.ZipFile(ar51,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(list(newhead51.items())+[('V3:first_full_interdeck_section',section51)]+[(r['other'],sectioncontext51[r['other']]) for r in sectionrows51]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);geo51.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=geo51,scope='Only twoNEW carrier100SKU heads width and ONE V3section gate; no oldsource tests'),indent=2)+'\n').encode())
rr51=dict(id='day07-carrier-T18R100-binding-and-V3-section-gate',head_status='SELECTED_NEW_TWO_T18R100_HEAD_EXTENT_RECEIVED' if all('HOLD' not in r['status'] for r in headrows51) else 'NEW_HEAD_HOLD',new_tie_sku='HellermannTyton111-01910 T18R-PA66-BK',new_units_installed=2,bounded_rare_renewal_units=2,actual_free_stock_NOT_asserted=True,old_tie_labels_or_K3_NOT_changed=True,selected145_alternative_NOT_used='111-02370 T18I145 stays in catalog; not assigned to these2newroles',axis_mapping=dict(worldX_feed_budget=5.3,supplier_head_length=4.8,worldY_head_budget=4.45,supplier_head_width=4.45,worldZ_head_project_reserve=5.,supplier_full_head_height=None,strap_source_thickness=1.,strap_budget_thickness=1.2,full_unit_length=100.,complete_loop_closure_head_upper_each=71.9,untrimmed_residual_capacity_each=100.,residual_capacity_not_another_stock_debit=True),head_rows=headrows51,head_outline=headoutline51,
 V3_candidate=dict(section_bounds_mm=saved_bounds(section51),capacity_profile_XZ_mm=[2.8,7.2],local_cores=['W020','W022','W024'],actual_OD_each_mm=2.,core_spacing_mm=.2,outer_allowance_mm=.4,choice_basis='Old9mm slot between housingmaxX-15.5/minX-6.5 is narrowed by existing4mm column[-13.5,-9.5]. West2/east3 gaps cannotfit profile2.8 plus twoforeign1.25. Choose source interdeck38.52..52 window atZ45.26, westX-18; test actual retainedrail before designing bends.',rows=sectionrows51,whole_V3_transport_branch_radius_length_NOT_received=True),
 archive=ar51.name,archive_sha256=hashlib.sha256(ar51.read_bytes()).hexdigest(),geometry=geo51,operation_seconds=time.monotonic()-t51,process_cpu_seconds=time.process_time()-c51,N01_complete=False,selected=False)
p51=OUT/'day07-carrier-T18R100-binding-and-V3-section-gate.json';assert not p51.exists();p51.write_bytes((json.dumps(rr51,ensure_ascii=False,indent=2)+'\n').encode());print('BIND_SECTION51',rr51['head_status'],headrows51,sectionrows51,rr51['operation_seconds'],rr51['process_cpu_seconds'],hashlib.sha256(p51.read_bytes()).hexdigest(),flush=True)
