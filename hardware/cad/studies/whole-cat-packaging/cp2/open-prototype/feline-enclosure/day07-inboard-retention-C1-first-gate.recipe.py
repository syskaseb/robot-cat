import time,json,hashlib,zipfile,math
t103=time.monotonic();cpu103=time.process_time();head103=Part.makeBox(5,5.3,5,A.Vector(-41.3,69.35,41.5));pull103=Part.makeBox(7,7,25,A.Vector(-42,68.5,46.5))
outer103=Part.makeCylinder(5.5,1,A.Vector(-11.8,72,40),A.Vector(0,0,1),180);outer103.rotate(A.Vector(-11.8,72,40),A.Vector(0,0,1),-90);arc103=outer103.cut(Part.makeCylinder(3,1.2,A.Vector(-11.8,72,39.9)))
tail103=Part.makeCompound([Part.makeBox(27.5,2.5,1,A.Vector(-39.3,y,40)) for y in [66.5,75]]+[arc103]);assert tail103.isValid()
points103=[A.Vector(*p) for p in [(-38.8,72,46.5),(-38.8,72,53.5),(-35.3,83.25,53.5),(-35.3,83.25,40.5),(-39.3,76.25,40.5)]];pieces103=[];transportlength103=0
for a,b in zip(points103,points103[1:]):
    v=b-a;transportlength103+=v.Length;pieces103.append(Part.makeCylinder(2,v.Length,a,v.normalize()))
for p in points103[1:-1]:pieces103.append(Part.makeSphere(5,p))
transport103=Part.makeCompound(pieces103);assert transport103.isValid();tray103=Part.makeBox(36.25,11,1.5,A.Vector(-42.55,66.5,38.5))
fields103={'C1_INBOARD_HEAD':head103,'C1_TEMP25_PULL':pull103,'C1_WHOLE100_TAIL_PARK':tail103,'C1_FULL100_TAIL_TRANSPORT':transport103,'C1_ROOTED_TAIL_TRAY_ENVELOPE':tray103};tasks103=[]
for n,s in fields103.items():
    for k,q in ctx99.items():
        if bbox_lower_bound(s.BoundBox,q.BoundBox)<1.25:tasks103.append((n,k))
tasks103.sort(key=lambda p:(0 if 'TRANSPORT' in p[0] else 1,0 if p[1]=='Underdeck:PositiveFoundation' else 1,p[0],p[1]));rows103=[];bad103=None
for n,k in tasks103:
    s=fields103[n];q=ctx99[k];r=dict(target=n,other=k,source_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='C1_WHOLE_FIXED_RETENTION_SEPARATED125' if gap>=1.25-1e-7 else 'C1_FIXED_RETENTION_OR_REGION_HOLD_NOT_ALL_HANDLAY')
        if gap<1e-7:
            co=s.common(q);r.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows103.append(r);print('RETAIN103',r,flush=True)
    if r['status']!='C1_WHOLE_FIXED_RETENTION_SEPARATED125':bad103=r;break
    if time.monotonic()-t103>15:break
headco103=head103.common(band101);headgap103,_,_=head103.distToShape(band101);assert headco103.isValid()
ar103=OUT/'day07-SOURCE-open9-inboard-retention-C1-first-gate.breps.zip';assert not ar103.exists();ge103=[]
with zipfile.ZipFile(ar103,'w',zipfile.ZIP_DEFLATED) as z:
    items=list(fields103.items())+([(bad103['other'],ctx99[bad103['other']])] if bad103 else [])
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge103.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge103,scope='ONEwholeinboardclosure/axialtailcompartment correction; root/open9guide/sourcepose unchanged. No actualnewguideprintyet.'),indent=2)+'\n').encode())
r103=dict(id='day07-SOURCE-open9-inboard-retention-C1-first-gate',status='C1_WHOLE_RETENTION_FIRST_FALSIFIER_HOLD' if bad103 else 'C1_WHOLE_RETENTION_CURRENT_CONTEXT_RECEIVED_SCOPED_R6_TOOLS_OPEN' if len(rows103)==len(tasks103) else 'C1_WHOLE_RETENTION_PENDING_NOT_PASS',proposal='day07-SOURCE-open9-inboard-retention-C1-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-open9-inboard-retention-C1-proposal.json').read_bytes()).hexdigest(),rows=rows103,cursor=len(rows103),total=len(tasks103),unreceived=len(tasks103)-len(rows103),decisive_negative=bad103,
 actual_head_band_interface=dict(gap_mm=headgap103,common_mm3=headco103.Volume,common_valid=True,head5projectheight=True,deliveredfit_phase2=True),
 full100_budget=dict(sku='111-01910',L_mm=100,band_length_mm=looplen101,required_with25once_mm=looplen101+25,whole_uncut_tail_mm=100-looplen101,parking_capacity_mm=tail103.Volume/2.5,inner_turn_R_mm=3,tail_transport_upper_mm=transportlength103,source_length_positive=(looplen101+25<=100 and transportlength103<100-looplen101),nominal_new_demand1_not_stock_availability=True,no_physicalcut=True),
 root_guide_reuse='Sameactualroot15/60 andfull9guideU1gap5.4498+allnoncandidatebboxseparation fromC0; no replay. CurrentBankPadisactualsubset1282.5/0outsideBankBed, notownershipfromname. FullcurrentR6withdraw/tool/220230parking stillrequired andnotpassedfromphysicalctx.',
 new_support_material='NOTBUILT_BEFORE_FULL_RETENTION_OCCUPANCY',all9_source_A_U_fit_slack=None,no_third_scalar_or_review=True,selected=False,N01_complete=False,current1292_effective1311_rest108_andproposedKnee25_unchanged=True,
 archive=ar103.name,archive_sha256=hashlib.sha256(ar103.read_bytes()).hexdigest(),geometry=ge103,operation_seconds=time.monotonic()-t103,process_cpu_seconds=time.process_time()-cpu103,pid=os.getpid(),session_id=46493)
p103=OUT/'day07-SOURCE-open9-inboard-retention-C1-first-gate.json';assert not p103.exists();p103.write_bytes((json.dumps(r103,ensure_ascii=False,indent=2)+'\n').encode());print('RETAIN103_FINAL',r103['status'],len(rows103),len(tasks103),r103['full100_budget'],r103['operation_seconds'],r103['process_cpu_seconds'],hashlib.sha256(p103.read_bytes()).hexdigest(),flush=True)
