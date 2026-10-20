"""Persist the whole JPWM proposal; never promote static fit to whole N01.

Inputs are the resident, already-received current scene. Transform both
connector mouths, axes and full-grip boundaries once, not the old R5 frame.
"""
import copy,hashlib,json,time,zipfile
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_usb_service_bight import outer_margin
from plan_feline_jpwm_pair_exit import factory_gate


def source_head_on_free_side(actors):
    """Close the same full T18I on+X, away from G_TAIL; no module shift."""
    import FreeCAD as A
    import Part
    new={n:s.copy() for n,s in actors.items()};band=new['JPWMGrip:source:band'];old=new['JPWMGrip:source:head']
    b=band.BoundBox;assert abs(b.ZLength-2.5)<1e-6
    h=Part.makeBox(4.3,5.3,5.,A.Vector(b.XMax,b.Center.y-2.65,b.Center.z-2.5))
    assert abs(h.Volume-old.Volume)<1e-6
    nylon=band.fuse(h);assert nylon.isValid() and len(nylon.Solids)==1
    new['JPWMGrip:source:head']=h
    return new


def receive_sampled_motion(world,actors,stem,pins):
    """Purchased bodies first; a body hit must not hide behind a wire hit."""
    import FreeCAD as A
    from receive_feline_global_case_candidates import placement
    from feline_fore_power_pair import SolidQueries
    from feline_solid_distance import bbox_lower_bound
    assert {a['pose'] for a in world.motion}==set(range(36)), '36 distinct current poses required'
    tick=time.monotonic();q=SolidQueries();checks={};done=[]
    order=sorted(actors,key=lambda n:(0 if n.endswith(':case') or n=='Ref_Material_JPWM_0_0' else 2 if ':wire:' in n or n.startswith('JPWMSource:') else 1,n))
    dest=OUT/(stem+'.json')
    def save():
        result=dict(status='SOURCE_UNIT_SAMPLE36_MOTION_HOLD' if any(not r['ok'] for r in checks.values()) else 'SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED' if len(done)==len(actors) else 'SOURCE_UNIT_SAMPLE36_MOTION_PARTIAL',
            completed=done,actor_count=len(actors),checks=checks,source_sha256=pins,
            sampled36_NOT_continuous_or_head_tail_motion=True,roots_assembly_and_full123_OPEN=True,
            N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result);return result
    for n in order:
        s=actors[n]
        for a in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*a['bounds'][0],*a['bounds'][1]))>=1.25:continue
            tf=placement(a['r'],a['t']);local=s.copy();local.Placement=tf.inverse()*local.Placement
            gap=q.distance(local,world.rest[a['name']]);key=n+'|motion:'+a['name']+':'+str(a['pose'])
            checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if not checks[key]['ok']:
                result=save();print(result['status'],key,checks[key],result['worker_seconds'],flush=True);return result
        done.append(n)
    result=save();print(result['status'],len(done),len(checks),result['worker_seconds'],flush=True);return result


def rear_gallery_proposal(template,case,fixed,vertical_outboard=False):
    """A single architecture derived from rear plate clearance, not nudges.

    Pair separation is normal to the rear XZ return bends. Keep the inline
    fuse/body/input in place; clock its entire output kit about its own Z
    mouth so the unchanged first9 precedes a front-facing rather than rear-
    facing escape. Roots, exact four routes and assembly remain OPEN.
    """
    import FreeCAD as A
    from receive_feline_global_case_candidates import placement
    rot=np.array([[0,-1,0],[0,0,1],[-1,0,0]]) if vertical_outboard else np.array([[1,0,0],[0,0,1],[0,-1,0]])
    centre=np.array([124.,68.,32.] if vertical_outboard else [124.,50.,20.]);old=np.asarray(list(case.BoundBox.Center))
    tf=placement(rot,(centre-rot@old).tolist());actors={};groups={}
    for n,s in {**template,'Ref_Material_JPWM_0_0':case}.items():
        a=s.copy();a.Placement=tf*a.Placement;actors[n]=a;groups[n]='JPWM'
    angle=-90 if vertical_outboard else 180
    pivot=A.Vector(116,75,69);r=A.Rotation(A.Vector(0,0,1),angle)
    fuse_tf=A.Placement(pivot-r.multVec(pivot),r)
    for n,s in fixed.items():
        if n.startswith('Station:F_PWM_whole:') and (':out_' in n or ':End1:' in n):
            a=s.copy();a.Placement=fuse_tf*a.Placement;actors[n]=a;groups[n]='FPWM_OUT'
    assert len(actors)==16
    return actors,groups,dict(rotation=rot.tolist(),centre_mm=centre.tolist(),old_centre_mm=old.tolist(),
        FPWM_output_clock_axis_mm=[0,0,1],FPWM_output_clock_pivot_mm=list(pivot),FPWM_output_clock_degrees=angle,
        topology='VERTICAL_OUTBOARD_OF_P0_AND_SPLICE_POST' if vertical_outboard else 'REAR_PLATE_RETURN',
        connector_pair_separation_normal_to_rear_XZ_returns=True,roots_factory_paths_and_assembly_OPEN=True)


