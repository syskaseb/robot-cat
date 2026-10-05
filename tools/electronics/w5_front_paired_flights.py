"""One coordinated pair of front returns, not two independent riser searches.

Keep the clear cage preparations. Turn south immediately below XL01; FL
goes west at161.5mm and rises8mm in its west flight. FR rises8mm before
crossing W061's south bend, then goes around the south side. Both arrive
at the actual169.5mm leg cages with6mm straight necks and exact arcs.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import math
import w5_received_central_scope as received
import w5_central_shared_routes as scope
from w5_s1_source_layout_r2 import CentreLine
from w5_parallel_connection import connect
from w5_bus_low_s_material import build
from servo_fuse_inputs_r1 import save,sha

OUT=scope.ROOT/'hardware/electronics/full-cat/w5-front-paired-flights-r1'


def recipes(family,rows):
    rows={r['wire']:r for r in rows};result=[]
    for wire in ('W025','W036'):
        a=family['ends'][wire];target=rows[wire]['b_datum']['point_mm']
        c=CentreLine(a['tip'],[0,0,1]);c.arc([0,-1,0],radius=21)
        if wire=='W025':
            c.arc([-1,0,0],radius=21)
            before_turn=[target[0]-6,c.p[1],target[2]]
            c.edges.extend(connect(c.p,before_turn,[-1,0,0],21));c.p=before_turn;c.t=[-1,0,0]
            radius=(target[1]-c.p[1])/2
            assert radius>=21
            c.arc([0,1,0],radius=radius);c.arc([1,0,0],radius=radius)
        else:
            rise_end=[c.p[0],c.p[1]-55,target[2]]
            c.edges.extend(connect(c.p,rise_end,[0,-1,0],21));c.p=rise_end;c.t=[0,-1,0]
            c.line([c.p[0],target[1]-21,c.p[2]])
            c.arc([-1,0,0],radius=21)
            c.line([target[0]-6,c.p[1],c.p[2]])
            c.arc([0,1,0],radius=21);c.arc([1,0,0],radius=21)
        c.line(target)
        assert math.dist(c.p,target)<1e-7 and math.dist(c.t,[1,0,0])<1e-7
        edges=a['edges']+c.edges
        body=sum(e['length_mm'] for e in edges)
        result.append(dict(wire=wire,edges=edges,OD_mm=4.2,radius_mm=21,
            body_mm=body,nominal_mm=body+25,trial_blank_mm=math.ceil((body+25+30)/10)*10,
            central_start=edges[0]['start'],leg_target=target,cage_neck_mm=6,
            leg_approach='same-height outer U',factory_geometry_provisional=True))
    return result


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    fixed,printed,ends,family,rows,pins,reused,replaced=received.load(A,Part)
    obstacles={**fixed,**{w:s for w,s in ends.items() if w not in ('W025','W036')}}
    proposed=recipes(family,rows);shapes={};hits=[];files=[];route_rows=[]
    for row in proposed:
        path,shape=build(A,Part,row);shapes[row['wire']]=shape
        route_hits=scope.contacts(shape,obstacles,Part)
        hits.extend(dict(wire=row['wire'],**h) for h in route_hits)
        route_rows.append(dict(row,hits=route_hits))
        for suffix,s in (('WORLD',shape),('CENTERLINE',path)):
            p=OUT/(row['wire']+'_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
        print('FRONT_PAIRED_ROUTE',row['wire'],len(route_hits),round(path.Length,3),flush=True)
    joint=scope.contacts(shapes['W025'],{'W036':shapes['W036']},Part)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),Path(scope.__file__),Path(received.__file__),
        scope.ROOT/'tools/electronics/w5_parallel_connection.py',
        scope.ROOT/'tools/electronics/w5_bus_low_s_material.py',
        scope.ROOT/'tools/electronics/w5_s1_source_layout_r1.py',scope.ROOT/'tools/electronics/w5_s1_source_layout_r2.py',
        scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json',dict(status='TWO_WHOLE_FRONT_RETURNS_PAIRED_FLIGHTS',routes=route_rows,hits=hits,
        joint_hits=joint,complete=not hits and not joint,errors=[],printed_pending=sorted(printed),
        replacement_obligations=replaced,native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('FRONT_PAIRED_DONE',len(hits),len(joint),flush=True)


if __name__=='__main__':main()
