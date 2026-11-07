import json,time,hashlib,os
tr113=time.monotonic();tc113=time.process_time();patch113=Part.makeBox(60,45,30,A.Vector(-135,25,20));near113=[]
for n,s in ctx111.items():
    if bbox_lower_bound(patch113.BoundBox,s.BoundBox)>0:continue
    near113.append(dict(actor=n,bounds_mm=saved_bounds(s),source='Currentfixed+rest108neutral+new21operating4tempcompletecontext; bboxselectionONLYnotcontact',relation='same_actual_retainedP0' if n==badname112 else 'unclassified_actual_or_capacity'))
cyl113=[]
for i,f in enumerate(bad112.Faces):
    if type(f.Surface).__name__=='Cylinder':cyl113.append(dict(face=i,Radius_mm=f.Surface.Radius,axis=list(f.Surface.Axis),centre=list(f.Surface.Center),face_area_mm2=f.Area))
under113=ctx111['Underdeck:PositiveFoundation'];planes113=[]
for i,f in enumerate(under113.Faces):
    if type(f.Surface).__name__=='Plane':
        n=f.normalAt(0,0);bb=f.BoundBox
        if n.z<-.99 and bb.XMax>-130 and bb.XMin<-85 and bb.YMax>38 and bb.YMin<67 and bb.ZMax<45:planes113.append(dict(face=i,area_mm2=f.Area,bounds_mm=saved_bounds(f),normal=list(n),centre=list(f.CenterOfMass),root_available_NOT_proved=True))
r113=dict(id='day07-SOURCE-actual-frame-passage-source-inputs',status='SOURCE_CURRENT_MATERIAL_AND_FULL_NEIGHBOR_METADATA_READ_NOT_ROUTE_ACCEPTANCE',frame_actor=badname112,actual_frame_isSame_Current1292=True,frame_bounds_mm=saved_bounds(bad112),actual_cylinder_faces=cyl113,hardware_function='Cylinder/hexrecessgeometryisNOTanunusedwireportal; actualselectedmetal+currentneighborhoodmustbeaccounted. No virtualboltremoval/materialcut.',neighbor_selection_bounds_mm=saved_bounds(patch113),neighbor_rows=near113,actual_U1_downfacing_material_faces=planes113,classification='Materialfaces/bores/fullneighborboundsONLY. Shape/bboxoverlapnotcontact; usefulU1undersideactualprint maycandidateleadingrootlater but NO rootproof/newmaterial built.',source_frame_evidence=p112.name,source_frame_evidence_sha256=hashlib.sha256(p112.read_bytes()).hexdigest(),operation_seconds=time.monotonic()-tr113,process_cpu_seconds=time.process_time()-tc113,source1292_effective1311_rest108_unchanged=True,pid=os.getpid(),session_id=46493)
p113=OUT/'day07-SOURCE-actual-frame-passage-source-inputs.json';assert not p113.exists();p113.write_bytes((json.dumps(r113,indent=2)+'\n').encode());print('SOURCE113_INPUTS',len(near113),len(planes113),cyl113,hashlib.sha256(p113.read_bytes()).hexdigest(),flush=True)
