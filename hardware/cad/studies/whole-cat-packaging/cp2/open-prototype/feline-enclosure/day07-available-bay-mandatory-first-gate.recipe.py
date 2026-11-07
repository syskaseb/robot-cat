import time,json,hashlib,zipfile,os
st144=time.monotonic();cp144=time.process_time();pp144=OUT/'day07-FPI-longitudinal-available-bay-source-gate.json';pr144=json.loads(pp144.read_bytes())
def box144(bb):
 a,b=bb;return Part.makeBox(*[b[i]-a[i] for i in range(3)],A.Vector(*a))
body144=box144(pr144['mandatory_body_core']);lid144=box144(pr144['mandatory_lid_core']);wholebody144=box144(pr144['union_body_cover']);wholelid144=box144(pr144['union_lid_cover']);bank144=[]
for k,v in ctx121.items():
 if k.startswith('Ref_Material_') and '_CP2_Housing' in k:bank144.append(dict(name=k,bounds_mm=saved_bounds(v),mandatory_body_bbox_lower_mm=bbox_lower_bound(body144.BoundBox,v.BoundBox),whole_body_family_bbox_lower_mm=bbox_lower_bound(wholebody144.BoundBox,v.BoundBox)))
parts144=[('MANDATORY_FULL_CASE_CORE_ALL_b',body144),('MANDATORY_UPWARD_LID_CORE_ALL_b',lid144)];tasks144=[]
for n,s in parts144:
 for k,v in ctx121.items():
  if k=='F_PI:registered_casing_reservation':continue
  if bbox_lower_bound(s.BoundBox,bounds126[k])<1.25:tasks144.append((n,k))
# New region proof only; exact prefix prevents a BankPad owner substring being mistaken for bought material.
def priority144(k):
 return 0 if k.startswith('Ref_Material_') or (k.startswith('Station:') and k.endswith(':case')) else 1
tasks144.sort(key=lambda t:(0 if t[0].startswith('MANDATORY_FULL_CASE') else 1,priority144(t[1]),t[1]));rows144=[];first144=None;co144=None
for n,k in tasks144:
 s=dict(parts144)[n];v=ctx121[k];row=dict(part=n,other=k,field_valid=s.isValid(),source_valid=v.isValid(),kind='necessary_shared_allocation_not_pose_or_physical_wire')
 if not v.isValid():row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 else:
  gap,ww,_=s.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]])
  if gap<1e-7:
   c=s.common(v);co144=c;row.update(common_valid=c.isValid(),mandatory_allocated_common_mm3=c.Volume if c.isValid() else None)
  if row.get('common_valid') and row.get('mandatory_allocated_common_mm3',0)>1e-6:row['status']='ALL_b_MANDATORY_MATERIAL_OCCUPANCY_HOLD'
  elif gap<1.25-1e-7:row['status']='MANDATORY_REGION_CLEARANCE_HOLD_NOT_MATERIAL_CONTACT'
  else:row['status']='NEW_REGION_SEPARATED125'
 rows144.append(row)
 if row['status']!='NEW_REGION_SEPARATED125':first144=row;break
 if time.monotonic()-st144>15:break
items144=[('MANDATORY_BODY_CORE',body144),('MANDATORY_UPWARD_LID_CORE',lid144),('UNION_ALL_BODY_POSITIONS',wholebody144),('UNION_ALL_LID_POSITIONS',wholelid144)]
if first144:items144.append(('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first144['other']]))
if co144 is not None and co144.isValid():items144.append(('FIRST_ACTUAL_MANDATORY_COMMON',co144))
ar144=OUT/'day07-FPI-source-constrained-bay-mandatory-first-gate.breps.zip';assert not ar144.exists();ge144=[]
with zipfile.ZipFile(ar144,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items144):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge144.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge144),indent=2)+'\n').encode())
r144=dict(id='day07-FPI-source-constrained-bay-mandatory-first-gate',status='LONGITUDINAL_UP_LAYER_NECESSARY_REGION_HOLD' if first144 else 'NECESSARY_REGIONS_ONLY_CLEAR_NOT_WHOLE_KIT_ACCEPTED',proposal=pp144.name,proposal_sha256=hashlib.sha256(pp144.read_bytes()).hexdigest(),source_bank_housings=bank144,derived_b_interval=pr144['derived_right_edge_interval_mm'],no_case_pose_selected=True,no_new_support_print_or_wires=True,proof_scope='Mandatorycores containedineachbody/lidofONEsource-constrainedXlongitudinal/lidUP/straightW043/planarW077minusYfamily; notall3Dcasearrangements. Positivecommonwithcurrentmaterial rejectsnecessaryspace, notdeliveredcontact. Operationfieldsclassifiedseparately.',rows=rows144,cursor=len(rows144),total=len(tasks144),unreceived=len(tasks144)-len(rows144),tasks=tasks144,first_falsifier=first144,archive=ar144.name,archive_sha256=hashlib.sha256(ar144.read_bytes()).hexdigest(),geometry=ge144,old29_or_root_source_tests_replayed=False,selected=False,N01_complete=False,operation_seconds=time.monotonic()-st144,process_cpu_seconds=time.process_time()-cp144,pid=os.getpid(),session_id=46493)
p144=OUT/(r144['id']+'.json');assert not p144.exists();p144.write_bytes((json.dumps(r144,indent=2)+'\n').encode());print('BODY144',r144['status'],'banks',len(bank144),'b',r144['derived_b_interval'],'first',first144,'rows',len(rows144),len(tasks144),'wall',r144['operation_seconds'],'CPU',r144['process_cpu_seconds'],flush=True);print('OWNER70_IDLE',os.getpid(),flush=True)
