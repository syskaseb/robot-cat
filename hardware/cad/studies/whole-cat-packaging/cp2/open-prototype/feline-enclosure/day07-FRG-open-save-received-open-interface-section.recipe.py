import json,time,hashlib,os
t211=time.monotonic();c211=time.process_time()
parts211={'Permanent_frame_and_lower':newframe209,'Separate_keyed_upper':newup209,'Whole_FRG_loop':band208,'Whole_FRG_head':head208,'Full83p3_open_capacity':tail208,'Actual_FRG_case':Current35['Station:FR_G:case'],'Actual_R4_bankpad':pad206}
sections211=[]
for view,vs in [('XZ_FORE_CLOSURE',[A.Vector(-23,Y208,35),A.Vector(66,Y208,35),A.Vector(66,Y208,55),A.Vector(-23,Y208,55)]),('YZ_REAR_KEY',[A.Vector(33.9,-65,37),A.Vector(33.9,-43,37),A.Vector(33.9,-43,52),A.Vector(33.9,-65,52)])]:
    plane=Part.Face(Part.makePolygon(vs+[vs[0]]))
    for n,s in parts211.items():
        sec=s.section(plane);ll=[]
        for e in sec.Edges:
            pts=e.discretize(Deflection=.05);ll.append([[p.x,p.z] if view.startswith('XZ') else [p.y,p.z] for p in pts])
        sections211.append(dict(view=view,actor=n,curves=ll,edges=len(sec.Edges)))
pending211=[dict(**q,actual_target_actor=names175[q['index']]) for q in mpending210]
p211=OUT/'day07-FRG-open-front-received-sections-and-motion-next.json';assert not p211.exists()
r211=dict(id=p211.stem,status='OPEN_PRESSURE_FEED_RECEIVED_SCOPED_NEXT_ONE_ACTUAL_MOTION_PAIR_NOT_COLLISION',sections=sections211,next_actual_motion_pairs=pending211,separated_new_motion_pairs=r210['new_motion_conservative_pairs'],new_motion_total=5*35*129,other_unreceived_new_motion_pairs=5*35*129-r210['new_motion_conservative_pairs']-len(pending211),not_bbox_collision=True,initialkey_case_installation_still_OPEN=True,operation_seconds=time.monotonic()-t211,process_cpu_seconds=time.process_time()-c211,pid=os.getpid(),session_id=46493);p211.write_bytes((json.dumps(r211,indent=2)+'\n').encode());print('OPEN_SECTION_NEXT',pending211,'unreceived',r211['other_unreceived_new_motion_pairs'],'wall',r211['operation_seconds'],'CPU',r211['process_cpu_seconds'],hashlib.sha256(p211.read_bytes()).hexdigest(),flush=True)
