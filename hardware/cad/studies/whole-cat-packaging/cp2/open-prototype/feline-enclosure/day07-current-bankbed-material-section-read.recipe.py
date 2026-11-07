import time,json,hashlib
t100=time.monotonic();cpu100=time.process_time();bottom100=parent99.Faces[1];assert bottom100.BoundBox.ZLength<1e-6 and abs(bottom100.CenterOfMass.z-52)<1e-6
contours100=[]
for wi,w in enumerate(bottom100.Wires):
    contours100.append(dict(index=wi,outer=w.isSame(bottom100.OuterWire),curves=[[[p.x,p.y] for p in e.discretize(Deflection=.1)] for e in w.Edges]))
gap100,witness100,_=patch99.distToShape(parent99)
# ONE actualsource material inventory strip following the retainedfrontedge,
# not another candidatepad/contact test or bracket variant.
strip100=Part.Face(Part.makePolygon([A.Vector(x,y,52) for x,y in [(-54.5,39.25),(-35,39.25),(-35,46.25),(-54.5,46.25),(-54.5,39.25)]]));stripactual100=strip100.common(bottom100);assert stripactual100.isValid();stripmissing100=strip100.cut(bottom100);assert stripmissing100.isValid()
source_match100=None
if parentname99 in Current35:
    q=Current35[parentname99];source_match100=dict(current1292_actor_present=True,isSame=q.isSame(parent99),bounds_mm=saved_bounds(q),volume_mm3=q.Volume,native_export_sha256=hashlib.sha256(q.exportBrepToString().encode()).hexdigest())
section100=parent99.section(Part.Face(Part.makePolygon([A.Vector(x,72,z) for x,z in [(-60,40),(115,40),(115,60),(-60,60),(-60,40)]])));sectioncurves100=[[[p.x,p.z] for p in e.discretize(Deflection=.1)] for e in section100.Edges]
moving100=[]
for n,s in proposed99.items():
    if ':PULL_TEMP:' in n:kind='temporary25pull/assembly_notoperatingrigid';
    elif ':TAIL_' in n:kind='flexiblefullstockgroupregion';
    elif ':FIXED_LOCAL_PROFILE:' in n:kind='newjointlocalfullprofileproposedKneeowned';
    else:kind='proposedmovingmaterial_or_wholeselectedtie/head'
    moving100.append(dict(name=n,owner='Motion_RL_Knee',kind=kind,world_bounds_mm=saved_bounds(s),valid=s.isValid()))
new_entry100=placement83.multVec(A.Vector(-43,8.5,4));new_exit100=placement83.multVec(A.Vector(43,8.5,4));newjoints100={k:list(placement83.multVec(A.Vector(u,8.5+v,4))) for k,u,v in [('D',-22,-2.85),('V',0,0),('G',22,2.85)]}
r100=dict(id='day07-SOURCE-current-bankbed-material-and-approach-inputs',status='ROOT_IN_VOID_RETAINED_FRONT_EDGE_MATERIAL_SOURCE_READ_ONLY',
 source_actor=parentname99,current1292_actor_relation=source_match100,source_BankOpenSpine_pin='bf0311c029d0caa23b28387114a5b8f0621cfd0c79ec72a25074733e5c80ff99',native_export_hash_is_not_claimed_identical_to_input_container=True,
 actual_bottom_face=dict(area_mm2=bottom100.Area,centre_mm=list(bottom100.CenterOfMass),contours=contours100),failed_root=dict(centre_mm=[-49,72,52],contact_area_mm2=0,embed_mm3=0,nearest_actual_material_gap_mm=gap100,witnesses=[[list(a),list(b)] for a,b in witness100[:2]]),
 real_front_edge_strip=dict(bounds_mm=[[-54.5,39.25,52],[-35,46.25,52]],required_rectangle_area_mm2=136.5,actual_material_area_mm2=stripactual100.Area,missing_area_mm2=stripmissing100.Area,not_another_root_or_support_built=True),
 actual_bank_section_y72=dict(curves_xz=sectioncurves100),new_source_frame=dict(entry_world_mm=list(new_entry100),exit_world_mm=list(new_exit100),joint_centres_world_mm=newjoints100,source_axis_world=list(axis81),source_side_world=list(side81),source_normal_world=list(normal81),all9_transport_new=True),
 new_moving_attachments=moving100,whole_source_approach='Original8x8underside-root hypothesisfalsified before newCS/length/motionqualification; no inheritedbodyroot. Actualpositive-frontspine material may supportONEfront-spine-to-open-lateral-landing loadinterface ratherthan padinvoid. Requiredfullneighbors/armsection/source9regions/R/length/slack/changedmotion must bequalified in thatnewwholeinterface, notscalarrootpointsearch.',
 all_actual_A_U_fit_slack=None,new_support_built=False,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t100,process_cpu_seconds=time.process_time()-cpu100)
p100=OUT/'day07-SOURCE-current-bankbed-material-and-approach-inputs.json';assert not p100.exists();p100.write_bytes((json.dumps(r100,ensure_ascii=False,indent=2)+'\n').encode());print('BODY100_FINAL',r100['real_front_edge_strip'],gap100,source_match100,len(moving100),r100['operation_seconds'],r100['process_cpu_seconds'],hashlib.sha256(p100.read_bytes()).hexdigest(),flush=True)
