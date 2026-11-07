import time,json,hashlib,zipfile,os
tr114=time.monotonic();tc114=time.process_time();field114=Part.makeBox(9.4,37.75,10.5,A.Vector(-137.45,39.25,38.75));assert field114.isValid();expanded114=Part.makeBox(15.9,44.25,17,A.Vector(-140.7,36,35.5));out114=expanded114.cut(BodyOuter31);assert out114.isValid();rawoutside114=None;realgap114=None
outline114=dict(required_margin_mm=3.25,method='Newwholefieldexpandedaxisalignedcover3.25 eachside containsEuclidean3.25offset; validcover.cut(ACTUALBodyOuter31)==0proves actualcontourmargin, notBBoxalone/oldoutline replay.',expanded_cover_bounds_mm=saved_bounds(expanded114),expanded_cover_outside_mm3=out114.Volume,source_BodyOuter_world_bounds_mm=saved_bounds(BodyOuter31),source_BodyOuter_volume_mm3=BodyOuter31.Volume)
if out114.Volume>1e-6:
    rawoutside114=field114.cut(BodyOuter31);assert rawoutside114.isValid();outline114['full_field_outside_mm3']=rawoutside114.Volume
    if rawoutside114.Volume<1e-6:
        realgap114=field114.distToShape(BodyOuter31.Shells[0])[0];outline114['actual_full_field_to_outer_shell_gap_mm']=realgap114
outline114['received_margin']=out114.Volume<1e-6 or (realgap114 is not None and realgap114>=3.25-1e-7)
ctx114=dict(ctx111);ctx114[parentname99]=parent99
# Whole105previouscandidatehad originalparent as0missingmember: revertingONLYunselectedextra8
# is a materialSUBSETdeletion, not oldsourcegeometry/motionreplay or purchasedpartremoval.
tasks114=[n for n,s in ctx114.items() if bbox_lower_bound(field114.BoundBox,s.BoundBox)<1.25];tasks114.sort();rows114=[];first114=None;obstacle114=None;common114=None
if not outline114['received_margin']:first114=dict(status='NEW_LEFT_BODY_PASSAGE_CONTOUR_MARGIN_HOLD_NOT_CONTACT',outline=outline114)
if first114 is None:
    for n in tasks114:
        s=ctx114[n];row=dict(target='FULL9_ACTUAL_LEFT_END_STRAIGHT_PASSAGE',other=n,source_valid=s.isValid())
        if row['source_valid']:
            gap,w,_=field114.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(aa),list(bb)] for aa,bb in w[:1]],status='FULL9_BODY_PASSAGE_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_REGION_HOLD_NOT_ACTUALWIRECONTACT')
            if gap<1e-7:
                common114=field114.common(s);row.update(common_valid=common114.isValid(),allocated_common_mm3=common114.Volume if common114.isValid() else None)
        else:row['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
        rows114.append(row)
        if row['status']!='FULL9_BODY_PASSAGE_SEPARATED125':first114=row;obstacle114=s;break
# Reusable bounds proof: all fullbody/movingneutral/new21+4temp considered, no bodypart omittedbylabel.
lowers114=sorted([(bbox_lower_bound(field114.BoundBox,s.BoundBox),n) for n,s in ctx114.items()]);nearest114=[dict(actor=n,conservative_full_source_bbox_lower_mm=lo,bounds_mm=saved_bounds(ctx114[n])) for lo,n in lowers114[:12]]
framefull114=[dict(actor=n,bounds_mm=saved_bounds(s)) for n,s in ctx114.items() if n!=badname112 and bbox_lower_bound(bad112.BoundBox,s.BoundBox)<1.25]
endfaces114=[]
for i,f in enumerate(under113.Faces):
    if type(f.Surface).__name__=='Plane':
        n=f.normalAt(0,0);b=f.BoundBox
        if n.x<-.99 and abs(b.XMin+126)<1e-5:endfaces114.append(dict(face=i,area_mm2=f.Area,bounds_mm=saved_bounds(f),normal=list(n),available_root_NOT_proved=True))
sections114=[]
for y in [39.25,55,70,77]:
    plane=Part.makePlane(120,130,A.Vector(-170,y,-10),A.Vector(0,1,0))
    for n,s in [('full9_left_end_passage_capacity',field114),('actual_U1carrier',under113),('actual_P0_MountFrontL',bad112),('actual_BodyOuter',BodyOuter31)]:
        q=s.section(plane);curves=[]
        for e in q.Edges:
            pp=e.discretize(Deflection=.15)
            if len(pp)>1:curves.append([[v.x,v.z] for v in pp])
        sections114.append(dict(axis='Y',value_mm=y,name=n,curves_xz=curves))
ar114=OUT/'day07-SOURCE-left-end-body-passage-first-gate.breps.zip';assert not ar114.exists();ge114=[]
with zipfile.ZipFile(ar114,'w',zipfile.ZIP_DEFLATED) as z:
    its=[('FULL9_LEFT_END_STRAIGHT_CAPACITY',field114),('NEW_3p25_EXPANDED_OUTLINE_COVER',expanded114),('NEW_OUTLINE_COVER_OUTSIDE_ACTUAL_BODY',out114)]
    if obstacle114 is not None:its.append(('FIRST_CURRENT_OBSTACLE',obstacle114))
    if common114 is not None:its.append(('ALLOCATED_COMMON_NOT_ACTUALWIRECONTACT',common114))
    for i,(n,s) in enumerate(its):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge114.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s) if not s.isNull() else None,volume_mm3=s.Volume,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge114,scope='NEWstraight9bodyregion+actualoutlinecoveronly; no printedmaterial/sourceworld/motion/reopenreplay'),indent=2)+'\n').encode())
