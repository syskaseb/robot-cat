import time,json,hashlib,zipfile,math,os
t111=time.monotonic();cpu111=time.process_time()
# Different local occupancy, not smaller wire/R or old whole9scalaroffset.
def sector111(cx,cy,z,h,start):
    p=A.Vector(cx,cy,z);s=Part.makeCylinder(39.8,h,p,A.Vector(0,0,1),90);s.rotate(p,A.Vector(0,0,1),start);s=s.cut(Part.makeCylinder(30.4,h+.2,A.Vector(cx,cy,z-.1)));assert s.isValid() and len(s.Solids)==1;assert abs(s.Volume-math.pi/4*(39.8**2-30.4**2)*h)<1e-5;return s
south111=sector111(-84.1,67,42.05,7.2,-90);north111=sector111(-84.1,77,38.75,3.9,0)
bodybounds111=saved_bounds(BodyOuter31);nb111=saved_bounds(north111);sb111=saved_bounds(south111);bodyYmax111=bodybounds111[1][1];northlower111=bodyYmax111-nb111[1][1];northoutline111=dict(source='CURRENTalreadyloadedBodyOuter31/worldboundsreadONLY/notoldoutline-replay',BodyOuter_bounds_mm=bodybounds111,fixed_Hip3_turn_bounds_mm=nb111,full_field_Ymax_mm=nb111[1][1],BodyOuter_Ymax_mm=bodyYmax111,signed_Y_capacity_margin_mm=northlower111,required_margin_mm=3.25,excess_past_margin_mm=nb111[1][1]-(bodyYmax111-3.25),status='FIXED_BODY_HIP3_NORTH_ALLOCATION_OUTLINE_HOLD' if northlower111<3.25 else 'BBOX_NECESSARY_Y_MARGIN_ONLY',meaning='YbeyondactualBodyOuterbboxprovesnotcontained; bboxNOTcontact. FIXEDbodyreturnfielddoesNOTinheritmovinglegexposure. Thisquarteronly/notall3Dpaths/no shorterR/offsetcorrectedvariant.')
ctx111=dict(ctx110);tasks111=[n for n,s in ctx111.items() if bbox_lower_bound(south111.BoundBox,s.BoundBox)<1.25];tasks111.sort(key=lambda n:(0 if n=='Underdeck:PositiveFoundation' else 2 if n==parentname99 else 1,n));rows111=[];first111=None;seam111=None;seamproof111=None
for n in tasks111:
    s=ctx111[n];row=dict(target='KNEE6_SOUTH_FULL9p4x7p2_R35p1',other=n,source_valid=s.isValid(),capacity_valid=True)
    if row['source_valid']:
        gap,w,_=south111.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(aa),list(bb)] for aa,bb in w[:1]])
        if n==parentname99 and gap<1.25:
            co=south111.common(s);row.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
            if co.isValid() and co.Volume<1e-7:
                # Only actual intended channel mouth endpoint. No blanket parent ownership.
                touch=south111.section(s);ys=[v.Point.y for v in touch.Vertexes];seamproof111=dict(common_mm3=co.Volume,section_vertex_Y_mm=ys,contact_confined_existing_portal_Y67=bool(ys) and max(abs(y-67) for y in ys)<1e-5,channel_margin_source='ExistingfullD/G3.1/V2,.2gaps,.4channelmargins receivedprofilesreuse; thisregionendmatchesupper2rowsY67andnooutsideownmaterialvolume. Notpurchasedforeignrulewaiver.',unclassified_if_no_touch_vertices=True)
                if seamproof111['contact_confined_existing_portal_Y67']:row['status']='FUNCTIONAL_EXISTING_PASSIVE_GUIDE_ENTRY_ONLY_ZERO_MATERIAL_COMMON';seam111=touch
                else:row['status']='PARENT_CONTACT_FUNCTION_UNRESOLVED_NO_WAIVER'
            else:row['status']='ALLOCATED_GROUP_REGION_HOLD_NOT_WIRECONTACT'
        else:
            if gap<1e-7:
                co=south111.common(s);row.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
            row['status']='FULL_KNEE6_REGION_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_GROUP_REGION_HOLD_NOT_WIRECONTACT'
    else:row['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
    rows111.append(row)
    if row['status'] not in ['FULL_KNEE6_REGION_SEPARATED125','FUNCTIONAL_EXISTING_PASSIVE_GUIDE_ENTRY_ONLY_ZERO_MATERIAL_COMMON']:first111=row;break
sections111=[]
for y in [55,60,67,77]:
    plane=Part.makePlane(300,200,A.Vector(-180,y,-50),A.Vector(0,1,0))
    for name,s in [('Knee6_south_fullregion',south111),('Hip3_north_fullregion',north111),('actual_U1carrier',ctx111['Underdeck:PositiveFoundation']),('actual_complete_BankBedguide',whole105)]:
        se=s.section(plane);curves=[]
        for e in se.Edges:
            pp=e.discretize(Deflection=.15)
            if len(pp)>1:curves.append([[v.x,v.z] for v in pp])
        sections111.append(dict(axis='Y',value_mm=y,name=name,curves_xz=curves))
ar111=OUT/'day07-SOURCE-split-portals-capacity-outline-first-gate.breps.zip';assert not ar111.exists();ge111=[]
with zipfile.ZipFile(ar111,'w',zipfile.ZIP_DEFLATED) as z:
    its=[('KNEE6_SOUTH_R35p1_FULL_REGION',south111),('HIP3_NORTH_R35p1_FULL_REGION',north111),('ACTUAL_CURRENT_U1CARRIER',ctx111['Underdeck:PositiveFoundation'])]
    if seam111 is not None:its.append(('FUNCTIONAL_EXISTING_GUIDE_PORTAL_SECTION',seam111))
    for i,(n,s) in enumerate(its):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge111.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge111,scope='Newsplit6/3fullcapacityonly; nochangedprint/newholder/sourceworld/motion/staticreplay'),indent=2)+'\n').encode())
