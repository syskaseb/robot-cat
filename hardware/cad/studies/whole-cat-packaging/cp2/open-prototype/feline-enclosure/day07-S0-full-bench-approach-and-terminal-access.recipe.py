import time,json,hashlib,zipfile,os
t65=time.monotonic();c65=time.process_time();fullcovers65={};delta65={};member65=[]
for n in moving64:
    source=Current35[n];cy=next(f for f in source.Faces if type(f.Surface).__name__=='Cylinder');low,high=sorted([f.CenterOfMass for f in source.Faces if type(f.Surface).__name__=='Plane'],key=lambda p:(np.array(list(p))-C56)@out56)
    whole=Part.makeCylinder(cy.Surface.Radius,(high-low).Length+50,low-A.Vector(*out56)*50,A.Vector(*out56));missing=covers64[n].cut(whole);assert whole.isValid() and missing.isValid() and missing.Volume<1e-5
    changed=whole.cut(covers64[n]);assert changed.isValid();fullcovers65[n]=whole;delta65[n]=changed;member65.append(dict(name=n,old_4mm_cover_missing_mm3=missing.Volume,whole_50mm_bounds_mm=saved_bounds(whole)))
case_tasks65=[(n,k) for n,s in delta65.items() for k,q in context64.items() if bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25];case_rows65=[]
for n,k in case_tasks65:
    s=delta65[n];q=context64[k];r=dict(moving=n,other=k,other_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=s.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        r['status']='SEPARATED125' if gap>=1.25-1e-7 else 'CASE_EXTERNAL_BENCH_APPROACH_ALLOCATION_HOLD'
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    case_rows65.append(r);print('CASE_BENCH65',r,flush=True)
    if r['status']!='SEPARATED125' or time.monotonic()-t65>12:break
tools65={};ringcovers65={};endfacts65=[]
inverse65=A.Matrix(place57);inverse65.invert()
for side in ['IN','OUT']:
    nutname='Ref_Material_S0_nut_'+side+'_0_0';nut=Current35[nutname];planes=[f for f in nut.Faces if type(f.Surface).__name__=='Plane' and abs(np.array(list(f.normalAt(0,0)))@out56)>.99];face=min(planes,key=lambda f:(np.array(list(f.CenterOfMass))-C56)@out56);outer=face.CenterOfMass
    tools65['M10_AF17_'+side+'_project_access']=Part.makeCylinder(12,35,outer-A.Vector(*out56)*35,A.Vector(*out56))
    ring=Current35['Ref_Material_S0_ring_'+side+'_0_0'];local=ring.transformGeometry(inverse65);b=local.BoundBox
    # Conservative complete purchasedring/barebarrel envelope, translated18mm axially to clear15mmstud. Not a rigidwholewire.
    ringcovers65['TE130207_'+side+'_18mm_install_region']=loc57(Part.makeBox(b.XLength,b.YLength,b.ZLength+18,A.Vector(b.XMin,b.YMin,b.ZMin-18)))
    endfacts65.append(dict(side=side,current_nut_outer_face_mm=list(outer),tool_outer_radius_mm=12,tool_approach_length_mm=35,tool_source='AF17matchesselectedM10nut; R12x35 isexplicitprototypeaccessallocation, notsupplieractualsocketmetal.',full_TE_local_bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],ring_install_translation_mm=18,associated_end='W076 intactF0factorylead/TE130207 IN' if side=='IN' else 'W066 HELU23802/TE130207 OUT',other_branch='W043 intactFHAC0001ZXJ toP_SYS.2 unchanged; no S0ring assignedtoit.'))
terminal_rows65=[];terminal_tasks65=[]
for n,s in list(tools65.items())+list(ringcovers65.items()):
    side='IN' if '_IN_' in n else 'OUT';excluded={x for x in s0names56 if any(k in x for k in ['_body_','_neck_','_key_']) or '_'+side+'_' in x}
    # Opposite live terminal geometry remains occupied. The case's own filledrear family cannot prove recessmetal.
    for k,q in effective62.items():
        if k in excluded or bbox_lower_bound(s.BoundBox,q.BoundBox)>1.25:continue
        terminal_tasks65.append((n,k))
