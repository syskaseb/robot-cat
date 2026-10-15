"""Bounded shared source-space allocation against actual retained material.

Reject complete fixed port/fan/arm-entry reservations before solving a wire.
Then verify full candidate curves in coupled source poses. No native mutation,
no change to radius/endpoints, no bbox collision verdict and no W5 acceptance.
"""
import argparse,ast,copy,hashlib,itertools,json,math,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
import FreeCAD as A
import Part
import check_near_axis_hip_sources as C
from plan_axial_hip_sources import ends as old_ends,build as old_build
import antiparallel_axial_flex as Return
from oblique_source_fans import fan
from plan_current_mta_interfaces import line
from plan_continuous_joint_family import self_screen
P=C.P


def ends(row,h):
    a,b,v,m=old_ends(row,h)
    if row.get('flex_construction')=='antiparallel_axial_return':
        a=[x+9*d for x,d in zip(row['fixed_anchor_world_mm'],row['fixed_tangent_world'])]
    return a,b,v,m


def solve_flex(row,h,length,parameter):
    a,b,v,_=ends(row,h)
    if row.get('flex_construction')=='antiparallel_axial_return':
        assert sum(abs(x+y) for x,y in zip(v,row['fixed_tangent_world']))<1e-6
        return Return.build(a,b,row['fixed_tangent_world'],length,parameter)
    return old_build(a,b,v,length,parameter)


def breakouts(row,direction):
    if row.get('flex_construction')!='antiparallel_axial_return':return fan(row,direction)
    rotation=A.Rotation(A.Vector(0,0,-1),A.Vector(*row['fixed_tangent_world']))
    local=list(rotation.inverted().multVec(A.Vector(*direction)))
    canonical=copy.deepcopy(row);canonical['fixed_entry_tilt_degrees']=0
    cores=fan(canonical,local);root=A.Vector(*row['fixed_anchor_world_mm'])
    for core in cores:
        for key in ('parts','after_5mm'):
            for part in core[key]:
                for field in ('start','mid','end'):
                    if field in part:part[field]=list(root+rotation.multVec(A.Vector(*part[field])-root))
    return cores


