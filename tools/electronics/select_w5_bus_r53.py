"""Select one replacement Deck and BUS pair, not a completed whole W5.

Retain R52 bank and exact114 supplier rows. Three new straps plus service
spares fit the existing300 stock; no new cable pack or duplicated print job.
"""
from datetime import datetime, timezone
from pathlib import Path
import copy
import json
import shutil
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT / 'hardware/manufacturing/one-batch-prototype-r53'


def main():
    begin = datetime.now(timezone.utc)
    pins = {}
    def read(rel):
        pins[rel] = sha(ROOT / rel)
        return json.loads((ROOT / rel).read_text(encoding='utf-8'))
    parent = 'hardware/manufacturing/one-batch-prototype-r52'
    selection = read(parent + '/selection.json')
    quantity = read(parent + '/one-order-quantities.json')
    catalog = read(parent + '/nonfastener-catalog.json')
    cart = read(parent + '/fixed-fastener-cart.json')
    assembly_rel = 'hardware/electronics/full-cat/w5-bus-assembly-r1/assembly.json'
    assembly = read(assembly_rel)
    proof_rel = 'hardware/electronics/full-cat/w5-bus-native-grips-r4/checks.json'
    proof = read(proof_rel)
    assert assembly['status'] == 'BUS_LOCAL_READY_FOR_SELECTION'
    assert not assembly['hits'] and not assembly['errors']
    assert proof['status'] == 'BUS_SLOTS_STATIC_COMPLETE_UNSELECTED'
    assert not proof['hits'] and not proof['errors']
    assert proof['closed_STL'] and proof['relocated_reopen']
    for receipt in (assembly, proof):
        for rel, value in {**receipt['source_sha256'], **receipt.get('files', {})}.items():
            assert sha(ROOT / rel) == value, rel
            pins[rel] = value
    assert selection['local_fuse_bank_complete'] and not selection['W5_complete']
    assert not (OUT / 'selection.json').exists()
    OUT.mkdir(parents=True, exist_ok=True)
    deck = next(p for p in selection['prints'] if p['identity'] == 'electronics:DeckP10-cover-mount')
    assert deck['quantity'] == 1
    stl_rel = assembly['deck_replacement']['stl']
    dest = OUT / 'prints/Deck_SELECTED_x1.stl'
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / stl_rel, dest)
    deck.update(stl=dest.relative_to(ROOT).as_posix(), sha256=sha(dest),
        native=assembly['deck_replacement']['native'], native_file=assembly['deck_replacement']['native'],
        native_final='BusStrapSlotsFinished', recipe=assembly_rel, dimensions_mm=proof['dimensions_mm'],
        total_brim_allowance_mm=6, supports='Phase2: inspect native BUS channel skin/grips and inherited supports. No slicer/strength PASS.')
    deck.pop('print_size_mm_including_5mm_brim', None)
    ties = next(r for r in quantity['lines'] if r['id'] == 'tie:111-02370')
    assert ties['planning_quantity'] == 300
    ties.update(BUS_new_installed=3, BUS_new_service_replacements=3,
                BUS_shared_W061_already_counted=1, conservative_stock_upper_bound=212,
                BUS_quantity_basis=assembly_rel)
    assert ties['historical_working_allowance'] + ties['local_installed'] + ties['local_service_replacements'] + 6 == 212
    ties['note'] += ' R53 BUS adds3 installed+3 service from same300 stock. SharedW061 is not counted again; finalK3census open.'
    cable = next(r for r in quantity['lines'] if r['id'] == 'p0:BUS-PIGTAIL-P0')
    assert cable['planning_quantity'] == 1 and cable['product_binding']['manufacturer_part'] == '34171'
    cable.update(selected_route_recipe=assembly_rel, factory_cables_installed=1, factory_pack_spares=5)
    assert len(selection['prints']) == 77
    assert len({p['identity'] for p in selection['prints']}) == 77
    assert sum(p['quantity'] for p in selection['prints'] if p['purpose'] == 'installed_candidate') == 115
    assert len(quantity['lines']) == 114
    selection.update(parent_selection=parent + '/selection.json', parent_selection_sha256=pins[parent+'/selection.json'],
        phase1_percent=75, phase1_complete=False, W5_complete=False, BUS_local_complete=True,
        BUS_wiring_recipe=assembly_rel, BUS_native_proof=proof_rel,
        current_deck_world='hardware/cad/studies/w5-bus-native-grips-r4/Deck_WORLD.brep',
        local_precedence='R53 replaces only the R52 Deck print/native and adds BUS D/G/3strap recipes. BankR47 and all unchanged interfaces retained; fullW5 remains open.',
        fixed_fastener_cart=(OUT/'fixed-fastener-cart.json').relative_to(ROOT).as_posix(),
        nonfastener_catalog=(OUT/'nonfastener-catalog.json').relative_to(ROOT).as_posix(), source_sha256=pins)
    selection.setdefault('conditions', []).extend(assembly['phase2_conditions'])
    quantity.update(selected_prints=(OUT/'selection.json').relative_to(ROOT).as_posix(),
        fixed_fastener_cart=selection['fixed_fastener_cart'], nonfastener_catalog=selection['nonfastener_catalog'],
        BUS_wiring_recipe=assembly_rel, W5_complete=False, phase1_complete=False, source_sha256=pins)
    catalog.update(current_quantities=(OUT/'one-order-quantities.json').relative_to(ROOT).as_posix(), source_sha256=pins)
    # Do not silently discard old inherited print hashes or change supplier rows.
    for row in selection['prints']:
        assert sha(ROOT / row['stl']) == row['sha256'], row['identity']
    for row in quantity['lines']:
        if 'product_binding' in row:
            assert row['planning_quantity'] == row['product_binding']['planning_quantity'], row['id']
    for name, obj in [('selection.json',selection), ('one-order-quantities.json',quantity),
                      ('fixed-fastener-cart.json',cart), ('nonfastener-catalog.json',catalog)]:
        save(OUT/name, obj)
    paths = [OUT/n for n in ('selection.json','one-order-quantities.json','fixed-fastener-cart.json','nonfastener-catalog.json')] + [dest, Path(__file__)]
    end = datetime.now(timezone.utc)
    save(OUT/'BUS-reconciliation.json', dict(status='ONE_R53_BUS_SELECTED_WHOLE_W5_OPEN',
        phase1_completed_count=15, phase1_total=20, physical_pass=False, W5_complete=False,
        jobs=77, PETG_installed=115, supplier_rows=114, new_screws=0,
        new_ties=3, reused_W061_tie=1, cable_pack_count=1, conservative_tie_stock_ceiling=212,
        source_sha256=pins, files={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        started_utc=begin.isoformat(), finished_utc=end.isoformat(), worker_wall_seconds=(end-begin).total_seconds()))
    print('ONE_R53_BUS_SELECTED_PHASE1_15_OF_20', flush=True)


if __name__ == '__main__':
    main()
