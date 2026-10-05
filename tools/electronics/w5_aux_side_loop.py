"""Whole AUX route bypassing both rear departures on their south side.

The45 upper-route failures share an obstructed initial AUX preparation.
Replace that preparation with a horizontal departure; no height search.
"""
from datetime import datetime,timezone
from pathlib import Path
import json
import math
import w5_central_shared_routes as scope
from w5_s1_source_layout_r2 import CentreLine
from w5_bus_low_s_material import build
from servo_fuse_inputs_r1 import save,sha

OUT=scope.ROOT/'hardware/electronics/full-cat/w5-aux-side-loop-r1'
REAR=scope.ROOT/'hardware/electronics/full-cat/w5-four-low-returns-r1/checks.json'
BRIDGE=scope.ROOT/'hardware/electronics/full-cat/w5-central-south-bridge-r1/checks.json'


def recipe(family,target):
    start=family['ends']['XA05']['edges'][0]['start']
    c=CentreLine(start,[1,0,0]);c.line([start[0]+6,start[1],start[2]])
    c.arc([0,-1,0],radius=15);c.line([c.p[0],target[1]-30,c.p[2]])
    c.arc([-1,0,0],radius=15);c.line([target[0]-30,c.p[1],c.p[2]])
    c.arc([0,1,0],radius=15);c.line([c.p[0],target[1]-15,c.p[2]])
    c.arc([1,0,0],radius=15);c.line(target)
    assert math.dist(c.p,target)<1e-7
    length=sum(e['length_mm'] for e in c.edges)
    return dict(wire='XA05',edges=c.edges,OD_mm=2.5,radius_mm=15,body_mm=length,
        nominal_mm=length+22,trial_blank_mm=math.ceil((length+22+30)/10)*10,
        old_upper_AUX_prefix_replaced=True,start=start,target=target)


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    fixed,printed,ends,family,rows,pins,reused,replaced=scope.load_scope(A,Part)
    for receipt_path in (REAR,BRIDGE):
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        for rel,digest in receipt['files'].items():
            assert sha(scope.ROOT/rel)==digest
            pins.append(scope.ROOT/rel)
        pins.append(receipt_path)
    for wire,folder in (('W061',BRIDGE.parent),('W062',REAR.parent),('W063',REAR.parent)):
        fixed[wire]=Part.read(str(folder/(wire+'_WORLD.brep')))
    obstacles={**fixed,**{w:s for w,s in ends.items() if w not in ('W062','W063','XA05') and not w.startswith('W061_')}}
    target=next(r for r in rows if r['wire']=='XA05')['b_datum']['point_mm']
    row=recipe(family,target);path,shape=build(A,Part,row)
    hits=scope.contacts(shape,obstacles,Part)
    files=[]
    for suffix,s in (('WORLD',shape),('CENTERLINE',path)):
        p=OUT/('XA05_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),Path(scope.__file__),scope.ROOT/'tools/electronics/w5_bus_low_s_material.py',
        scope.ROOT/'tools/electronics/w5_s1_source_layout_r2.py',scope.ROOT/'tools/electronics/w5_s1_source_layout_r1.py',
        scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json',dict(status='WHOLE_AUX_SIDE_LOOP_AND_REAR_RETURNS',recipe=row,hits=hits,errors=[],
        complete=not hits,rear=['W062','W063'],printed_pending=sorted(printed),replacement_obligations=replaced,
        native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('AUX_SIDE_LOOP_DONE',len(hits),round(path.Length,3),flush=True)


if __name__=='__main__':main()
