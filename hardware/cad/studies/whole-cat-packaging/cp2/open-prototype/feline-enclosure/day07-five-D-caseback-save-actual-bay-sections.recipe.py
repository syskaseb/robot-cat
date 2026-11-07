import json,time,hashlib,os,zipfile
t205=time.monotonic();c205=time.process_time();assert first204 is not None
parts205={'New_caseback_carrier':base201,'New_case_capture_upper':up202,'New_source_neck':kit199['Neck'],'Actual_P0_side':frame199,'Actual_D5_case':case201,'New_entire_M3':kit199['Hardware:Screw'],'Current_FRG_band':witb204,'Frozen_W004_capacity':voids193[0]}
sections205=[]
for view,vs in [('XZ_Yaxis',[A.Vector(25,-24.5,25),A.Vector(90,-24.5,25),A.Vector(90,-24.5,62),A.Vector(25,-24.5,62)]),('XY_Zstockwitness',[A.Vector(25,-65,40.52),A.Vector(90,-65,40.52),A.Vector(90,5,40.52),A.Vector(25,5,40.52)])]:
    plane=Part.Face(Part.makePolygon(vs+[vs[0]]))
    for n,s in parts205.items():
        sec=s.section(plane);lines=[]
        for e in sec.Edges:
            pts=e.discretize(Deflection=.06);lines.append([[q.x,q.z] if view.startswith('XZ') else [q.x,q.y] for q in pts])
        sections205.append(dict(view=view,actor=n,curves=lines,edges=len(sec.Edges)))
p205=OUT/'day07-five-D-caseback-actual-load-and-stock-sections.json';assert not p205.exists();r205=dict(id=p205.stem,status='ACTUAL_CASEBACK_BEARING_LOAD_AND_FRG_STOCK_MARGIN_HOLD_VIEW',actual_source_shapes=True,sections=sections205,first_falsifier=first204,not_physical_wire_or_band_contact=True,operation_seconds=time.monotonic()-t205,process_cpu_seconds=time.process_time()-c205,pid=os.getpid(),session_id=46493);p205.write_bytes((json.dumps(r205,indent=2)+'\n').encode());print('CASEBACK_ACTUAL_VIEW',sum(q['edges'] for q in sections205),r205['operation_seconds'],r205['process_cpu_seconds'],hashlib.sha256(p205.read_bytes()).hexdigest(),flush=True)
