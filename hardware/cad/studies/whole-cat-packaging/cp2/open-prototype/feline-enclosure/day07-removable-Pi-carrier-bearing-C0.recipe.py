import json,time,hashlib,zipfile,os
t48=time.monotonic();c48=time.process_time()
def box48(lo,hi):return Part.makeBox(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2],A.Vector(*lo))
bed48=box48([-17,41,101.1],[-7,55,104.1])
guides48=[box48([-17,44.8,104.1],[-16.2,51.2,106.1]),box48([-7.8,44.8,104.1],[-7,51.2,106.1]),box48([-16.2,41,104.1],[-7.8,41.8,106.1]),box48([-16.2,54.2,104.1],[-7.8,55,106.1])]
delta48=bed48.multiFuse(guides48)
col48=W37parts['west_bank_gap_column'];clip48=col48.common(box48([-20,40,40],[-5,60,104.1]));receiver48=clip48.fuse(delta48)
foot48=box48([-16,42,104.1],[-8,54,107.1]);bar48=W37parts['outside_PCB_west_return'];footbar48=foot48.fuse(bar48)
root48=bed48.common(clip48);join48=foot48.common(bar48)
bearing48=foot48.common(receiver48);face48=[f for f in foot48.Faces if abs(f.CenterOfMass.z-104.1)<1e-7 and abs(f.normalAt(0,0).z)>.99][0];bearingFace48=face48.common(receiver48)
new48={'receiver_delta':delta48,'moving_carrier_foot':foot48};ties48=[]
for i,Y in enumerate([43.5,52.5]):
 outer=box48([-18.2,Y-1.25,99.9],[-5.8,Y+1.25,108.3]);inner=box48([-17,Y-2,101.1],[-7,Y+2,107.1]);band=outer.cut(inner)
 head=box48([-23.5,Y-2.15,102.1],[-18.2,Y+2.15,107.1]);tail=box48([-123.5,Y-1.25,104],[-23.5,Y+1.25,105.2])
 new48['joint_tie'+str(i)+':band_budget']=band;new48['joint_tie'+str(i)+':head_budget']=head;new48['joint_tie'+str(i)+':full_unit_residual_capacity']=tail
 ties48.append(dict(unit=i,selected='T18I100',full_unit_mm=100,outer_loop_upper_mm=41.6,full_head_debit_mm=5.3,closure_pull_allowance_mm=25,required_upper_mm=71.9,capacity_for_any_untrimmed_residual_mm=100,no_additional100debit=True,no_trim_assumed=True,source_unit_availability_NOT_asserted=True))
valid48={n:dict(valid=s.isValid(),solids=len(s.Solids)) for n,s in dict(new48,receiver_full=receiver48,foot_plus_existing_return=footbar48).items()}
assert all(v['valid'] and v['solids']==1 for v in valid48.values())
roots48=dict(receiver_to_actual_column=dict(common_valid=root48.isValid(),common_mm3=root48.Volume,union_valid=receiver48.isValid(),union_solids=len(receiver48.Solids)),foot_to_existing_return=dict(common_valid=join48.isValid(),common_mm3=join48.Volume,union_valid=footbar48.isValid(),union_solids=len(footbar48.Solids)),bearing=dict(common_valid=bearing48.isValid(),material_intrusion_mm3=bearing48.Volume,face_valid=bearingFace48.isValid(),actual_bearing_area_mm2=bearingFace48.Area),guide_clearance_each_mm=.2,retired_original_column_cap_mm3=col48.Volume-clip48.Volume)
# Full current neighbors, but only ADDED delta/foot/stock. Never rerun unchanged lower-column interfaces.
foreign48=dict(Current35);foreign48.update({'C1:'+n:s for n,s in W37parts.items() if n!='west_bank_gap_column'})
tasks48=[]
for n,s in new48.items():
 for k,q in foreign48.items():
  if bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25:tasks48.append((n,k))
