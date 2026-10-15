"""Localize the named new RL1/retained RL3 witness to actual cable segments.

One changed failure only, not another assembly audit or geometric acceptance.
Distinguish Hip flex, downstream rigid joins and factory route before choosing
which cause to redesign. No material/native mutations.
"""
import copy,json,time
from pathlib import Path
import check_near_axis_hip_sources as C
from plan_axial_hip_sources import ends,build
from plan_current_mta_interfaces import line
P=C.P


def run():
    tick=time.monotonic();seed=P.OUT/'body-axial-hip-plan.json';familyfile=P.OUT/'leg-source-near-member-plan.json'
    family=json.loads(familyfile.read_text());row=copy.deepcopy(next(r for r in json.loads(seed.read_text())['hips'] if r['loom']=='RL1'))
    axesfile=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    row['fixed_anchor_world_mm']=[170,0,-16];witnesses=[]
    for beta in (60,0,-60):
        length=next((n for n in range(125,351,5) if all(build(*ends(row,h)[:3],n+d,beta) is not None for h in (-15,0,15) for d in (-5,0,5))),None)
        if length is None:continue
        for h in (-15,0,15):
            a,b,v,m=ends(row,h);parts=[line(row['fixed_anchor_world_mm'],a),*build(a,b,v,length,beta),line(b,m)]
            new=P.wire(parts+C.B.moved_parts(row['source_parts'],row['source'],h,0,axes))
            old=C.B.parts_for_loom(family,'RL3',h,0,axes)
            source=next(r for r in family['routes'] if r['loom']=='RL3')
            factory=C.B.moved_parts(source['source_parts'],source['source'],h,0,axes)
            distance,points,_=new.distToShape(P.wire(old+factory))
            if distance>=6.25:continue
            closest=[]
            for label,collection in (('joint_and_rigid_carried_route',old),('factory_approach',factory)):
                for index,part in enumerate(collection):
                    gap,pair,_=new.distToShape(P.wire([part]))
                    if gap<6.25:
                        closest.append(dict(label=label,index=index,part=part,gap_mm=gap,
                            points_mm=[[list(a),list(b)] for a,b in pair[:2]]))
            witnesses.append(dict(root=row['fixed_anchor_world_mm'],beta=beta,freeflex_mm=length,hip=h,gap_mm=distance,segments=closest))
    result=dict(status='NAMED_REAR_WIRE_CROSSING_LOCALIZATION_NOT_ACCEPTANCE',witnesses=witnesses,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (seed,familyfile,axesfile,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),physical_pass=False,selected=False,W5_complete=False)
    (P.OUT/'rear-source-crossing-witness.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(witnesses=[dict(beta=r['beta'],hip=r['hip'],freeflex=r['freeflex_mm'],segments=[dict(label=q['label'],index=q['index'],gap=round(q['gap_mm'],3),points=q['points_mm']) for q in r['segments']]) for r in witnesses],worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
