import time,json,hashlib,zipfile,os,math
t105=time.monotonic();cpu105=time.process_time();parts105=dict(parts104);parts105['root']=Part.makeBox(15,7,.75,A.Vector(-54.5,39.25,51.5));assert all(parts105[n] is parts104[n] for n in parts105 if n!='root')
foot105=parts105['root'];rootco105=foot105.common(parent99);rootface105=Part.Face(Part.makePolygon([A.Vector(x,y,52) for x,y in [(-54.5,39.25),(-39.5,39.25),(-39.5,46.25),(-54.5,46.25),(-54.5,39.25)]]));contact105=rootface105.common(parent99);assert rootco105.isValid() and contact105.isValid();rootok105=abs(rootco105.Volume-26.25)<1e-5 and abs(contact105.Area-105)<1e-5
added105=Part.makeCompound(list(parts105.values()));underlower105=bbox_lower_bound(foot105.BoundBox,ctx83['Underdeck:PositiveFoundation'].BoundBox);reuseU105=underlower105>=2.291-1e-6
alias105=[];tasks105=[];rows105=[]
for k,q in ctx99.items():
    if k==parentname99 or bbox_lower_bound(added105.BoundBox,q.BoundBox)>=1.25:continue
    if k=='Underdeck:PositiveFoundation' and reuseU105:continue
    if k.startswith('CurrentFoundation:BankPad:'):
        outside=q.cut(parent99);assert outside.isValid()
        if outside.Volume<1e-5:alias105.append(dict(actor=k,source_role='Actualselectedcasebottompad',actual_pad_outside_current_parent_mm3=outside.Volume,not_name_based=True));continue
    tasks105.append(k)
tasks105.sort(key=lambda k:(0 if k=='BankPortal2:Carrier' else 1,k))
if rootok105:
    for k in tasks105:
        q=ctx99[k];r=dict(other=k,source_valid=q.isValid())
        if q.isValid():
            low=bbox_lower_bound(added105.optimalBoundingBox(),q.optimalBoundingBox())
            if low>=1.25:r.update(conservative_tight_bounds_lower_mm=low,status='SOURCE_PAD_GUIDE_SEPARATED125_BY_FULL_BOUNDS')
            else:
                gap,w,_=added105.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='SOURCE_PAD_GUIDE_SEPARATED125' if gap>=1.25-1e-7 else 'SOURCE_PAD_GUIDE_ACTUAL_NEIGHBOR_HOLD')
                if gap<1e-7:
                    co=added105.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        rows105.append(r);print('PAD105',r,flush=True)
        if not r['status'].startswith('SOURCE_PAD_GUIDE_SEPARATED125') or time.monotonic()-t105>15:break
clear105=rootok105 and len(rows105)==len(tasks105) and all(r['status'].startswith('SOURCE_PAD_GUIDE_SEPARATED125') for r in rows105);whole105=None;coverage105=[];joints105=[];profiles105=[];section105=[];reopen105=None
if clear105:
    intended105={n:s.copy() for n,s in {'ACTUAL_UNCHANGED_BANKBED':parent99,**parts105}.items()}
    whole105=parent99.copy()
    for s in parts105.values():whole105=whole105.fuse(s.copy())
    for n,s in intended105.items():
        missing=s.cut(whole105);coverage105.append(dict(member=n,missing_valid=missing.isValid(),missing_mm3=missing.Volume if missing.isValid() else None,bounds_mm=saved_bounds(s),volume_mm3=s.Volume))
    for a,b in [('root','drop'),('drop','arm'),('arm','right_wall'),('right_wall','guide_floor'),('left_wall','guide_floor'),('left_capture_lip','left_wall'),('right_capture_lip','right_wall')]:
        c=parts105[a].common(parts105[b]);joints105.append(dict(a=a,b=b,valid=c.isValid(),positive_mm3=c.Volume if c.isValid() else None))
    for n,s in localprofiles101.items():
        c=added105.common(s);assert c.isValid();profiles105.append(dict(profile=n,allocated_common_mm3=c.Volume))
    cc=added105.common(guide101);assert cc.isValid();capacitycommon105=cc.Volume
    raw=whole105.exportBrepToString();reopened=Part.Shape();reopened.importBrepFromString(raw);reopen105=dict(scope='ONLYNEWcompleteBankBed+passiveguidepart, notoldsource56/strictreplay',valid=reopened.isValid(),solids=len(reopened.Solids),volume_delta_mm3=reopened.Volume-whole105.Volume,bounds_mm=saved_bounds(reopened))
for axis,val in [('Y',42.75),('Y',72)]:
    pl=Part.Face(Part.makePolygon([A.Vector(x,val,z) for x,z in [(-65,30),(-20,30),(-20,58),(-65,58),(-65,30)]]))
    for name,s in [('actual_BankBed',parent99),('actual_U1carrier',ctx83['Underdeck:PositiveFoundation']),('actual_BankPortal2',ctx83['BankPortal2:Carrier']),('new_source_pad_passive_guide',added105),('full9_capacity',guide101)]:
        sec=s.section(pl);section105.append(dict(axis=axis,value_mm=val,name=name,curves_xz=[[[p.x,p.z] for p in e.discretize(Deflection=.08)] for e in sec.Edges]))
