import time,json,hashlib,zipfile,os
t80=time.monotonic();cpu80=time.process_time();blocked80=rows79[-1]['other'];washer80=effective62[blocked80];point80=A.Vector(*rows79[-1]['witnesses'][0][0]);membership80=[n for n,s in hood79.items() if s.isInside(point80,1e-6,True)]
ar80=OUT/'day07-S0-cowl-C1-actual-washer-witness.breps.zip';assert not ar80.exists();ge80=[]
with zipfile.ZipFile(ar80,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([(blocked80,washer80),('S0:left_rear_return_NEWmaterial',hood79['left_rear_return']),('S0:full_C1_guard_not_selected',guard79),('S0:preserved_AF5_R3p2x35',tools57['caseM6_1:AF5_driver_approach'])]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);b=s.optimalBoundingBox();ge80.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge80,scope='Exactcurrentwasher+newmaterialwitness+unchangedfullAF5; no contactpairreplay ornewvariant.'),indent=2)+'\n').encode())
views80=[]
for yy in [0,-42]:
    plane=Part.Face(Part.makePolygon([A.Vector(x,yy,z) for x,z in [(-145,45),(-5,45),(-5,116),(-145,116),(-145,45)]]));lines=[]
    items=[('fixed_C1_guard_HOLD',guard79,'#df8219'),('current_S0_parent',u59,'#687b8e'),('actual_PWM_metal_washer',washer80,'#cb263a')]
    if yy==0:items += [('unchanged_AF5_full_region',tools57['caseM6_1:AF5_driver_approach'],'#7c4abb'),('unchanged_operator_R15',fullop75,'#1c9981')]
    for n,s,col in items:
        sec=s.section(plane);curves=[]
        for e in sec.Edges:curves.append([[p.x,p.z] for p in e.discretize(Deflection=.08)])
        lines.append(dict(name=n,color=col,curves_xz_mm=curves))
    views80.append(dict(section_y_mm=yy,lines=lines))
r80=dict(id='day07-S0-cowl-C1-actual-washer-witness-and-sections',status='VALID_ACTUAL_FOREIGN_METAL_WASHER_INTERSECTION_NEW_REAR_RETURN_NOT_TOOL_ENVELOPE_ONLY',first_gate_receipt=p79.name,first_gate_sha256=hashlib.sha256(p79.read_bytes()).hexdigest(),witness_members=membership80,negative=rows79[-1],washer_function='CurrentretainedPWMbottomfastenerwasher, actualringwithouterR2.25/innerR1.1/thickness.3; NOTnewS0casefixing orprintedownershipjoint. ExactpurchasedSKUmetrology notclaimed; actualcurrentretainedmetalgeometry cannotbeignored.',source_current1292_actor_present=blocked80 in Current35,source_current_role=Sources35.get(blocked80),not_retested_old_current_pairs=True,body_unchanged_no_current_overlay_applied=True,archive=ar80.name,archive_sha256=hashlib.sha256(ar80.read_bytes()).hexdigest(),geometry=ge80,views=views80,operation_seconds=time.monotonic()-t80,process_cpu_seconds=time.process_time()-cpu80,selected=False,N01_complete=False)
p80=OUT/'day07-S0-cowl-C1-actual-washer-witness-and-sections.json';assert not p80.exists();p80.write_bytes((json.dumps(r80,ensure_ascii=False,indent=2)+'\n').encode());print('COWL_EVIDENCE80',membership80,r80['operation_seconds'],r80['process_cpu_seconds'],hashlib.sha256(p80.read_bytes()).hexdigest(),flush=True)