r114=dict(id='day07-SOURCE-left-end-body-passage-first-gate',status='LEFT_END_FULL9_STRAIGHT_BODY_PASSAGE_AND_ACTUAL_OUTLINE_RECEIVED_SCOPED' if first114 is None else 'LEFT_END_BODY_PASSAGE_FIRST_FALSIFIER_HOLD',proposal='day07-SOURCE-left-end-frame-bypass-whole-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-left-end-frame-bypass-whole-proposal.json').read_bytes()).hexdigest(),whole_full_field=dict(bounds_mm=saved_bounds(field114),cross_section_mm=[9.4,10.5],straight_transport_mm=37.75,volume_mm3=field114.Volume,not_fullroute_percorefit_or_slack=True),outline=outline114,current_whole_neighbor_count=len(ctx114),rows=rows114,cursor=len(rows114),total=len(tasks114),unreceived=len(tasks114)-len(rows114),all_other_full_sources_bbox_positive=all(lo>=1.25 for lo,n in lowers114 if n not in tasks114),nearest_full_actor_bounds=nearest114,first_falsifier=first114,actual_P0_mount_neighbors=framefull114,actual_U1_left_end_material_faces=endfaces114,U1_functions_source='day07-coordinator-fixed-print-source-functions.json actualfeet/holes/lowerbranch/understep/foamC/metal/FHYsupport/screwaccess retained; no newrootaccepted/materialcut.',new_guide_root_accepted=False,new_material_built=False,old_guide105_evidence='Unselectedadded8guideoverlayNOTincludedasactualcurrent. OriginalactualBankBedparent retained; subsetofwhole105 byreceivedmembercoverage/no motionreplay. Newrouteguidefunction/rootstillproposal.',new_source21motion36_unchanged_proof_reuse=True,all_A_U_minimum_fit_slack=None,group_R35p1_external_loop_entryfan_roll_motion_reserve_storage='OPEN/straightfieldRinfiniteonly; no onefixedfreewirecurveforallposes',sections=sections114,archive=ar114.name,archive_sha256=hashlib.sha256(ar114.read_bytes()).hexdigest(),geometry=ge114,operation_seconds=time.monotonic()-tr114,process_cpu_seconds=time.process_time()-tc114,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p114=OUT/'day07-SOURCE-left-end-body-passage-first-gate.json';assert not p114.exists();p114.write_bytes((json.dumps(r114,indent=2)+'\n').encode());print('SOURCE114_FINAL',r114['status'],len(tasks114),len(rows114),first114,outline114,nearest114[:3],endfaces114,r114['operation_seconds'],r114['process_cpu_seconds'],hashlib.sha256(p114.read_bytes()).hexdigest(),flush=True);print('OWNER58_IDLE',os.getpid(),len(Current35),len(effective62),len(restMotion),'pendingnull unsavedfalse',flush=True)
