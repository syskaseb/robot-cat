"""One additive RR stock contribution, not a selected basket or extra variants."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    paths=dict(station=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-station-native-r4/checks.json',
        route=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-complete-r8/checks.json',
        prior=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2/checks.json',
        stock=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json')
    data={k:json.loads(p.read_text(encoding='utf-8')) for k,p in paths.items()}
    s=data['station'];assert not s['hits'] and not s['errors'] and s['additional_T18I']==2
    tie=next(r for r in data['stock']['lines'] if r['id']=='tie:111-02370')
    assert tie['dimensions_mm']==dict(length=145,width=2.5,thickness=1.2,head_length=4.8,head_width=4.5,height_H=3.5)
    old=next(r for r in data['prior']['routes'] if r['id']=='W052_extension')
    rows={r['id']:r for r in data['route']['routes']};new=rows['W052_extension'];factory=rows['W052_factory']
    joint=next(r for r in data['route']['joints'] if r['id']=='W052')
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-quantity-contribution-r1';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'checks.json').exists()
    save(out/'checks.json',dict(status='RR_ADDITIVE_CANDIDATE_CONTRIBUTION_COMPLETE',selected=False,physical_pass=False,W5_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths.values()},script_sha256=sha(Path(__file__)),
        additional_T18I_installed=2,tie_SKU='111-02370',tie_stock_length_mm=145,
        HELU23802=dict(role='W052_extension',old_blank_mm=old['stock_blank_mm'],replacement_blank_mm=new['stock_blank_mm'],
            delta_blank_mm=new['stock_blank_mm']-old['stock_blank_mm'],no_additional_duplicate_wire=True),
        factory=dict(SKU='MTA0100335',installed_holder_unchanged=True,nominal_need_mm=factory['minimum_blank_mm'],
            usable_length_PROJECT_assumption_mm=100,nominal_margin_to_assumption_mm=100-factory['minimum_blank_mm'],actual_cut_mm=None),
        shrink=dict(SKU=joint['sleeve_SKU'],retained_installed_pieces=1,blank_mm=26,additional_installed_pieces=0),
        solder=dict(SKU=joint['solder_SKU'],retained_lap_joint=1,additional_laps=0),
        prints=dict(replace_candidate_Deck='hardware/cad/studies/servo-fuse-rr-source-station-native-r4/Deck_UNSELECTED.stl',
            replace_candidate_Cover='hardware/cad/studies/servo-fuse-rr-source-station-native-r4/Cover_UNSELECTED.stl',additional_prints=0,additional_fasteners=0),
        terminations=[dict(role='MTA output of source-side lead',recipe='Preserve factory connection to same RR holder, no extra crimp.'),
            dict(role='Factory lap end',recipe='8mm stripped copper,9mm intact insulation sleeve overlap,4mm native insulation grip/T18I.'),
            dict(role='HELU lap end',recipe='Opposed8mm bare lap,9mm intact overlap, separate4mm native grip/T18I, RNF100 fitted after solder inspection.'),
            dict(role='P_REAR.3',recipe='One bare4mm2 conductor per221-615 cage,12..14mm strip from delivered marking, no tin/no doubled cage.')],
        selection_rule='Merge this contribution ONCE with other bank roles at full selection;200-piece tie stock is not a free new purchase and installed/spares/remaining stock must be reconciled. No selected R51 mutation now.',
        phase2='Actual MTA length/OD, radius, stripping/shrink profile, pull/creep/current/heat remain real delivery/prototype checks. Nominal100mm is not a supplier guarantee.'))
    print(json.dumps(dict(HELU_replacement_mm=new['stock_blank_mm'],HELU_delta_mm=new['stock_blank_mm']-old['stock_blank_mm'],ties=2,additional_prints=0)))
if __name__=='__main__':main()
