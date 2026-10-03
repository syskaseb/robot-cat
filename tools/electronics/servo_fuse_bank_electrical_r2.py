"""Carry the final local twelve-input blanks and24ends into E3 contribution.

A pinned inherited copper sensitivity model is NOT a fuse/ampacity approval.
No duplicate output lead/splice; no change to the selected whole R51 stock.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    start=datetime.now(timezone.utc);pins={}
    def read(rel):
        p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    old=read('hardware/electronics/full-cat/servo-fuse-bank-electrical-r1/interface.json')
    loop=read('hardware/electronics/full-cat/servo-fuse-lower-loop-materials-r1/materials.json')
    stock=read('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r6/stock.json')
    exits=read('hardware/electronics/full-cat/servo-fuse-output-clamps-fit-r1/checks.json')
    assert not exits['hits'] and not exits['errors']
    assert old['input_ends']==old['output_ends']==12 and len(old['ends'])==24
    blanks={r['wire']:r['nominal_blank_mm'] for r in loop['rows']}
    assert len(blanks)==12 and sum(blanks.values())==2880
    model=old['copper_model'];rho=model['rho20_Ohm_mm2_per_m']*(1+model['alpha_per_K']*(model['assumed_temperature_C']-20))
    updated=[]
    for r in old['input_losses']:
        length=blanks[r['id']];resistance=rho*(length/1000)/model['nominal_area_mm2']
        updated.append(dict(id=r['id'],nominal_blank_mm=length,actual_cut_mm=None,
            conductor_R60_mOhm=resistance*1000,
            sensitivity=[dict(assumed_current_A=i,voltage_mV=i*resistance*1000,conductor_loss_mW=i*i*resistance*1000) for i in (2.7,4,10)],
            excludes=['fuse','terminals','return','contact resistance'],source='Inherited Cu model applied to current blank, not delivered-wire rating.'))
    for r in old['ends']:
        if r['id'].endswith('.out'):
            r['restraint']='Integral upper keeper and oneT18I around intact insulation; bottom-open exit, no additional splice. Cut and replace strap for bank removal.'
        assert r['wire_id']
    end=datetime.now(timezone.utc)
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-electrical-r2';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'interface.json').exists()
    save(out/'interface.json',dict(status='CURRENT_LOCAL_24_ENDS_AND_E3_CONTRIBUTION_FULL_E3_OPEN',
        selected=False,physical_pass=False,E3_complete=False,W5_complete=False,
        input_ends=12,output_ends=12,ends=old['ends'],input_losses=updated,copper_model=model,
        LAPP0107001=stock['LAPP0107001'],HELU23802=stock['HELU23802'],
        whole_stock_changed=False,topology_changed=False,
        unresolved=['Whole source/branch protection-selection data are not completed by this local construction.',
            'Manufacturer maximum resistance, bundled admissible current and short-circuit coordination are not proved by the Cu sensitivity model.',
            'Delivered factory servo leads/terminals/blade engagement must be matched at phase2; no solder added to crimp terminals.',
            'Four source roles W064/W065/W067/W068 remain outside this local scope and unqualified.',
            'Do not power hardware on the authority of this local contribution.'],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('CURRENT_LOCAL_ELECTRICAL_RECEIPT',24,2880,stock['LAPP0107001']['nominal_total_mm'],flush=True)

if __name__=='__main__':main()
