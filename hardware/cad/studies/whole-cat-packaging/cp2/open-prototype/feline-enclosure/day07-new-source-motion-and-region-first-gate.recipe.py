import time,json,hashlib,zipfile,math,os
t106=time.monotonic();cpu106=time.process_time();assert r105['material_received'];stages106=['Hip','Knee','Ankle'];axisgroups106={code:[next(a for a in axes if a['code']==code and a['stage']==s) for s in stages106] for code in ['FL','FR','RL','RR']};owners106={n:(code,i) for code,gs in MotionSource31['membership'].items() for i,s in enumerate(stages106) for n in gs[s] if n in restMotion};assert len(owners106)==len(restMotion)==108
op106={n:s for n,s in proposed99.items() if ':PULL_TEMP:' not in n};assert len(op106)==21;sourcevol106={n:s.Volume for n,s in op106.items()};fixed106=dict(effective62);fixed106[parentname99]=whole105;skipalias106={q['actor'] for q in alias105};fixed106={n:s for n,s in fixed106.items() if n not in skipalias106};assert not(set(fixed106)&set(restMotion))
fixednames106=list(fixed106);fixedlo106=np.array([[fixed106[n].BoundBox.XMin,fixed106[n].BoundBox.YMin,fixed106[n].BoundBox.ZMin] for n in fixednames106]);fixedhi106=np.array([[fixed106[n].BoundBox.XMax,fixed106[n].BoundBox.YMax,fixed106[n].BoundBox.ZMax] for n in fixednames106]);qbody106=np.array([-49,77,44]);ports106=[];pose_rows106=[];actualrows106=[];floors106=[];first106=None;failedshape106=None;failedother106=None
def placement106(r,t):
    m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,'A'+str(i+1)+str(j+1),float(r[i,j]))
    m.A14=float(t[0]);m.A24=float(t[1]);m.A34=float(t[2]);return A.Placement(m)
sourceorig106=json.loads((OUT/'day07-whole-physical-SOURCE-approach-Knee-link-proposal.json').read_bytes())['source_origins']
for pi,pose in enumerate(MotionSource31['poses'][:36]):
    tr={code:leg_transforms(axisgroups106[code],pose['legs'][code]['angles_delta_degrees']) for code in axisgroups106};r,t=tr['RL'][1];assert np.linalg.norm(r.T@r-np.eye(3))<1e-10 and abs(np.linalg.det(r)-1)<1e-10
    p=np.array(list(placement83.multVec(A.Vector(43,8.5,4))));p=r@p+t;tan=r@np.array(list(axis81));delta=qbody106-p;perp=delta-tan*float(delta@tan);pn=float(np.linalg.norm(perp));toward=p+35.1*perp/pn;targetdist=float(np.linalg.norm(qbody106-toward));endradius=float(delta@delta/(2*pn));sourceframes=[]
    for ii,src in enumerate(sourceorig106):
        rr,tt=tr['RL'][0 if ii==0 else 1];pp=rr@np.array(src['source_outer_reservation_world_mm'])+tt;sourceframes.append(dict(loom=src['loom'],owner='Motion_RL_Hip' if ii==0 else 'Motion_RL_Knee',nominal_source14_outer_world_mm=pp.tolist(),nominal_departure_world=(rr@np.array(src['source_departure_axis'])).tolist(),not_supplier_pinout_or_received_prefix_length=True))
    joints={k:(r@np.array(list(placement83.multVec(A.Vector(u,8.5+v,4))))+t).tolist() for k,u,v in [('D',-22,-2.85),('V',0,0),('G',22,2.85)]}
    ports106.append(dict(pose=pi,body_drop_mm=pose['body_drop_mm'],Knee_entry_world_mm=(r@np.array(list(placement83.multVec(A.Vector(-43,8.5,4))))+t).tolist(),Knee_exit_world_mm=p.tolist(),Knee_exit_tangent=tan.tolist(),joint_centres_world_mm=joints,source_origins=sourceframes,short_toward_C_S=dict(group_R_mm=35.1,circle_centre_mm=toward.tolist(),target_to_circle_centre_mm=targetdist,target_inside_circle=targetdist<35.1-1e-7,direct_single_arc_radius_mm=endradius,meaning='Necessaryshorttoward-targetC/Sfamilyonly. Targetinsidecircleprecludesrealstraighttangentfromthatcircle. No endpointchordasroutedlength/slack/stock; guideaxis-Yendfan NOTqualified, external-loop/two-arcgroupbay stillpossible.')))
