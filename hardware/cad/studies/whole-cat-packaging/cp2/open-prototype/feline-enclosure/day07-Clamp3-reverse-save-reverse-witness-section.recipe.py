import json,time,hashlib,os,zipfile
t198=time.monotonic();c198=time.process_time();assert first197 is not None
frame198=Current35['Ref_Material_P0_SideRight22_0_0'];faces198=[]
for i,f in enumerate(frame198.Faces):
    bb=f.BoundBox
    if type(f.Surface).__name__=='Plane' and abs(bb.ZLength)<1e-6 and (abs(bb.ZMin-37.02)<1e-5 or abs(bb.ZMin-38.52)<1e-5) and bb.XMin<72<bb.XMax:
        faces198.append(dict(face_index=i,bounds_mm=saved_bounds(f),area_mm2=f.Area,plane_type=type(f.Surface).__name__))
parts198={'W004_fullallocated':lastfield194,'Original_full_screw':met197['Screw'],'Reversed_full_screw':rev197['Screw'],'Reversed_full_nut':rev197['Nut'],'Reversed_upper_washer':rev197['BottomWasher'],'Reversed_lower_washer':rev197['TopWasher'],'Actual_lower_jaw':Current35['Station:Anchor:Rear:LowerClampJaw3'],'Actual_top_pad':Current35['Station:Anchor:Rear:TopClampPad3'],'C1_primary_unchanged':base193,'Actual_P0_side_unchanged':frame198}
sections198=[]
for y in [-24.5,first197['witnesses'][0][1][1]]:
    vs=[A.Vector(58,y,25),A.Vector(85,y,25),A.Vector(85,y,62),A.Vector(58,y,62)]
    plane=Part.Face(Part.makePolygon(vs+[vs[0]]))
    for n,s in parts198.items():
        sec=s.section(plane);lines=[]
        for e in sec.Edges:
            pts=e.discretize(Deflection=.04);lines.append([[float(q.x),float(q.z)] for q in pts])
        sections198.append(dict(actor=n,Y_mm=y,curves_xz=lines,edges=len(sec.Edges)))
p198=OUT/'day07-Clamp3-opposite-face-actual-stack-sections.json';assert not p198.exists()
r198=dict(id=p198.stem,status='REVERSED_FULLSTACK_FIRST_TIP_MARGIN_HOLD_ACTUAL_SECTIONS_NO_NEW_DESIGN',first_gate=p197.name,first_gate_sha256=hashlib.sha256(p197.read_bytes()).hexdigest(),actual_P0_actor='Ref_Material_P0_SideRight22_0_0',actual_native_horizontal_bearing_faces=faces198,source_mount_classification='Actual+source paired printjaw/pad clamp native rail edge with inboard screw; source no rail drilling. These sections do not claim newassembly access/root approval.',actual_axis=[72,-24.5],source_frame_native_bounds_mm=saved_bounds(frame198),sections=sections198,first_falsifier=first197,meaning='Full14mm shaft reversal moves tip into upperwire neighborhood; newhead below is insufficient. Positive.739753marginHOLD, not wirecontact. Belowtool/uppernutantirotation/capture remainUNRECEIVED afterfirstfalsifier, no newpockets.',selected=False,N01_complete=False,operation_seconds=time.monotonic()-t198,process_cpu_seconds=time.process_time()-c198,pid=os.getpid(),session_id=46493)
p198.write_bytes((json.dumps(r198,indent=2)+'\n').encode());print('CL3_ACTUAL_SECTION',len(faces198),len(sections198),sum(q['edges'] for q in sections198),'wall',r198['operation_seconds'],'CPU',r198['process_cpu_seconds'],hashlib.sha256(p198.read_bytes()).hexdigest(),flush=True)
