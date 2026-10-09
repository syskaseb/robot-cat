"""Allocate the complete four-source corridor before any native detail.

Keep original free ring directions. Mathematical tangent construction
variables allocate the NORTH gallery as a whole, away from AUX sleeves.
Previous fixed/variable final-straight subsets are archived in e139dd8.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time
import open_prototype_s1_biarc_plan as G
from open_prototype_distribution_allocation import input_recipe
B=G.B;ROOT=G.ROOT;OUT=G.OUT
PLAN=OUT/'s1-grip-capacity.json';PROOF=OUT/'s1-grip-space.json';REUSE_PROOF=None

def connector(start,departure,end,arrival,d1):
    if arrival==B.WEST and end==[-38,33,131]:
        straight=B.line(start,B.add(start,B.mul(departure,d1)))
        turn=B.quarter(straight['end'],B.NORTH,B.WEST,25.2)
        parts=[straight,turn]+input_recipe(turn['end'],end,B.WEST,25.2)['segments']
        return parts
    if arrival==B.UP and abs(start[0]-132.2)<1e-6 and abs(start[1]-34.123)<1e-6:
        #Two arcs cannot maintainR25.2 with both9mm grips here. The whole
        #source first enters the free NORTH gallery before its rising pair.
        # Current P_REAR.5 is94.8X, not the obsolete81.8X/P_REAR.3.
        # Tangent constraint calculation gives max-minR23.123 for lead24,
        # but lead36/d1=48 yields26.430/25.907mm. This changes the whole
        # northern approach before geometry, not a terminal micro-offset.
        lead=B.line(start,B.add(start,B.mul(B.NORTH,36)))
        turn=B.quarter(lead['end'],B.NORTH,B.WEST,25.2)
        grip_start=B.sub(end,B.mul(B.UP,9))
        return [lead,turn]+G.A.connect(turn['end'],B.WEST,grip_start,B.UP,d1,straight=0)+[B.line(grip_start,end)]
    return G.A.connect(start,departure,end,arrival,d1)

def build():
    data=B.read(PLAN);assert data['family'] is not None
    for n,h in data['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return data['family']

if __name__=='__main__':
    if PLAN.exists():
        old=B.read(PLAN)
        assert old['status']=='NO_CONSERVATIVE_GRIP_SUBSET_NOT_PROOF_OF_IMPOSSIBILITY'
        assert any(B.sha(ROOT/n)!=h for n,h in old['source_sha256'].items()), 'No unchanged retry'
    tick=time.monotonic();choices,counts,reasons=G.search(connector);p=choices[0][1] if choices else None
    if p:
        for r in p['s1_routes']:r['end_straight_mm']=B.segment_geometry(r['segments'][-1])[0]
        for r in p['s1_routes']:r['source_straight_mm']=B.segment_geometry(r['segments'][0])[0]
        p.update(changed_case_names=['P_SYS','F_PI'],s1_geometry_changed=False,
            changed_path_names=['W064','W065','W067','W068','F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation','XB12','XB22'],
            status='FOUR_SOURCES_AND_VARIABLE_GRIPS_REQUIRE_ACTUAL_GATE')
    files=[Path(__file__),Path(G.__file__),Path(G.A.__file__),Path(G.S.__file__),Path(G.F.__file__),G.F.PLAN,G.F.PROOF,
        OUT/'routing-space-map.json',OUT/'obstacle-map-current.json']
    data=dict(status='ONE_SOURCE_FAMILY_REQUIRES_ACTUAL_GATE' if p else 'NO_CONSERVATIVE_GRIP_SUBSET_NOT_PROOF_OF_IMPOSSIBILITY',
        previous_failed_subset_snapshot='e139dd8:s1-grip-capacity.json; no previous source clearance accepted',
        near_wire_policy='Reject known sampled crossings only; close pairs are NOT waived and require exact centreline/radius proof. The extra0.5mm sample margin was a conservative filter, not a manufacturer requirement or a proven contact.',
        family=p,mutual_preflight=choices[0][2] if p else None,counts=counts,conservative_rejections=reasons,
        geometry_digest=G.S.R.geometry_digest(p) if p else None,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:data[k] for k in ('status','counts','conservative_rejections','worker_seconds')}),flush=True)
