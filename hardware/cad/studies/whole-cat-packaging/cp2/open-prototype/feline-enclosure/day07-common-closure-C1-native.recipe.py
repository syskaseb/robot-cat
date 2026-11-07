import time,json,hashlib,zipfile,os
st170=time.monotonic();cp170=time.process_time();pp170=OUT/'day07-SOURCE-G4-case-and-wire-common-closure-C1-proposal.json';pr170=json.loads(pp170.read_bytes());cb170=ctx121['FLG:case_band'];pb170=band167;case170=ctx121['CurrentFLG:case'];u170=u167
def ring_channel170(band,axial):
 bb=band.BoundBox;lo=[bb.XMin,bb.YMin,bb.ZMin];hi=[bb.XMax,bb.YMax,bb.ZMax];o=box153([[x-.2 for x in lo],[x+.2 for x in hi]]);il=[x+1.4 for x in lo];ih=[x-1.4 for x in hi];il[axial]=lo[axial]-.3;ih[axial]=hi[axial]+.3;ch=o.cut(box153([il,ih]));assert ch.isValid();missing=band.cut(ch).Volume;assert missing<1e-7;return ch,dict(axis=axial,source_stock_missing_mm3=missing,source_band_solids=len(band.Solids),empty_inner_window_preserved=True,bounds_mm=saved_bounds(ch))
pc170,pcmeta170=ring_channel170(pb170,0);cc170,ccmeta170=ring_channel170(cb170,1);channels170=[pc170,cc170]
rawlow170=cap167.common(box153([[20,45,30],[45,90,45.52]]));up170=cap167.common(box153([[20,45,45.52],[45,90,60]])).cut(cc170);members170=[]
for n,s in [('retained_casecup_root',keep166),('lower_pressure9',rawlow170)]+[(n,box153(bb)) for n,bb in pr167['permanent_new_members'].items()]:
 for ch in channels170:s=s.cut(ch)
 assert s.isValid() and s.Solids;members170.append((n,s))
for n,s in members170:
 if not n.startswith('key'):continue
 bb=s.BoundBox;up170=up170.cut(box153([[bb.XMin-.2,bb.YMin-.2,45.32],[bb.XMax+.2,bb.YMax+.2,bb.ZMax+.2]]))
assert up170.isValid();newG170=members170[0][1].multiFuse([s for _,s in members170[1:]]);assert newG170.isValid();primary170=u170.fuse(newG170);assert primary170.isValid();cov170=[dict(name=n,missing_mm3=s.cut(newG170).Volume,bounds_mm=saved_bounds(s)) for n,s in members170];protected170=dict(U1_missing_mm3=u170.cut(primary170).Volume,actual_casefloor_missing_mm3=casefloor167.cut(primary170).Volume,casefloor_volume_mm3=casefloor167.Volume);first170=None
if max(q['missing_mm3'] for q in cov170)>1e-7 or max(protected170['U1_missing_mm3'],protected170['actual_casefloor_missing_mm3'])>1e-7 or len(primary170.Solids)!=1:first170=dict(kind='MATERIAL_GUARD_HOLD',coverage=cov170,protected=protected170,primary_solids=len(primary170.Solids))
joints170=[]
for i,(n,s) in enumerate(members170):
 for m,v in members170[i+1:]:
  if bbox_lower_bound(s.BoundBox,v.BoundBox)<1e-7:
   c=s.common(v)
   if c.Volume>1e-7:joints170.append(dict(a=n,b=m,common_mm3=c.Volume,valid=c.isValid()))
