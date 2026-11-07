import time,json,hashlib,zipfile,os
t58=time.monotonic();c58=time.process_time();rootface58=max(top58,key=lambda f:f.Area);sideface58=max(side58,key=lambda f:f.Area)
tf58=rootface58.copy();tf58.translate(A.Vector(0,0,-.5));topfoot58=tf58.extrude(A.Vector(0,0,3));sf58=sideface58.copy();sf58.translate(A.Vector(0,-.5,0));sidefoot58=sf58.extrude(A.Vector(0,2.5,0))
rt58=rootface58.CenterOfMass+A.Vector(0,0,1.25);rs58=sideface58.CenterOfMass+A.Vector(0,1,0);bridge58=rod57(rt58,rs58,2);leg58=rod57(rt58,end57,2);fixture58=topfoot58.multiFuse([sidefoot58,bridge58,leg58,panel57]);assert fixture58.isValid() and len(fixture58.Solids)==1
root58=fixture58.common(rail56);union58=fixture58.fuse(rail56);assert root58.isValid() and root58.Volume>0 and union58.isValid() and len(union58.Solids)==len(rail56.Solids)
rows58=[];stop58=None
tasks58=[n for n,q in foreign57.items() if bbox_lower_bound(fixture58.BoundBox,q.BoundBox)<=1.25]
for n in tasks58:
 q=foreign57[n];r=dict(new='S0:integral_support_root_other_side_of_W077',other=n,new_valid=fixture58.isValid(),other_valid=q.isValid())
 if q.isValid():
  gap,w,_=fixture58.distToShape(q);r.update(gap_mm=gap,required_foreign_mm=1.25,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  if gap<1e-7:
   co=fixture58.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  r['status']='CORRECTED_ROOT_FOREIGN_SEPARATED125' if gap>=1.25-1e-7 else 'S0_C1_ROOT_FOREIGN_HOLD'
 else:r['status']='INVALID_SOURCE_UNRESOLVED_NOT_CONTACT'
 rows58.append(r)
 if 'HOLD' in r['status']:stop58=r;break
physical58={'S0:compact_panel_free_splice_side_root':fixture58,**hardware57}
own58=[]
for n,s in hardware57.items():
 co=fixture58.common(s);own58.append(dict(fixing=n,fixture_valid=True,fixing_valid=s.isValid(),own_material_common_valid=co.isValid(),own_material_intrusion_mm3=co.Volume,nominal_mount_hole_and_stack_scope=True))
family58=[]
for n,s in physical58.items():
 for k in ['Ref_Material_S0_body_CP2_0_0','Ref_Material_S0_neck_CP2_0_0','Ref_Material_S0_key_CP2_0_0']:
  if bbox_lower_bound(s.BoundBox,Current35[k].BoundBox)>1.25:continue
  q=Current35[k];gap=s.distToShape(q)[0];co=s.common(q) if gap<1e-7 else None
  family58.append(dict(part=n,source_family=k,gap_mm=gap,raw_common_valid=co.isValid() if co is not None else None,raw_common_mm3=co.Volume if co is not None and co.isValid() else 0 if co is None else None,classification='Own published38pitch casefixing against filledfamily/toolreserve withomittedfixingrecess; not exactcase-metalcollision. Project flange4/keyshaft/washerfit remains sourcebackedphase2prefit. Fullfamilygeometry kept, noholes cut in bought part.'))
excludedTools58={n for n in s0names56 if any(s in n for s in ['ring_','nut_','washer_','key_'])}|{'Ref_Material_S0_body_CP2_0_0','Ref_Material_S0_neck_CP2_0_0'}
toolcontext58={n:s for n,s in Current35.items() if n not in excludedTools58};toolcontext58['new_S0_print']=fixture58
toolrows58=[]
for n,s in tools57.items():
 for k,q in toolcontext58.items():
  if bbox_lower_bound(s.BoundBox,q.BoundBox)>0:continue
  if not q.isValid():toolrows58.append(dict(tool=n,other=k,status='INVALID_TOOL_NEIGHBOR_OPEN'));continue
  gap,w,_=s.distToShape(q);co=s.common(q) if gap<1e-7 else None;cv=co.isValid() if co is not None else None;vol=co.Volume if co is not None and cv else 0 if co is None else None
  toolrows58.append(dict(tool=n,other=k,gap_mm=gap,common_valid=cv,common_mm3=vol,status='INITIAL_TOOL_APPROACH_CLEAR' if vol is not None and vol<1e-7 else 'INITIAL_TOOL_APPROACH_HOLD',witnesses=[[list(a),list(b)] for a,b in w[:1]]))
outside58=fixture58.cut(BodyOuter31);outgap58=fixture58.distToShape(boundary56)[0];outline58=dict(valid=fixture58.isValid(),outside_valid=outside58.isValid(),outside_volume_mm3=outside58.Volume,boundary_gap_mm=outgap58,required_mm=3.25,ok=fixture58.isValid() and outside58.isValid() and outside58.Volume<1e-7 and outgap58>=3.25)
ar58=OUT/'day07-S0-current-case-mount-root-correction1.breps.zip';assert not ar58.exists();ge58=[]
with zipfile.ZipFile(ar58,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate([('S0:compact_panel_free_splice_side_root',fixture58),('SOURCE:actual_free_parent_twoface_coupon',coupon58),('S0:actual_parent_joint',root58)]+[(n,foreign57[n]) for n in tasks58]+[(r['other'],toolcontext58[r['other']]) for r in toolrows58]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge58.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge58,scope='One complete loadpath correction around preserved W077restraint. Samecasepanel/M6kit/tools by immutableC0refs, no furthercasepose or bracketvariant'),indent=2)+'\n').encode())
ok58=stop58 is None and all(r['own_material_common_valid'] and r['own_material_intrusion_mm3']<1e-7 for r in own58) and all(r['status']=='INITIAL_TOOL_APPROACH_CLEAR' for r in toolrows58) and outline58['ok']
r58=dict(id='day07-S0-current-mounted-case-correction1-receipt',status='S0_CASE_MOUNT_LOCAL_STATIC_ROOT_TOOL_OUTLINE_RECEIVED_OWN_PRODUCT_FIT_PHASE2' if ok58 else 'S0_CASE_MOUNT_C1_HOLD',rows=rows58,cursor=len(rows58),total=len(tasks58),unreceived=len(tasks58)-len(rows58),stop=stop58,
 actualroot=dict(parent='CurrentFoundation:FoundationRail:-1',top_source_face_mm2=rootface58.Area,side_source_face_mm2=sideface58.Area,source_face_centres=[list(rootface58.CenterOfMass),list(sideface58.CenterOfMass)],common_valid=root58.isValid(),common_mm3=root58.Volume,whole_parent_union_valid=union58.isValid(),whole_parent_union_solids=len(union58.Solids),source_parent_solids=len(rail56.Solids),strut_radius_mm=2),
 correction='C0anchored across protectedW077band space5.280364HOLD. Onewholeloadpath correction takesactualfreeparentland onother side ofcompleteW077restraint (top18/side12 actualfaces), preservescasepose/panel/hardware/wires/band, reroutesstructuralstrut fromthat source land. Not0.1mmclearance reduction/columnoffset or thirdvariant.',
 unchanged_hardware=dict(source_archive=r57['archive'],source_archive_sha256=r57['archive_sha256'],source_fixing_geometry=[r for r in r57['geometry'] if r['name'] in hardware57],physical_quantities={'M6x20':2,'M6washer':4,'M6nutAF10':2},oldM2deck_not_applicable=True,no_inventory_availability_or_suppliednut_credit=True,foreign_whole_current_scope='All8sourcecasefixings had no bboxcandidate foreign at1.25 in C0 full1292 and arebyteidentical; notretested.',operational_outline_reused={n:v for n,v in r57['outline'].items() if n in hardware57}),
 own_hardware_print_fit=own58,own_product_family_records=family58,own_fit_acceptance='Nominal publishedsource38pitch/neck24 mappedactualframe and full hardwarestack. Opaque ownfamily intersections retained as product-fit assumptions; NOTphysicalsuppliermetrologyPASS. Exact flange/recess/keyheight/torque/creep phase2, no inventedvoid or hole in boughtCAD. Casefixing foreigntoall unrelated8S0terminalmetals kept1.25.',
 tools=dict(geometry_source_archive=r57['archive'],geometry_source_archive_sha256=r57['archive_sha256'],tools=[r for r in r57['geometry'] if r['name'] in tools57],stage='Actualcase2M6before6ring/washer/nutterminalparts andkey, on accessibleunpoweredframe; thoseexactsourceparts notyetinstalled, source2studs andALLothercurrenthardware/prints remain. Ownopaque case recess fit remainsphase2; foreigninitialtoolproofnotcertifyinga hollowfamily.',excluded_not_yet_installed=sorted(excludedTools58),included_static_count=len(toolcontext58),rows=toolrows58,full_approachcount=4,not_fullN08_or_rapidservice=True),
 operational_outline=outline58,source_original11_outline_reused=p56.name,source_frame_mapping_reused=p56.name,
 remaining='CurrentW076/W066/W043endposes/selectedparts/nominalR/insulation unchanged. Their wholelayout routing/lengthslack and routineS0keyaperture remain in globalN01 scope; no historical80/330/40cutcredit. No actualpower/physicalcuts/purchases. Changedbodymotion/sourcewire fields ifnotreceived mustbe completed before wholeN01.',
 archive=ar58.name,archive_sha256=hashlib.sha256(ar58.read_bytes()).hexdigest(),geometry=ge58,operation_seconds=time.monotonic()-t58,process_cpu_seconds=time.process_time()-c58,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493,correction_used=1,correction_max=1,no_third_variant=True)
p58=OUT/'day07-S0-current-mounted-case-correction1-receipt.json';assert not p58.exists();p58.write_bytes((json.dumps(r58,ensure_ascii=False,indent=2)+'\n').encode());print('S0_MOUNT58',r58['status'],r58['actualroot'],rows58,own58,toolrows58,outline58,r58['operation_seconds'],r58['process_cpu_seconds'],hashlib.sha256(p58.read_bytes()).hexdigest(),flush=True)