r111=dict(id='day07-SOURCE-split-portals-capacity-outline-first-gate',status='SPLIT_PORTAL_ALLOCATION_HOLD_NORTH_FIXED_OUTLINE' if northlower111<3.25 else 'SPLIT_PORTAL_ALLOCATION_HOLD_SOUTH_CAPACITY' if first111 else 'LOCAL_SPLIT_PORTALS_RECEIVED_NOT_WHOLE_SOURCE',proposal='day07-SOURCE-split-Knee6-Hip3-portals-whole-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-split-Knee6-Hip3-portals-whole-proposal.json').read_bytes()).hexdigest(),Knee6_full_region=dict(bounds_mm=sb111,cross_section_mm=[9.4,7.2],R_mm=35.1,rows=rows111,cursor=len(rows111),total=len(tasks111),unreceived=len(tasks111)-len(rows111),first_falsifier=first111,functional_existing_guide_seam=seamproof111,actual_whole_quarter_received=first111 is None and len(rows111)==len(tasks111)),Hip3_north_outline=northoutline111,Hip3_other_pairs_received=0,Hip3_other_pairs_not_qualified=True,material_details_built=False,source21motion36_not_replayed=True,all_A_U_minimum_fit_slack=None,sections=sections111,archive=ar111.name,archive_sha256=hashlib.sha256(ar111.read_bytes()).hexdigest(),geometry=ge111,operation_seconds=time.monotonic()-t111,process_cpu_seconds=time.process_time()-cpu111,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p111=OUT/'day07-SOURCE-split-portals-capacity-outline-first-gate.json';assert not p111.exists();p111.write_bytes((json.dumps(r111,indent=2)+'\n').encode());print('SOURCE111_FINAL',r111['status'],len(rows111),len(tasks111),first111,northoutline111,seamproof111,r111['operation_seconds'],r111['process_cpu_seconds'],hashlib.sha256(p111.read_bytes()).hexdigest(),flush=True)
