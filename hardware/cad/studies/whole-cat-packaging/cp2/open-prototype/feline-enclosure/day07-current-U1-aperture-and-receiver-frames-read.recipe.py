import time,json,hashlib,os
st163=time.monotonic();cp163=time.process_time();u163=ctx121['Underdeck:PositiveFoundation'];roi163=[[-80,24,25],[80,96,44]];face163=[]
for i,f in enumerate(u163.Faces):
 bb=f.BoundBox
 if bb.ZMax<25 or bb.ZMin>44 or bb.XMax<-80 or bb.XMin>80 or bb.YMax<24 or bb.YMin>96:continue
 if type(f.Surface).__name__=='Plane' and f.Area>8:face163.append(dict(face=i,area_mm2=f.Area,bounds_mm=saved_bounds(f),normal=list(f.normalAt(0,0))))
sections163=[]
for xx in [xc160,xc160+R160,-63]:
 pl=Part.Face(Part.makePolygon([A.Vector(xx,y,z) for y,z in [(-5,18),(98,18),(98,52),(-5,52),(-5,18)]]));s=u163.section(pl);sections163.append(dict(X_mm=xx,actual_U1_curves_yz=[[[p.y,p.z] for p in e.discretize(Deflection=.05)] for e in s.Edges]))
cyl163=[]
for n in ['CurrentDFL:DFL:cap','CurrentFLG:split_common_comb','Station:Bank:W020/body/end:split_cap_exterior','Station:Bank:W022/body/end:split_cap_exterior','Station:Bank:W024/body/end:split_cap_exterior']:
 s=ctx121[n]
 for i,f in enumerate(s.Faces):
  if type(f.Surface).__name__!='Cylinder':continue
  su=f.Surface
  if su.Radius>2.5:continue
  cyl163.append(dict(actor=n,face=i,radius_mm=su.Radius,axis=list(su.Axis),axis_origin=list(su.Center),face_parameters=list(f.ParameterRange),actual_face_bounds_mm=saved_bounds(f)))
node163=CurrentCanon31['current_foreign_upper_plenum_correction1'];flg163=CurrentCanon31['current_foreign_FLG_complete_four_port'];r163=dict(id='day07-SOURCE-current-U1-aperture-and-nine-receiver-frame-read',status='ACTUAL_MATERIAL_SECTIONS_SOURCE_FUNCTIONS_AND_CYLINDER_LAND_FRAMES_NOT_NEW_FIT_ACCEPTANCE',actual_U1_bounds=saved_bounds(u163),actual_U1_member_sha256=hashlib.sha256(u163.exportBrepToString().encode()).hexdigest(),source_U1_short_loadpath=node163['U1_short_loadpath'],protected_retirement_function=node163['U1_old_return_complete_retirement'],current_U1_source_archive='day30-astra-upper-plenum-correction1.breps.zip',source_function_receipt='day07-coordinator-fixed-print-source-functions.json',lower_faces=face163,U1_YZ_sections=sections163,actual_receiver_cylindrical_lands=cyl163,FLG_source_recipes=flg163['recipes'],D_source_9frame_reuse=json.loads((OUT/'day07-SOURCE-current-BUS-DG-alias-stock-and-entry-function.json').read_bytes())['source_projection_interface']['D9'],no_native_transform_or_XML_applied=True,source_functions_not_cut_or_reclassified=True,no_paircheck_or_old_root_replay=True,operation_seconds=time.monotonic()-st163,process_cpu_seconds=time.process_time()-cp163,pid=os.getpid(),session_id=46493)
p163=OUT/(r163['id']+'.json');assert not p163.exists();p163.write_bytes((json.dumps(r163,indent=2)+'\n').encode());print('BODY163',len(face163),'faces',len(cyl163),'lands',json.dumps(cyl163)[:1200],'wall',r163['operation_seconds'],'CPU',r163['process_cpu_seconds'],flush=True);print('OWNER75_IDLE',os.getpid(),flush=True)