def screen_rear_gallery(world,fixed,meta,actors,groups,recipe,pins,stem='n01-JPWM-rear-gallery-whole16-static',label='JPWM_REAR_GALLERY_WHOLE16',own_face_mates=()):
    from feline_fore_power_pair import SolidQueries
    from feline_solid_distance import bbox_lower_bound
    from receive_feline_aux_vertical_unit import material_spacing
    from plan_feline_pi_root_access import profile_gap
    tick=time.monotonic();query=SolidQueries();checks={};targets={n:s for n,s in fixed.items() if n not in actors}
    localmeta={n:(dict(kind='wire',wire=n) if n.startswith('JPWMSource:') else
        dict(kind='PETG' if n.endswith(':pad') else 'T18I')) if groups[n]=='JPWM' else meta[n] for n in actors}
    localmeta['Ref_Material_JPWM_0_0']=dict(kind='purchased_case_reservation')
    for n,s in actors.items():
        for b,t in targets.items():
            # First9 on the original vertical mouth is invariant under this
            # clock. Preserve that existing own-case interface, not its root.
            if n.endswith(':out_first_bend') and b=='Station:F_PWM_whole:F_PWM:case':continue
            required=material_spacing(n,localmeta[n],b,meta.get(b,{}))
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=required+1e-6:continue
            a=s;other=t
            if b==world.bus['name']:
                a=s.copy();a.Placement=world.bus['inverse']*a.Placement;other=world.bus['original']
            if (n,b) in own_face_mates:required=0.
            gap=query.distance(a,other);checks[n+'|'+b]=dict(ok=gap>=required-1e-6,gap_mm=gap,minimum_mm=required)
            if (n,b) in own_face_mates:
                common=a.copy().common(other.copy()).Volume
                checks[n+'|'+b].update(common_mm3=common,intended_source_face_only=True,ok=common<1e-5)
        print('REAR_GALLERY_STATIC',n,'queries',len(checks),flush=True)
    names=list(actors)
    for i,n in enumerate(names):
        for b in names[i+1:]:
            if groups[n]==groups[b]:continue # rigid intrinsic kits unchanged
            required=material_spacing(n,localmeta[n],b,localmeta[b])
            if bbox_lower_bound(actors[n].BoundBox,actors[b].BoundBox)>=required+1e-6:continue
            gap=query.distance(actors[n],actors[b]);checks[n+'|'+b]=dict(ok=gap>=required-1e-6,gap_mm=gap,minimum_mm=required)
    failures=[k for k,v in checks.items() if not v['ok']]
    result=dict(status=label+'_STATIC_'+('HOLD' if failures else 'RECEIVED'),actor_count=len(actors),
        recipe=recipe,checks=checks,failures=failures,source_sha256=pins,
        factory_paths_roots_motion_outline_assembly_OPEN=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/(stem+'.json'),result)
    print(result['status'],result['worker_seconds'],failures,flush=True)
    return result


