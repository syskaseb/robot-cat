"""One current order draft: no duplicate cable packs or historical variants.

Bind existing supplier identities. This is a mutable unselected draft until
the current Cover/shared service and prototype selection are received. The
T18I ceiling is conservative material stock, not an invented installed count.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,math
from servo_fuse_inputs_r1 import save,sha
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-one-order-candidate-r1'

def main():
    start=datetime.now(timezone.utc);pins={}
    def read(rel):
        p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    if (OUT/'quantities.json').exists():assert not json.loads((OUT/'quantities.json').read_text(encoding='utf-8'))['selected']
    q=copy.deepcopy(read('hardware/manufacturing/one-batch-prototype-r53/one-order-quantities.json'))
    delta=read('hardware/electronics/full-cat/w5-current-order-contribution-r1/stock.json')
    cable=read('hardware/reference/leg-cable-2026-10-04/facts.json')
    long=read('hardware/reference/hellermann-11102189-2026-10-05/supplier-identity.json')
    loops=read('hardware/electronics/full-cat/w5-loop-preparation-r1/preparation.json')
    byid={r['id']:r for r in q['lines']};assert len(byid)==len(q['lines'])==114
    for row in delta['fastener_rows']:
        target=byid[row['id']];before=copy.deepcopy(target)
        target.update(copy.deepcopy(row))
        target['quantity_ids']=[r['id'] for r in target['roles']]
        assert target['planning_quantity']==sum(r['planning_quantity'] for r in target['roles'])
        if 'product_binding' in target:
            # The supplier binding is a consolidated order identity here.
            target['product_binding']['quantity_id']=target['id']
            target['product_binding']['planning_quantity']=target['planning_quantity']
    for row in delta['material_overrides']:
        target=byid[row['quantity_id']];target['planning_quantity']=row['planning_quantity']
        target['product_binding']['planning_quantity']=target['planning_quantity']
        target['current_W5_stock_basis']=delta['material_stock_basis']
        target['source']='hardware/electronics/full-cat/w5-current-order-contribution-r1/stock.json'
    ties=byid['tie:111-02370'];assert ties['conservative_stock_upper_bound']==212
    ties['current_W5_new_installed']=delta['new_T18I_installed_subtotal']
    ties['current_W5_one_replacement_set']=delta['new_T18I_installed_subtotal']
    upper=212+2*delta['new_T18I_installed_subtotal'];assert upper==384
    ties.update(conservative_stock_upper_bound=upper,planning_quantity=400,
        exact_installed_total_verified=False,note='212inherited conservative ceiling+86new installed+86one-service replacements=384;4packs100. Not384installed. Split12/frame12 counted once; no second local bank bag.')
    ties['product_binding']['planning_quantity']=400
    assert cable['manufacturer_sku']=='34172' and cable['manufacturer_nominal_length_mm']==900 and cable['factory_cables_per_pack']==6
    factory=byid['p0:BUS-PIGTAIL-P0'];old=copy.deepcopy(factory)
    factory.update(id='factory:Waveshare34172',name='Waveshare34172,900mm5264-3PIN,3packs6 for12leg looms+1BUS D/G loom',
        planning_quantity=3,unit='pack6',factory_cables_installed=13,factory_pack_spares=5,
        roles_installed={'BUS_D_G_shared':1,'leg_continuous_looms':12},
        supersedes_quantity_id=old['id'],supersedes_300mm_sku='34171',
        note='ONE900mmSKU for13physical looms; not36core cables, not three extra BUS leads. Retain servo plugs; remove V contact only from BUS adapter recipe.',
        selected=False)
    factory['product_binding']=dict(quantity_id=factory['id'],planning_quantity=3,unit='pack6',
        manufacturer='Waveshare',manufacturer_part=cable['manufacturer_part'],manufacturer_sku='34172',
        supplier='Waveshare',supplier_sku='34172',supplier_url=cable['manufacturer_url'],
        product_evidence='hardware/reference/leg-cable-2026-10-04/facts.json',
        commercial_refresh='Phase2 before purchase; no price/availability/shipping guarantee.')
    q['lines'].append(dict(id='tie:111-02189',name='HellermannTyton T18L9C2 Natural205x2.5mm',
        planning_quantity=100,unit='pcs',installed=12,service_replacements=12,planning_spares=76,
        source='hardware/reference/hellermann-11102189-2026-10-05/supplier-identity.json',
        product_binding=dict(quantity_id='tie:111-02189',planning_quantity=100,unit='pcs',
            manufacturer=long['manufacturer'],manufacturer_part=long['manufacturer_part'],manufacturer_article='111-02189',
            supplier=long['supplier'],supplier_sku=long['supplier_sku'],supplier_url=long['supplier_url'],
            manufacturer_factory_pack=100,retail_minimum=None,retail_multiple=None,
            commercial_refresh=long['commercial_refresh'])))
    assert len(q['lines'])==len({r['id'] for r in q['lines']})==115
    assert not any(r['id']=='p0:BUS-PIGTAIL-P0' for r in q['lines'])
    assert sum(r.get('factory_cables_installed',0) for r in q['lines'])==13
    # Older consolidated supplier rows retained the first role's quantity
    # in their top-level product identity. Keep role bindings unchanged,
    # but bind the actual combined order line to its own total.
    for row in q['lines']:
        if 'product_binding' in row:
            row['product_binding']['quantity_id']=row['id']
            row['product_binding']['planning_quantity']=row['planning_quantity']
            row['product_binding']['unit']=row['unit']
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    q.update(status='ONE_CURRENT_ORDER_DRAFT_PENDING_CURRENT_COVER_AND_SELECTION',selected=False,
        W1_complete=False,W5_complete=False,K3_complete=False,phase1_complete=False,physical_pass=False,
        final_tie_stock_is_bound_not_exact_installed_census=True,current_factory_cable_sku='34172',
        current_loop_preparation='hardware/electronics/full-cat/w5-loop-preparation-r1/preparation.json',
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds())
    save(OUT/'quantities.json',q)
    print(json.dumps(dict(lines=115,factory_packs=3,factory_installed=13,short_tie_stock=400,long_tie_stock=100)))

if __name__=='__main__':main()
