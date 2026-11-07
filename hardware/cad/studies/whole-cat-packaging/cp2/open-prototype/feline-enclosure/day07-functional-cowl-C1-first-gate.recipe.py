import time,json,hashlib,zipfile,os
t79=time.monotonic();cpu79=time.process_time();port79=lcyl57(0,19,10.6,4.45,35);members79={n:s.cut(port79) for n,s in members76.items()};hood79={}
hood79['rear_terminal_screen']=Part.makeBox(2,86,27,A.Vector(-138.25,-43,58))
poly79=[(-138.25,58),(-111,58),(-111,98.5),(-132,98.5),(-138.25,85),(-138.25,58)]
for side,sign in [('left',-1),('right',1)]:
    yy=-43 if sign<0 else 41
    face=Part.Face(Part.makePolygon([A.Vector(x,yy,z) for x,z in poly79]));hood79[side+'_terminal_wall']=face.extrude(A.Vector(0,2,0))
    hood79[side+'_upper_outboard_shield']=Part.makeBox(20,13,2,A.Vector(-132,-43 if sign<0 else 30,96.5))
    start=place57.multVec(A.Vector(sign*12,19,5));corner=A.Vector(start.x,sign*42,start.z);end=A.Vector(-112,sign*42,98.5)
    hood79[side+'_root_outboard_arm']=Part.makeBox(2,30,2,A.Vector(start.x-1,-42 if sign<0 else 12,start.z-1))
    def sq79(p):return Part.makePolygon([p+A.Vector(0,dy,dz) for dy,dz in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]])
    hood79[side+'_rear_return']=Part.makeLoft([sq79(corner),sq79(end)],True,True)
members79.update(hood79);guard79=None
for n,s in members79.items():
    assert s.isValid(),n
    guard79=s if guard79 is None else guard79.fuse(s)
coverage79=[]
for n,s in members79.items():
    missing=s.cut(guard79);coverage79.append(dict(name=n,missing_valid=missing.isValid(),missing_mm3=missing.Volume,material_valid=s.isValid(),volume_mm3=s.Volume))
oldmissing79=guard76.cut(guard79);allowed79=guard76.common(port79);unexpected79=oldmissing79.cut(allowed79)
joined79=u59.fuse(guard79);oldparentlost79=u59.cut(joined79);cowlmissing79=guard79.cut(joined79)
roots79=[]
for side in ['left','right']:
    c=members79[side+'_foot'].common(u59);roots79.append(dict(name=side,valid=c.isValid(),actual_common_mm3=c.Volume))
newhood79=None
for s in hood79.values():newhood79=s if newhood79 is None else newhood79.fuse(s)
delta79=newhood79.cut(u59);assert delta79.isValid()
ar79=OUT/'day07-S0-fixed-cowl-functional-port-C1.breps.zip';assert not ar79.exists();ge79=[]
with zipfile.ZipFile(ar79,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(list(members79.items())+[('S0:C1_full_guard_and_terminal_hood',guard79),('S0:C1_new_hood_only',delta79),('S0:C1_whole_parent_candidate',joined79),('S0:C1_upperM6_dedicated_R4p45_tool_port',port79)]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);b=s.optimalBoundingBox();ge79.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge79,role='ONEfunctionalguardC1. Allactualtoolradius/length/key/case/sourceendsunchanged. Newterminalhoodmustpasscase/assemblybeforeselection. Notcurrent.'),indent=2)+'\n').encode())
boundarygap79=guard79.distToShape(Part.makeShell(BodyOuter31.Faces))[0];outside79=guard79.cut(BodyOuter31)
toolgap79=guard79.distToShape(tools57['caseM6_1:AF5_driver_approach'])[0];operatorgap79=guard79.distToShape(fullop75)[0]
tasks79=[n for n,s in effective62.items() if n!='CurrentFoundation:FoundationRail:-1' and bbox_lower_bound(delta79.BoundBox,s.BoundBox)<1.25];tasks79.sort(key=lambda n:(0 if n.startswith('Ref_Material_S0') else 1,n));rows79=[]
materialok79=guard79.isValid() and len(guard79.Solids)==1 and joined79.isValid() and len(joined79.Solids)==1 and all(r['missing_valid'] and r['missing_mm3']<1e-5 for r in coverage79) and unexpected79.isValid() and unexpected79.Volume<1e-5 and oldparentlost79.Volume<1e-5 and cowlmissing79.Volume<1e-5
if materialok79:
    for n in tasks79:
        s=effective62[n];r=dict(other=n,valid=s.isValid())
        if s.isValid():
            gap,w,_=delta79.distToShape(s);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
            if gap<1e-7:
                c=delta79.common(s);r.update(common_valid=c.isValid(),common_mm3=c.Volume if c.isValid() else None)
            r['status']='NEW_HOOD_FOREIGN_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_HOOD_FULL_SOURCE_OR_NEIGHBOR_HOLD'
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        rows79.append(r);print('COWL_C1_FOREIGN79',r,flush=True)
        if r['status']!='NEW_HOOD_FOREIGN_SEPARATED125' or time.monotonic()-t79>18:break
