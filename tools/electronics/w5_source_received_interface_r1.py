"""Receive changed source interfaces without repeating unchanged CAD pairs."""
from pathlib import Path
from datetime import datetime,timezone
import json
from servo_fuse_inputs_r1 import sha,save
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-source-received-interface-r1'

def main():
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    paths=[ROOT/'hardware/electronics/full-cat'/name/'checks.json' for name in (
        'w5-s1-source-check-r8','w5-source-carrier-native-r1',
        'w5-source-bank-passage-native-r1','w5-source-cover-passages-native-r1')]
    rows=[json.loads(p.read_text(encoding='utf-8')) for p in paths]
    for row in rows:assert all(sha(ROOT/k)==v for k,v in {**row['source_sha256'],**row['files']}.items())
    source=rows[0]
    assert len(source['hits'])==10 and not source['errors']
    assert set(h['owner'] for h in source['hits'])=={'Cover','BankLeft'}
    assert [r['wire'] for r in source['routes']]==['W064','W065','W067','W068','XA01']
    for r in rows[1:]:
        assert not r['hits'] and not r.get('errors',[]) and r['solids']==1 and r['strict_BOP_errors']==0
        assert r['parameter_recompute'] and r['relocated_reopen'] and r['closed_STL']
    for r in rows[2:]:assert r['source_sha256'][paths[0].relative_to(ROOT).as_posix()]==sha(paths[0])
    carrier_path=ROOT/'hardware/cad/studies/w5-source-carrier-native-r1/Carrier_WORLD.brep'
    assert source['received_native_carrier_passages'] and source['source_sha256'][carrier_path.relative_to(ROOT).as_posix()]==sha(carrier_path)
    end=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'checks.json',dict(status='FIVE_SOURCE_ROUTE_STATIC_INTERFACE_CLEAR_SUPPORTS_SERVICE_OPEN',
        transfer_reason='R8 covers unchanged owners plus received Carrier; only ten contacts were Cover/BankLeft. Exact native subtractive replacements separately clear all five routes and preserve parent mounts. No added material, electrical parts or fasteners.',
        route_wires=[r['wire'] for r in source['routes']],route_trial_mm={r['wire']:r['nominal_trial_blank_mm'] for r in source['routes']},
        S1_trial_total_mm=sum(r['nominal_trial_blank_mm'] for r in source['routes'][:4]),legacy_S1_mm=920,
        exact_TE_reference=True,S1_casing_and_ring_seats_provisional=True,
        original_R8_pairs=source['pairs'],changed_cover_pairs=rows[3]['pairs'],changed_bank_pairs=rows[2]['pairs'],
        replacement_prints={'Carrier':1,'BankLeft':1,'Cover':1},added_parts=0,new_fasteners=0,
        hits=[],errors=[],selected=False,W5_complete=False,physical_pass=False,
        rejected_leg_fanouts_R5_not_qualified=True,
        open=['Native insulation grips and source-end restraints; above-Cover protection and E6 appearance.',
            'Complete source/Carrier/Bank/Cover staged mounting and continuous removal against the changed wires.',
            'One whole-family selection and SKU/stock reconciliation, including replacement of legacy920mm.',
            'XA01 complete prefuse length includes unknown holder internal path; do not set it to0.'],
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in [Path(__file__),*paths]},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('SOURCE_FIVE_ROUTE_RECEIPT_CLEAR_SUPPORTS_SERVICE_OPEN',flush=True)

if __name__=='__main__':main()