ar105=OUT/'day07-SOURCE-pad-conforming-passive9-whole-first-gate.breps.zip';assert not ar105.exists();ge105=[]
with zipfile.ZipFile(ar105,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('NEW:'+n,s) for n,s in parts105.items()]+[('ACTUAL:root_parent_common',rootco105),('ACTUAL:contact105',contact105)]
    if whole105 is not None:items.append(('PROPOSED_COMPLETE_BANKBED_PLUS_PASSIVE9',whole105))
    else:
        bad=next((r for r in rows105 if not r['status'].startswith('SOURCE_PAD_GUIDE_SEPARATED125')),None)
        if bad:items.append((bad['other'],ctx99[bad['other']]))
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge105.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,valid=s.isValid(),solids=len(s.Solids)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge105,scope='ONEactualBankPad15x7conformingROOT/growingcontact105; same7othermembers andpassiveguidepose/capture/stock/Portalfunctions. Newfixedcandidate, notcurrentselection.'),indent=2)+'\n').encode())
materialok105=clear105 and whole105 is not None and whole105.isValid() and len(whole105.Solids)==1 and all(q['missing_valid'] and q['missing_mm3']<1e-5 for q in coverage105) and all(q['valid'] and q['positive_mm3']>1e-5 for q in joints105) and all(q['allocated_common_mm3']<1e-5 for q in profiles105) and capacitycommon105<1e-5 and reopen105['valid'] and reopen105['solids']==1 and abs(reopen105['volume_delta_mm3'])<1e-5
bb=whole105.optimalBoundingBox() if whole105 is not None else added105.optimalBoundingBox()
r105=dict(id='day07-SOURCE-pad-conforming-passive9-whole-first-gate',status='SOURCE_PAD_PASSIVE_GUIDE_ROOT_MATERIAL_CURRENT_NEIGHBORS_RECEIVED_SCOPED' if materialok105 else 'SOURCE_PAD_PASSIVE_GUIDE_ROOT_MATERIAL_OR_NEIGHBOR_HOLD',proposal='day07-SOURCE-pad-conforming-passive9-whole-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-pad-conforming-passive9-whole-proposal.json').read_bytes()).hexdigest(),actual_root=dict(contact_xy_mm=[15,7],embed_mm3=rootco105.Volume,contact_mm2=contact105.Area,expected_embed_mm3=26.25,expected_contact_mm2=105,valid=True,full_material=rootok105,source_conforming_not_offset=True),
 actual_foreign_rows=rows105,cursor=len(rows105),total=len(tasks105),unreceived=len(tasks105)-len(rows105),Underdeck_true_unchanged_reuse=dict(previous_whole_gap_mm=2.291,new_foot_full_bounds_lower_mm=underlower105,other7members_same_object=True,valid_reuse=reuseU105,no_old_pair_retest=True),same_print_actual_subset_aliases=alias105,
 material_received=materialok105,whole_parent_valid=whole105.isValid() if whole105 else None,whole_parent_solids=len(whole105.Solids) if whole105 else None,intended9_member_coverage=coverage105,positive7_junctions=joints105,whole9_profile_fit=profiles105,full_capacity_material_common_mm3=capacitycommon105 if whole105 is not None else None,new_part_strict_reopen=reopen105,
 useful_sections=dict(root_xy_mm=[15,7],root_contact_mm2=105,drop_arm_mm=[4,4],floor_lips_mm=1.5,walls_mm=2,mouth_mm=3.9,fullD_G3p1_plus2x0p4=True,not_strength_certificate=True),
 proposed_part_print_bounds=dict(bounds_mm=saved_bounds(whole105) if whole105 else saved_bounds(added105),max_extent_mm=max(bb.XLength,bb.YLength,bb.ZLength),within200=max(bb.XLength,bb.YLength,bb.ZLength)<=200,BodyOuter_actual3p25='NOTYETCHECKED/no bboxoutlinePASS'),
 local_installation='Passiveguidance/captureONLY; realmoving/source/bodyendstrainreliefs retained. Beforebodyreceiverclosures lateral/sequentiallooseindividualfull3.1SOURCEconductors canenter3.9mouth with.4eachside atentry, thensettle3rows9.4x10.5. Notrigid9simultaneousinsertion/factorycasepassage/virtualunsolder/extra9. ActualwholeSOURCErouteR/slack/coupledinitialassembly stillOPEN, nofullN08.',
 R6='Saved26flexiblewitnessesconservativeboundsretaintruepreviousseparationforunchanged7members; newfootfurtherYmin/maxstillfarseparated. Actualwithdraw/tool/continuousmanualsourcequalificationOPEN.',all_source9_A_U_minimum_fit_slack=None,new_source_Knee21_plus4temp_in_full1444=True,current1292_effective1311_rest108_unchanged=True,selected=False,N01_complete=False,sections=section105,archive=ar105.name,archive_sha256=hashlib.sha256(ar105.read_bytes()).hexdigest(),geometry=ge105,operation_seconds=time.monotonic()-t105,process_cpu_seconds=time.process_time()-cpu105,pid=os.getpid(),session_id=46493)
p105=OUT/'day07-SOURCE-pad-conforming-passive9-whole-first-gate.json';assert not p105.exists();p105.write_bytes((json.dumps(r105,ensure_ascii=False,indent=2)+'\n').encode());print('PAD105_FINAL',r105['status'],r105['actual_root'],len(rows105),len(tasks105),materialok105,r105['whole_parent_solids'],len(coverage105),len(joints105),r105['operation_seconds'],r105['process_cpu_seconds'],hashlib.sha256(p105.read_bytes()).hexdigest(),flush=True)
