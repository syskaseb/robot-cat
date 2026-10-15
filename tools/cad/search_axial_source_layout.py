"""Bounded shared source-space allocation against actual retained material.

Reject complete fixed port/fan/arm-entry reservations before solving a wire.
Then verify full candidate curves in coupled source poses. No native mutation,
no change to radius/endpoints, no bbox collision verdict and no W5 acceptance.
"""
import copy,itertools,json,math,time
from datetime import datetime,timezone
from pathlib import Path
import FreeCAD as A
import Part
import check_near_axis_hip_sources as C
from plan_axial_hip_sources import ends,build
from oblique_source_fans import fan
from plan_current_mta_interfaces import line
from plan_continuous_joint_family import self_screen
P=C.P


def run():
    tick=time.monotonic();until=tick+25*60
    seedfile=P.OUT/'body-axial-hip-plan.json';seed=json.loads(seedfile.read_text())
    for n,h in seed['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,old,pins,family,axes,own,bare,files,subsets=C.prepare_context(seed)
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'axial-layout-search-pairs.json',bounds.near)
    selected=[];attempts=[];errors=[];checks=0;last_save=time.monotonic();extra=[]
    old_codes={r['loom']:r['cad_code'] for r in family['hips']}
    report=P.OUT/'body-axial-layout-search.json';resultfile=P.OUT/'body-axial-layout-chosen.json'
    def save():
        result=dict(status='FOUR_SOURCE_ALLOCATIONS_SAMPLED_CLEAR_ROOT_ARMS_NATIVE_OPEN' if len(selected)==4 else 'PARTIAL_BOUNDED_AXIAL_SOURCE_ALLOCATION',
            hips=selected,rejected=[],attempts=attempts,attempt_errors=errors,checks=checks,
            retained_subset_receipts=subsets,material_instances=len(targets),body_routes=20,
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in [seedfile,*files,Path(__file__),Path(C.__file__),Path(__file__).with_name('spatial_down_axial_flex.py')]}},
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
    try:
        for original in seed['hips']:
            if not alive():break
            row=copy.deepcopy(original);side=1 if row['fixed_anchor_world_mm'][1]>0 else -1
            front=row['physical_leg'].startswith('Front');code=row['cad_code'];loom=row['loom']
            _,moving=C.make_port(row,True)
            witness=profile_clear(row,moving,True)
            if witness:
                attempts.append(dict(loom=loom,phase='moving_profile_and_seed',witness=witness));save()
                print('source moving entry blocked',loom,witness,flush=True);continue
            chosen=None
            roots=itertools.product((25.,15.,35.5,50.,65.),(-16.,-24.,-8.,-32.),(-115.5,-105.,-95.) if front else (160.,170.,145.,185.))
            for y,z,x in roots:
                if not alive():break
                row['fixed_anchor_world_mm']=[x,side*y,z]
                for normal in ([1,0,0],[-1,0,0]) if front else ([-1,0,0],[1,0,0]):
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
                    for direction in (preferred,[0,side,0],[0,-side,0],[-v for v in preferred]):
                        cores=fan(row,direction);failure=None
                        for core in cores:
                            wire=P.wire(core['parts']);failure=clear_world(wire,1.25)
                            if failure:break
                            if any(hit(wire,fixed[k],1.25) for k in ('body','band')):
                                failure=dict(kind='fan_own_fixed_profile');break
                        if not failure:candidate_fans.append((direction,cores))
                    if not candidate_fans:attempt.update(phase='three_core_fans',witness=failure);save();continue
                    attempt['phase']='constant_length_full_source'
                    for beta in (60,45,30,15,0,-15,-30,-45,-60):
                        if not alive():break
                        for length in range(125,351,5):
                            if not alive():break
                            try:
                                if any(build(*ends(row,h)[:3],length+d,beta) is None for h in (0,-15,15) for d in (-5,0,5)):continue
                            except AssertionError:continue
                            poses=[];curves=[];failure=None
                            for h in (0,-15,15,*[a for a in range(-15,16) if a not in (0,-15,15)]):
                                a,b,v,m=ends(row,h);middle=build(a,b,v,length,beta)
                                if middle is None or any(build(a,b,v,length+d,beta) is None for d in (-5,5)):failure=dict(kind='length_margin',h=h);break
                                parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,m)]
                                full=parts+C.B.moved_parts(row['source_parts'],row['source'],h,0,axes)
                                if self_screen(full) is not None:failure=dict(kind='self_contact',h=h);break
                                wire=P.wire(full)
                                if wire.BoundBox.ZMin-3+168.319012764516<5:failure=dict(kind='ground_margin',h=h);break
                                if h in C.ANGLES:
                                    failure=clear_world(wire,3.25,(code,h))
                                    if failure:failure={**failure,'h':h};break
                                    for name,profile in (('fixed',fixed),('moving',moving)):
                                        for kind in ('body','band'):
                                            shape=C.moved(profile[kind],C.transform(axes,code,h,0,'Hip')) if name=='moving' else profile[kind]
                                            if hit(wire,shape,3 if kind=='band' else 3.25):failure=dict(kind='own_'+name+'_'+kind,h=h);break
                                        if failure:break
                                    if failure:break
                                    curves.append((h,wire))
                                poses.append(dict(angle=h,parts=parts))
                            if failure:attempt['last_curve_failure']=failure;continue
                            for direction,cores in candidate_fans:
                                if any(hit(P.wire(c['after_5mm']),w,1.25,3) for c in cores for _,w in curves):continue
                                poses.sort(key=lambda p:p['angle']);row.update(poses=poses,flex_length_mm=length,guide_mm=length+18,
                                    bridge_beta_degrees=beta,source_fan_direction=direction,source_fans=cores,
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


if __name__=='__main__':run()
