"""Reconcile the two selected blanks into the one R48 cut sheet and stock ledger."""
from pathlib import Path
import csv, io, json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
from release_check import verify
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r48'
OUT=ROOT/'hardware/electronics/full-cat/battery-feed-selected-r1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    manifest=read(BATCH/'manifest.json')
    # Tests are amended only before the first commit; preserve all CAD pins.
    for entry in manifest['files']:
        if entry['path']!='tools/electronics/test_battery_feed_selection_r1.py':
            assert sha(ROOT/entry['path'])==entry['sha256'], entry['path']
    assert not (OUT/'wire-cuts.csv').exists()
    body=read(OUT/'body-harness.json')
    cuts=list(csv.DictReader((ROOT/'hardware/electronics/full-cat/body-harness-w5-r2/wire-cuts.csv').read_text(encoding='utf-8-sig').splitlines()))
    assert len(cuts)==80
    for row in cuts:
        if row['id'] in ('W001','W075'):
            item=next(r for r in body['conductors'] if r['id']==row['id'])
            row.update(material=item['material'],nominal_selected_blank_mm=item['nominal_selected_blank_mm'],
                selected_recipe=item['selected_recipe'],route_state='SELECTED_LOCAL_NOMINAL_WITH_PHASE2_FIT')
    text=io.StringIO(newline='');writer=csv.DictWriter(text,fieldnames=list(cuts[0]),lineterminator='\n');writer.writeheader();writer.writerows(cuts)
    (OUT/'wire-cuts.csv').write_text(text.getvalue(),encoding='utf-8',newline='')
    stock=read(ROOT/'hardware/electronics/full-cat/body-harness-w5-r2/stock.json')
    lapp=next(r for r in stock['stock'] if r['stock_id']=='LAPP 0107001')
    lapp.update(selected_BAT_allocation_mm=140,battery_legacy_reserve_mm=0,
        unallocated_input_budget_mm=1860,allocation_status='PARTIAL_W001_SELECTED_OTHER_INPUTS_OPEN',
        note='140 replaces legacy150 reserve, not added to it. Failed2320 trial remains historical only; not allocated.')
    stock['stock'].append(dict(stock_id='Original FHAC0002ZXJ leads',purchase_quantity=0,unit='included_with_F0',
        selected_allocations_mm={'W075':40},W076_allocation_mm=None,allocation_status='W076_OPEN_NO_ADDED_LAPP'))
    stock.update(parent='one-batch-prototype-r47',local_source_feed='hardware/electronics/full-cat/battery-feed-selected-r1/interface.json',complete=False)
    save(OUT/'stock.json',stock)
    selection=read(BATCH/'selection.json');quantity=read(BATCH/'one-order-quantities.json')
    selection.update(current_wire_cut_sheet=(OUT/'wire-cuts.csv').relative_to(ROOT).as_posix(),current_stock_ledger=(OUT/'stock.json').relative_to(ROOT).as_posix())
    quantity.update(wire_cut_sheet=selection['current_wire_cut_sheet'],stock_ledger=selection['current_stock_ledger'])
    save(BATCH/'selection.json',selection);save(BATCH/'one-order-quantities.json',quantity)
    pins={r['path']:r['sha256'] for r in manifest['files']}
    for path in (OUT/'wire-cuts.csv',OUT/'stock.json',BATCH/'selection.json',BATCH/'one-order-quantities.json',Path(__file__),ROOT/'tools/electronics/test_battery_feed_selection_r1.py'):
        pins[path.relative_to(ROOT).as_posix()]=sha(path)
    manifest['files']=[dict(path=p,sha256=h) for p,h in sorted(pins.items())]
    result=verify(ROOT,manifest);assert result['integrity_ok'],result
    save(BATCH/'manifest.json',manifest)
    validation=read(BATCH/'validation.json');validation['integrity']=result;save(BATCH/'validation.json',validation)
    print(json.dumps(dict(selected_blanks=12,remaining_LAPP_input_budget_mm=1860,pins=len(pins),integrity=result['integrity_ok'])))

if __name__=='__main__':main()