r79=dict(id='day07-S0-fixed-cowl-functional-port-C1-first-gate',status='FUNCTIONAL_COWL_C1_MATERIAL_OR_NEW_HOOD_FIRST_GATE_HOLD' if not materialok79 or len(rows79)<len(tasks79) or any(r['status']!='NEW_HOOD_FOREIGN_SEPARATED125' for r in rows79) or outside79.Volume>1e-5 or boundarygap79<3.25-1e-7 else 'FUNCTIONAL_COWL_C1_FIRST_GATE_RECEIVED_INITIAL_ASSEMBLY_NEXT',proposal='day07-S0-fixed-cowl-functional-port-C1-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-S0-fixed-cowl-functional-port-C1-proposal.json').read_bytes()).hexdigest(),member_coverage=coverage79,material_scope_ok=materialok79,full_guard_valid=guard79.isValid(),full_guard_solids=len(guard79.Solids),whole_parent=dict(valid=joined79.isValid(),solids=len(joined79.Solids),old_parent_missing_mm3=oldparentlost79.Volume,new_guard_missing_mm3=cowlmissing79.Volume),roots=roots79,intended_AF5_port_removed_mm3=allowed79.Volume,old_guard_total_removed_mm3=oldmissing79.Volume,unexpected_old_guard_missing_mm3=unexpected79.Volume,full_AF5_R3p2x35_unchanged=True,full_AF5_gap_to_C1_mm=toolgap79,full_source_R15_gap_to_C1_mm=operatorgap79,BodyOuter_boundary_gap_mm=boundarygap79,BodyOuter_outside_mm3=outside79.Volume,rows=rows79,cursor=len(rows79),total=len(tasks79),unreceived=len(tasks79)-len(rows79),old_7static_pairs_not_replayed='C0guardcutstrictsubset, so7oldresultsreused; onlyNEWhoodchecked. ChangedAF5pairmeasuredagainstcompleteC1.',archive=ar79.name,archive_sha256=hashlib.sha256(ar79.read_bytes()).hexdigest(),geometry=ge79,current_1311_unchanged=True,selected=False,N01_complete=False,remaining='IfearlygateHOLDstopdependent10assembly/motion. Ifpasses, newhoodmustallowfullsourcecase50benchapproach/rings/M10andallports; no fabricateddetachment/hinge/door/ownershipwaiver. Fullterminalprotection/skinlocalclosure isnotimpliedby1solid.',operation_seconds=time.monotonic()-t79,process_cpu_seconds=time.process_time()-cpu79,pid=os.getpid(),session_id=46493)
p79=OUT/'day07-S0-fixed-cowl-functional-port-C1-first-gate.json';assert not p79.exists();p79.write_bytes((json.dumps(r79,ensure_ascii=False,indent=2)+'\n').encode());print('COWL_C1_FINAL79',r79['status'],materialok79,len(guard79.Solids),toolgap79,boundarygap79,outside79.Volume,len(rows79),len(tasks79),r79['operation_seconds'],r79['process_cpu_seconds'],hashlib.sha256(p79.read_bytes()).hexdigest(),flush=True)
