"""Select five exact retail bindings on R49, preserving the unresolved male lead.

No CAD/terminal substitution, buying or clock deadline. Parent evidence immutable.
Known retail packs remain distinct from installed/spare requirements.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, math, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/cad'))
from release_check import verify
PARENT = ROOT/'hardware/manufacturing/one-batch-prototype-r49'
OUT = ROOT/'hardware/manufacturing/nonfastener-offers-r2'
BATCH = ROOT/'hardware/manufacturing/one-batch-prototype-r50'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def update_quantities(q, review):
    q = copy.deepcopy(q)
    rows = {r['id']: r for r in q['lines']}
    assert len(rows) == len(q['lines']) == 114
    for offer in review['resolved']:
        row = rows[offer['quantity_id']]
        old = row['product_binding']
        assert old['manufacturer_part'] == offer['manufacturer_part']
        binding = copy.deepcopy(old)
        binding.pop('supplier_constraint', None)
        binding.update(offer)
        binding['planning_quantity'] = row['planning_quantity']
        order = math.ceil(max(row['planning_quantity'], offer['retail_minimum']) /
                          offer['retail_multiple']) * offer['retail_multiple']
        row.update(product_binding=binding, supplier=offer['supplier'],
                   supplier_sku=offer['supplier_sku'], url=offer['supplier_url'],
                   retail_order_quantity=order,
                   pack_excess_quantity=order-row['planning_quantity'],
                   retail_minimum_pieces=offer['retail_minimum'],
                   retail_multiple_pieces=offer['retail_multiple'])
    # The sixth role deliberately stays commercially unresolved, with a precise
    # new source and its limitation. This is not an automatic stock waiver.
    p = review['pending'][0]
    assert p['quantity_id'] == 'connector:2147632112'
    rows[p['quantity_id']]['product_binding']['supplier_constraint'] = p['constraint']
    rows[p['quantity_id']]['product_binding']['candidate_offer'] = copy.deepcopy(p)
    before = {r['id']: (r['planning_quantity'], r['unit']) for r in q['lines']}
    assert before == {r['id']: (r['planning_quantity'], r['unit']) for r in rows.values()}
    return q

def main():
    started = datetime.now(timezone.utc)
    assert not (BATCH/'manifest.json').exists(), 'Preserve completed package'
    parent = read(PARENT/'manifest.json')
    assert verify(ROOT, parent)['integrity_ok']
    review = read(OUT/'offer-review.json')
    oldq = read(PARENT/'one-order-quantities.json')
    q = update_quantities(oldq, review)
    assert {r['id']: (r['planning_quantity'], r['unit']) for r in q['lines']} == {
        r['id']: (r['planning_quantity'], r['unit']) for r in oldq['lines']}
    BATCH.mkdir(parents=True, exist_ok=True)
    selection = copy.deepcopy(read(PARENT/'selection.json'))
    selection.update(parent_selection_sha256=sha(PARENT/'selection.json'),
                     nonfastener_catalog='hardware/manufacturing/one-batch-prototype-r50/nonfastener-catalog.json',
                     nonfastener_offers='hardware/manufacturing/nonfastener-offers-r2/offer-review.json',
                     K2_complete=False, phase1_percent=70)
    q.update(selected_prints='hardware/manufacturing/one-batch-prototype-r50/selection.json',
             nonfastener_catalog=selection['nonfastener_catalog'], K2_complete=False)
    # Preserve all83 logical roles (fourWAGO roles are one supplier row).
    catalog = copy.deepcopy(read(ROOT/'hardware/manufacturing/one-batch-prototype-r48/nonfastener-catalog.json'))
    bindings = {r['quantity_id']: r for r in catalog['rows']}
    for r in q['lines']:
        if r['id'] in bindings:
            bindings[r['id']] = copy.deepcopy(r['product_binding'])
            bindings[r['id']]['planning_quantity'] = r['planning_quantity']
    catalog.update(rows=list(bindings.values()), role_count=83,
                   retail_offer_or_availability_pending=['connector:2147632112'],
                   current_quantities='hardware/manufacturing/one-batch-prototype-r50/one-order-quantities.json',
                   new_review=selection['nonfastener_offers'], K2_complete=False,
                   remaining='Practical retail source for red150mm male2147632112; W5/K3 quantities and any necessary fuse-interface SKU change still open. No physical fit or complete phase1 claim.')
    assert len(bindings) == 83
    # Current pack planning is synchronized to changed R49 T18I=200, not stale
    # catalog's R47=100. Other earlier local interfaces are untouched.
    assert bindings['tie:111-02370']['planning_quantity'] == 200
    save(BATCH/'selection.json', selection)
    save(BATCH/'one-order-quantities.json', q)
    save(BATCH/'nonfastener-catalog.json', catalog)
    validation = copy.deepcopy(read(PARENT/'validation.json'))
    validation.update(resolved_retail_roles=5,
                      retail_offer_or_availability_pending=['connector:2147632112'],
                      print_selection_unchanged=True, quantity_requirements_unchanged=True)
    save(BATCH/'validation.json', validation)
    end = datetime.now(timezone.utc)
    save(OUT/'work-time.json', dict(started_utc=started.isoformat(),
        finished_utc=end.isoformat(), worker_wall_seconds=(end-started).total_seconds(),
        note='Packaging worker only; continuation wall time recorded separately in plan.'))
    pins = {r['path']: r['sha256'] for r in parent['files']}
    for folder in (BATCH, OUT):
        for p in folder.glob('*.json'):
            if p.name != 'manifest.json': pins[p.relative_to(ROOT).as_posix()] = sha(p)
    for name in ('nonfastener_offers_r2.py', 'test_nonfastener_offers_r2.py'):
        p = ROOT/'tools/manufacturing'/name
        pins[p.relative_to(ROOT).as_posix()] = sha(p)
    manifest = copy.deepcopy(parent)
    manifest.update(files=[dict(path=p, sha256=h) for p,h in sorted(pins.items())],
        parent_pins_preserved=len(parent['files']), newly_selected_stls=0, K2_complete=False)
    assert verify(ROOT, manifest)['integrity_ok']
    save(BATCH/'manifest.json', manifest)
    print(json.dumps(dict(selected='R50', unchanged_print_jobs=73, quantity_rows=114,
        resolved_offers=5, pending=1, pins=len(pins), phase1_percent=70)))

if __name__ == '__main__': main()