for n,k in terminal_tasks65:
    s={**tools65,**ringcovers65}[n];q=effective62[k];r=dict(operation=n,other=k,other_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=s.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        r['status']='SEPARATED125' if gap>=1.25-1e-7 else 'TERMINAL_TOOL_OR_RING_ALLOCATION_HOLD'
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    terminal_rows65.append(r);print('TERMINAL65',r,flush=True)
    if r['status']!='SEPARATED125' or time.monotonic()-t65>22:break
ar65=OUT/'day07-S0-bench-case-and-terminal-first-gates.breps.zip';assert not ar65.exists();ge65=[]
with zipfile.ZipFile(ar65,'w',zipfile.ZIP_DEFLATED) as z:
    items=list(fullcovers65.items())+[(n+':changed_approach_only',s) for n,s in delta65.items()]+list(tools65.items())+list(ringcovers65.items())+[(k,effective62[k]) for k in sorted({r['other'] for r in case_rows65+terminal_rows65})]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge65.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge65,scope='Sourcecasebenchapproach onlynew50vs4mm volume; M10toolallocation andfullrealring installspace, no factorywirecurvechange/trim/newpart.'),indent=2)+'\n').encode())
r65=dict(id='day07-S0-bench-case-and-terminal-first-gates',status='BOUNDED_CASE_TERMINAL_ASSEMBLY_FACTS_RECEIVED_NO_WHOLE_PASS',case_4mm_own_neck_disposition=dict(raw_receipt=p64.name,raw_HOLD_preserved=True,selected_neck_OD_mm=22,source_panel_hole_mm=24,radial_clearance_mm=1,common_valid=True,common_mm3=0,remaining_rail_strut_gap_mm=8.158531436625292,classification='Actualsource-matchedownmountneck24/22 fit, requirednointrusion; notforeign1.25. Full4mmseat4/4scopedreceived withactualbodyrestgap1.8755098742/W0772.4351832724. Allotherforeign1.25kept.'),case_additional_approach=dict(travel_mm=50,delta_only=True,member_coverage=member65,rows=case_rows65,total=len(case_tasks65),cursor=len(case_rows65),unreceived=len(case_tasks65)-len(case_rows65)),terminal_facts=endfacts65,terminal_access=dict(rows=terminal_rows65,total=len(terminal_tasks65),cursor=len(terminal_rows65),unreceived=len(terminal_tasks65)-len(terminal_rows65)),assembly_scope='CurrentfullPi/head/otherparts presentforfirstfalsifier; sourcepermitsS0benchbeforehead/looms/P0BUS butnone silentlyexcluded. Headdeferralonlyafteractualfunctionclassification; integralrailalwayspresent. RingsbeforeM10washers/nuts, otherringoccupiedconservatively. CompletefreeW076/W066leads canbehandlaidonbenchbeforefinalsourceclamps; no virtualcut/solderbreak. Protected4x220MODULE/SOURCE unchanged.',length_scope='No currentroutechange/debit/slack invented; W076factory/W066HELU/W043factory materials retained, old80/330/40notcurrentfitproof. Fullsourceprefix/endretention and currentstockremainrequired.',archive=ar65.name,archive_sha256=hashlib.sha256(ar65.read_bytes()).hexdigest(),geometry=ge65,operation_seconds=time.monotonic()-t65,process_cpu_seconds=time.process_time()-c65,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p65=OUT/'day07-S0-bench-case-and-terminal-first-gates.json';assert not p65.exists();p65.write_bytes((json.dumps(r65,ensure_ascii=False,indent=2)+'\n').encode());print('S0_BENCH_FINAL65',r65['case_additional_approach'],r65['terminal_access'],r65['operation_seconds'],r65['process_cpu_seconds'],hashlib.sha256(p65.read_bytes()).hexdigest(),flush=True)
