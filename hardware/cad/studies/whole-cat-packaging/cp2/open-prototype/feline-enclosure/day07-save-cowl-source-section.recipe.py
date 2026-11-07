import time,json,hashlib,os
t78=time.monotonic();cpu78=time.process_time();plane78=Part.Face(Part.makePolygon([A.Vector(x,0,z) for x,z in [(-145,45),(-5,45),(-5,116),(-145,116),(-145,45)]]));lines78=[]
objects78=[('current_S0_panel_rail',u59,'#536477'),('source_selected_S0_case',effective62['Ref_Material_S0_body_CP2_0_0'],'#7c8794'),('source_selected_key_family',effective62['Ref_Material_S0_key_CP2_0_0'],'#845ec2'),('new_fixed_guard_HOLD',guard76,'#e88021'),('source_AF5_R3p2x35_access_HOLD',tools57['caseM6_1:AF5_driver_approach'],'#cc2936'),('operator_full_R15_region',fullop75,'#1b9c85')]
for n,s,col in objects78:
    sec=s.section(plane78);curves=[]
    for e in sec.Edges:
        pts=e.discretize(Deflection=.12);curves.append([[p.x,p.z] for p in pts])
    lines78.append(dict(name=n,color=col,section_plane_y_mm=0,curves_xz_mm=curves))
p78=OUT/'day07-S0-fixed-cowl-assembly-source-section.json';assert not p78.exists();d78=dict(id=p78.stem,status='ACTUAL_GEOMETRIC_Y0_SECTION_NOT_WHOLE_ACCEPTANCE',source_receipts=[dict(path=p76.name,sha256=hashlib.sha256(p76.read_bytes()).hexdigest()),dict(path=p77.name,sha256=hashlib.sha256(p77.read_bytes()).hexdigest())],lines=lines78,witness_xz_mm=[-68.03128197843054,106.5],root_patches_are_off_section_y_plusminus12=True,source_nominal_AF5_region_not_actual_supplier_tool=True,operation_seconds=time.monotonic()-t78,process_cpu_seconds=time.process_time()-cpu78,selected=False,N01_complete=False);p78.write_bytes((json.dumps(d78,ensure_ascii=False,indent=2)+'\n').encode());print('COWL_SECTION78',sum(len(r['curves_xz_mm']) for r in lines78),d78['operation_seconds'],d78['process_cpu_seconds'],hashlib.sha256(p78.read_bytes()).hexdigest(),flush=True)
