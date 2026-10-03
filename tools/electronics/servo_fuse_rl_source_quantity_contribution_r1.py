"""Reconcile one RL source replacement, without selecting the whole bank."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    paths=dict(station=ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-station-native-r5/checks.json',
        route=ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-complete-r2/checks.json',
        prior=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2/checks.json',
        stock=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json')
    data={k:json.loads(p.read_text(encoding='utf-8')) for k,p in paths.items()}
    s=data['station'];assert not s['hits'] and not s['errors'] and s['additional_T18I']==2
    assert all(r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen'] for r in s['exports'])
    tie=next(r for r in data['stock']['lines'] if r['id']=='tie:111-02370')
    assert tie['dimensions_mm']==dict(length=145,width=2.5,thickness=1.2,head_length=4.8,head_width=4.5,height_H=3.5)
    old=next(r for r in data['prior']['routes'] if r['id']=='W044_extension')
    rows={r['id']:r for r in data['route']['routes']};new=rows['W044_extension'];factory=rows['W044_factory']
    joint=next(r for r in data['route']['joints'] if r['id']=='W044')
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-quantity-contribution-r1';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'checks.json').exists()
    save(out/'checks.json',dict(status='RL_ADDITIVE_CANDIDATE_CONTRIBUTION_COMPLETE',selected=False,physical_pass=False,W5_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths.values()},script_sha256=sha(Path(__file__)),
        additional_T18I_installed=2,tie_SKU='111-02370',tie_stock_length_mm=145,
        HELU23802=dict(role='W044_extension',old_blank_mm=old['stock_blank_mm'],replacement_blank_mm=new['stock_blank_mm'],
            delta_blank_mm=new['stock_blank_mm']-old['stock_blank_mm'],no_additional_duplicate_wire=True),
        factory=dict(SKU='MTA0100335',installed_holder_unchanged=True,nominal_need_mm=factory['minimum_blank_mm'],
            usable_length_PROJECT_assumption_mm=100,nominal_margin_to_assumption_mm=100-factory['minimum_blank_mm'],actual_cut_mm=None),
        shrink=dict(SKU=joint['sleeve_SKU'],retained_installed_pieces=1,blank_mm=26,additional_installed_pieces=0),
        solder=dict(SKU=joint['solder_SKU'],retained_lap_joint=1,additional_laps=0),
        prints=dict(exports=s['exports'],additional_prints=0,additional_fasteners=0,
            rule='Replace the candidate Deck only; inherit verified RR Cover if unchanged. Do not print both old and new Deck.'),
        terminations=[dict(role='Factory holder',recipe='Preserve factory MTA connection; no extra crimp.'),
            dict(role='Lap',recipe='Opposed8mm bare ends;26mm RNF100 with9mm intact overlap each side; separate4mm native insulation seats/T18I.'),
            dict(role='P_REAR.2',recipe='One bare4mm2 conductor per221-615 cage;12..14mm strip from delivered marking; no tin/no doubled cage.')],
        selection_rule='Merge this and RR contributions ONCE at full-bank selection. Reconcile installed/spares/stock then; R51 is not mutated.',
        phase2='Delivered MTA length/OD, sleeve profile, tie insertion, pull/creep/current/heat remain real prototype trials.100mm is a PROJECT assumption, not supplier guarantee.'))
    print(json.dumps(dict(HELU_replacement_mm=new['stock_blank_mm'],HELU_delta_mm=new['stock_blank_mm']-old['stock_blank_mm'],ties=2,additional_prints=0)))
if __name__=='__main__':main()
