"""One provisional cutting/stock ledger for all 12 continuous leg looms.

Use received whole D/G paths and explicitly inherited V paths. No new splice,
purchase selection or physical cable fit is implied by these nominal lengths.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math
from servo_fuse_inputs_r1 import save, sha

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-leg-length-ledger-r1'


def main():
    start=datetime.now(timezone.utc)
    received=ROOT/'hardware/electronics/full-cat/w5-branch-joint-routes-r3/checks.json'
    origin=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json'
    inherited=ROOT/'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1/checks.json'
    proof=json.loads(received.read_text(encoding='utf-8'))
    assert not proof['errors'] and not proof['unresolved'] and len(proof['accepted'])==29
    chosen={r['wire']:r for r in proof['accepted']}
    inputs=json.loads(origin.read_text(encoding='utf-8'))
    old={r['wire']:r for r in json.loads(inherited.read_text(encoding='utf-8'))['routes']}
    groups={}
    for row in inputs['routes']:
        wire=row['wire'];role=row['role'];loom=row['loom'];term=row['termination']
        if role in ('D','G'):
            actual=chosen[wire]
            moving=actual['retained_moving_candidate_mm']
            assert abs(moving-row['moving_candidate_length_mm'])<1e-8
            total=actual['body_mm']+moving
            strip=term['strip_mm'];assert strip==11
            nominal=math.ceil((total+strip+30)/10)*10
            basis=received.relative_to(ROOT).as_posix()
        else:
            assert role=='V'
            actual=old[wire];assert actual['loom']==loom and actual['role']=='V'
            total=actual['continuous_external_design_mm']
            nominal=actual['provisional_far_end_blank_mm']
            strip=term.get('strip_mm') or term['end_allowance_assumption_mm']
            basis=inherited.relative_to(ROOT).as_posix()
        groups.setdefault(loom,[]).append(dict(wire=wire,role=role,body_end=row['body_end'],
            servo_end=row['servo_end'],external_candidate_mm=total,
            strip_or_end_allowance_mm=strip,unpowered_fit_reserve_mm=30,
            provisional_core_blank_mm=nominal,source=basis))
    assert len(groups)==12 and all({r['role'] for r in v}=={'D','G','V'} for v in groups.values())
    looms=[]
    for name,cores in sorted(groups.items()):
        required=max(c['provisional_core_blank_mm'] for c in cores)
        looms.append(dict(loom=name,cores=cores,common_uncut_blank_mm=required,
            nominal900_margin_mm=900-required,fits_nominal900=required<=900,
            split_and_trim_only_after_unpowered_fit=True))
    finish=datetime.now(timezone.utc)
    assert not (OUT/'ledger.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'ledger.json',dict(status='PROVISIONAL_12_LOOM_LENGTH_CONTRIBUTION_NOT_SELECTED',
        looms=looms,candidate_sku='Waveshare34172',nominal_cable_mm=900,
        cables_per_candidate_pack=6,required_continuous_cables=12,candidate_pack_quantity=2,
        candidate_nominal_cable_mm=10800,purchased=False,selected=False,
        nominal_blank_sum_mm=sum(l['common_uncut_blank_mm'] for l in looms),
        minimum_nominal_margin_mm=min(l['nominal900_margin_mm'] for l in looms),
        all_fit_nominal900=all(l['fits_nominal900'] for l in looms),new_splices=0,
        assumptions=['900mm/6pack/SKU inherited from fanout intent, not newly supplier-verified',
            'factory plug consumed length remains unknown; actual usable length must be checked',
            'actual copper area, insulation OD and moving bend radius remain unconfirmed',
            'V geometry is inherited; this ledger does not qualify the whole rejected earlier assembly',
            'routing, supports, connector access and moving bundles still require final integrated selection'],
        W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (Path(__file__),received,origin,inherited)},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print(json.dumps(dict(looms=len(looms),all_fit=all(l['fits_nominal900'] for l in looms),
        minimum_margin_mm=min(l['nominal900_margin_mm'] for l in looms))))


if __name__=='__main__':main()
