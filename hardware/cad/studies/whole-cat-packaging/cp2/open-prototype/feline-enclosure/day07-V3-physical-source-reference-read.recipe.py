import time,json,hashlib,zipfile,os
t73=time.monotonic();c73=time.process_time();budget73=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint';source73=budget73/'leg-source-near-member-plan.json';joins73=budget73/'leg-extension-budget-plan.json';route73=json.loads(source73.read_bytes());joinplan73=json.loads(joins73.read_bytes());refs73=[];shapes73={};nominal73={}
lookup73={**Current35,**restMotion};physical73=['FL1','FL2','FL3']
for route in route73['routes']:
    if route['loom'] not in physical73:continue
    src=route['source'];row=dict(loom=route['loom'],physical_leg=src['physical_leg'],source_CAD_code=src['cad_code'],source_stage=src['stage'],source_joint=src['joint'],source_owner=src['moving_saved_stage'],source_electrical=src['electrical'],source_connector_provisional=src['connector_datums_provisional'],source_pinout_not_inferred=True,parts=[])
    for label,feature,boundskey in [('pcb',src['pcb'],'pcb_bounds_world_mm'),('housing',src['housing'],'housing_bounds_world_mm'),('horn',src['drive_horn'],None)]:
        name='Ref_Material_P0_'+feature+'_0_0';s=lookup73.get(name)
        part=dict(role=label,actual_name=name,present_in_current_fixed_or_rest_motion=s is not None)
        if s is not None:
            b=saved_bounds(s);raw=s.exportBrepToString().encode();shapes73[name]=s;part.update(valid=s.isValid(),bounds_mm=b,world_brep_sha256=hashlib.sha256(raw).hexdigest(),stored_Placement=str(s.Placement),world_transform_not_reapplied=True)
            if boundskey:
                old=src[boundskey];new=b[0]+b[1];part.update(source_recorded_bounds_mm=[old[:3],old[3:]],source_vs_current_max_bound_difference_mm=max(abs(a-b) for a,b in zip(old,new)))
        row['parts'].append(part)
    pcbname='Ref_Material_P0_'+src['pcb']+'_0_0';pcb=lookup73.get(pcbname);row['recorded_nominal_socket_candidates']=[]
    if pcb is not None:
        for p in src['connector_reservation_world_mm']:
            gap=pcb.distToShape(Part.Vertex(A.Vector(*p)))[0];row['recorded_nominal_socket_candidates'].append(dict(recorded_source_world_point_mm=p,actual_current_PCB_gap_mm=gap,actual_PCB_contains_point=pcb.isInside(A.Vector(*p),1e-6,True)))
    row['frame_disposition']='SOURCE_REFERENCE_CONSISTENT_WITH_CURRENT_WORLD_NO_TRANSFORM' if all(p.get('source_vs_current_max_bound_difference_mm',0)<1e-5 and p.get('valid',False) for p in row['parts']) and all(p['actual_current_PCB_gap_mm']<1e-5 for p in row['recorded_nominal_socket_candidates']) else 'SOURCE_TO_CURRENT_PHYSICAL_DATUM_FRAME_UNRESOLVED_NO_GUESSED_TRANSFORM'
    refs73.append(row);print('PHYSICAL_SOURCE73',json.dumps(row),flush=True)
joint73=next(j for j in joinplan73['four_source_owned_extension_candidates'] if j['loom']=='FL3');ownerids73=MotionSource31['membership'].get('RL',{}).get('Knee',[]);nearest73=[]
for tag,p in [('V_lap_centre',next(r['joint_centre_world_mm'] for r in joint73['staggered_core_schedule'] if r['wire']=='W024'))]+[('source_independent9_land'+str(i),p) for i,p in enumerate(joint73['independent_land_centres_world_mm'])]:
    candidates=[]
    for name in ownerids73:
        if name not in lookup73:continue
        q=lookup73[name];gap,w,_=q.distToShape(Part.Vertex(A.Vector(*p)));candidates.append((gap,name,[[list(a),list(b)] for a,b in w[:1]]))
    candidates.sort();nearest73.append(dict(source_project_reference=tag,source_recorded_point_mm=p,nominal_owner=joint73['owner'],current_declared_owner_names=ownerids73,nearest_current_material=[dict(name=n,gap_mm=g,witnesses=w) for g,n,w in candidates[:2]],scope='Targetednominalreference-locationread, not currentworldsplicequalification or actualholder/rootproof; no motiontest/transformapplied.'))
    if candidates:shapes73[candidates[0][1]]=lookup73[candidates[0][1]]
ar73=OUT/'day07-V3-physical-source-reference-read.breps.zip';assert not ar73.exists();ge73=[]
with zipfile.ZipFile(ar73,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(shapes73.items()):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge73.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge73,scope='ONLYnamedsourcePCB/housing/horn andnearestmaterial forsourceownedjoinreference. CurrentworldBReps; no oldphysicalwirefragmentasserted.'),indent=2)+'\n').encode())
r73=dict(id='day07-V3-physical-source-reference-read',status='TARGETED_PHYSICAL_REFERENCE_READ_RECEIVED_CURRENT_WIRE_PREFIX_NOT_INFERRED',source_references=refs73,source_owned_Knee_join=joint73,join_reference_current_material=nearest73,source_physical_wire_prefix_missing_is_not_BRep_loss=True,actual_source_original_W024_minimum_mm=181.9178656704155,actual_original_cut_mm=None,physical_join_holder_qualification=joint73['holder_and_material_qualified'],splicing_geometry_material_qualification=not joint73['splice_geometry_not_yet_added_to_material_gate'],full_current_common_entry_mm=[-74.55,95.1,66.75],physical_prefix_to_current_entry_route_qualified=False,Ui=[None,None,None],source_pins=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [source73,joins73]],current_source1292_unchanged=True,current_rest_motion108_unchanged=True,no_motion_replay=True,archive=ar73.name,archive_sha256=hashlib.sha256(ar73.read_bytes()).hexdigest(),geometry=ge73,operation_seconds=time.monotonic()-t73,process_cpu_seconds=time.process_time()-c73,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p73=OUT/'day07-V3-physical-source-reference-read.json';assert not p73.exists();p73.write_bytes((json.dumps(r73,ensure_ascii=False,indent=2)+'\n').encode());print('PHYSICAL_SOURCE_FINAL73',r73['operation_seconds'],r73['process_cpu_seconds'],hashlib.sha256(p73.read_bytes()).hexdigest(),flush=True)
