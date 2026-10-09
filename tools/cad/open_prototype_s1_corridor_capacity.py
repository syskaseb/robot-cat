"""Whole ring-plane and four-circuit capacity, no native angle variants."""
from pathlib import Path
from datetime import datetime,timezone
import json,time,math,copy
import open_prototype_s1_biarc_plan as G
from open_prototype_distribution_allocation import input_recipe
B=G.B;ROOT=G.ROOT;OUT=G.OUT
PLAN=OUT/'s1-corridor-capacity.json';PROOF=OUT/'s1-corridor-space.json';REUSE_PROOF=None

def connector(start,departure,end,arrival,d1):
    if arrival==B.WEST and end==[-38,33,131]:
        straight=B.line(start,B.add(start,B.mul(departure,9)))
        #The current bearing stays XY. Exact azimuthal arc to WEST,
        #rather than shifting a wire while leaving the ring behind.
        side=[-departure[1],departure[0],0]
        centre=B.add(straight['end'],B.mul(side,25.2))
        stop=B.add(centre,[0,25.2,0])
        turn=G.A.arc(straight['end'],departure,stop)
        return [straight,turn]+input_recipe(stop,end,B.WEST,25.2)['segments']
    return G.A.connect(start,departure,end,arrival,d1)

def build():
    data=B.read(PLAN);assert data['family'] is not None
    for n,h in data['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return data['family']

if __name__=='__main__':
    assert not PLAN.exists(),'Receive whole corridor allocation'
    tick=time.monotonic();runs=[];chosen=None;report=None
    #All angles change the whole terminal and all four circuits are then
    #jointly checked. These are search variables, not produced CAD variants.
    for angle in (115,125,105):
        base=G.F.build();ring=next(r for r in base['s1_module']['rings'] if r['terminal']==3)
        direction=[math.cos(math.radians(angle)),math.sin(math.radians(angle)),0]
        ring.update(direction=direction,barrel_mm=B.add(ring['eye_mm'],B.mul(direction,22.123)),ring_rotation_z_deg=angle-180)
        choices,counts,reasons=G.search(connector,base)
        runs.append(dict(ring3_azimuth_deg=angle,counts=counts,conservative_rejections=reasons))
        if choices:chosen=choices[0][1];report=choices[0][2];break
    if chosen:chosen.update(changed_case_names=['P_SYS','F_PI'],s1_geometry_changed=False,changed_ring_terminals=[3],
        changed_path_names=['W064','W065','W067','W068','F_PI/input','F_PI/output','F_PI/sleeve','F_PI/new_insulation','XB12','XB22'],
        status='WHOLE_RING_PLANE_AND4SOURCE_APPROACHES_REQUIRE_ACTUAL_GATE')
    files=[Path(__file__),Path(G.__file__),Path(G.A.__file__),Path(G.S.__file__),
        Path(G.F.__file__),G.F.PLAN,G.F.PROOF,OUT/'routing-space-map.json',OUT/'obstacle-map-current.json']
    data=dict(status='ONE_SOURCE_FAMILY_REQUIRES_ACTUAL_GATE' if chosen else 'NO_CONSERVATIVE_RING_CORRIDOR_NOT_PROOF_OF_IMPOSSIBILITY',
        family=chosen,mutual_preflight=report,runs=runs,
        previous_producers_archived='11a999a/e4aff99; previous raw exclusions not relabelled as current pins',
        geometric_budget_search_not_actual_material_contacts=True,
        geometry_digest=G.S.R.geometry_digest(chosen) if chosen else None,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:data[k] for k in ('status','runs','worker_seconds')}),flush=True)
