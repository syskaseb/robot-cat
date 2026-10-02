"""Finish K2 for the current selected prototype, not W5/materials/final assembly.

The factory male225mm lead is trimmed at the free end to the retained150mm
working route. Do not select a new service loop or change the protected net.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, json, math, sys
from nonfastener_offers_r2 import ROOT, read, save, sha
sys.path.insert(0, str(ROOT/'tools/cad'))
from release_check import verify
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r50'
OUT=ROOT/'hardware/manufacturing/nonfastener-offers-r3'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r51'

def update_quantities(original, offer):
    q=copy.deepcopy(original)
    oldid,newid=offer['old_quantity_id'],offer['new_quantity_id']
    rows={r['id']:r for r in q['lines']}
    assert len(rows)==114 and oldid in rows and newid not in rows
    row=rows[oldid]; assert row['planning_quantity']==offer['planning_quantity']==2
    d=offer['manufacturer_drawing']
    assert (d['old_part'],d['new_part'],d['same_terminal'])==('2147632112','2147632113','430310001')
    assert d['purchased_length_L_mm'][0]>offer['trim_recipe']['nominal_finished_L_mm']
    assert offer['new_crimp_tool_SKU']==offer['new_STL']==0 and not offer['physical_pass']
    binding=copy.deepcopy(row['product_binding'])
    for key in ('supplier_constraint','candidate_offer'):binding.pop(key,None)
    binding.update(quantity_id=newid,manufacturer_part=offer['manufacturer_part'],
        supplier=offer['supplier'],supplier_sku=offer['supplier_sku'],supplier_url=offer['supplier_url'],
        retail_minimum=offer['retail_minimum'],retail_multiple=offer['retail_multiple'],
        product_evidence=d['url'],trim_recipe='hardware/manufacturing/nonfastener-offers-r3/offer-review.json',
        replaces_purchase_role=oldid)
    order=math.ceil(max(row['planning_quantity'],offer['retail_minimum'])/offer['retail_multiple'])*offer['retail_multiple']
    row.update(id=newid,name='Molex male red225+/-5mm factory lead2147632113; trim free end to existing XP02.board150mm working route',
        note='1 fitted+1 spare, purchase10/excess8. No extra loop. Factory crimp preserved; only free solder end trimmed after dry-fit. Phase2 delivery/fit refresh.',
        product_binding=binding,supplier=offer['supplier'],supplier_sku=offer['supplier_sku'],url=offer['supplier_url'],
        retail_order_quantity=order,pack_excess_quantity=order-row['planning_quantity'],
        retail_minimum_pieces=offer['retail_minimum'],retail_multiple_pieces=offer['retail_multiple'])
    assert len(q['lines'])==114 and order==10
    assert [r for r in original['lines'] if r['id']!=oldid]==[r for r in q['lines'] if r['id']!=newid]
    return q

def validate_catalog(catalog):
    rows=catalog['rows']; assert len(rows)==83
    assert len({r['quantity_id'] for r in rows})==83
    for r in rows:
        # Some commercial kits lack a separate manufacturer number; the exact
        # existing supplier SKU and evidence identify them, not an invented MPN.
        assert r['supplier'] and r['supplier_sku'] and r['supplier_url'],r['quantity_id']
        assert r['planning_quantity']>0 and r['product_evidence'],r['quantity_id']
        assert not r.get('supplier_constraint'),r['quantity_id']
    assert not any(r['quantity_id']=='connector:2147632112' for r in rows)
    assert next(r for r in rows if r['quantity_id']=='connector:2147632113')['manufacturer_part']=='2147632113'

def main():
    begin=datetime.now(timezone.utc)
    assert not (BATCH/'manifest.json').exists(),'Preserve completed selection'
    parent=read(PARENT/'manifest.json'); assert verify(ROOT,parent)['integrity_ok']
    offer=read(OUT/'offer-review.json');q=update_quantities(read(PARENT/'one-order-quantities.json'),offer)
    selection=copy.deepcopy(read(PARENT/'selection.json'))
    selection.update(parent_selection_sha256=sha(PARENT/'selection.json'),
        nonfastener_catalog='hardware/manufacturing/one-batch-prototype-r51/nonfastener-catalog.json',
        nonfastener_offers='hardware/manufacturing/nonfastener-offers-r3/offer-review.json',
        factory_pigtail_purchase_override='hardware/manufacturing/nonfastener-offers-r3/offer-review.json',
        K2_complete=True,phase1_percent=75)
    selection['historical_conditions'].append('R51 overrides ONLY red male XP02.board purchase2147632112 with factory2147632113, same430310001/20AWG/UL10002; trim FREE end to existing150mm nominal route. Do not add75mm storage loop or loose crimp. All other circuits/prints unchanged. K2 nominal cart complete; E3/W5/K3/A2/A3 open.')
    q.update(selected_prints='hardware/manufacturing/one-batch-prototype-r51/selection.json',
        nonfastener_catalog=selection['nonfastener_catalog'],K2_complete=True,
        factory_pigtail_purchase_override=selection['factory_pigtail_purchase_override'])
    catalog=copy.deepcopy(read(PARENT/'nonfastener-catalog.json'))
    replacement=next(r['product_binding'] for r in q['lines'] if r['id']==offer['new_quantity_id'])
    catalog['rows']=[copy.deepcopy(replacement) if r['quantity_id']==offer['old_quantity_id'] else r for r in catalog['rows']]
    catalog.update(status='CURRENT_SELECTED_NONFASTENER_CART_BOUND_K2',K2_complete=True,
        retail_offer_or_availability_pending=[],current_quantities='hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json',
        new_review=selection['nonfastener_offers'],remaining='E3/W5/K3/A2/A3 open. Later selected interfaces must reconcile quantities and revoke K2 if an unbound purchased role is introduced. No whole-phase or purchase-ready claim.')
    validate_catalog(catalog)
    fasteners=read(ROOT/selection['fixed_fastener_cart'])
    validation=copy.deepcopy(read(PARENT/'validation.json'))
    validation.update(K2_complete=True,retail_offer_or_availability_pending=[],
        factory_pigtail_override_checked=True,print_selection_unchanged=True,
        nominal_working_route_unchanged=True,quantity_requirements_unchanged=True,
        nonfastener_roles_checked=83,open_phase1=['E3','W5','K3','A2','A3'])
    BATCH.mkdir(parents=True,exist_ok=True)
    for name,value in [('selection.json',selection),('one-order-quantities.json',q),('nonfastener-catalog.json',catalog),('validation.json',validation)]:save(BATCH/name,value)
    end=datetime.now(timezone.utc)
    save(OUT/'work-time.json',dict(started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds(),note='Packaging worker only; do not add to continuation wall time.'))
    pins={r['path']:r['sha256'] for r in parent['files']}
    for folder in (OUT,BATCH):
        for p in folder.glob('*.json'):
            if p.name!='manifest.json':pins[p.relative_to(ROOT).as_posix()]=sha(p)
    for n in ('nonfastener_offers_r3.py','test_nonfastener_offers_r3.py'):
        p=ROOT/'tools/manufacturing'/n;pins[p.relative_to(ROOT).as_posix()]=sha(p)
    manifest=copy.deepcopy(parent)
    manifest.update(files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())],
        parent_pins_preserved=len(parent['files']),newly_selected_stls=0,K2_complete=True)
    assert verify(ROOT,manifest)['integrity_ok'];save(BATCH/'manifest.json',manifest)
    print(json.dumps(dict(selected='R51',phase1_percent=75,nonfastener_roles=83,quantity_rows=114,pins=len(pins),prints_unchanged=True)))

if __name__=='__main__':main()
