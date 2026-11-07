import json,time,hashlib,math,os
tr115=time.monotonic();tc115=time.process_time();r114=json.loads(p114.read_bytes());ge114=r114['geometry'];moving115=dict(restMotion);moving115.update(op106);names115=sorted(moving115);assert len(names115)==129;owners115={n:owners106[n] if n in owners106 else ('RL',1) for n in names115};boxes115={};lofield115=np.array([-137.45,39.25,38.75]);hifield115=np.array([-128.05,77,49.25])
for n,s in moving115.items():
    lo,hi=saved_bounds(s);pts=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]);assert np.isfinite(pts).all();boxes115[n]=pts
mat115=[];poses115=[];actual115=[];first115=None;last115=None
for pi in range(1,36):
    pose=MotionSource31['poses'][pi];tr={code:leg_transforms(axisgroups106[code],pose['legs'][code]['angles_delta_degrees']) for code in axisgroups106};lowers=[]
    for n in names115:
        code,si=owners115[n];rr,tt=tr[code][si];pts=boxes115[n]@rr.T+tt;lo=pts.min(axis=0);hi=pts.max(axis=0);g=np.maximum(np.maximum(lofield115-hi,lo-hifield115),0);lower=float(np.linalg.norm(g));lowers.append(lower)
        if lower<1.25:
            s=moving115[n].copy();s.Placement=placement106(rr,tt)*s.Placement;row=dict(pose=pi,actor=n,new_interface='ONLYNEWbodypassagevsposedactor',bbox_lower_mm=lower,source_valid=s.isValid())
            if row['source_valid']:
                gap,w,_=field114.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(aa),list(bb)] for aa,bb in w[:1]],status='NEW_FIXED_REGION_MOVING_ACTOR_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_FIXED_REGION_MOVING_CAPACITY_HOLD_NOT_WIRECONTACT')
                if gap<1e-7:
                    cc=field114.common(s);row.update(common_valid=cc.isValid(),allocated_common_mm3=cc.Volume if cc.isValid() else None)
            else:row['status']='POSED_SOURCE_INTEGRITY_OPEN_NOT_CONTACT'
            actual115.append(row)
            if row['status']!='NEW_FIXED_REGION_MOVING_ACTOR_SEPARATED125':first115=row;last115=s;break
        if time.monotonic()-tr115>12:first115=dict(pose=pi,status='NEW_INTERFACE_TIME_CURSOR_PENDING_NOT_PASS',actor=n);break
    mat115.append(lowers);poses115.append(dict(pose=pi,actors_processed=len(lowers),minimum_conservative_lower_mm=min(lowers),closest_actor=names115[lowers.index(min(lowers))],complete=len(lowers)==129))
    if first115:break
full115=len(poses115)==35 and all(q['complete'] for q in poses115) and first115 is None
r115=dict(id='day07-SOURCE-left-end-body-passage-new-moving-delta',status='NEW_BODY_PASSAGE_MOVING_INTERFACE_35_RECEIVED_SCOPED' if full115 else 'NEW_BODY_PASSAGE_MOVING_INTERFACE_FIRST_HOLD_OR_PENDING',scope='ONLYnewfixedfield114vs108rest+21Sourceposedactors. Neutralalreadyfull1443bboxproofreused. Allold21bodymatrix/155pairs/root/worldproofsUNTOUCHED. Fullsourcebbox8cornersproperfrozenR/T completeconservativecover; no rigidwirecurveassumption/newIK/oldsourceBRepvaliditytests.',source_scope='day07-SOURCE-left-end-body-passage-new-moving-delta-scope.json',source_scope_sha256=hashlib.sha256((OUT/'day07-SOURCE-left-end-body-passage-new-moving-delta-scope.json').read_bytes()).hexdigest(),required_pose_indices=[1,35],poses=poses115,source_actor_names=names115,source_NEUTRAL_world_bounds_mm={n:saved_bounds(moving115[n]) for n in names115},source_owners={n:list(owners115[n]) for n in names115},lower_bounds_mm_matrix=mat115,actual_new_interface_rows=actual115,received_complete_poses=sum(q['complete'] for q in poses115),conservative_pairs_computed=sum(len(a) for a in mat115),actual_new_pairs=len(actual115),minimum_full_cover_lower_mm=min(min(a) for a in mat115),first_falsifier=first115,bodyfixed_field_ground_lower_over_required36_mm=field114.BoundBox.ZMin-max(p['body_drop_mm'] for p in MotionSource31['poses'][:36])-MotionSource31['ground_rest_z_mm'],external_FREEFLEX_group_R35p1_slack_transport_NOT_qualified=True,operation_seconds=time.monotonic()-tr115,process_cpu_seconds=time.process_time()-tc115,N01_complete=False,selected=False,pid=os.getpid(),session_id=46493)
p115=OUT/'day07-SOURCE-left-end-body-passage-new-moving-delta.json';assert not p115.exists();p115.write_bytes((json.dumps(r115,indent=2)+'\n').encode());print('SOURCE115_NEW_INTERFACE',r115['status'],r115['received_complete_poses'],r115['conservative_pairs_computed'],len(actual115),r115['minimum_full_cover_lower_mm'],first115,r115['operation_seconds'],r115['process_cpu_seconds'],hashlib.sha256(p115.read_bytes()).hexdigest(),flush=True);print('OWNER58_FINAL_IDLE',os.getpid(),'1292/1311/108 pendingnull unsavedfalse',flush=True)
