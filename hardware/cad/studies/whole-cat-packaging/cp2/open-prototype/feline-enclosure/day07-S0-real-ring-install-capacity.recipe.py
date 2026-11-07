import time,json,hashlib,zipfile,os
t67=time.monotonic();c67=time.process_time();ringpieces67={};proof67=[]
for side in ['IN','OUT']:
    ring=Current35['Ref_Material_S0_ring_'+side+'_0_0'];barrel=ring;tongue=ring
    face=max([f for f in tongue.Faces if type(f.Surface).__name__=='Plane' and np.array(list(f.normalAt(0,0)))@out56>.99],key=lambda f:f.Area)
    ns=[(np.array(list(f.CenterOfMass))-C56)@out56 for f in tongue.Faces if type(f.Surface).__name__=='Plane' and abs(np.array(list(f.normalAt(0,0)))@out56)>.99];thickness=max(ns)-min(ns)
    tonguecover=face.extrude(A.Vector(*(-out56))*(18+thickness))
    cy=next(f for f in barrel.Faces if type(f.Surface).__name__=='Cylinder');axis=cy.Surface.Axis;axis.normalize();assert abs(axis.dot(A.Vector(*out56)))<1e-7
    cylfaces=[f for f in barrel.Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-3.2)<1e-7];cy=cylfaces[0];axis=cy.Surface.Axis;axis.normalize();vmin=min(f.ParameterRange[2] for f in cylfaces);vmax=max(f.ParameterRange[3] for f in cylfaces);p0=cy.Surface.Center+axis*vmin;p1=cy.Surface.Center+axis*vmax;r=cy.Surface.Radius;direction=A.Vector(*(-out56));w=axis.cross(direction);w.normalize();q=p0+direction*18
    aa=p0+w*r;bb=q+w*r;cc=q-w*r;dd=p0-w*r
    edges=[Part.makeLine(aa,bb),Part.Arc(bb,q+direction*r,cc).toShape(),Part.makeLine(cc,dd),Part.Arc(dd,p0-direction*r,aa).toShape()]
    barrelcover=Part.Face(Part.Wire(edges)).extrude(p1-p0)
    sourceTongue=face.extrude(A.Vector(*(-out56))*thickness);sourceBarrel=Part.makeCylinder(r,(p1-p0).Length,p0,axis)
    complete=tonguecover.fuse(barrelcover);assert complete.isValid()
    fullmissing=ring.cut(complete);lostTongue=tonguecover.cut(complete);lostBarrel=barrelcover.cut(complete);assert fullmissing.isValid() and fullmissing.Volume<1e-5 and lostTongue.isValid() and lostTongue.Volume<1e-5 and lostBarrel.isValid() and lostBarrel.Volume<1e-5
    proof67.append(dict(side=side,actual_source_fused_ring_missing_mm3=fullmissing.Volume,intended_tongue_missing_mm3=lostTongue.Volume,intended_barrel_missing_mm3=lostBarrel.Volume,source_shape='ActualcurrentTEisONEfusedsolid, not oldconstructor2solidcompound; useactualfaceandcylinderUVaxisrange.',full18_translation_analytic=True))
    for label,source,cover in [('tongue',sourceTongue,tonguecover),('barrel',sourceBarrel,barrelcover)]:
        missing=source.cut(cover);assert cover.isValid() and missing.isValid() and abs(missing.Volume)<1e-5
        name='TE130207_'+side+':'+label+'_full18mm_install';ringpieces67[name]=cover;proof67.append(dict(name=name,valid=cover.isValid(),source_missing_valid=missing.isValid(),source_missing_mm3=missing.Volume,source_radius_mm=r if label=='barrel' else None,tongue_thickness_mm=thickness if label=='tongue' else None,translation_mm=18,construction='Exactsourceperforatedtongueprism/exactsourcecylinderstadiumtranslation; actualpartcapacitypreserved, no OD/R/lengthreduction.'))
tasks67=[]
for n,s in ringpieces67.items():
    side='IN' if '_IN:' in n else 'OUT';excluded={x for x in s0names56 if any(k in x for k in ['_body_','_neck_','_key_']) or '_'+side+'_' in x}
    for k,q in effective62.items():
        if k not in excluded and bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25:tasks67.append((n,k))
rows67=[]
for n,k in tasks67:
    s=ringpieces67[n];q=effective62[k];row=dict(region=n,other=k,other_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co=s.common(q);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        row['status']='FULL_PURCHASED_RING_INSTALL_SEPARATED125' if gap>=1.25-1e-7 else 'REAL_RING_INSTALL_REGION_HOLD'
    else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows67.append(row);print('REAL_RING67',row,flush=True)
    if row['status']!='FULL_PURCHASED_RING_INSTALL_SEPARATED125' or time.monotonic()-t67>15:break
ar67=OUT/'day07-S0-real-ring-install-capacity.breps.zip';assert not ar67.exists();ge67=[]
with zipfile.ZipFile(ar67,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(list(ringpieces67.items())+[(k,effective62[k]) for k in sorted({r['other'] for r in rows67})]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge67.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge67,scope='Only named S1 ring-install hazard needs actual purchasedringtranslation profile; not an exactfreewiremodel or newcasevariant.'),indent=2)+'\n').encode())
r67=dict(id='day07-S0-real-ring-install-capacity',status='FULL_REAL_RING_18MM_INSTALL_REGIONS_RECEIVED' if len(rows67)==len(tasks67) and all(x['status']=='FULL_PURCHASED_RING_INSTALL_SEPARATED125' for x in rows67) else 'REAL_RING_INSTALL_CAPACITY_HOLD_OR_PENDING',raw_coarse_region_receipt=p65.name,raw_S1_gap_mm=.6344757619783465,raw_coarse_HOLD_not_physicalcontact=True,decision='Samechosenaxialringinstallation, refinedprofileonly atnamedS1hazard becauseAABBcannotdistinguishactualtongue/barreloccupiedspace. Preservekey/casepose/13hardware/source2rings andallfactorylengths. No offset or mountC2.',proof=proof67,rows=rows67,total=len(tasks67),cursor=len(rows67),unreceived=len(tasks67)-len(rows67),M10_tools_broadphase_scope=dict(count=2,geometry_source_archive=ar65.name,other_current_bbox_candidate_pairs=sum(1 for n,k in terminal_tasks65 if n in tools65),all_effective_foreign_parts_included=True,actual_own_tool_recess_and_stud_clearance_phase2=True),archive=ar67.name,archive_sha256=hashlib.sha256(ar67.read_bytes()).hexdigest(),geometry=ge67,operation_seconds=time.monotonic()-t67,process_cpu_seconds=time.process_time()-c67,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p67=OUT/'day07-S0-real-ring-install-capacity.json';assert not p67.exists();p67.write_bytes((json.dumps(r67,ensure_ascii=False,indent=2)+'\n').encode());print('S0_RING_FINAL67',r67['status'],r67['cursor'],r67['total'],r67['operation_seconds'],r67['process_cpu_seconds'],hashlib.sha256(p67.read_bytes()).hexdigest(),flush=True)
