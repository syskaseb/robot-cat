import time,json,hashlib,os,math
# Resume ONLYmissing newSOURCE21 pairs. Old r106 immutable.
rows108=list(r106['actual_candidate_rows']);floors108=list(r106['new_floor_rows']);doneposes108={q['pose'] for q in r106['received_pose_rows'] if q['status']!='POSE_PENDING_NOT_PASS'};pairkeys108={(q['pose'],q['new_actor'],q['other']) for q in rows108};floorkeys108={(q['pose'],q['actor']) for q in floors108};posecursor108=3;first108=None;failednew108=None;failedother108=None;chunks108=[];lastmoved108={};p108=OUT/'day07-SOURCE-new-motion-continuation-current.json';assert not p108.exists()
def save108():
    d=dict(id=p108.stem,status='NEW_SOURCE21_FIRST_FALSIFIER_STOP' if first108 else 'NEW_SOURCE21_36_BODY_FLOOR_RECEIVED_SCOPED' if len(doneposes108)==36 else 'NEW_SOURCE21_PARTIAL_SAVED_CURSOR_NOT_PASS',source_receipt=p106.name,source_sha256=hashlib.sha256(p106.read_bytes()).hexdigest(),required_poses=36,complete_pose_indices=sorted(doneposes108),pose_cursor=posecursor108,actual_candidate_rows=rows108,exact_skip_received_pair_keys=[list(k) for k in sorted(pairkeys108)],new_floor_rows=floors108,minimum_new_floor_lower_mm=min(q['conservative_ground_lower_mm'] for q in floors108),first_falsifier=first108,chunks=chunks108,world_frame='Samebakedworld/rigidPlacementONCE; bodyrelativeomitscommonbodydrop; floorusesexactfrozenbodydrop+ground; noXML/transformGeometry',no_old_matrix_replayed=True,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
    tmp=p108.with_suffix('.tmp');tmp.write_bytes((json.dumps(d,indent=2)+'\n').encode());os.replace(tmp,p108);return d
def changed_motion_chunk108(seconds=18):
    global posecursor108,first108,failednew108,failedother108,lastmoved108
    tw=time.monotonic();tc=time.process_time();before=len(rows108);beforefloor=len(floors108);startpose=posecursor108
    while posecursor108<36 and first108 is None:
        pi=posecursor108;pose=MotionSource31['poses'][pi];tr={code:leg_transforms(axisgroups106[code],pose['legs'][code]['angles_delta_degrees']) for code in axisgroups106};r,t=tr['RL'][1];pl=placement106(r,t);moved={}
        for n,s in op106.items():
            q=s.copy();q.Placement=pl*q.Placement
            if not q.isValid() or abs(q.Volume-sourcevol106[n])>1e-5:first108=dict(pose=pi,new_actor=n,status='NEW_RIGID_COPY_INTEGRITY_OPEN_NOT_DESIGNCONTACT');break
            moved[n]=q
            if (pi,n) not in floorkeys108:
                lower=q.BoundBox.ZMin-pose['body_drop_mm']-MotionSource31['ground_rest_z_mm'];floors108.append(dict(pose=pi,actor=n,kind='printedactualcandidate' if n.endswith((':lower',':upper')) else 'retained_stock_or_profile_capacity',conservative_ground_lower_mm=lower));floorkeys108.add((pi,n))
                if lower<1.25:first108=dict(pose=pi,new_actor=n,status='NEW_FLOOR_BOUND_HOLD_NOT_AUTOMATIC_CONTACT',lower_mm=lower);failednew108=q;break
        lastmoved108=moved
        if first108:break
        othernames=list(fixednames106);others=dict(fixed106);lo=list(fixedlo106);hi=list(fixedhi106)
        for n,s in restMotion.items():
            code,si=owners106[n]
            if code=='RL' and si==1:continue
            rr,tt=tr[code][si];q=s.copy();q.Placement=placement106(rr,tt)*q.Placement;othernames.append(n);others[n]=q;b=q.BoundBox;lo.append([b.XMin,b.YMin,b.ZMin]);hi.append([b.XMax,b.YMax,b.ZMax])
        lo=np.asarray(lo);hi=np.asarray(hi);complete=True
        for n,q in sorted(moved.items(),key=lambda z:(0 if z[0].endswith((':lower',':upper')) else 1,z[0])):
            b=q.BoundBox;ql=np.array([b.XMin,b.YMin,b.ZMin]);qh=np.array([b.XMax,b.YMax,b.ZMax]);g=np.maximum(np.maximum(ql-hi,lo-qh),0);indices=np.flatnonzero(np.sum(g*g,axis=1)<1.25**2)
            for jj in indices:
                k=othernames[int(jj)]
                if (pi,n,k) in pairkeys108:continue
                s=others[k];row=dict(pose=pi,new_actor=n,other=k,other_valid=s.isValid(),source_valid=True)
                if row['other_valid']:
                    gap,w,_=q.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(aa),list(bb)] for aa,bb in w[:1]],status='NEW_SOURCE_MOTION_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_SOURCE_MOTION_ACTUAL_OR_CAPACITY_HOLD')
                    if gap<1e-7:
                        co=q.common(s);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
                else:row['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
                rows108.append(row);pairkeys108.add((pi,n,k))
                if row['status']!='NEW_SOURCE_MOTION_SEPARATED125':first108=row;failednew108=q;failedother108=s;complete=False;break
                if time.monotonic()-tw>seconds:complete=False;break
            if not complete:break
        if complete:doneposes108.add(pi);posecursor108+=1
        if first108 or time.monotonic()-tw>seconds:break
    chunks108.append(dict(start_pose=startpose,end_cursor=posecursor108,new_pairs=len(rows108)-before,new_floor_properties=len(floors108)-beforefloor,operation_seconds=time.monotonic()-tw,process_cpu_seconds=time.process_time()-tc));d=save108();print('SOURCE108_CHUNK',d['status'],len(doneposes108),posecursor108,len(rows108),len(floors108),first108,chunks108[-1],hashlib.sha256(p108.read_bytes()).hexdigest(),flush=True)
save108();changed_motion_chunk108(18)
