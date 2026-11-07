import time,json,hashlib,os
t235=time.monotonic();c235=time.process_time();boxes235=[dict(actor=n,bounds_mm=saved_bounds(s),role='ACTUAL_CURRENT_BOUGHT_CASE_BOUND_ORIENTATION_NOT_CONTACT') for n,s in context230.items() if n.startswith('Carrier:bought:') and n.endswith(':case')];pl235=Part.makePlane(70,55,A.Vector(-145,-45,-29.5),A.Vector(0,0,1),A.Vector(1,0,0));sec235=[]
for n,s in [('CURRENT_BOUGHT_W037_CASE',case234),('NEW_W006_ALLOCATED_FIELD',fields233['W006']),('ONLY_NAMED_NOMINAL_QUARTER',nom234)]:
    sec=s.section(pl235);curves=[]
    for e in sec.Edges:curves.append([[v.x,v.y] for v in e.discretize(Deflection=.07)])
    sec235.append(dict(actor=n,curves_XY=curves))
p235=OUT/'day07-WHOLE9-new-order-current-bought-case-context-and-actual-section.json';assert not p235.exists();r235=dict(id=p235.stem,status='CURRENT_UNDERBODY_BOUGHT_CASE_CONTEXT_AND_ACTUAL_FIRST_SECTION_ONLY',bought_case_bounds=boxes235,actual_XY_section_Z_mm=-29.5,sections=sec235,no_new_variant_or_tests=True,source_case_world_placement_unchanged=True,operation_seconds=time.monotonic()-t235,process_cpu_seconds=time.process_time()-c235,pid=os.getpid(),session_id=46493);p235.write_bytes((json.dumps(r235,indent=2)+'\n').encode());print('ENTRY235_SECTION_SAVED',len(boxes235),r235['operation_seconds'],r235['process_cpu_seconds'],'OWNER93_NATIVE_IDLE',os.getpid(),flush=True)
