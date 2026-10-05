"""Reconcile changed material roles against R53, not a second shopping cart.

No commercial refresh, purchase or complete-robot stock claim. Keep inherited
spares; new installed fasteners are distinct roles. Wire revisions replace
obsolete subtotals rather than adding their complete historical versions.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, json
from servo_fuse_inputs_r1 import save, sha
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-current-order-contribution-r1'

def main():
    started=datetime.now(timezone.utc)
    if (OUT/'stock.json').exists():
        previous=json.loads((OUT/'stock.json').read_text(encoding='utf-8'))
        assert not previous['selected'] and previous['status']=='CURRENT_CHANGED_ORDER_ROLES_RECONCILED_FULL_TIE_CENSUS_OPEN'
    pins={}
    def read(rel):
        p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    selected='hardware/manufacturing/one-batch-prototype-r53/'
    fast=read(selected+'fixed-fastener-cart.json')
    catalog=read(selected+'nonfastener-catalog.json')
    prep=read('hardware/electronics/full-cat/w5-prototype-preparation-r2/preparation.json')
    platform=read('hardware/electronics/full-cat/w5-source-platform-assembly-r1/assembly.json')
    roof=read('hardware/electronics/full-cat/w5-source-roof-service-r2/assembly.json')
    frame=read('hardware/electronics/full-cat/w5-loom-mount-hardware-r2/checks.json')
    assert not platform['hits'] and not roof['hits'] and not frame['hits']
    rows=copy.deepcopy(fast['rows']);by_id={r['id']:r for r in rows}
    allocations=[]
    for owner,proof in [('Platform',platform),('Roof',roof)]:
        for r in proof['allocations']:
            if 'supplier_id' not in r:continue
            allocations.append(dict(role=r['role'],supplier_id=r['supplier_id'],quantity=r['quantity'],owner=owner))
    allocations.extend([dict(role='W5:fourFixedFrames:M3x16',supplier_id='supplier:BEJMET:SKL000625',quantity=8,owner='FourFixedFrames'),
        dict(role='W5:fourFixedFrames:M3nut',supplier_id='supplier:BEJMET:SKL000383',quantity=8,owner='FourFixedFrames')])
    assert len({r['role'] for r in allocations})==len(allocations)
    prior_roles={r['id'] for row in rows for r in row['roles']}
    assert not prior_roles.intersection(r['role'] for r in allocations),'Do not add a selected role twice'
    for a in allocations:
        row=by_id[a['supplier_id']]
        row['roles'].append(dict(id=a['role'],planning_quantity=a['quantity'],source='Current verified W5 native mounting allocation'))
        row['planning_quantity']+=a['quantity']
        minimum=row['retail_minimum_pieces'];multiple=row['retail_multiple_pieces']
        q=max(minimum,row['planning_quantity']);row['retail_order_quantity']=((q+multiple-1)//multiple)*multiple
        row['pack_excess_quantity']=row['retail_order_quantity']-row['planning_quantity']
    targets={'SKL000623':24,'SKL000625':22,'SKL000383':67,'SKL001158':75}
    assert all(by_id['supplier:BEJMET:'+sku]['planning_quantity']==q for sku,q in targets.items())
    changed=[r for r in rows if any(r['id']==a['supplier_id'] for a in allocations)]
    materials=copy.deepcopy(catalog['rows']);mby={r['quantity_id']:r for r in materials}
    assert len(mby)==len(materials)
    overrides={'p0:WIRE-INLET-BLACK12-P0':4,'p0:WIRE-RED4-P0':5,'p0:WIRE-BLACK4-P0':3}
    for ident,q in overrides.items():mby[ident]['planning_quantity']=q
    tie=read('hardware/reference/hellermann-11102189-2026-10-05/dimensions.json')
    assert tie['sku']=='111-02189' and tie['package_quantity']==100
    additional_tie=dict(quantity_id='W5:tie:111-02189',manufacturer='HellermannTyton',manufacturer_part='111-02189',
        installed=12,manufacturer_package_quantity=100,planning_packages=1,planning_quantity=100,unit='pcs',
        supplier_offer_not_received=True,commercial_refresh_phase2=True)
    assert additional_tie['quantity_id'] not in mby
    # Count changed ties separately. Existing selected 300 is not asserted
    # sufficient until all retained head/tail/Pi/bank service roles are summed.
    side=read('hardware/electronics/full-cat/w5-side-retention-native-r1/checks.json')
    central=read('hardware/electronics/full-cat/w5-central-retention-native-r1/checks.json')
    new_tie_roles=dict(fixed_frames=12,moving_insulation=12,remote_AUX=1,
        side_body=side['body_ties'],side_insulation=side['insulation_ties'],
        central_body=central['new_body_ties'],central_insulation=central['new_insulation_ties'],
        source_carrier=4,platform=2)
    assert all(isinstance(v,int) and v>=0 for v in new_tie_roles.values())
    finished=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'stock.json',dict(status='CURRENT_CHANGED_ORDER_ROLES_RECONCILED_FULL_TIE_CENSUS_OPEN',
        selected=False,W1_complete=False,W5_complete=False,K3_complete=False,physical_pass=False,
        fastener_rows=changed,new_installed_fastener_roles=allocations,
        retained_unmodified_fastener_rows=len(rows)-len(changed),retained_parent_spares=True,
        material_overrides=[mby[k] for k in overrides],material_stock_basis=prep['affected_material_stock'],
        old920mm_not_added=True,old_BUS300mm_not_added=True,shared_factory_looms='Retain12physical34172/900mm from two packs6, not36pieces.',
        additional_long_tie_order=additional_tie,new_T18I_roles=new_tie_roles,new_T18I_installed_subtotal=sum(new_tie_roles.values()),
        inherited_T18I_planning_quantity=mby['tie:111-02370']['planning_quantity'],
        alias_not_added_twice='The12body split straps ARE the12fixed-frame straps, not another12installed ties.',
        open=['Sum retained and current T18I service replacement roles before claiming complete stock.',
            'Bind these overrides to one selected whole-prototype package after shared service/loop preparation.',
            'Refresh retailer packaging/availability in phase2, no purchase or price promise.'],
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        started_utc=started.isoformat(),finished_utc=finished.isoformat(),worker_wall_seconds=(finished-started).total_seconds()))
    print(json.dumps(dict(changed_fastener_rows=len(changed),new_T18I=sum(new_tie_roles.values()),targets=targets)))

if __name__=='__main__':main()