# Onlynewoperatingattachments; old108 pose geometry followsreceivedmembership,
# no oldcollisionmatrixreplay. Temp4 pullregionsnotoperatingrigidstock.
for pi,pose in enumerate(MotionSource31['poses'][:36]):
    tr={code:leg_transforms(axisgroups106[code],pose['legs'][code]['angles_delta_degrees']) for code in axisgroups106};r,t=tr['RL'][1];pl=placement106(r,t);moved={};badcopy=False
    for n,s in op106.items():
        q=s.copy();q.Placement=pl*q.Placement
        if not q.isValid() or abs(q.Volume-sourcevol106[n])>1e-5:first106=dict(pose=pi,actor=n,status='NEW_RIGID_COPY_INTEGRITY_OPEN_NOT_DESIGNCONTACT');badcopy=True;break
        moved[n]=q;b=q.BoundBox;floorlower=b.ZMin-pose['body_drop_mm']-MotionSource31['ground_rest_z_mm'];floors106.append(dict(pose=pi,actor=n,kind='printedactualcandidate' if n.endswith((':lower',':upper')) else 'retained_stock_or_profile_capacity',conservative_ground_lower_mm=floorlower))
        if floorlower<1.25:first106=dict(pose=pi,actor=n,status='NEW_FLOOR_BOUND_HOLD_NOT_AUTOMATIC_CONTACT',lower_mm=floorlower);failedshape106=q;break
    if first106:break
    if pi==0:
        pose_rows106.append(dict(pose=pi,status='NEUTRAL_STATIC_REUSE_NEW_FLOOR_ONLY',new_floor_properties=21,neutral13stock5carrier_plusnewfixedguide_currentcontext_reused=True));continue
    othernames=list(fixednames106);others=dict(fixed106)
    for n,s in restMotion.items():
        code,si=owners106[n]
        if code=='RL' and si==1:continue
        rr,tt=tr[code][si];q=s.copy();q.Placement=placement106(rr,tt)*q.Placement;othernames.append(n);others[n]=q
    lo=np.array([[others[n].BoundBox.XMin,others[n].BoundBox.YMin,others[n].BoundBox.ZMin] for n in othernames]);hi=np.array([[others[n].BoundBox.XMax,others[n].BoundBox.YMax,others[n].BoundBox.ZMax] for n in othernames]);candidates=0
    for n,q in sorted(moved.items(),key=lambda z:(0 if z[0].endswith((':lower',':upper')) else 1,z[0])):
        b=q.BoundBox;ql=np.array([b.XMin,b.YMin,b.ZMin]);qh=np.array([b.XMax,b.YMax,b.ZMax]);g=np.maximum(np.maximum(ql-hi,lo-qh),0);indices=np.flatnonzero(np.sum(g*g,axis=1)<1.25**2)
        for jj in indices:
            k=othernames[int(jj)];s=others[k];row=dict(pose=pi,new_actor=n,other=k,other_valid=s.isValid(),source_valid=q.isValid())
            if s.isValid():
                gap,w,_=q.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='NEW_SOURCE_MOTION_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_SOURCE_MOTION_ACTUAL_OR_CAPACITY_HOLD')
                if gap<1e-7:
                    co=q.common(s);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            else:row['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
            actualrows106.append(row);candidates+=1
            if row['status']!='NEW_SOURCE_MOTION_SEPARATED125':first106=row;failedshape106=q;failedother106=s;break
            if time.monotonic()-t106>18:break
        if first106 or time.monotonic()-t106>18:break
    if first106:break
    complete=time.monotonic()-t106<=18;pose_rows106.append(dict(pose=pi,status='NEW21_WHOLE_CURRENT_POSE_RECEIVED' if complete else 'POSE_PENDING_NOT_PASS',actual_candidate_pairs=candidates,full21_processed=complete,shared_Knee_rigid_relative_pairs_reused=True))
    if not complete:break
ar106=OUT/'day07-SOURCE-new-moving-module-region-first-gate.breps.zip';assert not ar106.exists();ge106=[]
with zipfile.ZipFile(ar106,'w',zipfile.ZIP_DEFLATED) as z:
    items=[]
    if failedshape106 is not None:items.append(('NEW_SOURCE_AT_FIRST_HOLD',failedshape106))
    if failedother106 is not None:items.append(('CURRENT_NEIGHBOR_AT_FIRST_HOLD',failedother106))
    if not items:items=[('NEW_SOURCE_PRINT_LOWER_LAST_RECEIVED',moved['PROPOSED_SOURCE_KNEE:lower']),('NEW_SOURCE_PRINT_UPPER_LAST_RECEIVED',moved['PROPOSED_SOURCE_KNEE:upper'])]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge106.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge106,scope='ONLYNEWSource21motiondelta/frozen36, sourceworldPlacementONCE. SavedfirstHOLDorlastnewprint, notold108matrix/123axes.'),indent=2)+'\n').encode())
