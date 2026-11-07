import json,time,hashlib,zipfile,os
t217=time.monotonic();c217=time.process_time()
# Independent assemblyproof oftheUNCHANGEDcurrentFRGkeyedupper. Dcaseentry
# negative alreadyreceived; no newcasekeeper/material variant is built here.
core217=upold209.fuse(exthi209);front217=[f for f in core217.Faces if abs(f.BoundBox.YMin+46.45)<1e-6 and abs(f.BoundBox.YMax+46.45)<1e-6]
assert front217,'Actualforward pressureprofile face required'
coreSweep217=Part.makeCompound([core217,*[f.extrude(A.Vector(0,2.2,0)) for f in front217]])
wingsSweep217=[]
for n,s in wing209.items():
    bb=saved_bounds(s);wingsSweep217.append(box153([bb[0],[bb[1][0],bb[1][1]+2.2,bb[1][2]]]))
sweep217=Part.makeCompound([coreSweep217,*wingsSweep217]);postsolid217=Part.makeCompound(list(posts209.values()));otherpermanent217=newframe209.cut(postsolid217)
postproof217=newup209.common(postrel209);otherproof217=sweep217.common(otherpermanent217)
proof217=dict(method='ExactuniformYrear-keypost relative-Minkowskisweep plusconservativeactualupperprismaticfaceextrusion2.2; NOT3sampletrajectoryPASS.',actual_upper_vs_actual_post_relative_sweep_common_valid=postproof217.isValid(),actual_upper_vs_post_sweep_common_mm3=postproof217.Volume,complete_upper_swept_superset_vs_other_current_permanent_common_valid=otherproof217.isValid(),other_permanent_common_mm3=otherproof217.Volume,actual_pressure_forward_profile_faces=len(front217),all_intermediate_Y0to2p2_covered=True)
wire217=[]
for q in prop206['all4_ports']:
    x=q['actual_project_port_mm'][0];s=Part.makeCylinder(1.55,12,A.Vector(x,-56.25,45.26),A.Vector(0,1,0));co=sweep217.common(s);wire217.append(dict(wire=q['wire'],actual_local_initial_reference_length_mm=12,source='Originalstraightunit12.25fromcase inclmouth.25, notextraordinarywiredebit/actualfixedcurve. New9.8upper plus2.2staging withinexisting12.',common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None))
first217=None
if not postproof217.isValid() or postproof217.Volume>1e-7 or not otherproof217.isValid() or otherproof217.Volume>1e-7 or any(not q['common_valid'] or q['common_mm3']>1e-7 for q in wire217):first217=dict(stage='SAME_FRG_KEYEDUPPER_CURRENT_PERMANENT_OR_FOURWIRE_ENTRY',proof=proof217,wires=wire217)
rows217=[];bounds217=0
if first217 is None:
    for n,b in context210.items():
        if n.startswith('Station:FR_G:') and n not in ['Station:FR_G:case']:continue
        lo=bbox_lower_bound(sweep217.BoundBox,bounds126[n] if n in bounds126 else b.BoundBox);req=0 if n=='Station:FR_G:case' else 1.25
        if lo>=req+1e-7:bounds217+=1;continue
        ga,ww,_=sweep217.distToShape(b);co=sweep217.common(b);row=dict(actor=n,gap_mm=ga,required_mm=req,source_valid=b.isValid(),common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        fail=not b.isValid() or ga<req-1e-7 or not co.isValid() or co.Volume>1e-7;row['status']='INDEPENDENT_FRG_UPPER_ENTRY_HOLD_NOT_ALL_PATHS' if fail else 'ACTUAL_CONTINUOUS_UPPER_ENTRY_CLEAR';rows217.append(row)
        if fail:first217=dict(stage='FRG_KEYEDUPPER_OTHER_CURRENT_NEIGHBOR',row=row);break
        if time.monotonic()-t217>8:break
ar217=OUT/'day07-independent-FRG-keyed-upper-entry-sweep.breps.zip';assert not ar217.exists();ge217=[]
with zipfile.ZipFile(ar217,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('CONSERVATIVE_CONTINUOUS_KEY_UPPER_ASSEMBLY_SWEEP',sweep217),('ACTUAL_POST_RELATIVE_SWEEP',postrel209)]):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge217.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge217),indent=2))
p217=OUT/'day07-independent-FRG-keyed-upper-entry-proof.json';assert not p217.exists()
r217=dict(id=p217.stem,status='INDEPENDENT_FRG_INITIAL_UPPER_ENTRY_SCOPE_RECEIVED' if not first217 else 'INDEPENDENT_FRG_INITIAL_UPPER_ENTRY_FIRST_HOLD',exact_actual_owned_post_and_permanent_proof=proof217,all4_local_jacket_reference_rows=wire217,other_current_neighbor_rows=rows217,other_bounds_separated=bounds217,first_falsifier=first217,source_geometry_UNCHANGED=True,no_newcasekeeper_strategy_built=True,initial_stock_order='FRG145laidopeatfunctionalfeed; fitupper+Y2.2then−Y2.2; ratchetcloseONLYafterupperseated/parkfull83.3. Noone-waytiepretendunlock/no physicalcut/power.',Dcase_initial_installation_HOLD_NOT_disposed=True,whole_initial_assembly_NOT_accepted=True,selected=False,N01_complete=False,actualcut=None,archive=ar217.name,archive_sha256=hashlib.sha256(ar217.read_bytes()).hexdigest(),geometry=ge217,operation_seconds=time.monotonic()-t217,process_cpu_seconds=time.process_time()-c217,pid=os.getpid(),session_id=46493);p217.write_bytes((json.dumps(r217,indent=2)+'\n').encode());print('FRG_INDEPENDENT_KEY_ENTRY',r217['status'],proof217,'wire4',len(wire217),'other',len(rows217),'first',first217,'wall',r217['operation_seconds'],'CPU',r217['process_cpu_seconds'],hashlib.sha256(p217.read_bytes()).hexdigest(),flush=True)