def run(resume_commit=None,rear_upper_corridor=False,rear_axial_return=False):
    tick=time.monotonic();until=tick+25*60
    seedfile=P.OUT/'body-axial-hip-plan.json';seed=json.loads(seedfile.read_text())
    for n,h in seed['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,old,pins,family,axes,own,bare,files,subsets=C.prepare_context(seed)
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'axial-layout-search-pairs.json',bounds.near)
    selected=[];attempts=[];errors=[];checks=0;last_save=time.monotonic();extra=[];resume_proof=None
    if resume_commit:
        relative=(P.OUT/'body-axial-layout-search.json').relative_to(P.ROOT).as_posix()
        previous_bytes=subprocess.check_output(['git','show',resume_commit+':'+relative],cwd=P.ROOT)
        previous=json.loads(previous_bytes)
        script=Path(__file__).relative_to(P.ROOT).as_posix()
        old_code=subprocess.check_output(['git','show',resume_commit+':'+script],cwd=P.ROOT).decode()
        assert hashlib.sha256(old_code.encode()).hexdigest()==previous['source_sha256'][script], 'Resume script pin mismatch'
        for name,digest in previous['source_sha256'].items():
            if name!=script:assert P.SHA(P.ROOT/name)==digest,('Resume input changed',name)
        def evaluators(source):
            return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name in ('hit','coupled_wire','clear_world','profile_clear')}
        assert evaluators(old_code)==evaluators(Path(__file__).read_text()),'Resume evaluator changed'
        selected=copy.deepcopy(previous['hips'])
        resume_proof=dict(commit=resume_commit,report_sha256=hashlib.sha256(previous_bytes).hexdigest(),input_pins_verified=True,evaluator_AST_verified=True,retained_looms=[r['loom'] for r in selected])
    old_codes={r['loom']:r['cad_code'] for r in family['hips']}
    report=P.OUT/'body-axial-layout-search.json';resultfile=P.OUT/'body-axial-layout-chosen.json'
    def save():
        result=dict(status='FOUR_SOURCE_ALLOCATIONS_SAMPLED_CLEAR_ROOT_ARMS_NATIVE_OPEN' if len(selected)==4 else 'PARTIAL_BOUNDED_AXIAL_SOURCE_ALLOCATION',
            hips=selected,rejected=[],attempts=attempts,attempt_errors=errors,checks=checks,resume_proof=resume_proof,
            retained_subset_receipts=subsets,material_instances=len(targets),body_routes=20,
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in [seedfile,*files,Path(__file__),Path(C.__file__),Path(Return.__file__),Path(__file__).with_name('spatial_down_axial_flex.py')]}},
            scope='Chosen source fixedport+threecorefan+armseed and complete freewire/factory in3coupledHip samples. Otherlegs independent; retained material and8otherfamilies/20bodyroutes present. Complete8rootedarms/native/36bodycores/stock/wholeW5 OPEN.',
            candidate_count=len(attempts),worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            continuous_sweep_verified=False,errors=[])
        for path in (report,*([resultfile] if len(selected)==4 else [])):
            tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(path)
        cache.save();return result
    def alive():
        return time.monotonic()<until and datetime.now(timezone.utc)<datetime(2026,10,15,7,tzinfo=timezone.utc)
    def hit(a,b,rs=0,rt=0):
        nonlocal checks,last_save
        if not bounds.near(a,b,rs+rt+.0001):return False
        checks+=1
        try:
            gap,vol=cache.check(a,b,rs,rt)
            found=vol>1e-5 or ((rs or rt) and gap<rs+rt-1e-6)
        except (AssertionError,ValueError) as e:
            errors.append(str(e));found=True
        if time.monotonic()-last_save>20:
            save();last_save=time.monotonic()
        return found
    def coupled_wire(name,code,h):
        if not name.startswith('leg/'):return True
        _,loom,angle,*_=name.split('/')
        return old_codes[loom]!=code or int(angle)==h
    def clear_world(shape,radius=0,owner=None):
        code,h=owner or (None,0)
        for name,target in targets.items():
            if code is not None and not C.same_leg_pose(own.get(name),code,h):continue
            if hit(shape,target,radius):return dict(kind='retained_material',target=name)
        for name,(wire,r) in old.items():
            if code is not None and not coupled_wire(name,code,h):continue
            if hit(shape,wire,radius,r+.25 if not radius else r):return dict(kind='retained_wire',target=name)
        for name,other,r,other_owner in extra:
            if code is not None and not C.same_leg_pose(other_owner,code,h):continue
            if hit(shape,other,radius,r):return dict(kind='chosen_source',target=name)
        return None
    def profile_clear(row,profile,moving=False):
        code=row['cad_code']
        for h in C.ANGLES if moving else (0,):
            T=C.transform(axes,code,h,0,'Hip') if moving else None
            for kind in ('body','band'):
                shape=C.moved(profile[kind],T) if moving else profile[kind]
                witness=clear_world(shape,owner=(code,h) if moving else None)
                if witness:return dict(profile=kind,hip=h,**witness)
        goal=profile['arrival_world_mm'];box=P.box([goal[i]-d for i,d in enumerate((2,3,2))]+[goal[i]+d for i,d in enumerate((2,3,2))])
        if hit(box,profile['band']):return dict(kind='arm_seed_band_contact')
        if box.common(profile['body']).Volume<1:return dict(kind='arm_seed_not_joined')
        for h in C.ANGLES if moving else (0,):
            shape=C.moved(box,C.transform(axes,code,h,0,'Hip')) if moving else box
            witness=clear_world(shape,owner=(code,h) if moving else None)
            if witness:return dict(profile='arm_seed',hip=h,**witness)
        return None
    for saved in selected:
        loom,code=saved['loom'],saved['cad_code']
        for pose in saved['poses']:
            h=pose['angle']
            if h in C.ANGLES:
                extra.append((loom+'/'+str(h),P.wire(pose['parts']+C.B.moved_parts(saved['source_parts'],saved['source'],h,0,axes)),3,(code,h)))
        for name,is_moving in (('Fixed',False),('Moving',True)):
            _,profile=C.make_port(saved,is_moving)
            for kind in ('body','band'):
                for h in C.ANGLES if is_moving else (0,):
                    shape=C.moved(profile[kind],C.transform(axes,code,h,0,'Hip')) if is_moving else profile[kind]
                    extra.append((loom+'/'+name+'/'+kind,shape,0,(code,h) if is_moving else None))
        for core in saved['source_fans']:extra.append((loom+'/core/'+core['core'],P.wire(core['parts']),1,None))
    try:
        for original in seed['hips']:
            if original['loom'] in {r['loom'] for r in selected}:continue
            if not alive():break
            row=copy.deepcopy(original);side=1 if row['fixed_anchor_world_mm'][1]>0 else -1
            front=row['physical_leg'].startswith('Front');code=row['cad_code'];loom=row['loom']
            return_mode=rear_axial_return and not front
            if return_mode:row.update(fixed_tangent_world=[1,0,0],flex_construction='antiparallel_axial_return')
            _,moving=C.make_port(row,True)
            witness=profile_clear(row,moving,True)
            if witness:
                attempts.append(dict(loom=loom,phase='moving_profile_and_seed',witness=witness));save()
                print('source moving entry blocked',loom,witness,flush=True);continue
            chosen=None
            # Centreline and shallow cross-centre roots change the loop corridor,
            # unlike repeating longer slack in the rejected same-side corridor.
            heights=(105.,80.,130.,60.) if return_mode else (60.,80.,105.,40.) if rear_upper_corridor and not front else (-16.,-24.,-8.,-32.)
            roots=itertools.product((0.,25.,50.) if return_mode else (0.,25.,-10.,15.,50.,65.,35.5) if rear_upper_corridor else (0.,-10.,15.,35.5,50.,65.,25.),heights,(-115.5,-105.,-95.) if front else (145.,130.,160.,170.) if return_mode else (170.,185.,145.,160.))
            for y,z,x in roots:
                if not alive():break
                row['fixed_anchor_world_mm']=[x,side*y,z]
                for normal in ([0,1,0],[0,-1,0],[0,0,1],[0,0,-1]) if return_mode else ([1,0,0],[-1,0,0]) if front else ([-1,0,0],[1,0,0]):
                    if not alive():break
                    row['fixed_port_normal_world']=normal
                    _,fixed=C.make_port(row,False)
                    b=fixed['band'].BoundBox
                    if b.XMin<-120 or b.XMax>205 or b.YMin<-100 or b.YMax>100:continue
                    attempt=dict(loom=loom,root=list(row['fixed_anchor_world_mm']),normal=normal,phase='fixed_profile_and_seed');attempts.append(attempt)
                    witness=profile_clear(row,fixed)
                    if witness:attempt['witness']=witness;save();continue
                    candidate_fans=[]
                    preferred=[-1,0,0] if front else [1,0,0]
                    for direction in ([0,side,0],[0,-side,0],[0,0,1],[0,0,-1]) if return_mode else (preferred,[0,side,0],[0,-side,0],[-v for v in preferred]):
                        cores=breakouts(row,direction);failure=None
                        for core in cores:
                            wire=P.wire(core['parts']);failure=clear_world(wire,1.25)
                            if failure:break
                            if any(hit(wire,fixed[k],1.25) for k in ('body','band')):
                                failure=dict(kind='fan_own_fixed_profile');break
                        if not failure:candidate_fans.append((direction,cores))
                    if not candidate_fans:attempt.update(phase='three_core_fans',witness=failure);save();continue
                    attempt['phase']='constant_length_full_source'
                    for beta in ((0,.5,-.5) if return_mode else (-60,-45,-30,-15,0,15,30,45,60) if rear_upper_corridor and not front else (60,45,30,15,0,-15,-30,-45,-60)):
                        if not alive():break
                        for length in range(125,351,5):
                            if not alive():break
                            try:
                                if any(solve_flex(row,h,length+d,beta) is None for h in (0,-15,15) for d in (-5,0,5)):continue
                            except AssertionError:continue
                            poses=[];curves=[];failure=None
                            # Complete cheap31-pose self/length/ground screening
                            # BEFORE the first world-material query. An invalid
                            # shortest loop is not a rejected spatial corridor.
                            for h in (0,-15,15,*[a for a in range(-15,16) if a not in (0,-15,15)]):
                                a,b,v,m=ends(row,h);middle=solve_flex(row,h,length,beta)
                                if middle is None or any(solve_flex(row,h,length+d,beta) is None for d in (-5,5)):failure=dict(kind='length_margin',h=h);break
                                parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,m)]
                                full=parts+C.B.moved_parts(row['source_parts'],row['source'],h,0,axes)
                                if self_screen(full) is not None:failure=dict(kind='self_contact',h=h);break
                                wire=P.wire(full)
                                if wire.BoundBox.ZMin-3+168.319012764516<5:failure=dict(kind='ground_margin',h=h);break
                                poses.append(dict(angle=h,parts=parts))
                            if failure:
                                attempt['last_math_failure']=failure
                                continue
                            for pose in poses:
                                h=pose['angle']
                                if h in C.ANGLES:
                                    full=pose['parts']+C.B.moved_parts(row['source_parts'],row['source'],h,0,axes)
                                    wire=P.wire(full)
                                    failure=clear_world(wire,3.25,(code,h))
                                    if failure:failure={**failure,'h':h};break
                                    for name,profile in (('fixed',fixed),('moving',moving)):
                                        for kind in ('body','band'):
                                            shape=C.moved(profile[kind],C.transform(axes,code,h,0,'Hip')) if name=='moving' else profile[kind]
                                            if hit(wire,shape,3 if kind=='band' else 3.25):failure=dict(kind='own_'+name+'_'+kind,h=h);break
                                        if failure:break
                                    if failure:break
                                    curves.append((h,wire))
                            if failure:
                                attempt['last_curve_failure']=failure
                                break  # First robust compact curve failed: change geometry, not slack.
                            for direction,cores in candidate_fans:
                                if any(hit(P.wire(c['after_5mm']),w,1.25,3) for c in cores for _,w in curves):continue
                                poses.sort(key=lambda p:p['angle']);row.update(poses=poses,flex_length_mm=length,guide_mm=length+18,
                                    bridge_beta_degrees=None if return_mode else beta,bridge_cosine=beta if return_mode else None,source_fan_direction=direction,source_fans=cores,
                                    fixed_port_recipe=fixed['recipe'],moving_port_recipe=moving['recipe'],
                                    fixed_port_arrival_world_mm=fixed['arrival_world_mm'],moving_port_arrival_world_mm=moving['arrival_world_mm'],
                                    fixed_lands=[dict(id=loom+'/Hip/Fixed',parts=[poses[15]['parts'][0]],owner='Body')],
                                    moving_lands=[dict(id=loom+'/Hip/Moving',parts=[poses[15]['parts'][-1]],owner='Hip')])
                                chosen=copy.deepcopy(row);break
                            if chosen:break
                        if chosen:break
                    if chosen:
                        attempt['phase']='SCOPED_SOURCE_ALLOCATED';attempt['beta']=beta;attempt['freeflex_mm']=length;break
                    save()
                if chosen:break
            if chosen:
                selected.append(chosen)
                for h,w in curves:extra.append((loom+'/'+str(h),w,3,(code,h)))
                for name,profile in (('Fixed',fixed),('Moving',moving)):
                    for kind in ('body','band'):
                        for h in C.ANGLES if name=='Moving' else (0,):
                            shape=C.moved(profile[kind],C.transform(axes,code,h,0,'Hip')) if name=='Moving' else profile[kind]
                            extra.append((loom+'/'+name+'/'+kind,shape,0,(code,h) if name=='Moving' else None))
                for core in chosen['source_fans']:extra.append((loom+'/core/'+core['core'],P.wire(core['parts']),1,None))
                print('received source allocation',loom,'root',chosen['fixed_anchor_world_mm'],'freeflex',chosen['flex_length_mm'],'checks',checks,flush=True)
            save()
            if not chosen:print('source allocation open',loom,'attempts',len(attempts),'checks',checks,flush=True)
    finally:
        result=save();print(json.dumps({k:result[k] for k in ('status','candidate_count','checks','worker_seconds')}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume-commit');parser.add_argument('--rear-upper-corridor',action='store_true');parser.add_argument('--rear-axial-return',action='store_true')
    args=parser.parse_args();run(args.resume_commit,args.rear_upper_corridor,args.rear_axial_return)
