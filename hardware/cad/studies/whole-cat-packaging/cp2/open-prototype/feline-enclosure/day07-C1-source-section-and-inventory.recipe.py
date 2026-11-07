# Only source-derived section and unopened candidate inventory after first falsifier; no further collision tests.
st136=time.monotonic();cp136=time.process_time();names136=[]
for n,s in parts135:
 for k in ctx121:
  if k==q135['root']['actor'] or k in ['W068/single/end:0:saddle','W068/single/end:0:band_budget','W068/single/end:0:head_budget']:continue
  if bbox_lower_bound(s.BoundBox,bounds126[k])<1.25:names136.append([n,k])
plane136=Part.makePlane(80,80,A.Vector(-140,-23,0),A.Vector(0,1,0));sections136=[]
for n,s in [('CURRENT_FRAME',fr135),('PLANNED_UPSTAND',up135),('PLANNED_BRIDGE',bridge135),('ACTUAL_INTERSECTION',lastco135)]:
 sec=s.section(plane136);curves=[]
 for e in sec.Edges:curves.append([[v.x,v.z] for v in e.discretize(Deflection=.03)])
 sections136.append(dict(name=n,curves_xz=curves))
r136=dict(id='day07-W068-inboard-C1-source-prong-section',status='ACTUAL_SECTION_DATA_NO_MORE_COLLISION_TESTS',section_Y_mm=-23,sections=sections136,unreceived_foreign_candidate_keys=names136,unreceived_foreign_count=len(names136),own_frame_received=3,own_frame_unreceived=['OVERFRAME_BRIDGE','ROOT_FULL6_HEAD'],full_stock_pressure_tails_unreceived=True,source_frame_name=q135['root']['actor'],source_frame_brep_sha256=ge135[0]['sha256'],actual_member_common_mm3=first135['common_mm3'],no_union_built=True,union_coverage_not_claimed=True,operation_seconds=time.monotonic()-st136,process_cpu_seconds=time.process_time()-cp136,pid=os.getpid(),session_id=46493)
p136=OUT/'day07-W068-inboard-C1-source-prong-section.json';assert not p136.exists();p136.write_bytes((json.dumps(r136,indent=2)+'\n').encode());print('BODY136',len(names136),'UNRECEIVED source candidates section data saved wall',r136['operation_seconds'],'CPU',r136['process_cpu_seconds'],flush=True);print('OWNER67_IDLE',os.getpid(),flush=True)
