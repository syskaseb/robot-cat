"""Twelve whole cable contracts; candidate lengths are not cut instructions."""
from datetime import datetime, timezone
import json, math
from w5_ground_joint_layout_r4 import ROOT, ports
from servo_fuse_inputs_r1 import save, sha

def main():
    begin=datetime.now(timezone.utc)
    out=ROOT/'hardware/electronics/full-cat/w5-space-plan-inputs-r1/looms.json'
    assert not out.exists()
    source=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json'
    raw=json.loads(source.read_text(encoding='utf-8'))['routes']; datums=ports()
    groups={}
    for row in raw:
        start=datums[row['body_end']]['point_mm'] if row['role']=='G' else row['waypoints_mm'][0]
        end=row['waypoints_mm'][-1]
        body_floor=math.dist(start,end)+row.get('bank_local_path_mm',0)
        strip=row['termination']['strip_mm']; moving=row['moving_candidate_length_mm']
        groups.setdefault(row['loom'],[]).append(dict(wire=row['wire'],role=row['role'],
            body_end=row['body_end'],servo_end=row['servo_end'],body_datum_mm=start,
            retained_breakout_mm=end,moving_candidate_mm=moving,
            bank_local_mm=row.get('bank_local_path_mm',0),termination=row['termination'],
            straight_distance_only_lower_bound_mm=body_floor+moving+strip+30,
            lower_bound_is_NOT_routed_length=True,qualified=False))
    assert len(groups)==12 and all({r['role'] for r in rows}=={'D','V','G'} for rows in groups.values())
    looms=[dict(loom=k,conductors=v,stock_basis='one continuous 3-core 900mm candidate with original servo plug',
        minimum_possible_blank_mm=max(r['straight_distance_only_lower_bound_mm'] for r in v),
        nominal_candidate_mm=900,actual_cut_mm=None,route_length_and_motion_qualification_pending=True)
        for k,v in sorted(groups.items())]
    finish=datetime.now(timezone.utc)
    save(out,dict(status='TWELVE_COMPLETE_LOOM_INTERFACE_CONTRACTS_NOT_ROUTING_PASS',looms=looms,
        count=12,conductors=36,stock_selected=False,W5_complete=False,physical_pass=False,
        routing_order=['Preserve whole factory cable from servo to retained breakout.',
            'Allocate D/V/G together at each breakout; keep exact body termination identities.',
            'Use maximum required D/V/G path per cable including strip and trial reserve.',
            'Recheck changed moving envelope and restraints before selecting any cable length.'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (source,ROOT/'tools/electronics/w5_ground_joint_layout_r4.py',__import__('pathlib').Path(__file__))},
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))
    print(json.dumps({x['loom']:round(x['minimum_possible_blank_mm'],1) for x in looms}))

if __name__=='__main__':main()
