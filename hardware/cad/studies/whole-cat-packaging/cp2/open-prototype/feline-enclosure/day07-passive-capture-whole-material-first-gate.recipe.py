import time,json,hashlib,zipfile,math
t104=time.monotonic();cpu104=time.process_time()
parts104={'root':root101.copy(),'drop':Part.makeBox(4,4,9,A.Vector(-44.3,40.75,42.75)),'arm':Part.makeBox(4,30.25,4,A.Vector(-44.3,42.75,42.75)),'guide_floor':Part.makeBox(13.4,10,1.5,A.Vector(-55.7,67,37.25)),'left_wall':Part.makeBox(2,10,12.25,A.Vector(-55.7,67,38.5)),'right_wall':Part.makeBox(2,10,12.25,A.Vector(-44.3,67,38.5)),'left_capture_lip':Part.makeBox(4.75,10,1.5,A.Vector(-55.7,67,49.25)),'right_capture_lip':Part.makeBox(4.75,10,1.5,A.Vector(-47.05,67,49.25))}
added104=Part.makeCompound(list(parts104.values()));assert added104.isValid();tasks104=[];rows104=[];alias104=[]
for k,q in ctx99.items():
    if k==parentname99 or bbox_lower_bound(added104.BoundBox,q.BoundBox)>=1.25:continue
    if k.startswith('CurrentFoundation:BankPad:'):
        outside=q.cut(parent99);assert outside.isValid()
        if outside.Volume<1e-5:
            alias104.append(dict(actor=k,source_role='Actualselectedcasebottompad/feline_channelled_foundation.py',actual_pad_outside_current_BankBed_mm3=outside.Volume,relation='Exactsubvolumeofretainedsameprintedcarrier—notownershipfromname; allcasebearingunchanged/no boughtshapeignored.'));continue
    tasks104.append(k)
tasks104.sort(key=lambda k:(0 if k=='Underdeck:PositiveFoundation' else 1,k))
for k in tasks104:
    q=ctx99[k];r=dict(other=k,source_valid=q.isValid())
    if q.isValid():
        gap,w,_=added104.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='PASSIVE_WHOLE_LOAD_GUIDE_SEPARATED125' if gap>=1.25-1e-7 else 'PASSIVE_WHOLE_LOAD_GUIDE_HOLD')
        if gap<1e-7:
            co=added104.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows104.append(r);print('PASSIVE104',r,flush=True)
    if r['status']!='PASSIVE_WHOLE_LOAD_GUIDE_SEPARATED125' or time.monotonic()-t104>12:break
clear104=len(rows104)==len(tasks104) and all(r['status']=='PASSIVE_WHOLE_LOAD_GUIDE_SEPARATED125' for r in rows104);whole104=None;coverage104=[];joints104=[];profiles104=[]
if clear104:
    whole104=parent99.copy()
    for s in parts104.values():whole104=whole104.fuse(s)
    for n,s in {'ACTUAL_UNCHANGED_BANKBED':parent99,**parts104}.items():
        missing=s.cut(whole104);coverage104.append(dict(member=n,missing_valid=missing.isValid(),missing_mm3=missing.Volume if missing.isValid() else None,full_intended_bounds_mm=saved_bounds(s)))
    for a,b in [('root','drop'),('drop','arm'),('arm','right_wall'),('right_wall','guide_floor'),('left_wall','guide_floor'),('left_capture_lip','left_wall'),('right_capture_lip','right_wall')]:
        co=parts104[a].common(parts104[b]);joints104.append(dict(a=a,b=b,valid=co.isValid(),positive_mm3=co.Volume if co.isValid() else None))
    for n,s in localprofiles101.items():
        co=added104.common(s);assert co.isValid();profiles104.append(dict(profile=n,allocated_common_mm3=co.Volume))
section104=[]
for axis,val in [('Y',72),('X',-42.3)]:
    if axis=='Y':pl=Part.Face(Part.makePolygon([A.Vector(x,val,z) for x,z in [(-70,28),(-30,28),(-30,58),(-70,58),(-70,28)]]))
    else:pl=Part.Face(Part.makePolygon([A.Vector(val,y,z) for y,z in [(35,28),(85,28),(85,58),(35,58),(35,28)]]))
    for name,s in [('actual_BankBed',parent99),('actual_U1carrier',ctx83['Underdeck:PositiveFoundation']),('passive_Cguide_added_members',added104),('full9_capacity',guide101)]:
        sec=s.section(pl);section104.append(dict(axis=axis,value_mm=val,name=name,coordinates='XZ' if axis=='Y' else 'YZ',curves=[[[p.x,p.z] if axis=='Y' else [p.y,p.z] for p in e.discretize(Deflection=.08)] for e in sec.Edges]))
# OnlysavedR6flexiblewitness26 sourcecovers; neverclaimfullwithdraw/tool/continuousmanualregion.
r6p104=OUT/'day06-R6-existing-witness-source-bounds.json';r6d104=json.loads(r6p104.read_bytes());r6rows104=[]
for q in r6d104['segments']:
    lo,hi=q['bounds_mm'];bb=A.BoundBox(*lo,*hi);low=bbox_lower_bound(added104.BoundBox,bb);r6rows104.append(dict(witness=q['name'],conservative_lower_mm=low,typed_flexible_capacity_not_rigidwire=True))
