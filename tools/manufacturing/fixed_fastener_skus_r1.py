"""Bind all R45 fixed-fastener roles to exact offers; never claim whole K2."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, math, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/cad'))
from release_check import verify
OUT = ROOT / 'hardware/manufacturing/fixed-fastener-skus-r1'
PARENT = ROOT / 'hardware/manufacturing/one-batch-prototype-r45'
BATCH = ROOT / 'hardware/manufacturing/one-batch-prototype-r46'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def compile_cart(q, allocation):
    by_id = {r['id']:r for r in q['lines']}
    assert len(by_id) == len(q['lines'])
    added = allocation['added_quantity']
    assert added['id'] not in by_id
    assert added['installed'] == 4 and added['spares'] == 2
    assert added['planning_quantity'] == added['installed'] + added['spares'] == 6
    by_id[added['id']] = added
    expected = {k for k in by_id if k.startswith('fastener:')} | {added['id']}
    ids = [k for r in allocation['rows'] for k in r['quantity_ids']]
    assert len(ids) == len(set(ids)) and set(ids) == expected
    offers = [(r['supplier'],r['supplier_sku']) for r in allocation['rows']]
    assert len(offers) == len(set(offers)), 'Merge identical offers, retaining roles'
    cart = []
    for offer in allocation['rows']:
        minimum, multiple = offer['retail_minimum_pieces'], offer['retail_multiple_pieces']
        assert isinstance(minimum,int) and minimum > 0
        assert isinstance(multiple,int) and multiple > 0
        roles = [dict(id=k,planning_quantity=by_id[k]['planning_quantity'],
                      source=by_id[k]['source'],note=by_id[k].get('note',''))
                 for k in offer['quantity_ids']]
        planned = sum(r['planning_quantity'] for r in roles)
        order = math.ceil(max(planned,minimum)/multiple)*multiple
        assert order >= planned and order % multiple == 0
        row = copy.deepcopy(offer)
        row.update(id='supplier:'+offer['supplier']+':'+offer['supplier_sku'],
                   name=offer['supplier_sku'],unit='pcs',planning_quantity=planned,
                   retail_order_quantity=order,pack_excess_quantity=order-planned,
                   roles=roles,source='hardware/manufacturing/fixed-fastener-skus-r1/allocation.json')
        cart.append(row)
    assert sum(r['planning_quantity'] for r in cart) == sum(by_id[k]['planning_quantity'] for k in expected)
    for stack in allocation['nominal_thread_intervals']:
        low, high = stack['nut_from_head_mm']
        assert stack['L']-stack['b'] <= low < high <= stack['L'], stack
    washers = {r['supplier_sku']:r for r in cart if 'washers:' in ' '.join(r['quantity_ids'])}
    assert washers['00125202']['dimensions_mm'] == dict(ID=2.2,OD=5,t=.3)
    assert washers['00125202']['planning_quantity'] == 74
    assert washers['SKL001158']['planning_quantity'] == 63
    assert washers['1755994']['planning_quantity'] == 15 and washers['1755994']['retail_order_quantity'] == 100
    assert washers['SKL001221']['dimensions_mm']['OD'] == 9
    return cart

def build(select=False):
    assert not (OUT/'cart.json').exists(), 'Preserve completed evidence'
    q, allocation = read(PARENT/'one-order-quantities.json'), read(OUT/'allocation.json')
    cart = compile_cart(q, allocation)
    source_cart = read(ROOT/'hardware/build-readiness/p0-order-cart.json')
    frames = [r for store in source_cart['stores'].values() for r in store
              if r['id'] == 'FASTENER-M2P5X12-P0']
    assert len(frames) == 1 and frames[0]['installed'] == 4
    assert all('M2.5x12' not in r['name'] for r in q['lines'])
    pins = {p:sha(ROOT/p) for p in allocation['supporting_sources']}
    pins['hardware/build-readiness/p0-order-cart.json'] = sha(ROOT/'hardware/build-readiness/p0-order-cart.json')
    pins['hardware/manufacturing/one-batch-prototype-r45/one-order-quantities.json'] = sha(PARENT/'one-order-quantities.json')
    pins['hardware/manufacturing/fixed-fastener-skus-r1/allocation.json'] = sha(OUT/'allocation.json')
    report = dict(status='FIXED_FASTENER_CART_NOT_COMPLETE_ROBOT_PURCHASE_RELEASE',
                  rows=cart,source_sha256=pins,source_roles=33,supplier_rows=29,
                  added_missing_frame_screws=dict(installed=4,spares=2,planned=6),
                  K2_complete=False,phase1_percent=70,physical_pass=False,
                  prices_or_stock_guaranteed=False,purchase_authorized=False)
    save(OUT/'cart.json', report)
    if not select:
        return report
    assert not (BATCH/'manifest.json').exists(), 'Preserve earlier package'
    parent = read(PARENT/'manifest.json')
    assert verify(ROOT,parent)['integrity_ok']
    BATCH.mkdir(parents=True, exist_ok=True)
    s = copy.deepcopy(read(PARENT/'selection.json'))
    s.update(parent_selection_sha256=sha(PARENT/'selection.json'),
             fixed_fastener_cart='hardware/manufacturing/fixed-fastener-skus-r1/cart.json',
             K2_complete=False,phase1_percent=70,
             fastener_precedence='R46 exact offer allocation replaces generic fixed-fastener supplier roles only. Same sizes/geometry; adds omitted4P0frameM2.5x12+2spares; preserves all R45 print/wire selections. Factory MG92B supplied screw remains provisional. No protection or rejected fuse route selected.')
    assert len(s['prints']) == 71 and s['prints'] == read(PARENT/'selection.json')['prints']
    original_fixed = {r['id'] for r in q['lines'] if r['id'].startswith('fastener:')}
    q['lines'] = [r for r in q['lines'] if r['id'] not in original_fixed] + cart
    q.update(selected_prints=(BATCH/'selection.json').relative_to(ROOT).as_posix(),
             fixed_fastener_cart=s['fixed_fastener_cart'],K2_complete=False)
    assert len(q['lines']) == 112
    save(BATCH/'selection.json',s)
    save(BATCH/'one-order-quantities.json',q)
    inherited = {r['path']:r['sha256'] for r in parent['files']}
    pins2 = dict(inherited)
    sources = list(pins) + ['hardware/manufacturing/one-batch-prototype-r45/manifest.json',
                          'tools/manufacturing/fixed_fastener_skus_r1.py',
                          'tools/manufacturing/test_fixed_fastener_skus_r1.py']
    own = sources + [p.relative_to(ROOT).as_posix() for folder in (OUT,BATCH)
                     for p in folder.iterdir() if p.is_file() and p.name not in ('manifest.json','validation.json')]
    for rel in own:
        h = sha(ROOT/rel)
        assert rel not in pins2 or pins2[rel] == h, rel
        pins2[rel] = h
    m = copy.deepcopy(parent)
    m.update(parent_pins_preserved=len(inherited),newly_selected_stls=0,new_stls=0,
             K2_complete=False,phase1_percent=70,
             files=[dict(path=p,sha256=h) for p,h in sorted(pins2.items())])
    checked = verify(ROOT,m)
    assert checked['integrity_ok']
    assert not verify(ROOT,m,True)['integrity_ok']
    save(BATCH/'manifest.json',m)
    save(BATCH/'validation.json',dict(integrity=checked,parent_pins_preserved=len(inherited),
        unchanged_prints=71,installed_PETG=110,fit_samples=4,new_STLs=0,
        previous_quantity_rows=115,current_quantity_rows=112,
        mapped_roles=33,retail_offers=29,merged_existing_roles=4,
        missing_frame_screw_correction=6,phase1_percent=70,
        K2_complete=False,physical_pass=False,
        scope='Changed supplier/quantity interfaces only; no repeated CAD or electrical qualification.'))
    print(json.dumps(dict(pins=len(pins2),preserved=len(inherited),quantity_rows=112,
                         fixed_offers=29,phase1_percent=70,physical_pass=False)))
    return report

if __name__ == '__main__':
    build('--select' in sys.argv)
