import time,json,hashlib,os
t223=time.monotonic();c223=time.process_time();ss223=[]
# A makePlane normal +Y and local +X extends local V toward -Z. Move origin to Z80, not Z30.
plane223=Part.makePlane(50,45,A.Vector(30,-23.375,80),A.Vector(0,1,0),A.Vector(1,0,0))
for n,s in parts222:
    sc=s.section(plane223);curves=[]
    for e in sc.Edges:curves.append([[v.x,v.z] for v in e.discretize(Deflection=.08)])
    ss223.append(dict(view='XZ_Yminus23p375',actor=n,curves=curves))
assert all(q['curves'] for q in ss223 if q['actor'] in ['SAME_FINAL_BOUGHT_CASE','EXACT_VERTICAL_CASE_ENTRY12','RETAINED_ACTUAL_FR4_IN_BODY'])
p223=OUT/'day07-D5-open-top-XZ-actual-section-plane-range-correction.json';assert not p223.exists();r223=dict(id=p223.stem,status='VISUAL_PLANE_RANGE_CORRECTION_ONLY_NO_GEOMETRY_OR_GATE_CHANGE',source=p222.name,source_sha256=hashlib.sha256(p222.read_bytes()).hexdigest(),prior_XZ_empty_reason='Original plane local+V ran toward -Z from30, outside operands. Correctorigin80 covers actualZ35..80. PriorYZactualsections and allBOPevidence unchanged.',sections=ss223,operation_seconds=time.monotonic()-t223,process_cpu_seconds=time.process_time()-c223,pid=os.getpid(),session_id=46493);p223.write_bytes((json.dumps(r223,indent=2)+'\n').encode());print('KEEPER223_SECTION_ONLY',[(q['actor'],len(q['curves'])) for q in ss223],r223['operation_seconds'],r223['process_cpu_seconds'],'OWNER89_IDLE',os.getpid(),flush=True)
