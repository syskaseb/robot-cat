"""Qualify the complete low BUS ground path against received material.

The old unselected W003 departure is replaced, not kept as an obstacle.
Printed reconstruction obligations are reported separately.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import w5_central_shared_routes as scope
from servo_fuse_inputs_r1 import save, sha

OUT = scope.ROOT/'hardware/electronics/full-cat/w5-bus-low-s-material-r1'
PLAN = scope.ROOT/'hardware/electronics/full-cat/w5-bus-low-s-plan-r1/intent.json'
BRIDGE = scope.ROOT/'hardware/electronics/full-cat/w5-central-south-bridge-r1/checks.json'


def build(A, Part, recipe):
    edges = [Part.makeLine(A.Vector(*e['start']), A.Vector(*e['end'])) if e['kind']=='line'
             else Part.Arc(A.Vector(*e['start']), A.Vector(*e['mid']), A.Vector(*e['end'])).toShape()
             for e in recipe['edges']]
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length < 1e-7
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length < 1e-7
    parts = [Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(recipe['OD_mm']/2,
             e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False) for e in edges]
    assert all(s.isValid() and len(s.Solids)==1 and not s.check(True) for s in parts)
    return Part.Wire(edges),Part.makeCompound(parts)


def main():
    import FreeCAD as A, Part
    start = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    for rel,digest in plan['source_sha256'].items():
        assert sha(scope.ROOT/rel)==digest,rel
    fixed,printed,ends,family,rows,pins,reused,replaced = scope.load_scope(A,Part)
    bridge = json.loads(BRIDGE.read_text(encoding='utf-8'))
    assert bridge['bridge_complete'] and not bridge['hits']
    for rel,digest in bridge['files'].items():
        assert sha(scope.ROOT/rel)==digest,rel
        pins.append(scope.ROOT/rel)
    fixed['W061']=Part.read(str(BRIDGE.parent/'W061_WORLD.brep'))
    path,shape=build(A,Part,plan['recipe'])
    assert abs(path.Length-plan['recipe']['body_mm'])<1e-6
    obstacles={**fixed,**{w:s for w,s in ends.items() if w!='W003' and not w.startswith('W061_')}}
    hits=scope.contacts(shape,obstacles,Part)
    witnesses=[]
    for hit in hits:
        common=shape.common(obstacles[hit['owner']]);b=common.BoundBox
        hit['witness_bbox_mm']=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
        p=OUT/('contact_'+str(len(witnesses))+'.brep');common.exportBrep(str(p));witnesses.append(p)
    files=list(witnesses)
    for suffix,s in (('WORLD',shape),('CENTERLINE',path)):
        p=OUT/('W003_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins += [PLAN,BRIDGE,Path(__file__),Path(scope.__file__),
             scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json',dict(status='WHOLE_BUS_GROUND_MATERIAL_CHECK',recipe=plan['recipe'],
        hits=hits,errors=[],route_complete=not hits,reused=reused,printed_pending=sorted(printed),
        replacement_obligations=replaced,native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('BUS_LOW_MATERIAL_DONE',len(hits),round(path.Length,3),flush=True)


if __name__=='__main__':main()
