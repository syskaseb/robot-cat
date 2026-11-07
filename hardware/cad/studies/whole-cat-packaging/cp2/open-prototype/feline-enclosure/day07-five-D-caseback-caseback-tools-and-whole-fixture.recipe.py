import json,time,hashlib,os,zipfile
t200=time.monotonic();c200=time.process_time();assert first199 is None and len(foreign199)==len(tasks199)
tools200={'AboveM3Driver_R4p25':Part.makeCylinder(4.25,60,A.Vector(33.75,-24.5,46.22)), 'BelowM3NutSocket_R3p5':Part.makeCylinder(3.5,12,A.Vector(33.75,-24.5,19.12))}
fixednames200=['Ref_Material_P0_SideRight22_0_0','Ref_Material_P0_SideLeft22_0_0','CurrentFoundation:FoundationRail:-1','Underdeck:RestoredBank']
# These are actual retained integralparents; none may be removed to clear a tool.
fixed200={n:ctx182[n] for n in fixednames200 if n in ctx182}
# PROPOSED G4 actualwholeprimary stays integral, cannot be virtually detached.
fixed200['PROPOSED_G4_WHOLE_PRIMARY']=primary170
fixed200.update({'NEW_'+n:s for n,s in kit199.items() if not n.startswith('Hardware:')})
toolrows200=[];first200=None;wita200=None;witb200=None
for kn,a in tools200.items():
    for n,b in fixed200.items():
        lo=bbox_lower_bound(a.BoundBox,b.BoundBox)
        if lo>1e-7:row=dict(tool=kn,part=n,evidence='FULL_BOUNDS_SEPARATED',gap_lower_mm=lo,status='INITIAL_ACCESS_CLEAR')
        else:
            ga,ww,_=a.distToShape(b);co=a.common(b);ok=co.isValid() and co.Volume<1e-7
            row=dict(tool=kn,part=n,evidence='ACTUAL_COMPLETE_TOOL_AND_RETAINED_PRINT_FRAME',gap_mm=ga,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,witnesses=[[list(x),list(y)] for x,y in ww[:1]],status='INITIAL_ACCESS_CLEAR' if ok else 'INITIAL_TOOL_RETAINED_INTERFACE_HOLD')
        toolrows200.append(row)
        if row['status']!='INITIAL_ACCESS_CLEAR':first200=dict(stage='INITIAL_TOOL_FIXED_PRINT_FRAME',row=row);wita200=a;witb200=b;break
    if first200:break
parts200=[];deferred200=[];remaining200=[]
if first200 is None:
    # Complete OTHERactualcontext tool overlaps recorded for explicitassemblydependency,
    # not silently skipped as if they were absent. No newassemblyPASS from this list.
    for kn,a in tools200.items():
        for n,b in neigh199.items():
            if n in fixed200:continue
            lo=bbox_lower_bound(a.BoundBox,bounds126[n] if n in bounds126 else b.BoundBox)
            if lo>1e-7:continue
            co=a.common(b)
            if co.isValid() and co.Volume<1e-7:continue
            q=dict(tool=kn,actor=n,source_valid=b.isValid(),tool_common_valid=co.isValid(),tool_common_mm3=co.Volume if co.isValid() else None)
            # Only actual boughtbankmodules+ownends (NOT integralprintedroot) could
            # be bench-installed afterward. Their complete dependency remains OPEN.
            if n.startswith('Ref_Material_F_R') and ('Housing' in n or '_IN_' in n or '_OUT_' in n):q['classification']='BOUGHT_BANK_INSTALL_AFTER_CLAMP_REQUIRED_NOT_YET_WHOLEASSEMBLY_PROOF';deferred200.append(q)
            elif n.startswith('Station:Bank:'):q['classification']='BANK_END_FIELD_LATE_LAY_REQUIREMENT_NOT_PROVEN';deferred200.append(q)
            else:q['classification']='UNRESOLVED_REQUIRED_INITIAL_CONTEXT';remaining200.append(q)
            if time.monotonic()-t200>12:break
        if time.monotonic()-t200>12:break
    if remaining200:
        first200=dict(stage='INITIAL_TOOL_OTHER_ACTUAL_CONTEXT_FUNCTION',row=remaining200[0]);wita200=tools200[remaining200[0]['tool']];witb200=neigh199[remaining200[0]['actor']]
ar200=OUT/'day07-five-D-caseback-initial-tools-first-gate.breps.zip';assert not ar200.exists();ge200=[]
exp200=dict(tools200)
if wita200 is not None:exp200['FIRST_TOOL']=wita200;exp200['FIRST_ACTUAL_FIXED_WITNESS']=witb200
with zipfile.ZipFile(ar200,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(exp200.items()):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge200.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge200),indent=2))
p200=OUT/'day07-five-D-caseback-initial-tool-and-whole-fixture-gate.json';assert not p200.exists()
r200=dict(id=p200.stem,status='CASEBACK_INITIAL_TOOL_FIRST_FALSIFIER_STOP_BEFORE_CARRIER' if first200 else 'CASEBACK_REQUIRED_TOOL_CORE_CLEAR_OTHER_ASSEMBLY_DEPENDENCIES_OPEN',parent=p199.name,parent_sha256=hashlib.sha256(p199.read_bytes()).hexdigest(),tools=dict(above=dict(radius_mm=4.25,Z_mm=[46.22,106.22],source='Existingnominalhead2.75+125R4.25 unchangednotshrink'),below=dict(radius_mm=3.5,Z_mm=[19.12,31.12],source='Sourceopen_prototype_board_hardware.pyM3D7nominalnuttool, phase2 actualtoolprefitOPEN')),fixed_print_frame_rows=toolrows200,explicit_bank_lateinstallation_dependencies=deferred200,other_context_open=remaining200,first_falsifier=first200,actual_whole_case_carrier_not_built=True,oldC1pressure_sourceports_stock_unchanged=True,selected=False,N01_complete=False,actualcut=None,archive=ar200.name,archive_sha256=hashlib.sha256(ar200.read_bytes()).hexdigest(),geometry=ge200,operation_seconds=time.monotonic()-t200,process_cpu_seconds=time.process_time()-c200,pid=os.getpid(),session_id=46493)
p200.write_bytes((json.dumps(r200,indent=2)+'\n').encode());print('CASEBACK_TOOL_FIRST',r200['status'],'core',len(toolrows200),'defer',len(deferred200),'other',len(remaining200),'first',first200,'wall',r200['operation_seconds'],'CPU',r200['process_cpu_seconds'],hashlib.sha256(p200.read_bytes()).hexdigest(),flush=True)
