"""One replacement ledger for all four output extensions, not four additions."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    paths=dict(old=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2/checks.json',
        front=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r3/checks.json',
        rear=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r8/checks.json',
        front_native=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r5/checks.json',
        stock=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json')
    data={k:json.loads(p.read_text(encoding='utf-8')) for k,p in paths.items()}
    assert not data['front']['hits'] and not data['front']['errors']
    assert not data['rear']['errors'] and not data['rear']['factory_failures']
    casing={'CandidateDeck','ModifiableCover','Bank/RightClipAccessFinished_WORLD',
        'hardware/cad/studies/pwm-branch-restraints-r4/ShelfPWMGroundTerminal.brep'}
    assert all(h['owner'] in casing for h in data['rear']['hits'])
    n=data['front_native']['native'];assert n['closed_STL'] and n['relocated_reopen'] and n['strict_BOP_errors']==0
    ids=['W026_extension','W037_extension','W045_extension','W053_extension']
    old={r['id']:r for r in data['old']['routes'] if r['id'] in ids};assert len(old)==4
    new=dict(old)
    for k in ('front','rear'):
        for r in data[k]['routes']:
            if r['id'] in ids:new[r['id']]=r
    rows=[dict(id=i,old_blank_mm=old[i]['stock_blank_mm'],replacement_blank_mm=new[i]['stock_blank_mm'],
        delta_blank_mm=new[i]['stock_blank_mm']-old[i]['stock_blank_mm'],actual_cut_mm=None,
        source='front-source-ports-r2 unchanged' if i=='W026_extension' else 'output-returns-complete-r3' if i=='W037_extension' else 'output-returns-complete-r8') for i in ids]
    factory=[dict(id=r['id'],nominal_need_mm=r['minimum_blank_mm'],project_available_mm=100,
        margin_to_assumption_mm=100-r['minimum_blank_mm'],supplier_length_verified=False,actual_cut_mm=None)
        for k in ('front','rear') for r in data[k]['routes'] if r['kind']=='MTA_factory']
    assert len(factory)==3 and all(r['margin_to_assumption_mm']>=0 for r in factory)
    ties=data['front_native']['ties'];assert len(ties)==3 and sum(r['installed'] for r in ties)==3
    catalogue={r['id']:r for r in data['stock']['lines']}
    assert catalogue['p0:WIRE-RED4-P0']['product_binding']['manufacturer_part']=='23802'
    assert catalogue['splice:WAGO221-412']['product_binding']['manufacturer_part']=='221-412'
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-output-quantity-contribution-r1';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'checks.json').exists()
    save(out/'checks.json',dict(status='OUTPUT_REPLACEMENT_LEDGER_COMPLETE_CONSTRUCTION_OPEN',selected=False,physical_pass=False,W5_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths.values()},script_sha256=sha(Path(__file__)),
        recorded_utc=datetime.now(timezone.utc).isoformat(),HELU23802=dict(roles=rows,
            previous_four_output_blank_mm=sum(r['old_blank_mm'] for r in rows),
            replacement_four_output_blank_mm=sum(r['replacement_blank_mm'] for r in rows),
            delta_blank_mm=sum(r['delta_blank_mm'] for r in rows),
            no_duplicate_previous_wires=True,whole_robot_stock_m=None,
            rule='Replace these four roles exactly once. Retained source contributions are separate IDs. Do not infer total stock from this partial ledger.'),
        factory_assumptions=factory,additional_FR_T18I_roles=[dict(role=r['role'],SKU=r['sku'],installed=1) for r in ties],
        additional_FR_T18I=3,additional_FR_fasteners=0,additional_FR_prints=0,
        FR_print_replacement='FRGuardOutputStation replaces FRReturnGuard, not an additional part.',
        WAGO221412=dict(retain_four_output_joints=True,additional_from_this_replacement=0,
            final_installed_and_spares='OPEN: merge all main source/output joints and existing XB11 once at bank selection.'),
        terminations=['Each 221412: two separate untinned bare ends,11mm nominal strip, one conductor per cage.',
            'HELU output allowance25mm =11mm splice plus14mm P-leg end;10mm retained trim reserve, not a delivered measurement.',
            'P-leg221615: one bare4mm2 conductor per mapped cage,12..14mm from marking; no tin/folding/doubled cage.',
            'MTA factory side is retained, not an extra crimp or extra purchased extension.'],
        open=['Rear native channels/grips, lever/assembly release and whole stock/E3 remain open.',
            'No selected quantity/order-cart mutation. Check delivery100mm assumption and actual strip/tie/pull/heat in phase2.']))
    print(json.dumps(dict(outputs=4,old_mm=sum(r['old_blank_mm'] for r in rows),new_mm=sum(r['replacement_blank_mm'] for r in rows),FR_ties=3,selected=False)))
if __name__=='__main__':main()