root170=newG170.common(u170);assert root170.isValid();head170=head167.copy();head170.rotate(A.Vector(0,68.375,45.52),A.Vector(1,0,0),180);assert head170.isValid() and abs(head170.Volume-head167.Volume)<1e-7
lands170=[];wire170=[]
for rr in pr167['pressure_lane']['all4_current_recipes']:
 y=rr['point_mm'][1];upperzone=box153([[28.125,y-.5,47.22],[37.125,y+.5,48.2]]);lowerzone=box153([[28.125,y-.5,42.82],[37.125,y+.5,43.82]]);q=dict(wire=rr['wire'],full_land_length_mm=9,upper_crest_missing_mm3=upperzone.cut(up170).Volume,lower_bearing_missing_mm3=lowerzone.cut(newG170).Volume,upper_zone_volume_mm3=upperzone.Volume,lower_zone_volume_mm3=lowerzone.Volume);lands170.append(q)
 cyl=Part.makeCylinder(rr['radius_mm'],24.25,A.Vector(*rr['point_mm']),A.Vector(*rr['departure_axis']));c1=cyl.common(primary170);c2=cyl.common(up170);wire170.append(dict(wire=rr['wire'],retained_prefix_mm=24.25,lower_common_mm3=c1.Volume,upper_common_mm3=c2.Volume,valid=c1.isValid() and c2.isValid()))
 if max(q['upper_crest_missing_mm3'],q['lower_bearing_missing_mm3'],c1.Volume,c2.Volume)>1e-7 and first170 is None:first170=dict(kind='FULL4_PRESSURE9_OR_WIRE_GUARD_HOLD',land=q,wire=wire170[-1])
own170=[]
for n,a,b,req in [('caseband_to_upper',cb170,up170,.2),('caseband_to_primary',cb170,primary170,.2),('pressureband_to_primary',pb170,primary170,.2),('pressureband_upper_BEARING',pb170,up170,0),('pressurehead_primary',head170,primary170,.2),('pressurehead_upper',head170,up170,.2),('two_complete_stock_units',head170,cb170,.2),('boughtcase_primary',case170,primary170,0),('boughtcase_upper',case170,up170,0),('upper_lower',up170,newG170,0)]:
 c=a.common(b);gap=a.distToShape(b)[0];q=dict(role=n,gap_mm=gap,common_valid=c.isValid(),common_mm3=c.Volume,required_mm=req);own170.append(q)
 if (not c.isValid() or c.Volume>1e-7 or gap<req-1e-7) and first170 is None:first170=dict(kind='COMMON_CLOSURE_OWN_FUNCTION_HOLD',**q)
tail170=[('CASE_FULL_UNCUT_TAIL_CAPACITY',box153([[49.525,76.85,33.97],[135,80.15,35.97]])),('PRESSURE_HEAD_NECK_CAPACITY',box153([[30,80.25,48.17],[35.125,85.5,60]])),('PRESSURE_R3_ROLL_TURN_CAPACITY',box153([[30,84.2,48.17],[40,95.4,60]])),('PRESSURE_FULL_UNCUT_ROLLED_TAIL_CAPACITY',box153([[35.625,93.4,49.52],[130,95.4,52.82]]))]
stockreal170=dict(pressure_parking_profile_axes_YZ_mm=[2,3.3],reason='90degrollmakes2.5widthZ/1.2thicknessY; source2.5x1.2and.4margins unchanged, notthinnerprofile. Sourceproposal genericparkingaxis correctedbyactualdeclaredR3turn/roll beforefirstspatialtest.',nominal_feed='headtangent+Z,R3turnto+Y,6mmPROJECTrollthenR3turnto+X; centre(35.625,94.4,51.17), manualtwistfitphase2, no manuf torsionguarantee',source_stock_full_nominal_mm=[77.6,83.3],pull25_within_each_once=True,regions_are_flexible_capacity_NOT_actual_delivered_band_shapes=True)
delta170=primary170.cut(u170.fuse(oldG166));parts170=[('NEW_PRIMARY_G_DELTA',delta170),('NEW_G_KEYED_UPPER',up170),('NEW_COMPLETE_PRESSURE_HEAD_REAR',head170)]+tail170;exclude170={'FLG:print','CurrentFLG:split_common_comb','CurrentFLG:band_budget','CurrentFLG:head_budget','Underdeck:PositiveFoundation','CurrentFLG:case','FLG:case_band','FLG:case_head'};tasks170=[]
for n,s in parts170:
 bb=s.BoundBox
 for k,v in context160.items():
  if k not in exclude170 and bbox_lower_bound(bb,bounds126[k] if k in bounds126 else v.BoundBox)<1.25:tasks170.append((n,k))
