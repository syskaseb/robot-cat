"""Name every blocked exit at a current receiver before another route search."""
import json
import time
import numpy as np
from plan_body_fanout_layout import OUT,ROOT,SHA,Scene,AXES,part_points,reverse_part
from plan_current_moving_looms import exact_quarter,add,mul
from plan_current_mta_interfaces import line


def run():
    tick=time.monotonic();layoutfile=OUT/'body-fanout-layout.json'
    turnsfile=OUT/'body-fanout-receiving-turns.json'
    layout=json.loads(layoutfile.read_text());turns=json.loads(turnsfile.read_text())
    receipt=json.loads((OUT/'body-fanout-scene.json').read_text())
    scene=Scene(np.load(ROOT/receipt['scene'],allow_pickle=False))
    for row in layout['rows']:
        scene.add_points('new/'+row['wire']+'/source',np.linspace(row['start'],row['free_start'],9))
        entry=add(row['receiver_point_mm'],mul(row['bodyward_bundle_tangent'],-3))
        scene.add_points('new/'+row['wire']+'/receiver',np.linspace(entry,row['receiver_point_mm'],6))
        if row['wire'] in turns['chosen']:
            scene.add_points('new/'+row['wire']+'/receiver',np.concatenate([part_points(p) for p in turns['chosen'][row['wire']]['receiving_parts']]))
    for name,r in layout['routes'].items():scene.add_points('new/'+name,np.concatenate([part_points(p) for p in r['parts']]))
    results=[]
    row=next(r for r in layout['rows'] if r['wire']=='W024')
    for direction in AXES:
        u=row['receiver_outward_axis'];start=row['free_end']
        if direction==tuple(u):recipe=line(start,add(start,mul(u,10)))
        elif sum(a*b for a,b in zip(u,direction))==0:recipe=exact_quarter(start,u,direction,10)
        else:continue
        ok=scene.clear(part_points(recipe),row)
        results.append(dict(direction=list(direction),recipe=recipe,screen_clear=ok,blocker=None if ok else scene.last_blocker))
    result=dict(status='NAMED_RECEIVER_EXIT_RESERVATIONS_NOT_ACTUAL_CONTACT',wire='W024',rows=results,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (layoutfile,turnsfile,OUT/'body-fanout-scene.json',__import__('pathlib').Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),physical_pass=False,W5_complete=False)
    (OUT/'body-fanout-corridor-exit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
