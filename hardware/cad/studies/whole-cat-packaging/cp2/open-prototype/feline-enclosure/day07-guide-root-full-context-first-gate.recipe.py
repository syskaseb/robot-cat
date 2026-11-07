import time,json,hashlib,zipfile,math,os
t101=time.monotonic();cpu101=time.process_time();bankpadname101='CurrentFoundation:BankPad:Ref_Material_F_L1_CP2_Housing_0_0:0';bankpad101=ctx83[bankpadname101];assert bankpad101.isValid()
padoutside101=bankpad101.cut(parent99);padco101=bankpad101.common(parent99);assert padoutside101.isValid() and padco101.isValid()
root101=Part.makeBox(12,5,.75,A.Vector(-50,40.25,51.5));rootco101=root101.common(parent99);rootface101=Part.Face(Part.makePolygon([A.Vector(x,y,52) for x,y in [(-50,40.25),(-38,40.25),(-38,45.25),(-50,45.25),(-50,40.25)]]));contact101=rootface101.common(parent99);assert rootco101.isValid() and contact101.isValid()
guide101=Part.makeBox(9.4,10,10.5,A.Vector(-53.7,67,38.75));localprofiles101={}
for row,z in enumerate([40.7,44,47.3]):
    for core,x,r in [('D',-51.75,1.55),('V',-49,1),('G',-46.25,1.55)]:localprofiles101[str(row)+core]=Part.makeCylinder(r,10,A.Vector(x,67,z),A.Vector(0,1,0))
band101=band93(72,42.3,55.7,37.25,50.75,1);band101.rotate(A.Vector(0,0,0),A.Vector(0,0,1),90);assert band101.isValid();looplen101=band101.Volume/2.5
head101=Part.makeBox(5,5.3,5,A.Vector(-61.7,69.35,41.5));pull101=Part.makeBox(7,7,25,A.Vector(-63,68.5,46.5))
outer101=Part.makeCylinder(5.5,1,A.Vector(-62.2,45.5,40),A.Vector(0,0,1),180);outer101.rotate(A.Vector(-62.2,45.5,40),A.Vector(0,0,1),180);arc101=outer101.cut(Part.makeCylinder(3,1.2,A.Vector(-62.2,45.5,39.9)))
tail101=Part.makeCompound([Part.makeBox(2.5,31.5,1,A.Vector(x,45.5,40)) for x in [-67.7,-59.2]]+[arc101]);assert tail101.isValid()
tp101=[A.Vector(*p) for p in [(-59.2,72,46.5),(-59.2,72,53.5),(-57.95,83,53.5),(-57.95,83,40.5),(-57.95,77,40.5)]];transportparts101=[];transportlength101=0
for a,b in zip(tp101,tp101[1:]):
    v=b-a;transportlength101+=v.Length;transportparts101.append(Part.makeCylinder(2,v.Length,a,v.normalize()))
for p in tp101[1:-1]:transportparts101.append(Part.makeSphere(5,p))
transport101=Part.makeCompound(transportparts101);assert transport101.isValid()
fields101={'FULL9_GUIDE_CAPACITY':guide101,'WHOLE_T18R100_BAND':band101,'WHOLE_T18R100_HEAD':head101,'TEMP25_PULL':pull101,'FULL_UNCUT100_TAIL_PARK':tail101,'FULL100_TAIL_TRANSPORT':transport101};tasks101=[]
for n,s in fields101.items():
    for k,q in ctx99.items():
        if bbox_lower_bound(s.BoundBox,q.BoundBox)>=1.25:continue
        tasks101.append((n,k))
tasks101.sort(key=lambda p:(0 if p[0]=='FULL9_GUIDE_CAPACITY' else 1,0 if p[1]=='Underdeck:PositiveFoundation' else 1,p[0],p[1]));rows101=[];firstbad101=None
for n,k in tasks101:
    s=fields101[n];q=ctx99[k];r=dict(target=n,other=k,source_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='CURRENT_WHOLE_GUIDE_OR_STOCK_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_GUIDE_OR_STOCK_HOLD_NOT_ACTUALWIRECONTACT')
        if gap<1e-7:
            co=s.common(q);r.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows101.append(r);print('GUIDE101',r,flush=True)
    if r['status']!='CURRENT_WHOLE_GUIDE_OR_STOCK_SEPARATED125':firstbad101=r;break
    if time.monotonic()-t101>15:break
profilefacts101=[]
if firstbad101 and firstbad101['target']=='FULL9_GUIDE_CAPACITY' and firstbad101['source_valid']:
    obstacle=ctx99[firstbad101['other']]
    for n,s in localprofiles101.items():
        co=s.common(obstacle);assert co.isValid();gap,_,_=s.distToShape(obstacle);profilefacts101.append(dict(profile=n,allocated_profile_common_mm3=co.Volume,gap_mm=gap,operand='FullreservedD/G3.1/V2profilesONLY10mmnamedguidehazard, not9wholewireaxesoractualdeliveredwirecontact'))
