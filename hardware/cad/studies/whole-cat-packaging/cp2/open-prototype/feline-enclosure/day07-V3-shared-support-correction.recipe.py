import time,json,hashlib,zipfile,os
t54=time.monotonic();c54=time.process_time();oldroot54=Current35['V:new_root_material'];oldsupport54=Current35['V:functional_pressure_support']
cuts54=[box49([-17,15.65,59],[-15.6,37.75,61]),box49([-17,15.65,61],[-15.6,16.65,64.5])];cut54=cuts54[0].fuse(cuts54[1]);retroot54=oldroot54.cut(cut54);retsupport54=oldsupport54.cut(cut54)
bar54=box49([-41.4,13.5,64.5],[9.4,15.5,66.2]);fingers54=[box49([x,15.3,64.5],[x+1.4,16,66.2]) for x in [-41,-17,7]];add54=bar54.multiFuse(fingers54);root54=retroot54.fuse(add54);support54=retsupport54.fuse(add54)
protected54=oldsupport54.cut(oldroot54);lostcap54=protected54.cut(support54);removed54=oldsupport54.cut(retsupport54);assert not removed54.isNull() and removed54.isValid() and abs(removed54.Volume-(oldsupport54.Volume-retsupport54.Volume))<1e-6;insideDeclared54=removed54.common(cut54);assert insideDeclared54.isValid();outside_volume54=removed54.Volume-insideDeclared54.Volume;assert support54.isValid() and root54.isValid() and lostcap54.Volume<1e-7 and outside_volume54<1e-7
wire54=[]
for n,s in new53.items():
 gap,w,_=s.distToShape(root54);co=s.common(root54) if gap<1e-7 else None
 wire54.append(dict(region=n,new_support_valid=root54.isValid(),region_valid=s.isValid(),gap_mm=gap,required_mm=.2,common_valid=co.isValid() if co is not None else None,common_mm3=co.Volume if co is not None and co.isValid() else 0 if co is None else None,status='FUNCTIONAL_GUIDE_REGION_CLEAR02' if gap>=.2-1e-7 else 'CHANGED_V3_SUPPORT_INTERFACE_HOLD_NOT_PHYSICAL_WIRECONTACT',witnesses=[[list(a),list(b)] for a,b in w[:1]]))
rows54=[];stop54=next((r for r in wire54 if 'HOLD' in r['status']),None)
# Only added crossbar/fingers vs full real context. Old support/oldroot are construction children of THIS part, not foreign.
for n,q in Current35.items():
 if n in ['V:new_root_material','V:functional_pressure_support','V:common_region'] or any(n.startswith(w+':') for w in ['W020','W022','W024']):continue
 if bbox_lower_bound(add54.BoundBox,q.BoundBox)>1.25:continue
 r=dict(added='V:shared_source_clamp_crossbar',other=n,added_valid=add54.isValid(),other_valid=q.isValid())
 if q.isValid():
  gap,w,_=add54.distToShape(q);owncap=n.startswith('Station:Bank:') and any(w+'/' in n for w in ['W020','W022','W024']) and n.endswith(':split_cap_exterior');r.update(named_source_cap_print_own=owncap,gap_mm=gap,required_mm=0 if owncap else 1.25,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  if gap<1e-7:
   co=add54.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  r['status']='NAMED_V3_SOURCE_RECEIVER_SAMEPRINT_JOINT' if owncap else 'ADDED_SHARED_SUPPORT_SEPARATED125' if gap>=1.25-1e-7 else 'ADDED_SHARED_SUPPORT_HOLD'
 else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 rows54.append(r)
 if 'HOLD' in r['status']:stop54=r;break
 if time.monotonic()-t54>40:break
ar54=OUT/'day07-V3-source-clamp-shared-support-correction.breps.zip';assert not ar54.exists();ge54=[]
with zipfile.ZipFile(ar54,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate([('V:new_root_material',root54),('V:functional_pressure_support',support54),('V:sourceclamp_crossbar_added',add54),('DECLARED:old_W022_arm_lower_tab_cut',cut54)]+[(r['other'],Current35[r['other']]) for r in rows54]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge54.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge54,scope='One source-driven support correction; actual3full9caps and boughtTE preserved'),indent=2)+'\n').encode())
r54=dict(id='day07-V3-source-clamp-shared-support-correction',status='SHARED_V3_SUPPORT_HOLD' if stop54 else 'SHARED_V3_SUPPORT_LOCAL_GATE_RECEIVED',wire_region_interfaces=wire54,changed_foreign_rows=rows54,stop=stop54,
 source_function='Old12-cell root carries3 original full9 bank clamps. W020 new lower regionalbody crosses old W022 arm, not bought hardware. Replace only declared W022arm/lower-tab material by one transverse shared sourcecap bar; keep W020/W024 original root paths and all three cap geometries. W022foot/riser may remain harmless unloaded material connected through BankBed; no fake physical extra part.',
 C0_root_witness=dict(file=p53.name,sha256=hashlib.sha256(p53.read_bytes()).hexdigest(),validcommon_mm3=13.220227399757654,not_actual_wirecontact=True),correction_used=1,correction_max=1,no_third_support_offset=True,
 protected_cap_lost_mm3=lostcap54.Volume,removed_outside_declared_old_W022_arm_lower_tab_mm3=outside_volume54,removed_measured_before_added_bar_mm3=removed54.Volume,initial_build_interruption="ValueError Nullshape on empty outside-cut Boolean; independent valid removed/commonwithdeclaredcut both66.78 proves covered removal. One metadata NameError corrected. Resumed missing gates only; no geometry rebuild/offset.",source_grip_interface="Free-region radius1.4 tested against root material; original full9 nominal1.0 tube/own groove interface preserved unchanged. No foreign physical/clamp margin waived.",source_full9_and_all_stock_untouched=True,
 actual_print_join=dict(crossbar_to_retained_support_common_mm3=add54.common(retsupport54).Volume,corrected_support_valid=support54.isValid(),support_solids=len(support54.Solids),whole_BankBed_connection_inherited_from_unchanged_W020_W024_sourcefeet=True,not_whole_reopen_or_strengthproof=True),
 original_V_capacity_HOLD_NOT_closed=True,remaining='All changed V3 region foreign pairs beyond first C0 witness remain unreceived. Require current corrected whole support/region root integration, source intermediate guide lifecycle/replacement, local crossoccupancy and whole physicalunit nominalbudgets before V3 acceptance. No third wire offset or column move.',
 archive=ar54.name,archive_sha256=hashlib.sha256(ar54.read_bytes()).hexdigest(),geometry=ge54,operation_seconds=time.monotonic()-t54,process_cpu_seconds=time.process_time()-c54,selected=False,N01_complete=False)
p54=OUT/'day07-V3-source-clamp-shared-support-correction.json';assert not p54.exists();p54.write_bytes((json.dumps(r54,ensure_ascii=False,indent=2)+'\n').encode());print('V54_SHARED_SUPPORT',r54['status'],wire54,rows54,stop54,r54['actual_print_join'],r54['operation_seconds'],r54['process_cpu_seconds'],hashlib.sha256(p54.read_bytes()).hexdigest(),flush=True)
