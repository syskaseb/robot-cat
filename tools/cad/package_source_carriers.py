"""Pin the complete local candidate, never count it as whole W5."""
import json
import sys
import time
from pathlib import Path
from plan_remaining_loom_roots import ROOT,OUT,sha


def run():
    tick=time.monotonic()
    front='--front-clearance' in sys.argv
    rf=OUT/('front-fixed-port-clearance-native.json' if front else 'complete-source-carriers-native.json')
    receipt=json.loads(rf.read_text())
    assert receipt['status']==('FRONT_FIXED_PORT_CLEARANCE_NATIVE_PREPARED_W5_OPEN' if front else 'FOUR_HIP_SOURCE_CARRIERS_NATIVE_PREPARED_W5_OPEN')
    assert not receipt['selected'] and not receipt['W5_complete'] and not receipt['physical_pass']
    assert receipt['relocated_reopen'] and receipt['parameter_restore_mm']==([.4,.5,.4] if front else [4,4.2,4])
    assert len(receipt['exports'])==4 and len(receipt['root_contact_faces'])==4
    sketches=receipt.get('fully_constrained_sketches',receipt.get('retained_native_sketches',0)+receipt.get('added_fully_constrained_sketches',0))
    assert sketches==(258 if front else 252)
    files={rf.relative_to(ROOT).as_posix():sha(rf)}
    # Pin the actual received geometry receipts and their direct run inputs.
    # Historical wiring's embedded build-card generator is not executed by
    # this carrier build. Its stale provenance cannot certify today's BOM,
    # and recursively treating it as current would be a false global audit.
    actual_receipts=[rf,OUT/'source-carrier-port-bridges-material.json',
                     OUT/'complete-source-carriers-material.json',
                     OUT/'complete-source-carriers-plan.json',
                     OUT/'leg-source-near-member-plan-material.json']
    if front:actual_receipts += [OUT/'front-fixed-port-clearance.json',OUT/'complete-source-carriers-native.json']
    pending=[]
    for actual in actual_receipts:
        files[actual.relative_to(ROOT).as_posix()]=sha(actual)
        pending.extend((n,h,actual.parent) for n,h in json.loads(actual.read_text())['source_sha256'].items())
    pending += [(receipt['native'],receipt['native_sha256'],ROOT)]
    pending += [(r['path'],r['sha256'],ROOT) for r in receipt['exports']]
    while pending:
        name,digest,declaring_dir=pending.pop()
        path=ROOT/name
        if not path.is_file() and '/' not in name:
            # Historical wiring-p0 provenance names neighboring documents.
            # Resolve against the declaring JSON, never an arbitrary search.
            path=declaring_dir/name
            name=path.relative_to(ROOT).as_posix()
        if name in files:
            assert files[name]==digest,name
            continue
        assert sha(path)==digest,name
        files[name]=digest
    for r in receipt['exports']:
        assert r['quantity']==1 and max(r['size_mm'])+2*r['brim_each_mm']<256
    for r in receipt['root_contact_faces']:
        assert r['bond_case_area_mm2']>40 and r['carrier_bond_area_mm2']>49.9
    gate=OUT/'source-carrier-port-bridges-material.json'
    data=json.loads(gate.read_text())
    assert data['pairs']==158 and not data['contacts'] and not data['errors']
    evidence=[rf.relative_to(ROOT).as_posix(),gate.relative_to(ROOT).as_posix()]
    gates={name:dict(status='open',reason=reason) for name,reason in {
        'assembly':'Local unpowered assembly instructions recorded. Whole wiring/order and remaining supports still OPEN.',
        'fit':'Delivered cable/case, replaceable PETG fit and adhesive compatibility are phase2 gates.',
        'petg':'Brim allowance checked; print orientation/support/profile and coupon trials remain OPEN.',
        'loads':'Case bond peel/load/creep and long arm stiffness are not physically qualified.',
        'electrical':'No full W5/E3 or live acceptance; source-owned extensions and body fanouts remain OPEN.',
        'service':'Support wires, cut dedicated bands and remove compatible case bond; whole sequence OPEN.'}.items()}
    gates['geometry']=dict(status='pass',reason='Exact changed-material158pairs plus inherited pinned subset. Native identity, parameter restore, relocated reopen and4closed meshes verified.',evidence=evidence)
    if front:
        fg=OUT/'front-fixed-port-clearance.json';f=json.loads(fg.read_text())
        assert f['status']=='FRONT_FIXED_PORT_CLEARANCE_SUBSET_NATIVE_OPEN' and not f['errors']
        gates['geometry']['evidence'].append(fg.relative_to(ROOT).as_posix())
        gates['geometry']['reason']+=' Front0.4mmpockets are a subset; all caps/lands/old branch cores unchanged and fixed ports clear in3Hip samples. Six new native pockets and depth0.4/0.5/0.4 checked.'
    manifest=dict(schema_version=1,readiness='prototype',
        scope='Four local Hip source carriers only; complete native candidate, not selected whole W5 or print approval.',
        selected=False,W5_complete=False,physical_pass=False,
        provenance_limit='Actual geometry receipt inputs only. Historical wiring-p0 generator p0_build_card.py has changed since its embedded provenance hash; this does not qualify current global wiring/BOM. Current received wire recipes and actual scene bytes are pinned, not regenerated by that historical generator.',
        files=[dict(path=n,sha256=h) for n,h in sorted(files.items())],gates=gates,
        source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    path=OUT/'source-carriers-fixed-interface/manifest.json' if front else OUT/'source-carriers-manifest.json'
    path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(files),native_worker_seconds=receipt['worker_seconds'],
                         fully_constrained_sketches=sketches,
                         worker_seconds=manifest['worker_seconds'],W5_complete=False)))


if __name__=='__main__':
    run()
