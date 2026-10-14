"""Identify the exact crossing portion, not another whole candidate retry."""
import json
import time
from pathlib import Path
import FreeCAD as A
from diagnose_remaining_support_endpoints import transform,moved
import build_remaining_loom_supports as G
P=G.P


def run():
    tick=time.monotonic();pf=P.OUT/'body-low-hip-rail-exit-plan.json'
    plan=json.loads(pf.read_text());row=next(r for r in plan['hips'] if r['loom']=='RR1')
    sf=P.OUT/'remaining-supports/KneeLoomCarriers.FCStd'
    reader=G.B.H.P.SavedShapes();base=reader.shape(sf,'RearRightKneeCarrier')
    gf=P.OUT/'remaining-support-shared-material.json';gate=json.loads(gf.read_text())
    recipe=gate['recipes']['RearRightKneeCarrier']
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    trials=[]
    for h in (-15,0,15):
        t=transform(axes,row['cad_code'],h,15,'Knee');target=moved(base,t)
        pose=next(p for p in row['poses'] if p['angle']==h)
        for i,part in enumerate(pose['parts']):
            wire=P.wire([part]);gap,points,info=wire.distToShape(target)
            if gap>=3.25:continue
            components=[]
            for pad in recipe['pads']:
                q=moved(G.oriented(pad['bounds_mm'],pad.get('placement')),t)
                d=wire.distToShape(q)[0]
                if d<3.25:components.append(dict(name=pad['name'],gap_mm=d,bounds_mm=pad['bounds_mm'],placement=pad.get('placement')))
            trials.append(dict(hip=h,knee=15,part_index=i,part=part,gap_mm=gap,
                witness_pairs_mm=[[list(a),list(b)] for a,b in points],support_pad_candidates=components))
    result=dict(status='EXACT_RR_FLEX_KNEE_CROSSING_WITNESSES',rows=trials,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (pf,sf,gf,af,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False)
    (P.OUT/'body-rail-knee-crossing-witnesses.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(worker_seconds=result['worker_seconds'],rows=[dict(hip=r['hip'],part=r['part_index'],gap=r['gap_mm'],pads=[p['name'] for p in r['support_pad_candidates']]) for r in trials])),flush=True)


if __name__=='__main__':run()
