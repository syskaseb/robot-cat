import json,time,hashlib,zipfile,os
t49=time.monotonic();c49=time.process_time()
def box49(lo,hi):return Part.makeBox(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2],A.Vector(*lo))
bed49=box49([-17,34,101.1],[-7,49,104.1])
guides49=[box49([-17,35.8,104.1],[-16.2,47.2,106.1]),box49([-7.8,35.8,104.1],[-7,47.2,106.1]),box49([-16.2,34,104.1],[-13.2,34.8,106.1]),box49([-9.8,34,104.1],[-7.8,34.8,106.1]),box49([-16.2,48.2,104.1],[-7.8,49,106.1])]
delta49=bed49.multiFuse(guides49)
col49=W37parts['west_bank_gap_column'];clip49=col49.common(box49([-20,40,40],[-5,60,104.1]));receiver49=clip49.fuse(delta49)
foot49=box49([-16,35,104.1],[-8,48,107.1]);bar49=W37parts['outside_PCB_west_return'];footbar49=foot49.fuse(bar49)
root49=bed49.common(clip49);join49=foot49.common(bar49)
bearing49=foot49.common(receiver49);face49=[f for f in foot49.Faces if abs(f.CenterOfMass.z-104.1)<1e-7 and abs(f.normalAt(0,0).z)>.99][0];bearingFace49=face49.common(receiver49)
new49={'receiver_delta':delta49,'moving_carrier_foot':foot49};ties49=[]
for i,Y in enumerate([36.5,41.5]):
 outer=box49([-18.2,Y-1.25,99.9],[-5.8,Y+1.25,108.3]);inner=box49([-17,Y-2,101.1],[-7,Y+2,107.1]);band=outer.cut(inner)
 head=box49([-23.5,Y-2.15,102.1],[-18.2,Y+2.15,107.1]);tail=box49([-123.5,Y-1.25,104],[-23.5,Y+1.25,105.2])
 new49['joint_tie'+str(i)+':band_budget']=band;new49['joint_tie'+str(i)+':head_budget']=head;new49['joint_tie'+str(i)+':full_unit_residual_capacity']=tail
 ties49.append(dict(unit=i,selected='T18I100',full_unit_mm=100,outer_loop_upper_mm=41.6,full_head_debit_mm=5.3,closure_pull_allowance_mm=25,required_upper_mm=71.9,capacity_for_any_untrimmed_residual_mm=100,no_additional100debit=True,no_trim_assumed=True,source_unit_availability_NOT_asserted=True))
valid49={n:dict(valid=s.isValid(),solids=len(s.Solids)) for n,s in dict(new49,receiver_full=receiver49,foot_plus_existing_return=footbar49).items()}
assert all(v['valid'] and v['solids']==1 for v in valid49.values())
roots49=dict(receiver_to_actual_column=dict(common_valid=root49.isValid(),common_mm3=root49.Volume,union_valid=receiver49.isValid(),union_solids=len(receiver49.Solids)),foot_to_existing_return=dict(common_valid=join49.isValid(),common_mm3=join49.Volume,union_valid=footbar49.isValid(),union_solids=len(footbar49.Solids)),bearing=dict(common_valid=bearing49.isValid(),material_intrusion_mm3=bearing49.Volume,face_valid=bearingFace49.isValid(),actual_bearing_area_mm2=bearingFace49.Area),guide_clearance_each_mm=.2,actual_foot_guide_gaps_mm=[foot49.distToShape(q)[0] for q in guides49],retired_original_column_cap_mm3=col49.Volume-clip49.Volume)
# Full current neighbors, but only ADDED delta/foot/stock. Never rerun unchanged lower-column interfaces.
foreign49=dict(Current35);foreign49.update({'C1:'+n:s for n,s in W37parts.items() if n!='west_bank_gap_column'})
tasks49=[]
for n,s in new49.items():
 for k,q in foreign49.items():
  if bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25:tasks49.append((n,k))