def short_straight_template(ends):
    """Remove the old ATO-avoidance turn when the WHOLE unit leaves that bay.

    Both opposed sides have9mm backed lands; no legacy31mm module detour.
    """
    from plan_feline_n01_shared import pipe
    from plan_feline_u1_common_restraints import open_seat
    actors={};metadata={};lands={}
    rows=[e for e in ends if e.get('group')=='JPWM'];assert len(rows)==4
    for e in rows:
        p=np.asarray(e['point_mm']);d=np.asarray(e['departure_axis']);q=p+9*d
        parts=[dict(kind='line',start=p.tolist(),end=q.tolist())]
        n='JPWMSource:'+e['wire'];actors[n]=pipe(parts,.925);metadata[n]=dict(kind='wire',wire=e['wire'])
        lands[e['id']]=dict(wire=e['wire'],parts=parts,prefix_used_mm=9.,routing_exit_mm=q.tolist(),
            source_mouth_mm=p.tolist(),full_grip_arclength_mm=[0.,9.],R_mm=12.4,
            factory_whole_nominal_mm=225.,factory_whole_min_mm=220.,factory_middle_NOT_received=True)
    for side in ('source','module'):
        rs=[e for e in rows if e['physical_side']==side];p=np.mean([e['point_mm'] for e in rs],axis=0)
        kit=open_seat(p,rs[0]['departure_axis'],[0,1,0],1.075,2.575)
        for k,s in kit.items():
            n='JPWMGrip:'+side+':'+k;actors[n]=s;metadata[n]=dict(kind='PETG' if k=='pad' else 'T18I',side=side)
    return actors,metadata,lands


def direct_outboard_proposal(template,case,ends):
    """Factory geometry derived from2R separation and a straight fuse exit."""
    import FreeCAD as A
    from plan_feline_u1_common_restraints import open_seat
    from plan_feline_n01_shared import pipe
    from receive_feline_global_case_candidates import placement
    fuse=next(e for e in ends if e['id']=='XP02.source/extra/start')
    p=np.asarray(fuse['jacket_routing_point_mm']);assert np.allclose(fuse['jacket_departure_axis'],[0,0,1])
    rot=np.array([[0,-1,0],[0,0,1],[-1,0,0]])
    centre=np.array([p[0]+2*12.4,p[1]+1.5,32.]);old=np.asarray(list(case.BoundBox.Center))
    tf=placement(rot,(centre-rot@old).tolist());actors={};groups={}
    for n,s in {**template,'Ref_Material_JPWM_0_0':case}.items():
        a=s.copy();a.Placement=tf*a.Placement;actors[n]=a;groups[n]='JPWM'
    q=p+[0,0,10.25];prefix='Station:F_PWM_whole:'
    actors[prefix+'F_PWM:out_first_bend']=pipe([dict(kind='line',start=p.tolist(),end=q.tolist())],.925)
    kit=open_seat((p+[0,0,1.25]).tolist(),[0,0,1],[1,0,0],1.075)
    for suffix,shape in zip(('split_cap_exterior','band_budget','head_budget'),(kit['pad'],kit['band'],kit['head'])):
        actors[prefix+'End1:'+suffix]=shape
    for n in actors:
        if n.startswith(prefix):groups[n]='FPWM_OUT'
    retired=[prefix+'F_PWM:out_first_bend',prefix+'F_PWM:out_after_turn_grip',
             *[prefix+'End1:'+k for k in ('split_cap_exterior','band_budget','head_budget')]]
    recipe=dict(rotation=rot.tolist(),centre_mm=centre.tolist(),old_centre_mm=old.tolist(),
        topology='STRAIGHT_FPWM_AND_DIRECT_VERTICAL_OUTBOARD',retired=retired,
        FPWM_new_outlet_mm=q.tolist(),FPWM_new_axis=[0,0,1],FPWM_prefix_mm=10.25,
        current_FPWM_unknown_electrical_pad_NOT_changed=True,
        pair_pitch_mm=3.,red_semicircle_R_mm=12.4,
        X_from_FPWM_outlet_plus_2R=True,root_tools_and_actual_fit_OPEN=True)
    return actors,groups,recipe


