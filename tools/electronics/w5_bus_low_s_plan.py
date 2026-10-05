"""Full300mm BUS ground lead with a low S corridor, not a high riser.

Preserve factory plug and G2 cage datum; replace its unselected up-prefix.
The whole route and all restraints still need joint material qualification.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
from w5_s1_source_layout_r2 import CentreLine
from w5_parallel_connection import connect
from servo_fuse_inputs_r1 import save,sha

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-bus-low-s-plan-r1'


def recipe(family, source):
    start=family['ends']['W003']['edges'][0]['start']
    c=CentreLine(start,[1,0,0]);c.line([start[0]+6,start[1],start[2]])
    c.arc([0,0,-1],radius=10);c.arc([-1,0,0],radius=10)
    end=[source[0]+10,source[1],source[2]+16]
    mid=connect(c.p,end,[-1,0,0],10)
    c.edges.extend(mid);c.p=list(end);c.t=[-1,0,0]
    c.arc([0,0,-1],radius=10);c.line(source)
    assert math.dist(c.p,source)<1e-7 and math.dist(c.t,[0,0,-1])<1e-7
    body=sum(e['length_mm'] for e in c.edges)
    assert body+41+30<=300
    return dict(wire='W003',edges=c.edges,start_mm=start,end_mm=source,
        body_mm=body,nominal_mm=body+41,trial_blank_mm=math.ceil((body+41+30)/10)*10,
        factory_length_mm=300,radius_mm=10,OD_mm=2,
        factory_source_outward_axis=[0,0,1],source_straight_mm=6,
        unselected_up_prefix_superseded=True)


def main():
    start=datetime.now(timezone.utc)
    assert not (OUT/'intent.json').exists()
    family=ROOT/'hardware/electronics/full-cat/w5-central-bridge-low-arc-r1/received-family.json'
    bus=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    row=recipe(json.loads(family.read_text(encoding='utf-8')),
               json.loads(bus.read_text(encoding='utf-8'))['source_lead_datums']['W003'])
    OUT.mkdir(parents=True,exist_ok=True)
    files=[Path(__file__),Path(__file__).with_name('w5_parallel_connection.py'),
           Path(__file__).with_name('w5_s1_source_layout_r2.py'),
           Path(__file__).with_name('w5_s1_source_layout_r1.py'),family,bus]
    finish=datetime.now(timezone.utc)
    save(OUT/'intent.json',dict(status='BUS_GROUND_LOW_CORRIDOR_PLAN',recipe=row,
        material_checked=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
    print('BUS_LOW_PLAN',row['body_mm'],row['trial_blank_mm'])


if __name__=='__main__':main()
