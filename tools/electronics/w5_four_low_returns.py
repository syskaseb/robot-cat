"""One common low-plane plan for all four central-to-leg returns.

Replace obstructed vertical departures with sideways departures at113.5mm.
The leg approach is from below, with exactR21 arcs and straight cage ends.
There is no scalar position/height search in this stage.
"""
from datetime import datetime, timezone
from pathlib import Path
from itertools import combinations
import json
import math
import w5_central_shared_routes as scope
from w5_s1_source_layout_r2 import CentreLine
from w5_parallel_connection import connect
from w5_bus_low_s_material import build
from servo_fuse_inputs_r1 import save,sha

OUT=scope.ROOT/'hardware/electronics/full-cat/w5-four-low-returns-r1'
BRIDGE=scope.ROOT/'hardware/electronics/full-cat/w5-central-south-bridge-r1/checks.json'
WIRES=('W025','W036','W062','W063')


def reverse_edges(edges):
    return [dict(e,start=e['end'],end=e['start']) for e in reversed(edges)]


def recipes(family,rows):
    result=[]
    rows={r['wire']:r for r in rows}
    for wire in WIRES:
        start=family['ends'][wire]['edges'][0]['start']
        end=rows[wire]['b_datum']['point_mm']
        outward=rows[wire]['b_datum']['outward_axis']
        b=CentreLine(end,outward)
        b.line([x+6*t for x,t in zip(b.p,b.t)])
        b.arc([0,0,-1],radius=21)
        b.line([b.p[0],b.p[1],b.p[2]-6])
        if wire in ('W025','W036'):
            a=CentreLine(start,[0,1,0]);a.line([start[0],start[1]+6,start[2]])
            a.arc([-1,0,0],radius=21)
            before_rise=[b.p[0]+21,b.p[1],start[2]]
            a.edges.extend(connect(a.p,before_rise,[-1,0,0],21))
            a.p=before_rise;a.t=[-1,0,0]
        else:
            direction=[0,1 if wire=='W062' else -1,0]
            a=CentreLine(start,[1,0,0]);a.line([start[0]+16,start[1],start[2]])
            a.arc(direction,radius=21)
            a.line([a.p[0],b.p[1]-21*direction[1],a.p[2]])
        a.arc([0,0,1],radius=21)
        a.line(b.p)
        assert math.dist(a.t,[0,0,1])<1e-7 and math.dist(a.p,b.p)<1e-7
        es=a.edges+reverse_edges(b.edges)
        body=sum(e['length_mm'] for e in es)
        result.append(dict(wire=wire,edges=es,OD_mm=4.2,radius_mm=21,
            body_mm=body,nominal_mm=body+25,trial_blank_mm=math.ceil((body+25+30)/10)*10,
            central_start=start,leg_end=end,cage_straight_min_mm=6,
            central_old_up_prefix_replaced=True,leg_approach='below'))
    return result


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    fixed,printed,ends,family,rows,pins,reused,replaced=scope.load_scope(A,Part)
    bridge=json.loads(BRIDGE.read_text(encoding='utf-8'))
    assert bridge['bridge_complete'] and not bridge['hits']
    for rel,digest in bridge['files'].items():
        assert sha(scope.ROOT/rel)==digest
        pins.append(scope.ROOT/rel)
    fixed['W061']=Part.read(str(BRIDGE.parent/'W061_WORLD.brep'))
    obstacles={**fixed,**{w:s for w,s in ends.items() if w not in WIRES and not w.startswith('W061_')}}
    intent=recipes(family,rows)
    shapes={};routes=[];files=[];hits=[]
    for row in intent:
        path,shape=build(A,Part,row)
        assert abs(path.Length-row['body_mm'])<1e-6
        shapes[row['wire']]=shape
        route_hits=scope.contacts(shape,obstacles,Part)
        hits.extend(dict(wire=row['wire'],**hit) for hit in route_hits)
        routes.append(dict(row,hits=route_hits))
        for suffix,s in (('WORLD',shape),('CENTERLINE',path)):
            p=OUT/(row['wire']+'_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
        print('FOUR_LOW_ROUTE',row['wire'],len(route_hits),round(path.Length,3),flush=True)
    joint=[]
    for a,b in combinations(WIRES,2):
        joint.extend(dict(a=a,b=b,**hit) for hit in scope.contacts(shapes[a],{b:shapes[b]},Part))
    finish=datetime.now(timezone.utc)
    pins += [BRIDGE,Path(__file__),Path(scope.__file__),
        scope.ROOT/'tools/electronics/w5_bus_low_s_material.py',
        scope.ROOT/'tools/electronics/w5_parallel_connection.py',
        scope.ROOT/'tools/electronics/w5_s1_source_layout_r2.py',
        scope.ROOT/'tools/electronics/w5_s1_source_layout_r1.py',
        scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json',dict(status='FOUR_WHOLE_LOW_GROUND_RETURNS',routes=routes,hits=hits,joint_hits=joint,
        complete=not hits and not joint,errors=[],reused=reused,printed_pending=sorted(printed),
        replacement_obligations=replaced,native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('FOUR_LOW_DONE',len(hits),len(joint),flush=True)


if __name__=='__main__':main()