rows48=[];stop48=None
for n,k in tasks48:
 s,q=new48[n],foreign48[k]
 own=(n=='moving_carrier_foot' and k=='C1:outside_PCB_west_return')
 if k.startswith(('Flat:MODULE:','Underdeck:SOURCE:')) or k=='V:common_region':
  rows48.append(dict(a=n,b=k,status='FLEXIBLE_CONNECTED_CAPACITY_OPEN_NOT_RIGIDCONTACT'));continue
 r=dict(a=n,b=k,a_valid=s.isValid(),b_valid=q.isValid(),required_mm=0 if own else 1.25)
 if r['a_valid'] and r['b_valid']:
  g,w,_=s.distToShape(q);r.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  if g<1e-7:
   co=s.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  r['status']='ACTUAL_POSITIVE_SAME_MOVING_PRINT_JOINT' if own and r.get('common_valid') and r['common_mm3']>1e-7 else 'SEPARATED125' if not own and g>=1.25-1e-7 else 'NEW_INTERFACE_HOLD'
 else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 rows48.append(r)
 if r['status']=='NEW_INTERFACE_HOLD':stop48=r;break
 if time.monotonic()-t48>45:break
outline48={};outer48=BodyOuter31
for n,s in new48.items():
 if hasattr(outer48,'Faces'):
  outside=s.cut(outer48);bound=Part.makeCompound(outer48.Faces);gap=s.distToShape(bound)[0]
  outline48[n]=dict(outside_valid=outside.isValid(),outside_null=outside.isNull(),outside_volume_mm3=outside.Volume,boundary_gap_mm=gap,required_mm=3.25,ok=(outside.isNull() or outside.isValid()) and outside.Volume<1e-7 and gap>=3.25-1e-7)
 else:
  outline48[n]=dict(status='BODYOUTER_SOURCE_NOT_SHAPE_NEEDS_CURRENT_BOUNDARY_PROOF',ok=False)
ar48=OUT/'day07-removable-Pi-carrier-functional-bearing.breps.zip';assert not ar48.exists();ge48=[]
with zipfile.ZipFile(ar48,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(list(new48.items())+[('receiver_with_actual_column',receiver48),('carrier_foot_plus_source_upper_return',footbar48)]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge48.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge48,scope='ONE new separable coarse functional mounting interface, not production CAD or installed selection'),indent=2)+'\n').encode())
r48=dict(id='day07-removable-Pi-carrier-bearing-functional-gate',status='FUNCTIONAL_MOUNT_HOLD' if stop48 else 'FUNCTIONAL_MOUNT_LOCAL_PROOFS_RECEIVED' if len(rows48)==len(tasks48) and all(v['ok'] for v in outline48.values()) else 'FUNCTIONAL_MOUNT_PENDING',roots=roots48,geometry_validity=valid48,rows=rows48,cursor=len(rows48),total=len(tasks48),unreceived=len(tasks48)-len(rows48),stop=stop48,full_neighbor_count=len(foreign48),outline=outline48,ties=ties48,
 stock_classification='Two new nominal independent selected100mm tie units are structural joint retention. Full head/band/100 residual capacity represents the SAME unit, not spare material or service sling. No physical cut; no stock availability/purchase assertion. Existing PAS power restraint is an additional source unit, not a structural parent.',
 assembly_access='Thread two ties beneath bed atY43.5/52.5, outside retained columnY45..49, before lowering carrier; complete heads lateral. Removable foot has .2nominal side/end guide clearance. Pi/Card/4M2/PAS source ownrails move together; U1 soldered MODULE+SOURCE/JPWM/S0 remain installed. No PCBdrop5/left99 required.',
 proof_scope='Prototype functional support only: actualroot/bearing/section/fullstock/neighbors/outline; not FEM, manufacturing fit or fullN08/N09. Normal printed sliding fit and final hand-tension require phase2 dryfit.',
 archive=ar48.name,archive_sha256=hashlib.sha256(ar48.read_bytes()).hexdigest(),geometry=ge48,operation_seconds=time.monotonic()-t48,process_cpu_seconds=time.process_time()-c48,current1292_unchanged=True,new_proposal_NOT_installed=True,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p48=OUT/'day07-removable-Pi-carrier-bearing-functional-gate.json';assert not p48.exists();p48.write_bytes((json.dumps(r48,ensure_ascii=False,indent=2)+'\n').encode());print('CARRIER48_FUNCTION',r48['status'],roots48,len(rows48),len(tasks48),stop48,outline48,r48['operation_seconds'],r48['process_cpu_seconds'],hashlib.sha256(p48.read_bytes()).hexdigest(),flush=True)
