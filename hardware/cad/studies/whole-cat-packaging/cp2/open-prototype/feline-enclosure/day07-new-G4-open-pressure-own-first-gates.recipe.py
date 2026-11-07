import time,json,hashlib,zipfile,os
st167=time.monotonic();cp167=time.process_time();pp167=OUT/'day07-SOURCE-G4-open-pressure-primary-load-and-lay-whole-proposal.json';pr167=json.loads(pp167.read_bytes());case167=ctx121['CurrentFLG:case'];u167=ctx121['Underdeck:PositiveFoundation'];cap167=oldcap166.copy();cap167.translate(A.Vector(12,0,0));band167=ctx121['CurrentFLG:band_budget'].copy();band167.translate(A.Vector(12,0,0));head167=ctx121['CurrentFLG:head_budget'].copy();head167.translate(A.Vector(12,0,0));low167=cap167.common(box153([[20,45,30],[45,90,45.52]]));up167=cap167.common(box153([[20,45,45.52],[45,90,60]]));assert low167.isValid() and up167.isValid()
mem167=[('retained_casecup_and_oldroot',keep166),('new_lower9',low167)]+[(n,box153(bb)) for n,bb in pr167['permanent_new_members'].items()];keys167=[(n,s) for n,s in mem167 if n.startswith('key')]
for n,k in keys167:
 bb=k.BoundBox;up167=up167.cut(box153([[bb.XMin-.2,bb.YMin-.2,45.32],[bb.XMax+.2,bb.YMax+.2,bb.ZMax+.2]]))
assert up167.isValid() and len(up167.Solids)==1
channels167=[]
for prefix,b in [('pressure',band167),('UNCHANGED_case',ctx121['FLG:case_band'])]:
 for i,s in enumerate(b.Solids):
  bb=s.BoundBox;channels167.append((prefix+':'+str(i),box153([[bb.XMin-.2,bb.YMin-.2,bb.ZMin-.2],[bb.XMax+.2,bb.YMax+.2,bb.ZMax+.2]])))
members167=[]
for n,s in mem167:
 for _,c in channels167:
  if bbox_lower_bound(s.BoundBox,c.BoundBox)<1e-7:s=s.cut(c)
 assert s.isValid() and s.Solids;members167.append((n,s))
newG167=members167[0][1].multiFuse([s for _,s in members167[1:]]);assert newG167.isValid();primary167=u167.fuse(newG167);assert primary167.isValid();cov167=[dict(name=n,missing_mm3=s.cut(newG167).Volume,bounds_mm=saved_bounds(s)) for n,s in members167];assert max(q['missing_mm3'] for q in cov167)<1e-7
casefloor167=keep166.common(box153([[37.375,51,38.52],[56.375,81,41.02]]));prot167=dict(U1_missing_mm3=u167.cut(primary167).Volume,actual_casefloor_missing_mm3=casefloor167.cut(primary167).Volume,actual_casefloor_volume_mm3=casefloor167.Volume,whole_source_old_casecup_root_retired_channel_mm3=keep166.cut(newG167).Volume);assert prot167['U1_missing_mm3']<1e-7 and prot167['actual_casefloor_missing_mm3']<1e-7
joints167=[]
for i,(n,s) in enumerate(members167):
 for m,v in members167[i+1:]:
  if bbox_lower_bound(s.BoundBox,v.BoundBox)<1e-7:
   c=s.common(v)
   if c.Volume>1e-7:joints167.append(dict(a=n,b=m,common_mm3=c.Volume,valid=c.isValid()))
root167=newG167.common(u167);assert root167.isValid();own167=[];first167=None
for n,s,v,required in [('bought_case',newG167,case167,0),('upper_to_case',up167,case167,0),('upper_to_lower',up167,newG167,0),('whole_pressure_band_to_primary',band167,primary167,.2),('whole_pressure_head_to_primary',head167,primary167,.2),('whole_pressure_band_to_upper',band167,up167,.2)]:
 c=s.common(v);gap=s.distToShape(v)[0];q=dict(role=n,common_valid=c.isValid(),common_mm3=c.Volume,gap_mm=gap,required_mm=required);own167.append(q)
 if (not c.isValid() or c.Volume>1e-7 or gap<required-1e-7) and first167 is None:first167=dict(kind='FUNCTIONAL_G4_OWN_MOUNT_FIRST_HOLD',**q)
for rr in pr167['pressure_lane']['all4_current_recipes']:
 p=A.Vector(*rr['point_mm']);wire=Part.makeCylinder(rr['radius_mm'],24.25,p,A.Vector(*rr['departure_axis']));c1=newG167.common(wire);c2=up167.common(wire);q=dict(wire=rr['wire'],endpoint=rr['endpoint'],same_prefix_length_mm=24.25,lower_common_mm3=c1.Volume,upper_common_mm3=c2.Volume,valid=c1.isValid() and c2.isValid());own167.append(q)
 if (not q['valid'] or c1.Volume>1e-7 or c2.Volume>1e-7) and first167 is None:first167=dict(kind='FULL4_G_PREFIX_MATERIAL_HOLD',**q)
