"""Close the two low rear returns jointly with their only obstacle, XA05.

The received four-return proof rejects the front pair, but each rear whole
route touches only the old unselected AUX departure. Preserve those rear
routes and qualify one whole AUX path; do not search the rear lanes again.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import time
import w5_central_shared_routes as scope
from w5_central_remaining_routes import choices
from w5_coupled_corridors import prefix
from w5_ground_network_r1 import from_recipe
from servo_fuse_inputs_r1 import save,sha

OUT=scope.ROOT/'hardware/electronics/full-cat/w5-rear-aux-low-joint-r1'
REAR=scope.ROOT/'hardware/electronics/full-cat/w5-four-low-returns-r1/checks.json'
BRIDGE=scope.ROOT/'hardware/electronics/full-cat/w5-central-south-bridge-r1/checks.json'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);tic=time.monotonic()
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    rear=json.loads(REAR.read_text(encoding='utf-8'))
    assert not rear['errors']
    assert all(h['owner']=='XA05' for h in rear['hits'] if h['wire'] in ('W062','W063'))
    assert not any({h['a'],h['b']}=={'W062','W063'} for h in rear['joint_hits'])
    fixed,printed,ends,family,rows,pins,reused,replaced=scope.load_scope(A,Part)
    for receipt_path in (REAR,BRIDGE):
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        for rel,digest in receipt['files'].items():
            assert sha(scope.ROOT/rel)==digest,rel
            pins.append(scope.ROOT/rel)
        pins.append(receipt_path)
    for wire,folder in (('W061',BRIDGE.parent),('W062',REAR.parent),('W063',REAR.parent)):
        fixed[wire]=Part.read(str(folder/(wire+'_WORLD.brep')))
    obstacles={**fixed,**{w:s for w,s in ends.items() if w not in ('W062','W063','XA05') and not w.startswith('W061_')}}
    row=next(r for r in rows if r['wire']=='XA05')
    proposed=[c for orientation in ('up','left','right')
              for c in choices(row,family['ends']['XA05'],prefix(row['b_datum'],'XA05',orientation))]
    proposed.sort(key=lambda c:sum(__import__('math').dist(a,b) for a,b in zip(c['middle'],c['middle'][1:])))
    attempts=[];chosen=None;files=[]
    for candidate in proposed:
        if time.monotonic()-tic>120:break
        path,shape=from_recipe(A,Part,candidate)
        hits=scope.contacts(shape,obstacles,Part)
        attempts.append(dict(recipe=candidate,hits=hits,body_mm=path.Length))
        if not hits:
            chosen=dict(recipe=candidate,body_mm=path.Length,nominal_mm=path.Length+22)
            for suffix,s in (('WORLD',shape),('CENTERLINE',path)):
                p=OUT/('XA05_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
            break
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),Path(scope.__file__),
        scope.ROOT/'tools/electronics/w5_central_remaining_routes.py',
        scope.ROOT/'tools/electronics/w5_coupled_corridors.py',
        scope.ROOT/'tools/electronics/w5_ground_network_r1.py',
        scope.ROOT/'tools/electronics/w5_rounded_path.py',
        scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json',dict(status='REAR_TWO_RETURNS_AND_AUX_JOINT',complete=chosen is not None,
        rear_whole_routes=['W062','W063'],rear_inherited_scope_proof=REAR.relative_to(scope.ROOT).as_posix(),
        solution=chosen,attempts=attempts,errors=[],reused=reused,printed_pending=sorted(printed),
        replacement_obligations=replaced,native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('REAR_AUX_JOINT_DONE',chosen is not None,len(attempts),flush=True)


if __name__=='__main__':main()
