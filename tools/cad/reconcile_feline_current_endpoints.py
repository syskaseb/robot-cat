"""Whole end ledger after receiving changes; identity is not routing approval."""
import json,time
from collections import Counter
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import BASE,OUT
from plan_feline_endpoints import owner,source_port_frames,transfer_port


def main():
    tick=time.monotonic();receiptfile=OUT/'motion-receivers-checks.json';receipt=json.loads(receiptfile.read_text())
    assert receipt['native_built'];native=ROOT/receipt['native'];assert sha(native)==receipt['native_sha256']
    planfile=ROOT/receipt['module_plan'];plan=json.loads(planfile.read_text());roles={g['role']:g for g in plan['groups']}
    source=BASE/'body-harness-checkpoint/w5-current-end-coverage.json';old=json.loads(source.read_text())
    frames=source_port_frames(plan);rows=[];missing=Counter();ids=set()
    for kind in ('fixed_physical_guide_ends','body_fixed_boundary_ends'):
        for end in old[kind]:
            assert end['id'] not in ids;ids.add(end['id']);group=owner(end['role'],roles)
            if group=='RetainedBattery':point=np.array(end['point_world_mm'])
            elif group in roles:group,point,_=transfer_port(plan,end['role'],end['point_world_mm'],frames=frames)
            else:point=None;missing[end['role'].split('.')[0]]+=1
            rows.append(dict(id=end['id'],wire=end['wire'],role=end['role'],source_kind=kind,group=group,
                candidate_point_mm=None if point is None else point.tolist(),old_point_mm=end['point_world_mm'],
                old_restraint_owner=end['restraint']['owner'],old_restraint_reselected=False,
                actual_mouth_axis_verified=False,full_route_complete=False,
                changed_receiving_role=group in plan['motion_receiving_changes']))
    factory={r['wire']:r for r in receipt['factory_routes']}
    result=dict(status='CURRENT_WHOLE_END_IDENTITY_LEDGER_NOT_WIRING_ACCEPTANCE',selected=False,physical_pass=False,
        native=native.relative_to(ROOT).as_posix(),native_sha256=sha(native),logical_nets=80,
        endpoint_records=len(rows),unique_endpoint_ids=len(ids),mapped_identity_only=sum(r['candidate_point_mm'] is not None for r in rows),
        unallocated_roles=dict(missing),endpoints=rows,
        complete_factory_piece_count=len(factory),factory_custom_extensions_complete=False,
        stale_changed_approaches_not_reused=True,full80net_paths_complete=False,
        moving12looms_complete=False,old_source920mm_reselected=False,
        source920mm_action='Split original source segments by actual moved component mouths; derive full cut/strip/route/grip lengths only after common architecture. No automatic reuse of920mm.',
        required_next_gate=['Joint design includes load paths, both connector exits, grip lands and removable skin with true3D minimum wall.',
            'Replace or reorient two rear inline source receivers as one supported topology; compulsory9mm lands currently hit feet.',
            'Resolve S1 mandatory lands and tail bridge volume in the common fore/tail cowl plan, not serial wall notches.',
            'Every mapped end needs confirmed direction, independent grip and complete middle; unmapped head/leg boundaries need actual attachment allocation.',
            'Preserve bank/P0/E6/15drives; derive materials and service only from the accepted complete paths.'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (native,receiptfile,planfile,source,BASE/'body-harness-checkpoint/leg-stations-plan.json',Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'endpoint-current-receivers.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','endpoint_records','mapped_identity_only','unallocated_roles','worker_seconds')}),flush=True)


if __name__=='__main__':main()