tasks170.sort(key=lambda t:(0 if t[1].startswith('Ref_Material_') or 'bought' in t[1].lower() or 'case' in t[1].lower() else 1,t));rows170=[];common170=None
if first170 is None:
 for n,k in tasks170:
  a=dict(parts170)[n];b=context160[k];q=dict(part=n,other=k,source_valid=b.isValid(),required_mm=1.25)
  if not b.isValid():q['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
  else:
   gap,ww,_=a.distToShape(b);q.update(gap_mm=gap,witnesses=[[list(p),list(q)] for p,q in ww[:1]],status='NEW_COMMON_CLOSURE_DELTA_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_COMMON_CLOSURE_DELTA_HOLD')
   if gap<1e-7:common170=a.common(b);q.update(common_valid=common170.isValid(),allocated_common_mm3=common170.Volume if common170.isValid() else None)
  rows170.append(q)
  if q['status']!='NEW_COMMON_CLOSURE_DELTA_SEPARATED125':first170=q;break
  if time.monotonic()-st170>18:break
items170=[('PROTECTED_U1',u170),('PROTECTED_CASEFLOOR',casefloor167)]+members170+[('NEW_PRIMARY_G_U1',primary170),('NEW_G_PERMANENT',newG170),('NEW_UPPER_CASEBAND_SEAT',up170),('UNCHANGED_CASE_BAND',cb170),('UNCHANGED_PRESSURE_LOOP',pb170),('NEW_REAR_PRESSURE_FULL_HEAD',head170),('CASE_RING_CHANNEL_WITH_EMPTY_WINDOW',cc170),('PRESSURE_RING_CHANNEL_WITH_EMPTY_WINDOW',pc170),('ACTUAL_NEW_G_U1_JOINT',root170)]+tail170
if first170 and first170.get('other'):items170.append(('FIRST_ACTUAL_NEIGHBOR',context160[first170['other']]))
if common170 is not None and not common170.isNull():items170.append(('FIRST_VALID_ALLOCATED_COMMON',common170))
ar170=OUT/'day07-SOURCE-G4-common-closure-C1-current-geometry.breps.zip';assert not ar170.exists();ge170=[]
with zipfile.ZipFile(ar170,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items170):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge170.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge170),indent=2)+'\n').encode())
r170=dict(id='day07-SOURCE-G4-common-closure-C1-current-receipt',status='C1_FIRST_COMMON_CLOSURE_OR_STOCK_INTERFACE_HOLD' if first170 else 'C1_COMMON_CLOSURE_STATIC_SCOPED_RECEIVED_INITIAL_LAY_AND_MOTION_OPEN',selected=False,N01_complete=False,proposal=pp170.name,proposal_sha256=hashlib.sha256(pp170.read_bytes()).hexdigest(),protected_source=protected170,member_coverage=cov170,new_G_solids=len(newG170.Solids),new_primary_solids=len(primary170.Solids),positive_joints=joints170,new_G_U1_positive_common_mm3=root170.Volume,actual_ring_channel_containment=[pcmeta170,ccmeta170],full4_G_9lands=lands170,full4_prefix_nonpenetration=wire170,own_common_closure_rows=own170,stock_regions_realisation=stockreal170,rows=rows170,cursor=len(rows170),total=len(tasks170),unreceived=len(tasks170)-len(rows170),first_falsifier=first170,caseband_C0_positive_common_preserved_not_replayed=True,technical_ringbbox_137p75_floor_loss_repaired_NOT_design_failure=True,new9_fixed_freeframes=[dict(wire=q['wire'],bought_port=q['point_mm'],fixed9_X_mm=[28.125,37.125],outward_free_end=[28.125,q['point_mm'][1],45.52],outward_T=[-1,0,0],total_source_prefix_mm=24.25,remaining15_notextra_slack=True) for q in pr167['pressure_lane']['all4_current_recipes']],whole_A_U_minfit_slack_deltaL_NULL=True,current_parent_unchanged=True,archive=ar170.name,archive_sha256=hashlib.sha256(ar170.read_bytes()).hexdigest(),geometry=ge170,operation_seconds=time.monotonic()-st170,process_cpu_seconds=time.process_time()-cp170,pid=os.getpid(),session_id=46493)
p170=OUT/(r170['id']+'.json');assert not p170.exists();p170.write_bytes((json.dumps(r170,indent=2)+'\n').encode());print('BODY170',r170['status'],'protected',protected170,'root',root170.Volume,'lands',lands170,'first',first170,'rows',len(rows170),len(tasks170),'wall',r170['operation_seconds'],'CPU',r170['process_cpu_seconds'],flush=True);print('OWNER77_IDLE',os.getpid(),flush=True)