rows49=[];stop49=None
for n,k in tasks49:
 s,q=new49[n],foreign49[k]
 own=(k=='C1:outside_PCB_west_return' and (n in ['moving_carrier_foot','receiver_delta'] or ':band_budget' in n))
 if k.startswith(('Flat:MODULE:','Underdeck:SOURCE:')) or k=='V:common_region':
  rows49.append(dict(a=n,b=k,status='FLEXIBLE_CONNECTED_CAPACITY_OPEN_NOT_RIGIDCONTACT'));continue
 r=dict(a=n,b=k,a_valid=s.isValid(),b_valid=q.isValid(),required_mm=0 if own else 1.25)
 if r['a_valid'] and r['b_valid']:
  g,w,_=s.distToShape(q);r.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  if g<1e-7:
   co=s.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  r['mate_function']='same_moving_print_positive_joint' if own and n=='moving_carrier_foot' else 'removable_bearing_or_own_structural_tie_NO_INTRUSION' if own else 'foreign125'
  r['status']='ACTUAL_POSITIVE_SAME_MOVING_PRINT_JOINT' if own and n=='moving_carrier_foot' and r.get('common_valid') and r['common_mm3']>1e-7 else 'OWN_REMOVABLE_BEARING_OR_TIE_WITHOUT_INTRUSION' if own and n!='moving_carrier_foot' and r.get('common_valid',True) and r.get('common_mm3',0)<1e-7 else 'SEPARATED125' if not own and g>=1.25-1e-7 else 'NEW_INTERFACE_HOLD'
 else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 rows49.append(r)
 if r['status']=='NEW_INTERFACE_HOLD':stop49=r;break
 if time.monotonic()-t49>45:break
outline49={};outer49=BodyOuter31
for n,s in new49.items():
 if hasattr(outer49,'Faces'):
  outside=s.cut(outer49);bound=Part.makeCompound(outer49.Faces);gap=s.distToShape(bound)[0]
  outline49[n]=dict(outside_valid=outside.isValid(),outside_null=outside.isNull(),outside_volume_mm3=outside.Volume,boundary_gap_mm=gap,required_mm=3.25,ok=(outside.isNull() or outside.isValid()) and outside.Volume<1e-7 and gap>=3.25-1e-7)
 else:
  outline49[n]=dict(status='BODYOUTER_SOURCE_NOT_SHAPE_NEEDS_CURRENT_BOUNDARY_PROOF',ok=False)
ar49=OUT/'day07-removable-Pi-carrier-functional-bearing-correction1.breps.zip';assert not ar49.exists();ge49=[]
with zipfile.ZipFile(ar49,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(list(new49.items())+[('receiver_with_actual_column',receiver49),('carrier_foot_plus_source_upper_return',footbar49)]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge49.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge49,scope='ONE new separable coarse functional mounting interface, not production CAD or installed selection'),indent=2)+'\n').encode())
r49=dict(id='day07-removable-Pi-carrier-bearing-functional-correction1-gate',status='FUNCTIONAL_MOUNT_HOLD' if stop49 else 'FUNCTIONAL_MOUNT_LOCAL_PROOFS_RECEIVED' if len(rows49)==len(tasks49) and all(v['ok'] for v in outline49.values()) else 'FUNCTIONAL_MOUNT_PENDING',roots=roots49,geometry_validity=valid49,rows=rows49,cursor=len(rows49),total=len(tasks49),unreceived=len(tasks49)-len(rows49),stop=stop49,full_neighbor_count=len(foreign49),outline=outline49,ties=ties49,
 stock_classification='Two new nominal independent selected100mm tie units are structural joint retention. Full head/band/100 residual capacity represents the SAME unit, not spare material or service sling. No physical cut; no stock availability/purchase assertion. Existing PAS power restraint is an additional source unit, not a structural parent.',
 assembly_access='Thread two ties beneath bed atY36.5/41.5, outside retained columnY45..49, before lowering carrier; complete heads lateral. Removable foot has .2nominal side/end guide clearance. Pi/Card/4M2/PAS source ownrails move together; U1 soldered MODULE+SOURCE/JPWM/S0 remain installed. No PCBdrop5/left99 required.',
 correction_scope='Single source-caused correction of removable mounting interface: move BOTH complete strap threading lanes IN FRONT OF fixedcolumn, enlarge bearing toward South and slot the front guide around the unchanged carrierreturn. Keep FR_P case/fullband/head untouched. C0 receiverbandcommon30.8125 retained; no thirdattempt.',proof_scope='Prototype functional support only: actualroot/bearing/section/fullstock/neighbors/outline; not FEM, manufacturing fit or fullN08/N09. Normal printed sliding fit and final hand-tension require phase2 dryfit.',
 archive=ar49.name,archive_sha256=hashlib.sha256(ar49.read_bytes()).hexdigest(),geometry=ge49,operation_seconds=time.monotonic()-t49,process_cpu_seconds=time.process_time()-c49,current1292_unchanged=True,new_proposal_NOT_installed=True,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p49=OUT/'day07-removable-Pi-carrier-bearing-functional-correction1-gate.json';assert not p49.exists();p49.write_bytes((json.dumps(r49,ensure_ascii=False,indent=2)+'\n').encode());print('CARRIER49_FUNCTION',r49['status'],roots49,len(rows49),len(tasks49),stop49,outline49,r49['operation_seconds'],r49['process_cpu_seconds'],hashlib.sha256(p49.read_bytes()).hexdigest(),flush=True)