oldprimary167=u167.fuse(oldG166);delta167=primary167.cut(oldprimary167);parts167=[('NEW_PRIMARY_PRINT_DELTA',delta167),('NEW_G_UPPER_PRESSURE_HALF',up167),('SAME_SELECTED_PRESSURE_LOOP_RELOCATED',band167),('SAME_SELECTED_FULL_PRESSURE_HEAD',head167)];ex167={'FLG:print','CurrentFLG:split_common_comb','CurrentFLG:band_budget','CurrentFLG:head_budget','Underdeck:PositiveFoundation','CurrentFLG:case','FLG:case_band','FLG:case_head'};tasks167=[]
for n,s in parts167:
 for k,v in context160.items():
  if k in ex167:continue
  if bbox_lower_bound(s.BoundBox,bounds126[k] if k in bounds126 else v.BoundBox)<1.25:tasks167.append((n,k))
tasks167.sort();rows167=[]
if first167 is None:
 for n,k in tasks167:
  s=dict(parts167)[n];v=context160[k];q=dict(part=n,other=k,source_valid=v.isValid(),required_mm=1.25)
  if not v.isValid():q['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
  else:
   gg,ww,_=s.distToShape(v);q.update(gap_mm=gg,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='NEW_RECEIVER_DELTA_SEPARATED125' if gg>=1.25-1e-7 else 'NEW_RECEIVER_DELTA_HOLD')
   if gg<1e-7:cc=s.common(v);q.update(common_valid=cc.isValid(),common_mm3=cc.Volume if cc.isValid() else None)
  rows167.append(q)
  if q['status']!='NEW_RECEIVER_DELTA_SEPARATED125':first167=q;break
  if time.monotonic()-st167>14:break
items167=[('PROTECTED_ACTUAL_U1',u167),('PROTECTED_ACTUAL_G_CASEFLOOR',casefloor167)]+members167+[('NEW_WHOLE_G_PERMANENT',newG167),('PROPOSED_U1_G_PRIMARY_PRINT',primary167),('NEW_G_UPPER_REMOVABLE_PRESSURE',up167),('COMPLETE_PRESSURE_BAND',band167),('COMPLETE_SELECTED_PRESSURE_HEAD',head167),('ACTUAL_CASECUP_ROOT_COMMON',root167),('ONLY_NEW_PRINT_DELTA',delta167)]
ar167=OUT/'day07-SOURCE-G4-open-pressure-primary-own-first-gates.breps.zip';assert not ar167.exists();ge167=[]
with zipfile.ZipFile(ar167,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items167):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge167.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge167),indent=2)+'\n').encode())
r167=dict(id='day07-SOURCE-G4-open-pressure-primary-own-first-gates',status='NEW_OPEN_G4_FIRST_FUNCTIONAL_OR_FOREIGN_HOLD' if first167 else 'NEW_OPEN_G4_ROOT_OWN_AND_CHANGED_FOREIGN_SCOPED_RECEIVED_WHOLE_STOCK_OPEN',selected=False,N01_complete=False,proposal=pp167.name,proposal_sha256=hashlib.sha256(pp167.read_bytes()).hexdigest(),new_permanent_solids=len(newG167.Solids),primary_solids=len(primary167.Solids),primary_valid=primary167.isValid(),all_postchannel_members_coverage=cov167,protected_source_material=prot167,positive_connections=joints167,newG_U1_actual_positive_common_mm3=root167.Volume,own_rows=own167,rows=rows167,cursor=len(rows167),total=len(tasks167),unreceived=len(tasks167)-len(rows167),first_falsifier=first167,channel_details='Fourfullstraightstocksolids+.2clearanceboxes each forpressure/caseband cutONLYnewGprint; no U1/boughtcasecut. ExpectedmembersAFTERintentionalchannels preserveallactualcasefloor/U1. Upper/separate2keys nominal.2fit/4full9grooves unchangedsource r1.7; no deliveredclampforcePASS.',whole_tails_case_unit_binding_roll_installation_and_DGV_source_fans_OPEN=True,no_new_source_curve_reservoir_or_V3_material=True,current_parent_not_replaced=True,archive=ar167.name,archive_sha256=hashlib.sha256(ar167.read_bytes()).hexdigest(),geometry=ge167,operation_seconds=time.monotonic()-st167,process_cpu_seconds=time.process_time()-cp167,pid=os.getpid(),session_id=46493)
p167=OUT/(r167['id']+'.json');assert not p167.exists();p167.write_bytes((json.dumps(r167,indent=2)+'\n').encode());print('BODY167',r167['status'],'root',root167.Volume,'coverage',len(cov167),'joints',len(joints167),'first',first167,'rows',len(rows167),len(tasks167),'wall',r167['operation_seconds'],'CPU',r167['process_cpu_seconds'],flush=True);print('OWNER76_IDLE',os.getpid(),flush=True)