rootok101=abs(rootco101.Volume-15)<1e-5 and abs(contact101.Area-60)<1e-5
ar101=OUT/'day07-SOURCE-Ymin-guide-root-occupancy-first-gate.breps.zip';assert not ar101.exists();ge101=[]
with zipfile.ZipFile(ar101,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('PROPOSED_ROOT:12x5foot',root101),('ACTUAL_ROOT:parent_common',rootco101),('ACTUAL_ROOT:contact60',contact101)]+list(fields101.items())+[(n,s) for n,s in localprofiles101.items()]
    if firstbad101:items.append((firstbad101['other'],ctx99[firstbad101['other']]))
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge101.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,area_mm2=s.Area,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge101,scope='Whole9guide/full100/source-rootFIRSTcapacity gate BEFOREanynewdrop/arm/guideprintedmaterial. CurrentU1carrieractualvalidoperand.'),indent=2)+'\n').encode())
r101=dict(id='day07-SOURCE-Ymin-guide-root-occupancy-first-gate',status='WHOLE_YMIN_GUIDE_RETENTION_FIRST_FALSIFIER_HOLD' if firstbad101 or not rootok101 else 'ROOT_GUIDE_STOCK_RECEIVED_SCOPED_FULL_TOOL_R6_PENDING',proposal='day07-SOURCE-Ymin-spine-open9-guide-whole-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-Ymin-spine-open9-guide-whole-proposal.json').read_bytes()).hexdigest(),
 actual_root=dict(parent=parentname99,valid=True,common_mm3=rootco101.Volume,expected_common_mm3=15,contact_area_mm2=contact101.Area,required_area_mm2=60,full_material_root=rootok101,no_new_support_print_built=True),
 BankPad_relation=dict(actor=bankpadname101,constructor='tools/cad/feline_channelled_foundation.py:120-134/graphmaterial_connections',actual_parent_pad_common_mm3=padco101.Volume,pad_outside_parent_mm3=padoutside101.Volume,actual_pad_source_role='ActualselectedF_L1housingbottom-bearingprint',meaning='Subset0wouldprovesubvolumeofsamecurrentprintedbankcarrier; newrootbelowunchangedpadpreservescasebearing. Ifnot0, no automaticwholeownership/fusion. ThisisnotnewcontactruleforU1carrier/Purchasedparts.'),
 proposed_context=dict(base=1419,new_Knee21_operating=21,new_Knee4_temporary=4,total=1444,fullPi_MODULE_currentActors=True,R6_routine_reservations='UNRECEIVED_AFTER_FIRST_FALSIFIER ifHOLD; neverinferredPASS fromrigidctx. 220/230parking mustbetypedflexible forfullgate.'),
 rows=rows101,cursor=len(rows101),total=len(tasks101),unreceived=len(tasks101)-len(rows101),decisive_negative=firstbad101,local_named_hazard_profiles=profilefacts101,
 named_exact_profile_scope='Guideboxoverlapalonecouldbeair/packingmargin. Only9SHORT10mmfullprofilesusedtodecidewhetherthisactualretainedcarrierblocksthislocalcrosssection; no123axis/wholewire scan. PrintedcarrierfunctionalreplacementrequirescurrentU1feet/holes/lowerbranch/understep/foamC/metal/FHYsupport/access/assemblyproof; no ownfromname.',
 full100_budget=dict(sku='111-01910',nominal_new_installed_demand=1,availability_NOT_claimed=True,L_mm=100,band_length_mm=looplen101,required_with25once_mm=looplen101+25,full_uncut_tail_mm=100-looplen101,head_height5_projectreserve=True,parking_capacity_length_mm=tail101.Volume/2.5,parking_minimum_inner_radius_mm=3,transport_polyline_upper_mm=transportlength101,transport_minimum_inner_radius_mm=3,transport_centre_radius3p5_plus_cross_capacity_within_turnsphere5=True,physicalcut=None),
 source14_terminal11_full9_lap4_850_900MAX3_4independent220_unchanged=True,all_source_A_U_fit_slack=None,new_support_detail_built=False,new_source_moving_pose_unchanged=True,current1292_effective1311_rest108_unchanged=True,selected=False,N01_complete=False,archive=ar101.name,archive_sha256=hashlib.sha256(ar101.read_bytes()).hexdigest(),geometry=ge101,operation_seconds=time.monotonic()-t101,process_cpu_seconds=time.process_time()-cpu101,pid=os.getpid(),session_id=46493)
p101=OUT/'day07-SOURCE-Ymin-guide-root-occupancy-first-gate.json';assert not p101.exists();p101.write_bytes((json.dumps(r101,ensure_ascii=False,indent=2)+'\n').encode());print('GUIDE101_FINAL',r101['status'],r101['actual_root'],r101['BankPad_relation'],len(rows101),len(tasks101),profilefacts101,r101['operation_seconds'],r101['process_cpu_seconds'],hashlib.sha256(p101.read_bytes()).hexdigest(),flush=True)
