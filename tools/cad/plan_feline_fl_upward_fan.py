"""Whole FL9 body-side escape; preserve all fixed/moving bookkeeping seams.

Increasing radii with initial Z diverge instead of merging three vertical
outlets. This is not a new connector, full moving loom, or finished restraint.
"""
import copy,json,math,time,hashlib,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_n01_shared import pipe
from feline_source_saddles import segment
from feline_atomic_save import save_json
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_aux_vertical_unit import material_spacing
from plan_feline_usb_service_bight import outer_margin
from plan_feline_pi_root_access import profile_gap


def construct(ends,downward=False,lateral=False):
    actors={};metadata={};updates={};routes={}
    for e in ends:
        if e['group']!='NineWireCuffFL':continue
        p=np.asarray(e['point_mm'],float);assert np.allclose(e['departure_axis'],[1,0,0]) and abs(p[0]+75.5)<1e-6
        oldp=p.copy()
        if lateral:
            # BOTH bank case and its lower bed constrain this shared route.
            # Change plane: inboard XY, never another lower-Z trial.
            required=19.6+1.55+.15+2+1.25
            xmax=-62-math.sqrt(required**2-(39.25-34)**2)
            p[0]=math.floor(xmax)-1
        elif downward:
            # Full common envelope: Rmax19.6 + jacket1.55 + fit.15 +
            # PETGwall2 + foreign1.25. Solve left/bottom bank corner first.
            required=19.6+1.55+.15+2+1.25
            xmax=-54.5-math.sqrt(required**2-(55-54)**2)
            p[0]=math.floor(xmax*2)/2
        R=p[1]-34 if lateral else p[2]-54 if downward else 12.4+p[2]-66.4
        assert R>=12.4-1e-6
        point=lambda a:(p+R*np.array([math.sin(a),-(1-math.cos(a)) if lateral else 0,0 if lateral else (-1 if downward else 1)*(1-math.cos(a))])).tolist()
        row=dict(kind='arc',start=point(0),mid=point(math.pi/4),end=point(math.pi/2),radius_mm=R)
        n='CuffPrefix:'+e['id'];actors[n]=pipe([row],1.55)
        metadata[n]=dict(kind='wire',wire=e['wire'],nominal_profile_radius_mm=1.55,capacity_NOT_supplier_profile=True)
        end=copy.deepcopy(e);end.update(point_mm=p.tolist(),routing_exit_mm=row['end'],routing_exit_axis=[0,-1,0] if lateral else [0,0,-1 if downward else 1],
            source_prefix_length_mm=math.pi*R/2,grip_length_mm=9,
            full_grip_arclength_mm=[math.pi*R/2-9,math.pi*R/2],
            fixed_kinematic_seam_mm=p.tolist(),previous_fixed_kinematic_seam_mm=oldp.tolist(),
            fixed_and_moving_seams_NOT_moved=not (downward or lateral),moving_seam_unchanged=True,
            routing_boundary_status='PROSPECTIVE_FL9_UPWARD_PREFIX_RESTRAINT_OPEN',
            full_middle_route_accepted=False)
        updates[e['id']]=end;routes[e['id']]=row
    assert len(actors)==9
    return actors,metadata,dict(updates=updates,routes=routes,
        retired=[*actors,'BundleCuff:FL','BundleTie:FL','BundleTie:FLHead'],
        fixed_and_moving_seams_unchanged=not (downward or lateral),full_moving_flex_NOT_qualified=True,
        topology='INBOARD_XY_OUTSIDE_BANK_AND_BED' if lateral else 'DOWNWARD_CONCENTRIC_COMMON_54_REJECTED' if downward else 'UPWARD_DIVERGING_REJECTED',
        whole_common_restraint_root_and_assembly_OPEN=True,N01_complete=False,physical_pass=False)


