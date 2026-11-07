import time,json,hashlib,zipfile,os
t76=time.monotonic();cpu76=time.process_time();members76={}
for label,u,y in [('left',-12,-18),('right',12,18)]:
    members76[label+'_foot']=loc57(Part.makeBox(2,2,6.5,A.Vector(u-1,18,.5)))
    a=place57.multVec(A.Vector(u,19,5));b=A.Vector(-74,y,106.5)
    def square76(p):return Part.makePolygon([p+A.Vector(0,dy,dz) for dy,dz in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]])
    members76[label+'_web']=Part.makeLoft([square76(a),square76(b)],True,True)
portal76=Part.makeCylinder(16.25,length74+extra75+40,tip68-axis74*20,axis74)
roof76=Part.makeBox(58.5,42,2.25,A.Vector(-76,-21,106.5));members76['roof_with_operator_aperture']=roof76.cut(portal76)
guard76=None
for n,s in members76.items():
    assert s.isValid() and len(s.Solids)==1,(n,'invalidmember')
    guard76=s if guard76 is None else guard76.fuse(s)
assert guard76.isValid()
coverage76=[]
for n,s in members76.items():
    miss=s.cut(guard76);assert miss.isValid();coverage76.append(dict(name=n,missing_mm3=miss.Volume,valid=miss.isValid(),bounds_mm=saved_bounds(s)))
assert all(r['missing_mm3']<1e-5 for r in coverage76)
roots76=[]
for label in ['left','right']:
    c=members76[label+'_foot'].common(u59);roots76.append(dict(name=label,common_valid=c.isValid(),common_mm3=c.Volume))
joined76=u59.fuse(guard76);parentmissing76=u59.cut(joined76);guardmissing76=guard76.cut(joined76)
delta76=guard76.cut(u59);assert delta76.isValid()
ar76=OUT/'day07-S0-fixed-cowl-material-first-gate.breps.zip';assert not ar76.exists();ge76=[]
with zipfile.ZipFile(ar76,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(list(members76.items())+[('S0:complete_fixed_cowl',guard76),('S0:whole_current_rail_plus_cowl_candidate',joined76),('S0:only_added_cowl_material',delta76),('S0:aperture_tool',portal76)]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge76.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge76,role='ONEfixedcowl materialcandidate, notselected/no change current1311. Everymembercoveragechecked.'),indent=2)+'\n').encode())
rows76=[];checks76={n:s for n,s in effective62.items() if n!='CurrentFoundation:FoundationRail:-1'}
# Fullinstalledkey/case/metal andactualotherparts, notoldoperatorfieldreplay.
tasks76=[n for n,s in checks76.items() if bbox_lower_bound(delta76.BoundBox,s.BoundBox)<1.25]
tasks76.sort(key=lambda n:(0 if n.startswith('Ref_Material_S0') else 1,n))
for n in tasks76:
    s=checks76[n];r=dict(other=n,valid=s.isValid())
    if s.isValid():
        gap,w,_=delta76.distToShape(s);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            c=delta76.common(s);r.update(common_valid=c.isValid(),common_mm3=c.Volume if c.isValid() else None)
        r['status']='NEW_COWL_FOREIGN_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_COWL_FULL_SOURCE_OR_NEIGHBOR_HOLD'
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows76.append(r);print('COWL76',r,flush=True)
    if r['status']!='NEW_COWL_FOREIGN_SEPARATED125' or time.monotonic()-t76>20:break
operatorgap76=guard76.distToShape(fullop75)[0]
outline76=guard76.distToShape(BodyOuter31)[0];outside76=guard76.cut(BodyOuter31)
r76=dict(id='day07-S0-fixed-cowl-material-first-gate',status='FIXED_COWL_MATERIAL_AND_CHANGED_FOREIGN_RECEIVED_CLOSURE_OPEN' if len(rows76)==len(tasks76) and all(r['status']=='NEW_COWL_FOREIGN_SEPARATED125' for r in rows76) and len(joined76.Solids)==1 and outside76.Volume<1e-5 and outline76>=3.25-1e-7 else 'FIXED_COWL_FIRST_GATE_HOLD_NO_CURRENT_CHANGE',proposal='day07-S0-fixed-cowl-whole-interface-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-S0-fixed-cowl-whole-interface-proposal.json').read_bytes()).hexdigest(),full_material_valid=guard76.isValid(),full_material_solids=len(guard76.Solids),intended_members=coverage76,actual_roots=roots76,complete_parent_union=dict(valid=joined76.isValid(),solids=len(joined76.Solids),old_parent_missing_valid=parentmissing76.isValid(),old_parent_missing_mm3=parentmissing76.Volume,cowl_missing_valid=guardmissing76.isValid(),cowl_missing_mm3=guardmissing76.Volume),rows=rows76,cursor=len(rows76),total=len(tasks76),unreceived=len(tasks76)-len(rows76),source_R15_operator_gap_mm=operatorgap76,actual_BodyOuter_gap_mm=outline76,outside_BodyOuter_mm3=outside76.Volume,archive=ar76.name,archive_sha256=hashlib.sha256(ar76.read_bytes()).hexdigest(),geometry=ge76,actual_current1311_unchanged=True,selected=False,N01_complete=False,terminal_shield_function_not_claimed_from_shape_alone=True,E6_closure_and_structural_rim_open=True,operation_seconds=time.monotonic()-t76,process_cpu_seconds=time.process_time()-cpu76,pid=os.getpid(),session_id=46493)
p76=OUT/'day07-S0-fixed-cowl-material-first-gate.json';assert not p76.exists();p76.write_bytes((json.dumps(r76,ensure_ascii=False,indent=2)+'\n').encode());print('COWL_FINAL76',r76['status'],len(rows76),len(tasks76),roots76,outline76,operatorgap76,r76['operation_seconds'],r76['process_cpu_seconds'],hashlib.sha256(p76.read_bytes()).hexdigest(),flush=True)
