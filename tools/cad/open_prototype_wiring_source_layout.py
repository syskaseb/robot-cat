"""Shared five-holder source layout, before native mount/routing investment.

The cheap screen identifies candidate pairs, not actual collisions. Preserve
all bought holders, both lead exits and mount/board datums. No wire is selected.
"""
import json
import math
from datetime import datetime, timezone
from open_prototype_wiring_endpoints import ROOT, BASE, OUT, read, sha


def overlap(a, b):
    return all(min(a[i+3],b[i+3])-max(a[i],b[i]) > 1e-6 for i in range(3))


def build():
    source = read(OUT)
    datums = {e['role']:e for r in source['body_conductors'] for e in r['ends']}
    for r in source['distribution_boundary']:
        datums.update(r['resolved_datums'])
    candidates = []
    # Two thin pre-fuse leads need short nearby inputs, not extensions.
    # P_REAR ports2/5 are the SAME bus: a documented permutation puts AUX
    # near the rail and leaves its51mm body clear of the retained rear MTA.
    for holder, target, side, approach in [('F_PI','P_SYS.2',1,17),
            ('F_AUX','P_REAR.2',1,21), ('F_HY','P_AUX.2',-1,21.5),
            ('F_HP','P_AUX.3',-1,44), ('F_TY','P_AUX.4',-1,66.25)]:
        goal = datums[target]['point_mm']
        entry = [goal[0]+side*9, goal[1]-side*approach, goal[2]]
        exit_point = [entry[0]+side*51, entry[1], entry[2]]
        b = [min(entry[0],exit_point[0]),entry[1]-10.125,entry[2]-10,
             max(entry[0],exit_point[0]),entry[1]+10.125,entry[2]+12]
        #3mm factory exit, quarter-circleR6, >=9mm insulated WAGO approach.
        straight = approach-6
        assert straight >= 9
        length = 3+math.pi*6/2+straight+datums[target]['insertion_strip_max_mm']
        assert length < (50 if holder in ('F_PI','F_AUX') else 84.5)
        candidates.append(dict(holder=holder,target=target, proposed_body_bounds_mm=b,
            input_exit_mm=entry,output_exit_mm=exit_point, input_departure=[-side,0,0],
            output_departure=[side,0,0], nominal_input_blank_mm=length,
            input_recipe=dict(exit_straight_mm=3, quarter_radius_mm=6, entry_straight_mm=straight,
                basis='Project wire geometry, not delivered bend specification'),
            factory_nominal_minimum_margin_mm=84.5-length,
            both_output_route_and_independent_load_path_pending=True))
    self_pairs = [(a['holder'],b['holder']) for i,a in enumerate(candidates)
        for b in candidates[i+1:] if overlap(a['proposed_body_bounds_mm'],b['proposed_body_bounds_mm'])]
    possible = []
    omitted = {r['holder']+'_CP2' for r in candidates}
    for row in candidates:
        for name, ob in source['components'].items():
            if name in omitted or name.startswith(('Corridor_', 'W0')):
                continue
            if overlap(row['proposed_body_bounds_mm'],ob['bounds_mm']):
                possible.append(dict(holder=row['holder'], target=name,
                    disposition='BBOX_CANDIDATE_PAIR_ONLY; actual valid BRep check required'))
    return dict(status='ONE_SHARED_SOURCE_LAYOUT_PLANNED_NOT_SELECTED',selected=False,
        physical_pass=False,stage_completed=False,
        endpoint_source_sha256=sha(OUT),source_plan=candidates,
        proposed_same_bus_port_permutation={'P_REAR.2':'P_REAR.5','P_REAR.5':'P_REAR.2'},
        affected_connections=['W044/F_RL.in','F_AUX.in/XA01'],
        electrical_nets_or_installed_holder_counts_changed=False,
        candidate_self_bbox_pairs=self_pairs,possible_context_pairs=possible,
        retained=['MAIN46.52','current mounting set','20WAGO body positions','R47','4MTA'],
        output_plan=['F_PI protected solder splice may move; keep one8mm overlap and separate insulation grips',
            'Bind F_AUX/F_HY/F_HP outputs to existing documented joints/boards before choosing lead blanks',
            'No thin pre-fuse extension to evade50mm; reconcile factory leads/extension elements and stock'],
        plan_changes_before_CAD=['PI upper+Y approach17mm avoids S0 allowance by2.125mm',
            'HP/TY old bays overlap newly raised WAGO; allocate all three AUX branch bodies jointly instead of preserving invalid bays',
            'TY minimum margin below1mm is not delivered acceptance; keep extension/trim gate explicit'],
        next='Validate coherent source bodies against mount and context BRep; then full input/output paths and load-bearing seats together',
        created_utc=datetime.now(timezone.utc).isoformat())


if __name__ == '__main__':
    result=build()
    dest=BASE/'wiring-checkpoint/source-layout-plan.json'
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=dest.relative_to(ROOT).as_posix(),
        self_bbox_pairs=result['candidate_self_bbox_pairs'],
        context_candidate_count=len(result['possible_context_pairs']))))
