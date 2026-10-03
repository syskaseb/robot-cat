"""One current local ledger:53installed,49replacement service loops.

The shared lift must be clear before accepting the local service allowance.
This does not turn historical whole-robot allowances into an actual census.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    t=datetime.now(timezone.utc);pins={}
    def read(rel):p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    j=read('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r6/stock.json')
    service=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json')
    native=read('hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-native-r1/checks.json')
    assert not service['hits'] and not service['errors'] and service['completed_clear_lifts_mm']==[2,5,10,30,60,100]
    assert service['FR_guard_owner']=='FIXED_DECK_WITH_2SCREWS_2NUTS' and service['total_service_ties_cut']==49
    assert native['added_prints']==native['added_fasteners']==native['added_wires']==native['added_ties']==0
    groups=j['T18I']['local_groups']
    for row in groups:row['removal_replacements']=0 if row['role']=='fixed_lower_input_feeds' else row['installed']
    assert sum(r['installed'] for r in groups)==53 and sum(r['removal_replacements'] for r in groups)==49
    j['T18I'].update(local_removal_replacement_allowance=49,FR_source_loops_cut=2,all_source_loops_cut=6,
        P_WAGO_body_ties_cut_for_bank_removal=4,main_MTA_body_ties_cut_for_bank_removal=6,
        service_allowance_status='NOMINAL_SHARED_SAMPLED_SEQUENCE_ACCEPTED_PHYSICAL_PHASE2',local_installed_plus_one_removal=102,
        whole_robot_installed_census_qualified=False)
    j['fixed_FR_guard']=dict(owner='Deck',additional_prints=0,additional_fasteners=0,existing_M3x8=2,existing_M3nuts=2,
        new_axes_xz_mm=native['axes_xz_mm'],fasteners_horizontal=True,Deck_total_brim_allowance_mm=6)
    j.update(replaces='stock-r6 superseded only by current local service49loops, not33;53installed unchanged. Never add variants or call historical global104an actual census.',
        status='CURRENT_LOCAL_BANK_LEDGER_NOMINAL_SERVICE_ACCEPTED_WHOLE_STOCK_OPEN',source_sha256=pins,script_sha256=sha(Path(__file__)),
        started_utc=t.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat())
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r7';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'stock.json').exists();save(out/'stock.json',j);print('LOCAL_BANK_CURRENT_STOCK',53,49,flush=True)
if __name__=='__main__':main()