done106=len(pose_rows106)==36 and all(q['status']!='POSE_PENDING_NOT_PASS' for q in pose_rows106) and first106 is None
r106=dict(id='day07-SOURCE-new-moving-module-region-first-gate',status='NEW_SOURCE21_BODY_FLOOR_36_RECEIVED_SCOPED_GROUP_APPROACH_OPEN' if done106 else 'NEW_SOURCE21_MOTION_FIRST_HOLD' if first106 else 'NEW_SOURCE21_MOTION_PENDING_NOT_PASS',scope='NewKnee21operating vscurrentfixedbodywithnewBankBedguide+all108actuallyposedfromfrozenmembership exceptsameKneecommonrigidtransformneutralreused. Temp4onlyinitialassembly excludedoperation. No oldcollision/sourceworld/IK/reopenreplay.',source_world_frame='Copy.Placement=KneeR/T*sourceworldPlacementONCE; no XML/transformGeometry. Eachnewrigidcopyvalid/volumepreserved, Rorthonormal. Forrelativebody omitcommonbodydrop; forground subtractSAMEsourcebody_drop, samefloor/end35.',required_poses=36,received_pose_rows=pose_rows106,received_complete_poses=sum(q['status']!='POSE_PENDING_NOT_PASS' for q in pose_rows106),first_falsifier=first106,actual_candidate_rows=actualrows106,new_floor_rows=floors106,minimum_new_conservative_floor_lower_mm=min(q['conservative_ground_lower_mm'] for q in floors106) if floors106 else None,ground_rest_z_mm=MotionSource31['ground_rest_z_mm'],new_port_frame_rows36=ports106,short_toward_CS_falsified_pose_count=sum(q['short_toward_C_S']['target_inside_circle'] for q in ports106),neutral_group_premise=ports106[0]['short_toward_C_S'],actual_group_R_source_minimum_fit_slack=None,guide_end_tangent_fan='NOTQUALIFIED axis-Y/full9entry remainsrequired; no C/StextPASS/endpointseparationfitcredit.',whole_source9_12portions4MAX3_budgets='ALLNULL untiloccupiedR/transport/slack regions qualified. No oldprefix/181205225/chord-as-route/physicalshortage claim.',fixed_pad_module='Received40e8847e/root26.25/contact105/newcompletePart1solid9members7joints, oneNEWstrictreopen; proposedshadowcontextnotselected.',archive=ar106.name,archive_sha256=hashlib.sha256(ar106.read_bytes()).hexdigest(),geometry=ge106,operation_seconds=time.monotonic()-t106,process_cpu_seconds=time.process_time()-cpu106,selected=False,N01_complete=False,current1292_effective1311_rest108_unchanged=True,pid=os.getpid(),session_id=46493)
p106=OUT/'day07-SOURCE-new-moving-module-region-first-gate.json';assert not p106.exists();p106.write_bytes((json.dumps(r106,ensure_ascii=False,indent=2)+'\n').encode());print('SOURCE106_FINAL',r106['status'],r106['received_complete_poses'],first106,len(actualrows106),r106['minimum_new_conservative_floor_lower_mm'],r106['short_toward_CS_falsified_pose_count'],r106['neutral_group_premise'],r106['operation_seconds'],r106['process_cpu_seconds'],hashlib.sha256(p106.read_bytes()).hexdigest(),flush=True)