def receive(posed,old_ends,lands,rotation,centre,old_centre,static,world,outer,boundaries_only=False):
    tick=time.monotonic();rot=np.asarray(rotation);centre=np.asarray(centre);old_centre=np.asarray(old_centre)
    assert np.allclose(rot@rot.T,np.eye(3)) and np.linalg.det(rot)>.999
    assert len(posed)==11 and all(v['ok'] for v in static['checks'].values())
    pt=lambda p:(centre+rot@(np.asarray(p)-old_centre)).tolist()
    vec=lambda p:(rot@np.asarray(p)).tolist()
    updates={};new_lands={}
    for r in old_ends:
        if r.get('group')!='JPWM':continue
        land=copy.deepcopy(lands[r['id']]);parts=land['parts'];last=parts[-1]
        assert last['kind']=='line' and abs(np.linalg.norm(np.array(last['end'])-last['start'])-9)<1e-6
        tangent=(np.asarray(last['end'])-last['start'])/9
        e=copy.deepcopy(r)
        e.update(point_mm=pt(r['point_mm']) if r['point_mm'] is not None else None,
            departure_axis=vec(r['departure_axis']),routing_exit_mm=pt(land['routing_exit_mm']),
            routing_exit_axis=vec(tangent),jacket_grip9_mm=[pt(last['start']),pt(last['end'])],
            source_prefix_length_mm=land['prefix_used_mm'],grip_length_mm=9,
            prefix_geometry_owner='JPWMSource:'+r['wire'],
            restraint_owner='JPWMGrip:'+r['physical_side']+':pad',
            current_pose_basis='Whole JPWM rigid proposal '+str(centre.tolist())+', not selected native CAD',
            pose_status='PROSPECTIVE_JPWM_STATIC_RECEIVED_FACTORY_ROOT_ASSEMBLY_OPEN',
            routing_boundary_status='PROSPECTIVE_FULL9_OUTLET_ROOT_FACTORY_MIDDLE_OPEN',
            full_middle_route_accepted=False)
        for part in parts:
            for k in ('start','mid','end'):
                if k in part:part[k]=pt(part[k])
        land.update(routing_exit_mm=e['routing_exit_mm'],source_mouth_mm=e['point_mm'])
        updates[e['id']]=e;new_lands[e['id']]=land
    assert len(updates)==4
    gate=factory_gate([updates.get(r['id'],r) for r in old_ends]);assert not gate['hard_holds']
    if boundaries_only:
        return dict(status='PROSPECTIVE_BOUNDARIES_ONLY_NOT_RECEIVED',updates=updates,lands=new_lands,
            necessary_factory_bound=gate,N01_complete=False)
    leg_max=max(a['bounds'][1][2] for a in world.motion)
    leg_gap=min(s.BoundBox.ZMin for s in posed.values())-leg_max
    assert leg_gap>=1.25
    # Separation is positive proof for these36 sampled leg poses only.
    outlines={n:outer_margin(s,outer) for n,s in posed.items()}
    dest=OUT/'n01-JPWM-whole11-posed-plan.json';bundle=dest.with_suffix('.breps.zip')
    rows=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in posed.items():
            assert s.isValid() and s.Solids
            raw=s.exportBrepToString().encode();entry=str(len(rows))+'.brep';z.writestr(entry,raw)
            rows.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(status='JPWM_WHOLE11_STATIC36_RECEIVED_OUTLINE_'+('RECEIVED' if all(r['ok'] for r in outlines.values()) else 'HOLD'),
        geometry=rows,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        rotation=rot.tolist(),centre_mm=centre.tolist(),updates=updates,lands=new_lands,
        necessary_factory_bound=gate,static_receipt='n01-JPWM-whole11-AUX37-static.json',
        sampled_leg36_vertical_separation_mm=leg_gap,sampled_leg36_NOT_continuous_or_head_tail_motion=True,
        outer=outlines,coil_box_NOT_routed_wires=True,
        roots_factory_middles_and_assembly_OPEN=True,selected_native_unchanged=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
            (OUT/'n01-JPWM-whole11-AUX37-static.json',OUT/'n01-JPWM-whole-unit-factory-space-AUX37-proposals.json')},
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(result['status'],result['worker_seconds'],'leg_gap',leg_gap,
          'outline_holds',[n for n,r in outlines.items() if not r['ok']],flush=True)
    return result
