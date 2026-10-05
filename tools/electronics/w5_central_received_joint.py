"""Receive five complete central conductors without duplicating their CAD.

This is not W5 completion: four central conductors and native construction
remain open. The rear two proof's only XA05 contacts are superseded by the
whole, jointly clear AUX receipt; its rejected front pair is NOT inherited.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
from servo_fuse_inputs_r1 import save,sha

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-central-received-joint-r1'
BASE=ROOT/'hardware/electronics/full-cat'


def main():
    start=datetime.now(timezone.utc)
    assert not (OUT/'received.json').exists()
    paths={
        'family':BASE/'w5-central-bridge-low-arc-r1/received-family.json',
        'bridge':BASE/'w5-central-south-bridge-r1/checks.json',
        'rear':BASE/'w5-four-low-returns-r1/checks.json',
        'aux':BASE/'w5-aux-diagonal-loop-r3/checks.json'}
    data={k:json.loads(p.read_text(encoding='utf-8')) for k,p in paths.items()}
    pins=[Path(__file__),ROOT/'tools/electronics/servo_fuse_inputs_r1.py',*paths.values()]
    for key,receipt in data.items():
        for rel,digest in {**receipt.get('source_sha256',{}),**receipt.get('files',{})}.items():
            assert sha(ROOT/rel)==digest,rel
            pins.append(ROOT/rel)
    assert data['bridge']['bridge_complete'] and not data['bridge']['hits']
    assert data['aux']['complete'] and not data['aux']['hits'] and not data['aux']['errors']
    assert all(h['owner']=='XA05' for h in data['rear']['hits'] if h['wire'] in ('W062','W063'))
    assert not any({h['a'],h['b']}=={'W062','W063'} for h in data['rear']['joint_hits'])
    routes={
        'W001':dict(receipt=paths['family'].relative_to(ROOT).as_posix(),
                     geometry=(paths['family'].parent/'W001_FULL_RECEIVED.brep').relative_to(ROOT).as_posix(),
                     nominal_mm=data['family']['whole_W001']['nominal_mm']),
        'W061':dict(receipt=paths['bridge'].relative_to(ROOT).as_posix(),
                     geometry=(paths['bridge'].parent/'W061_WORLD.brep').relative_to(ROOT).as_posix(),
                     nominal_mm=data['bridge']['nominal_mm']),
        'XA05':dict(receipt=paths['aux'].relative_to(ROOT).as_posix(),
                     geometry=(paths['aux'].parent/'XA05_WORLD.brep').relative_to(ROOT).as_posix(),
                     nominal_mm=data['aux']['recipe']['nominal_mm'])}
    for wire in ('W062','W063'):
        row=next(r for r in data['rear']['routes'] if r['wire']==wire)
        routes[wire]=dict(receipt=paths['rear'].relative_to(ROOT).as_posix(),
            geometry=(paths['rear'].parent/(wire+'_WORLD.brep')).relative_to(ROOT).as_posix(),
            nominal_mm=row['nominal_mm'])
    pins += [ROOT/r['geometry'] for r in routes.values()]
    OUT.mkdir(parents=True,exist_ok=True)
    finish=datetime.now(timezone.utc)
    save(OUT/'received.json',dict(status='FIVE_WHOLE_CENTRAL_ROUTES_RECEIVED',routes=routes,
        inherited_rear_old_XA05_contacts_superseded_by_whole_joint_aux=True,
        remaining_central=['W025','W036','W060','W003'],unchanged_leg_backbone_paths=28,
        printed_pending=data['bridge']['printed_pending'],replacement_obligations=data['bridge']['replacement_obligations'],
        W1_complete=False,W5_complete=False,native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)}))
    print('CENTRAL_RECEIVED',len(routes),'REMAINING',4,flush=True)


if __name__=='__main__':main()
