"""Preserve all178 end identities in ONE candidate; no route/fit acceptance.

Transforms source-pinned current points, reuses24 complete bank lands and
allocates36 distinct leg wires plus the existing solder splice. Never invent
missing departure axes or silently convert allocation into full wiring.
"""
import hashlib
import json
import math
import sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'
I=[[1,0,0],[0,1,0],[0,0,1]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mv(m,v):return [sum(a*b for a,b in zip(row,v)) for row in m]
def plus(a,b):return [x+y for x,y in zip(a,b)]
def minus(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def unit(v):
    length=math.sqrt(dot(v,v));assert length>1e-9
    return [x/length for x in v]
def tangent(part,at_start):
    a,b=part['start'],part['end']
    if part['kind']=='line':return unit(minus(b,a))
    mid=part['mid'];u,v=minus(mid,a),minus(b,a);n=cross(u,v);nn=dot(n,n);assert nn>1e-12
    c=plus(a,[(dot(u,u)*x+dot(v,v)*y)/(2*nn) for x,y in zip(cross(v,n),cross(n,u))])
    t=unit(cross(n,minus(a if at_start else b,c)))
    toward=minus(mid,a) if at_start else minus(b,mid)
    return t if dot(t,toward)>0 else [-x for x in t]
def curvature_chord_bound(a,start_direction,b,end_direction,R):
    """Necessary length bound, valid even when it does not construct a path.

    Direction angular speed is at most1/R. For the firstR*alpha length,
    angular distance to chord is >=alpha-s/R; integrate1-cos(angle).
    The analogous final interval is disjoint when chord>=R*(alpha+beta),
    since actual curve length>=chord. Otherwise use the plain chord bound.
    """
    assert R>0
    delta=minus(b,a);chord=math.sqrt(dot(delta,delta))
    if chord<1e-9:return dict(chord_mm=chord,penalty_mm=0,intervals_disjoint=False,lower_bound_mm=chord)
    u=unit(delta);d,e=unit(start_direction),unit(end_direction)
    alpha=math.acos(max(-1,min(1,dot(d,u))));beta=math.acos(max(-1,min(1,dot(e,u))))
    valid=chord>=R*(alpha+beta)
    penalty=R*(alpha-math.sin(alpha)+beta-math.sin(beta)) if valid else 0
    return dict(chord_mm=chord,penalty_mm=penalty,intervals_disjoint=valid,lower_bound_mm=chord+penalty)


def main():
    dest=OUT/'n01-complete-end-allocation.json';refresh='--reconcile-motion-frames' in sys.argv
    assert refresh or not dest.exists(),'Receive existing allocation'
    prior=json.loads(dest.read_text()) if refresh else None
    prior_hash=sha(dest) if refresh else None
    names=['endpoint-current-receivers.json','prefix-allocation.json','n01-module-plan-r5.json',
        'n01-shared-preflight-r5.json','n01-compact-bank-plan-r2.json',
        'n01-compact-bank-preflight-r2.json','n01-common-backbone-preflight-r4.json']
    paths=[OUT/n for n in names]
    old,pre,plan,rear,bank,bankproof,common=[json.loads(p.read_text()) for p in paths]
    assert common['status']!='RUNNING'
    assert len(common['allocations'])==38
    new={r['id']:r for r in common['allocations']};bg={r['id']:r for r in bankproof['grip_allocations']}
    specs={r['id']:r for r in pre['specifications']};roles={g['role']:g for g in plan['groups']}
    harnessfile=OUT.parent/'body-harness-checkpoint/harness-interfaces-plan.json'
    stationfile=OUT.parent/'body-harness-checkpoint/leg-stations-plan.json'
    harness=json.loads(harnessfile.read_text());stations=json.loads(stationfile.read_text())['stations']
    canonical={(r['id'],e['role']):e for r in harness['body_conductors'] for e in r['current_ends']}
    aliases={'P_FRONT':'P_FRONT_new','P_SYS':'P_SYS_new','G1':'G1_CP2','G2':'G2_CP2'}
    nominal_axes={'WAGO:'+aliases.get(k,k):v['entry_axis'] for k,v in stations.items()}
    # Same physical WAGO common rail can have reassigned circuit cavities.
    # Reuse its explicit casing entry axis, not the old wire-to-port identity.
    canonical_axes=defaultdict(list);axis_conflicts=[]
    for data in canonical.values():
        base=data['role'].split('.')[0];key='WAGO:'+aliases.get(base,base)
        if key in roles and data.get('departure') is not None:
            canonical_axes[key].append(data['departure'])
    for key,ds in canonical_axes.items():
        if key in nominal_axes:
            if any(math.dist(nominal_axes[key],d)>1e-6 for d in ds):
                axis_conflicts.append(dict(group=key,action='Current explicit station recipe has priority; old generic departure is NOT silently reused'))
        elif all(math.dist(ds[0],d)<1e-6 for d in ds):nominal_axes[key]=ds[0]
        else:axis_conflicts.append(dict(group=key,action='Conflicting generic axes remain unallocated'))
    paths.extend((harnessfile,stationfile))
    retainedfile=OUT.parent/'body-harness-checkpoint/current-retained-endpoints.json'
    retained={r['wire']:r for r in json.loads(retainedfile.read_text())['rows']};paths.append(retainedfile)
    recipe_cache={};tangent_transfers=[]
    extra={'JPWM':[-90,44,30],'W041_Joint':[0,15,3],'W042_Joint':[0,-15,3]}
    rows=[]
    for e in old['endpoints']:
        n=e['id'];group=e['group'];spec=specs.get(n);p=e['candidate_point_mm'];d=spec['direction'] if spec else None
        direction_already_R5=False
        if spec and group in plan['motion_receiving_changes']:
            # Prefix recipes predate FelineInteriorMotion. Points below already
            # come from that current native; direction must independently receive
            # the motion-receiver rotation ONCE, before the R5 relative rotation.
            d=mv(plan['motion_receiving_changes'][group]['rotation_rows'],d)
        if d is None and group in roles:
            data=canonical.get((e['wire'],e['role']),{})
            source_axis=nominal_axes.get(group,data.get('departure'))
            if source_axis is not None:
                d=mv(roles[group]['rotation_rows'],source_axis);direction_already_R5=True
            elif e['role'].endswith('.factory') and 'factory_exit_axis' in roles[group]:
                d=roles[group]['factory_exit_axis'];direction_already_R5=True
            elif e['wire'] in retained:
                rf=retainedfile.parent/retained[e['wire']]['recipe_file']
                if rf not in recipe_cache:
                    recipe_cache[rf]=json.loads(rf.read_text());paths.append(rf)
                key=e['wire']
                if key=='W076':key='W076_FACTORY' if '/retained0/' in n else 'W076_EXTENSION'
                parts=recipe_cache[rf]['routes'][key]['parts'];start=n.endswith('/start')
                part=parts[0 if start else -1];old_point=part['start' if start else 'end']
                assert math.dist(old_point,e['old_point_mm'])<.01,(n,'Old GUIDE frame mismatch; no axis inferred')
                td=tangent(part,start)
                if not start:td=[-x for x in td]
                d=mv(roles[group]['rotation_rows'],td);direction_already_R5=True
                tangent_transfers.append(dict(id=n,recipe=rf.relative_to(ROOT).as_posix(),
                    coordinate_match_mm=math.dist(old_point,e['old_point_mm']),
                    basis='Exact named old GUIDE endpoint/tangent under current whole-group rotation. NOT a producer mating contact or measured cable exit.'))
        support=None;basis='Retained current nominal end identity; actual mouth/whole route not qualified'
        if n in new:
            a=new[n];p=a['point_mm'];d=a['bodyward_axis'];support=a['owner'];group=support
            if e['role'].startswith('SPLICE_PI.'):
                d=[-1,0,0] if e['role'].endswith('.16') else [1,0,0]
            basis='New project boundary/splice allocation; not manufacturer data'
        elif n in bg:
            a=bg[n];p=a['start_mm'];v=[y-x for x,y in zip(p,a['end_mm'])];length=math.sqrt(sum(x*x for x in v));d=[x/length for x in v]
            support='BankFull9mmGrip:'+a['holder'];basis='Full unchanged TE part and source-pinned flat bank9mm land'
        else:
            assert p is not None,n
            if group in rear['changed_complete_receiving_groups']:
                rr=rear['relative_rotations'].get(group,I)
                p=plus(mv(rr,p),rear['changed_complete_receiving_groups'][group])
                if d and not direction_already_R5:d=mv(rr,d)
            if group in extra:p=plus(p,extra[group])
            if group and group.startswith('WAGO:'):support='IndependentWireGrip:'+group
            elif group in ('Pi4','MAIN','BUS'):support='UpperPCBWireRelief:'+group
            elif group in ('F_PI','S0','S1'):support='ForeWireRelief:'+group
            else:support='LowerOrTailWireRelief:'+str(group)
        assert len(p)==3 and all(math.isfinite(x) for x in p),n
        rows.append(dict(id=n,wire=e['wire'],role=e['role'],group=group,point_mm=p,
            departure_axis=d,departure_status='PROJECT_RECIPE' if d else 'OPEN_NO_AXIS_IN_CURRENT_PREFIX_RECIPE',
            support_owner=support,owner_status='PROPOSED_NOT_NATIVE_MOUNT',basis=basis,
            datum_kind='EXPLICIT_NEW_BOUNDARY_OR_BANK_LAND' if n in new or n in bg else 'TRANSFERRED_GUIDE_ENDPOINT_NOT_AUTOMATICALLY_ACTUAL_MOUTH',
            actual_port_verified=False,complete_route_verified=False,old_restraint_retired=True))
    assert len(rows)==178 and len({r['id'] for r in rows})==178
    by_station=defaultdict(list)
    for row in rows:
        if row['group'].startswith('WAGO:') and row['departure_axis'] is not None:
            by_station[row['group']].append(row['departure_axis'])
    for row in rows:
        directions=by_station.get(row['group'],[])
        if row['departure_axis'] is None and directions and all(math.dist(d,directions[0])<1e-6 for d in directions):
            row['departure_axis']=directions[0]
            row['departure_status']='SAME_CASING_PARALLEL_PORT_RECIPE_NOT_MANUFACTURER_DATUM'
    if prior:
        assert {(r['id'],r['wire'],r['role']) for r in prior['endpoints']}=={(r['id'],r['wire'],r['role']) for r in rows}
    wires=defaultdict(list)
    for row in rows:wires[row['wire']].append(row['id'])
    assert len(wires)==80
    physical=defaultdict(list)
    for row in rows:physical[row['id'].rsplit('/',1)[0]].append(row)
    segments=[]
    factory_failures=[]
    for key,es in physical.items():
        assert len(es)==2,(key,len(es))
        distance=math.dist(es[0]['point_mm'],es[1]['point_mm'])
        limits=[canonical.get((e['wire'],e['role']),{}).get('supplied_shortest_including_strip_mm') for e in es]
        limits=[v for v in limits if v is not None];limit=min(limits) if limits else None
        row=dict(id=key,endpoint_ids=[e['id'] for e in es],straight_distance_lower_bound_mm=distance,
            is_not_cut_length=True,full_curve_and_land_allowances_open=True,
            supplier_shortest_raw_mm=limit,passes_only_necessary_distance_test=None if limit is None else distance<=limit)
        if limit is not None and distance>limit:factory_failures.append(dict(id=key,straight_lower_bound_mm=distance,
            available_shortest_including_strip_mm=limit,deficit_before_bends_and_lands_mm=distance-limit))
        segments.append(row)
    result=dict(status='ONE178_END_CANDIDATE_ALLOCATED_NOT_ROUTE_OR_N01_ACCEPTANCE',selected=False,physical_pass=False,
        endpoint_records=len(rows),logical_nets=len(wires),physical_segments=len(segments),
        newly_allocated_old_gaps=38,allocation_missing=0,departure_axes_still_open=sum(r['departure_axis'] is None for r in rows),
        roots_geometry_screen=common['status'],endpoints=rows,physical_segment_lower_bounds=segments,
        known_factory_lower_bound_failures=factory_failures,
        axis_recipe_conflicts=axis_conflicts,
        exact_legacy_guide_tangent_transfers=tangent_transfers,
        all_manufactured_length_limits_verified=False,
        body_bundle_hierarchy=dict(wires_per_leg=9,after_hip=6,after_knee=3,electrical_nets_joined=False,
            intended_OD_upper_bound_mm=3.1,three_by_three_pitch_mm=3.6,outer_cuff_width_mm=14.3,
            relation_to_motion='Fixed boundaries only. Constant length/R/torsion through all36poses still N05, not inferred here.'),
        JPWM=dict(relative_shift_mm=extra['JPWM'],outside_80_body_net_ledger=True,
            head_tail_JR_factory_segments_must_be_reallocated=True),
        open=['Transferred GUIDE tangents are project recipes, not measured current mouths/plug exits; reconstruct local mating geometry before full grips',
            'Full80net curves, independent grips, corridor capacity and lengths/stock',
            'Head/tail factory looms outside80net ledger',
            'Tools/reverse assembly and cowls/actual wall containment'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths+[Path(__file__)]},
        updated_utc=datetime.now(timezone.utc).isoformat())
    result['N01_preflight_gate']=dict(ready_for_native_details=False,
        reason='Known raw-factory length failures and unresolved physical departures; do not spend a CAD rebuild on this candidate.',
        order=['Current physical endpoint/frame identity','Raw manufactured length and strip/land lower bounds',
            'Shared multiwire-grip capacity and full middle corridors','Actual changed BRep interfaces',
            'Adopted motion samples and functional wall/assembly/tool access','One complete selection'],
        passes_only_scoped=['48flat-bank purchased parts/24lands/12nominal ATO envelopes',
            'R5 rear receiving bay static factory paths','New common structure at adopted36leg samples'],
        failed=[r['id'] for r in factory_failures],
        open=['Eight source/plug GUIDE exits need current local mating reconstruction; guide tangent alone is not a producer datum',
            'Full routes/independent relief for all80nets and head/tail looms',
            'All carrier/clip roots and actual reverse tools/parking',
            'Whole cowl/panel containment and true-wall budget'],
        earliest_safe_next='Solve F_PI/P_SYS/splice/MAIN with BOTH84.5mm raw factory leads, actual source/body frames and full grip/strip allowances BEFORE one new geometry trial.',
        do_not_repeat=['Old high-splice F_PI layout','Completed flat-bank case/ATO screens',
            'Unchanged36adopted leg samples or old generic spacer columns'],
        N01_complete=False,N01_awarded_percent=0)
    # Necessary box budget, NEVER a loft-containment or real-contact claim.
    # Old guide exits can be provisional mating-plug allowances; keep that
    # distinction visible instead of adding another9mm as if every point were
    # a producer pin. After-bend relief is allowed where the source recipe says so.
    inner_lo=[-139.1,-95.6,-45.6];inner_hi=[181.1,95.6,109.6]
    outside=[];direct_lands=[]
    for row in rows:
        p=row['point_mm'];excess=[max(0,l-v,v-h) for v,l,h in zip(p,inner_lo,inner_hi)]
        if max(excess)>1e-5:outside.append(dict(id=row['id'],role=row['role'],point_mm=p,
            excess_vs_main_inner_box_mm=excess,
            source='Transferred guide or explicit project boundary, not delivered plug measurements',
            action='Needs assigned functional cowl OR corrected source-level/exit recipe before containment acceptance'))
        if row['departure_axis'] is None:continue
        spec=specs.get(row['id']);radius=spec['radius'] if spec else None
        if radius is None:continue
        q=plus(p,[9*x for x in row['departure_axis']]);r=radius+2
        excess=[max(0,l-min(a,b)+r,max(a,b)+r-h) for a,b,l,h in zip(p,q,inner_lo,inner_hi)]
        if max(excess)>1e-5:direct_lands.append(dict(id=row['id'],role=row['role'],
            direct9mm_outer_grip_excess_mm=excess,
            is_not_proof_of_real_collision=True,
            action='Whole grip may need documented AFTER-bend location; do not require9mm at every connector mouth'))
    result['enclosure_necessary_box_budget']=dict(main_outer_mm=[[-141.5,-98,-48],[183.5,98,112]],
        assumed_normal_wall_mm=2.4,inner_box_mm=[inner_lo,inner_hi],
        point_exceptions=outside,direct_grip_reservation_exceptions=direct_lands,
        not_a_true_skin_or_full_cowl_containment_test=True,
        BUS_note='H5 producer header reference is explicitly NOT mating plug exit. Current guide includes a nominal plug allowance; reconstruct it from BUS-port-binding/BUS-routes-plan before moving board or accepting roof.')
    searchfile=OUT/'n01-pi-fuse-bay-search.json'
    if searchfile.exists():
        search=json.loads(searchfile.read_text());assert search['status']!='RUNNING'
        lookup={r['role']:r for r in rows};pin=lookup['P_SYS.5'];pout=lookup['SPLICE_PI.16'];budgets=[]
        for candidate in search['candidates']:
            rr=candidate['rotation_relative_current'];c=candidate['centre_mm'];axis=mv(rr,[1,0,0])
            ends=[('input',plus(c,mv(rr,[25.5,0,0])),axis,pin['point_mm'],pin['departure_axis'],6.5,9,12,50),
                ('output',plus(c,mv(rr,[-25.5,0,0])),[-v for v in axis],pout['point_mm'],pout['departure_axis'],3,17,0,84.5)]
            per=[]
            for label,a,d,b,back,first,last,strip,limit in ends:
                a=plus(a,[first*v for v in d]);b=plus(b,[last*v for v in back])
                lb=curvature_chord_bound(a,d,b,[-v for v in back],6)
                lower=first+lb['lower_bound_mm']+last+strip
                per.append(dict(branch=label,chord_mm=lb['chord_mm'],minimum_curvature_penalty_mm=lb['penalty_mm'],
                    lower_bound_intervals_disjoint=lb['intervals_disjoint'],raw_lower_bound_mm=lower,raw_limit_mm=limit,
                    fails_necessary_R6_budget=lower>limit,full_curve_constructed=False))
            budgets.append(dict(centre_mm=c,rotation_rows=rr,branches=per,
                passes_both_necessary_R6_budgets=all(not r['fails_necessary_R6_budget'] for r in per)))
        result['pi_fuse_search_curvature_followup']=dict(source=searchfile.relative_to(ROOT).as_posix(),
            source_sha256=sha(searchfile),candidates=budgets,
            survivors=sum(r['passes_both_necessary_R6_budgets'] for r in budgets),
            project_static_R_mm=6,manufacturer_bend_limit_verified=False,
            scope='Only the four conservative grid candidates, fixed P_SYS/splice and assumedR6. No general proof of physical infeasibility.',
            next='Solve F_PI, P_SYS and splice as one coupled bay before another CAD test; never promote Euclidean-only candidates to feasible routes.')
        result['source_sha256'][searchfile.relative_to(ROOT).as_posix()]=sha(searchfile)
    if prior:result['motion_frame_reconciliation']=dict(previous_unselected_local_report_sha256=prior_hash,
        correction='Pre-motion prefix directions now receive motion_receiving_changes once; current-native points do not receive that transform again.',
        already_current_factory_joint_axes_reused=8,identity_set_unchanged=True,
        unknown_axes_not_invented=True,actual_port_or_route_acceptance=False)
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','endpoint_records','logical_nets','physical_segments','departure_axes_still_open')}))


if __name__=='__main__':main()
