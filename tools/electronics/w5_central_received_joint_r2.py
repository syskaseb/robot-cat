"""Receive all nine whole central paths, checking the changed four together.

Five prior whole paths are immutable inherited proofs, not rebuilt CAD.
Only the new four are checked mutually here; their foreign scope checks
already include those five and the28 retained leg/backbone paths.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_central_shared_routes as scope
from servo_fuse_inputs_r1 import sha,save

ROOT=scope.ROOT;BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-central-received-joint-r2'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'received.json').exists()
    prior_path=BASE/'w5-central-received-joint-r1/received.json'
    prior=json.loads(prior_path.read_text(encoding='utf-8'))
    routes=dict(prior['routes']);pins=[prior_path,Path(__file__),Path(scope.__file__)]
    shapes={};proofs={}
    for folder,wires in (
        ('w5-front-paired-flights-r2',('W025','W036')),
        ('w5-main-ground-low-return-r3',('W060',)),
        ('w5-bus-factory900-r4',('W003',))):
        p=BASE/folder/'checks.json';proof=json.loads(p.read_text(encoding='utf-8'))
        assert proof['complete'] and not proof['errors'],folder
        proofs[folder]=proof;pins.append(p)
        for wire in wires:
            geometry=BASE/folder/(wire+'_WORLD.brep');shapes[wire]=Part.read(str(geometry))
            if wire in ('W025','W036'):row=next(r for r in proof['routes'] if r['wire']==wire)
            elif wire=='W060':row=proof
            else:row=proof['recipe']
            routes[wire]=dict(receipt=p.relative_to(ROOT).as_posix(),geometry=geometry.relative_to(ROOT).as_posix(),
                nominal_mm=row['nominal_mm'],trial_blank_mm=row['trial_blank_mm'])
    for receipt in [prior,*proofs.values()]:
        for rel,digest in {**receipt.get('source_sha256',{}),**receipt.get('files',{})}.items():
            assert sha(ROOT/rel)==digest,rel;pins.append(ROOT/rel)
    hits=[];pairs=0
    keys=list(shapes)
    for i,a in enumerate(keys):
        for b in keys[i+1:]:
            pairs+=1
            for hit in scope.contacts(shapes[a],{b:shapes[b]},Part):hits.append(dict(a=a,b=b,**hit))
    assert len(routes)==9
    OUT.mkdir(parents=True,exist_ok=True);finish=datetime.now(timezone.utc)
    save(OUT/'received.json',dict(status='NINE_WHOLE_CENTRAL_PATHS_RECEIVED' if not hits else 'JOINT_CONFLICT',
        routes=routes,changed_mutual_pairs=pairs,changed_mutual_hits=hits,complete=not hits,
        remaining_central=[],unchanged_leg_backbone_paths=28,
        printed_pending=prior['printed_pending'],replacement_obligations=prior['replacement_obligations'],
        stock_BUS900_candidate=proofs['w5-bus-factory900-r4']['stock_change'],
        provisional_BUS_diameter_radius_and_delivered_length=True,
        W1_complete=False,W5_complete=False,native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)}))
    print('CENTRAL_RECEIVED',len(routes),'PAIRS',pairs,'HITS',len(hits),flush=True)


if __name__=='__main__':main()