ar104=OUT/'day07-SOURCE-passive-open9-whole-load-first-gate.breps.zip';assert not ar104.exists();ge104=[]
with zipfile.ZipFile(ar104,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('NEW:'+n,s) for n,s in parts104.items()]
    if whole104 is not None:items.append(('PROPOSED_COMPLETE_BANKBED_PLUS_GUIDE',whole104))
    badnext=next((r for r in rows104 if r['status']!='PASSIVE_WHOLE_LOAD_GUIDE_SEPARATED125'),None)
    if badnext:items.append((badnext['other'],ctx99[badnext['other']]))
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge104.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge104,scope='ONEcausalpassiveCcapture withfull9capacity/bentloadpath, NOTthirdextra100stockvariant; onlyUNBUILTOPTIONAL100role retired. CurrentParentnotmutated.'),indent=2)+'\n').encode())
matok104=whole104 is not None and whole104.isValid() and len(whole104.Solids)==1 and all(q['missing_valid'] and q['missing_mm3']<1e-5 for q in coverage104) and all(q['valid'] and q['positive_mm3']>1e-5 for q in joints104) and all(q['allocated_common_mm3']<1e-5 for q in profiles104)
r104=dict(id='day07-SOURCE-passive-open9-whole-load-first-gate',status='PASSIVE_CGUIDE_FULL_MATERIAL_CURRENT_NEIGHBORS_RECEIVED_SCOPED_SOURCE_APPROACH_OPEN' if clear104 and matok104 else 'PASSIVE_CGUIDE_ACTUAL_LOAD_LAYER_OR_PENDING_HOLD',proposal='day07-SOURCE-open9-passive-capture-causal-decision.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-open9-passive-capture-causal-decision.json').read_bytes()).hexdigest(),rows=rows104,cursor=len(rows104),total=len(tasks104),unreceived=len(tasks104)-len(rows104),same_print_actual_subset_aliases=alias104,
 root15_contact60_reuse='Sameunchangedroot101/actualBankBed&subsetBankPad alreadyreceived—notreplayed.',material_received=matok104,complete_parent_valid=whole104.isValid() if whole104 else None,complete_parent_solids=len(whole104.Solids) if whole104 else None,intended_member_coverage=coverage104,positive_junctions=joints104,full9_profiles=profiles104,
 guide_function=dict(full_capacity_mm=[9.4,10.5],mouth_mm=3.9,full_DG3p1_plus2xmargin0p4=True,individual_source_conductors_lateral_lay_notthreadfactorycases=True,no_new9_terminal_debit=True,realends_Knee4ties_bodyends_retained=True,extra100_role='UNBUILTOPTIONALonlyretired—noactualselectedpartremoved'),
 sections=section104,source_R6_saved_flexible_witnesses=dict(path=r6p104.name,sha256=hashlib.sha256(r6p104.read_bytes()).hexdigest(),rows=r6rows104,all_conservative_separated=all(q['conservative_lower_mm']>=1.25 for q in r6rows104),actual_withdraw25_tool12x41x25='SOURCEOPERANDS_NOTRECEIVED/HOLD, notPASSfrom26witnesses',continuous_manual_parking='OPEN'),
 source_whole9_R_motionlengthslack='OPEN_ALL_A_U_FIT_SLACK_NULL; noCS/chordcredit/oldprefix/36replay. Onlyifactualfixedloadguidecredible nextwholeKnee6/Hip3/9merge/DGV/all12portions4MAX3.',initialassembly='OpenpassiveCguide: laybodyfreeconductorsonebyonebeforefinalreceiverclosures, factoryplug/splices/soldersintact; sourceendstrainreliefsremainreal9ends. WholefeasibleR/slack/initialinstallstillneedsSOURCEapproachqualification. NewBankBed+guideintegralinitialfoundationbeforebankcases, nophantomdetachablearms.',selected=False,N01_complete=False,current1292_effective1311_rest108_plusproposedKnee25_unchanged=True,new_parent_NOT_selected=True,archive=ar104.name,archive_sha256=hashlib.sha256(ar104.read_bytes()).hexdigest(),geometry=ge104,operation_seconds=time.monotonic()-t104,process_cpu_seconds=time.process_time()-cpu104,pid=os.getpid(),session_id=46493)
p104=OUT/'day07-SOURCE-passive-open9-whole-load-first-gate.json';assert not p104.exists();p104.write_bytes((json.dumps(r104,ensure_ascii=False,indent=2)+'\n').encode());print('PASSIVE104_FINAL',r104['status'],len(rows104),len(tasks104),matok104,[(q['other'],q.get('gap_mm')) for q in rows104],r104['operation_seconds'],r104['process_cpu_seconds'],hashlib.sha256(p104.read_bytes()).hexdigest(),flush=True)