def receive(world,fixed,meta,pins,docs,ends,downward=False,additional_retired=(),additional_fixed=None,lateral=False):
    tick=time.monotonic();actors,md,plan=construct(ends,downward,lateral);checks={};q=SolidQueries()
    plan['retired'].extend(additional_retired)
    scene={**{n:s for n,s in fixed.items() if n not in plan['retired']},**(additional_fixed or {}),**actors}
    allmeta={**meta,**md}
    for n,s in actors.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for b,t in scene.items():
            if b==n or b in actors and b>=n:continue
            limit=material_spacing(n,md[n],b,allmeta.get(b,{}))
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            a=s;other=t
            if b==world.bus['name']:a=s.copy();a.Placement=world.bus['inverse']*a.Placement;other=world.bus['original']
            if not other.Solids:row=profile_gap(a,other,allmeta.get(b,{}).get('nominal_profile_radius_mm'),limit)
            else:
                gap=q.distance(a,other);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
            checks[n+'|'+b]=row
    dest=OUT/('n01-FL9-inboard-whole-plan.json' if lateral else 'n01-FL9-downward-concentric-whole-plan.json' if downward else 'n01-FL9-upward-whole-plan.json');bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            assert s.isValid() and len(s.Solids)==1
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(md[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    plan.update(status='FL9_WHOLE_'+plan['topology']+'_STATIC_'+('HOLD' if any(not r['ok'] for r in checks.values()) else 'RECEIVED_RESTRAINT_OPEN'),
        checks=checks,failures=[k for k,v in checks.items() if not v['ok']],geometry=geometry,
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),source_sha256=pins,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,plan);print(plan['status'],len(checks),plan['failures'],plan['worker_seconds'],flush=True)
    return actors,md,plan


def receive_fhy_closure_delta(world,fixed,metadata,docs,actors,old_static,new_head,tf,source_end,pins):
    """After2 blocked clocks change closure SIDE, not another scalar angle.

    Full6mm inherited budget is larger than the selected T18I head. Reuse
    the17 unchanged actual pairs, but check this whole head in all neighbors.
    """
    from receive_feline_jpwm_whole_pose import receive_sampled_motion
    tick=time.monotonic();name='ForeFHAC:out:factory:head_budget'
    expected=name+'|W066/retained0/start:0:band_budget'
    assert old_static['failures']==[expected]
    assert abs(actors[name].Volume-new_head.Volume)<1e-5
    new=dict(actors);new[name]=new_head
    checks={k:v for k,v in old_static['checks'].items() if not k.startswith(name+'|')}
    q=SolidQueries();band='ForeFHAC:out:factory:band_budget'
    for b,t in {**fixed,**new}.items():
        if b==name:continue
        limit=0. if b==band else .2 if b=='ForeFHAC:out:factory:saddle' else 1.25
        if bbox_lower_bound(new_head.BoundBox,t.BoundBox)>limit+1e-6:continue
        gap=q.distance(new_head,t);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
        if b==band:
            row['common_mm3']=new_head.common(t).Volume;row['ok'] &= row['common_mm3']<1e-5
            assert gap<1e-6
        checks[name+'|'+b]=row
    checks[name+'|outer']=outer_margin(new_head,docs['outer'])
    motion=receive_sampled_motion(world,new,'n01-FHY-diagonal-side-head-motion',pins)
    dest=OUT/'n01-FHY-diagonal-side-head-source.json';bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in new.items():
            assert s.isValid() and s.Solids
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(metadata[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    end=copy.deepcopy(source_end)
    for key in ('factory_end_mm','routing_exit_mm'):
        if end.get(key) is not None:end[key]=list(tf.multVec(A.Vector(*end[key])))
    end['custom_grip9_mm']=[list(tf.multVec(A.Vector(*p))) for p in end['custom_grip9_mm']]
    end['routing_exit_axis']=list(tf.Rotation.multVec(A.Vector(*end['routing_exit_axis'])))
    end.update(routing_boundary_status='PROSPECTIVE_FHY_WHOLE_OUTPUT_SIDE_HEAD_ROOT_OPEN',full_middle_route_accepted=False)
    result=dict(status='FHY_DIAGONAL_SIDE_HEAD_STATIC36_RECEIVED_ROOT_OPEN' if all(r['ok'] for r in checks.values()) and motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED' else 'FHY_DIAGONAL_SIDE_HEAD_HOLD',
        geometry=geometry,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        checks=checks,failures=[k for k,v in checks.items() if not v['ok']],updates={end['id']:end},
        old_clock45_head_failure={expected:old_static['checks'][expected]},changed_whole_head_only=True,
        full_head_volume_mm3=new_head.Volume,unchanged_pair_distances_reused=len(checks)-sum(k.startswith(name+'|') for k in checks),
        retired=list(new),source_sha256=pins,factory97_sleeve20_custom26_lengths_preserved=True,
        motion_receipt='n01-FHY-diagonal-side-head-motion.json',root_case_floor_and_full123_OPEN=True,
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['failures'],result['worker_seconds'],flush=True)
    return new,result
