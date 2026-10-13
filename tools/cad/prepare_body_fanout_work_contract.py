"""Bind the next shared fanout job to current roots/receivers/cable budgets.

No routing, new parts or acceptance. Reuse the existing extension ledger;
do not resurrect the rejected old body docks or count donor wire twice.
"""
import hashlib,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def combine(family,budget,retention):
    result=[]
    for row in budget['rows']:
        hip=next(h for h in family['hips'] if h['loom']==row['loom'])
        group=next(g for g in retention['groups'] if g['id']==hip['physical_leg']+'FixedCarrier')
        land=row['loom']+'/Hip/Fixed'
        assert any(p['land_id']==land for p in group['ports']),land
        route=next(r for r in family['routes'] if r['loom']==row['loom'])
        assert abs(route['guide_to_body_grip_mm']-row['guide_to_body_grip_mm'])<1e-8
        extension=row.get('extension_candidate')
        for core in row['body_cores']:
            electrical=route['source']['electrical'][core['core']]
            assert (core['wire'],core['role'])==(electrical['wire'],electrical['body_end'])
            capacity=row['remaining_after_guide_mm']
            if extension:
                capacity=next(c['donor_core_capacity_before_terminal_mm'] for c in extension['staggered_core_schedule'] if c['wire']==core['wire'])
            result.append(dict(wire=core['wire'],loom=row['loom'],core=core['core'],
                bundle_root_world_mm=hip['fixed_anchor_world_mm'],
                bodyward_bundle_tangent=[-v for v in hip['fixed_tangent_world']],
                existing_fixed_support=group['id'],existing_bundle_land=land,
                receiver_role=core['role'],receiver_point_mm=core['point_mm'],
                receiver_outward_axis=core['departure'],
                capacity_before_terminal_mm=capacity,
                terminal_allowance_project_mm=core['terminal_allowance_project_mm'],
                length_lower_bound_mm=core['route_lower_bound_mm'],
                optimistic_margin_mm=capacity-core['terminal_allowance_project_mm']-core['route_lower_bound_mm'],
                source_extension_candidate=extension['loom'] if extension else None,
                actual_core_start=None,actual_route=None,receiving_restraint=None,actual_cut_mm=None))
    assert len(result)==36 and len({r['wire'] for r in result})==36
    assert len({r['loom'] for r in result})==12
    assert all({r['core'] for r in result if r['loom']==loom}=={'D','V','G'} for loom in {r['loom'] for r in result})
    assert all(r['optimistic_margin_mm']>0 for r in result),'Length lower bound already impossible; do not route'
    return result

def run():
    tick=time.monotonic()
    files=[OUT/n for n in ('leg-source-near-member-plan.json','leg-extension-budget-plan.json','remaining-retention-entry.json','remaining-support-shared-material.json')]
    family,budget,retention,gate=[json.loads(f.read_text()) for f in files]
    assert gate['status']=='COMBINED_SUPPORT_MATERIAL_CLEAR_NATIVE_OPEN' and not gate['contacts'] and not gate['errors']
    # Existing ledger binds the actual receiver overlay, not old dock coordinates.
    for receipt in (budget,gate):
        for name,digest in receipt['source_sha256'].items():assert sha(ROOT/name)==digest,name
    rows=combine(family,budget,retention)
    report=dict(status='CURRENT_36_CORE_WORK_CONTRACT_NO_ROUTES_OR_ACCEPTANCE',
        rows=rows,source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in files+[Path(__file__)]},
        candidate_stock=budget['candidate_stock'],selected=False,W5_complete=False,physical_pass=False,
        rules=['One shared body layout includes all36cores, retained modules and ALL new supports before native detail.',
            'Bundle root is not three coincident core centre lines: choose a physically packed breakout once, preserve continuity mapping.',
            'Capacities reuse50mm factory reserve and staggered donor bookkeeping; do not subtract/add those twice.',
            'Use receiving outward axes, actual insertion limits, independent grips and installation access together.',
            'Screen shared radii/length/mutual clearance cheaply; only viable full layout goes to actual valid material.',
            'Old leg-fanouts/channels docks are not current. No imaginary longer factory cable, extra source connector or accepted stock.',
            'This contract does not close19other body guides, sleeve supplier selection or electricalE3.'],
        next_result='One complete shared36core routed/retained body fanout plus lengths. First freeze breakout packing and receiver-side support ownership.',
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'body-fanout-work-contract.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],wires=len(rows),minimum_optimistic_margin_mm=min(r['optimistic_margin_mm'] for r in rows),seconds=report['worker_seconds'])))

if __name__=='__main__':run()
