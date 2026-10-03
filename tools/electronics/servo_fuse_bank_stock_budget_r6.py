"""Four P-WAGO body ties included once;33service cuts remain a candidate.

Keep R51 whole-stock untouched. The original four P-block retention roles
are replaced, not an additional four on top of their eventual global census.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    start=datetime.now(timezone.utc);p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r5/stock.json'
    j=json.loads(p.read_text(encoding='utf-8'));pins={p.relative_to(ROOT).as_posix():sha(p)}
    wp=ROOT/'hardware/electronics/full-cat/servo-fuse-p-wago-retention-r3/checks.json'
    w=json.loads(wp.read_text(encoding='utf-8'));pins[wp.relative_to(ROOT).as_posix()]=sha(wp)
    assert w['static_contacts']==0 and not w['errors'] and len(w['blocks'])==4
    groups=j['T18I']['local_groups'];assert sum(r['installed'] for r in groups)==49
    groups.append(dict(role='four_native_slot_P_WAGO_bodies',installed=4,removal_replacements=0,
        replaces_existing_global_four_P_block_tie_roles=True))
    target=next(r for r in groups if r['role']=='FR_RL_RR_output_cage_and_two_insulated_ends')
    assert target['installed']==9;target['removal_replacements']=9
    j['T18I'].update(local_installed_known=53,local_removal_replacement_allowance=33,
        FR_source_loops_cut=0,fixed_RR_output_ties_cut_for_bank_removal=3,
        output_cage_and_insulation_ties_cut=9,P_WAGO_body_ties_cut_for_bank_removal=0,
        missing_groups=[],service_allowance_status='CANDIDATE_UNTIL_SHARED_RELEASE_ACCEPTED',
        whole_robot_installed_census_qualified=False)
    assert sum(r['installed'] for r in groups)==53 and sum(r['removal_replacements'] for r in groups)==33
    end=datetime.now(timezone.utc)
    j.update(replaces='stock-r5 local49replaced by53including4P-WAGO roles; not an additive quantity. Service33rather than24is provisional until shared release.',
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r6';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'stock.json').exists();save(out/'stock.json',j)
    print('LOCAL_BANK_STOCK_CANDIDATE',53,33,flush=True)

if __name__=='__main__':main()
