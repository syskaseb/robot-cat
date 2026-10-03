"""One R52 print/order preparation supersedes R51 after local bank closure.

No purchase release, fullW5/K3/E3/A2/A3 still open. All changed print jobs
replace exact identities; three genuinely new PETG parts are counted once.
Bank/Guard fasteners reuse exact existing supplier offers, not spare stock.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,copy,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r52'
def main():
    t=datetime.now(timezone.utc);pins={}
    def read(rel):p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    parent='hardware/manufacturing/one-batch-prototype-r51'
    sel=read(parent+'/selection.json');qty=read(parent+'/one-order-quantities.json');catalog=read(parent+'/nonfastener-catalog.json')
    cart=read('hardware/manufacturing/one-batch-prototype-r49/fixed-fastener-cart.json')
    stock=read('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r7/stock.json')
    assembly=read('hardware/electronics/full-cat/servo-fuse-bank-assembly-r6/assembly.json')
    lift=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json')
    electrical=read('hardware/electronics/full-cat/servo-fuse-bank-electrical-r2/interface.json')
    assert assembly['assembly_complete'] and not lift['hits'] and not lift['errors']
    assert lift['completed_clear_lifts_mm']==[2,5,10,30,60,100]
    assert len(sel['prints'])==73 and len(qty['lines'])==114
    assert not (OUT/'selection.json').exists();OUT.mkdir(parents=True,exist_ok=True)
    definitions=[
      ('Deck','electronics:DeckP10-cover-mount','servo-fuse-guard-fixed-deck-native-r1','DeckFixedGuardFinished','PETG',6),
      ('Guard','electronics:FR-return-guard','servo-fuse-guard-fixed-deck-native-r1','GuardFixedFinished','PETG',10),
      ('BankRight','electronics:servo-fuse-bank-right','servo-fuse-fr-source-fixed-deck-native-r2','BankRightFixedSourceFinished','PETG',10),
      ('BankLeft','electronics:servo-fuse-bank-left','servo-fuse-output-rib-exits-native-r3','BankLeftOutputExitsFinished','PETG',10),
      ('Cover','body:raised-upper-cover-mount','servo-fuse-cover-main-service-r6','CoverWholeRearFeedServiceFinished','PETG',10),
      ('Shelf','electronics:XB11-SpliceShelf','servo-fuse-rear-output-reliefs-native-r1','RearOutputPassagesFinished','PETG',10)]
    prints=[]
    for tag,identity,folder,final,material,brim in definitions:
        native=read('hardware/electronics/full-cat/'+folder+'/checks.json')
        rows=native.get('exports') or native.get('parts') or [native['native']]
        row=next(r for r in rows if r['tag']==tag)
        assert row['final']==final and row['single_solid'] and row['closed_STL'] and row['relocated_reopen']
        cad=ROOT/row['file'];pins[row['file']]=sha(cad)
        stl=cad.parent/(tag+'_UNSELECTED.stl');pins[stl.relative_to(ROOT).as_posix()]=sha(stl)
        dest=OUT/'prints'/(tag+'_SELECTED_x1.stl');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(stl,dest)
        old=next((p for p in sel['prints'] if p['identity']==identity),None)
        if old:assert old['quantity']==1
        item=copy.deepcopy(old) if old else dict(identity=identity,module='electronics',quantity=1,purpose='installed_candidate')
        item.update(stl=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),material=material,status='selected_nominal_prototype_STL',
            recipe='hardware/electronics/full-cat/servo-fuse-bank-assembly-r6/assembly.json',native_file=row['file'],native_final=final,
            dimensions_mm=row['dimensions_mm'],total_brim_allowance_mm=brim,
            orientation='Pinned native export, translated onto bed; no slicer run.',
            supports='Phase2 slicer: inspect openings and stepped post cap. No unsupported-print or physical fit PASS.')
        if old:sel['prints'][sel['prints'].index(old)]=item
        else:sel['prints'].append(item)
        prints.append(item)
    assert len({p['identity'] for p in sel['prints']})==len(sel['prints'])==76
    assert sum(p['quantity'] for p in sel['prints'] if p['purpose']=='installed_candidate')==115
    added_roles=[]
    for sku,n,role in [('0912A2-M020X012VISK',4,'bank:M2x12'),('SKL000381',4,'bank:M2nuts'),('00125202',4,'bank:M2washers'),
                       ('0912A2-M030X008VISK',2,'fixedGuard:M3x8'),('SKL000383',2,'fixedGuard:M3nuts')]:
        row=next(r for r in qty['lines'] if r.get('supplier_sku')==sku)
        newrole='fastener:local-fuse:'+role;assert newrole not in row['quantity_ids']
        row['quantity_ids'].append(newrole);row['roles'].append(dict(id=newrole,planning_quantity=n,
            source='hardware/electronics/full-cat/servo-fuse-bank-assembly-r6/assembly.json',note='New installed local bank/Guard role; parent spares unchanged, not counted twice.'))
        row['planning_quantity']+=n;row['retail_order_quantity']+=n
        assert sum(r['planning_quantity'] for r in row['roles'])==row['planning_quantity']
        idx=next(i for i,r in enumerate(cart['rows']) if r.get('supplier_sku')==sku);cart['rows'][idx]=copy.deepcopy(row)
        added_roles.append(dict(id=newrole,sku=sku,installed=n))
    overrides={'p0:WIRE-INLET-BLACK12-P0':4,'p0:WIRE-RED4-P0':3,'splice:WAGO221-412':6}
    for identity,n in overrides.items():
        row=next(r for r in qty['lines'] if r['id']==identity);row['planning_quantity']=n
        row['product_binding']['planning_quantity']=n
        row['note']='R52 replaces quantity once from current bank-stock-r7; preserves inherited other roles. HELU remaining source920mm is provisional, fullK3/W5 still OPEN.'
        binding=next(r for r in catalog['rows'] if r['quantity_id']==identity);binding['planning_quantity']=n
        if identity=='splice:WAGO221-412':row.update(installed=5,name='WAGO221-412:XB11 and4output splices',spare=1)
    ties=next(r for r in qty['lines'] if r['id']=='tie:111-02370')
    ties['historical_working_allowance']=ties.pop('installed');ties['local_installed']=53;ties['local_service_replacements']=49
    ties['planning_quantity']=300;ties['product_binding']['planning_quantity']=300
    ties['note']='Conservative shared stock ceiling104historical allowance+53local installed+49service=206, rounded to3packs100. NOT actual installed206: known overlap deliberately not deducted before fullK3census. Do not add variants or buy a second separate local bag. Phase1 K3 remains OPEN.'
    next(r for r in catalog['rows'] if r['quantity_id']=='tie:111-02370')['planning_quantity']=300
    # Current exact catalogue and offer allocations stay bound to the same
    # existing114supplier rows; only five installed roles added.
    cart.update(source_roles=sum(len(r['roles']) for r in cart['rows']),supplier_rows=len(cart['rows']),phase1_percent=75,
        local_fuse_added_roles=added_roles,source_sha256=pins)
    catalog.update(current_quantities=(OUT/'one-order-quantities.json').relative_to(ROOT).as_posix(),phase1_percent=75,
        source_sha256=pins,unbound_identity_count=0)
    sel.update(parent_selection=parent+'/selection.json',parent_selection_sha256=pins[parent+'/selection.json'],
        jobs=76,installed_jobs=72,installed_petg_parts=115,fit_samples=4,phase1_percent=75,phase1_complete=False,W5_complete=False,E3_complete=False,
        fixed_fastener_cart=(OUT/'fixed-fastener-cart.json').relative_to(ROOT).as_posix(),nonfastener_catalog=(OUT/'nonfastener-catalog.json').relative_to(ROOT).as_posix(),
        local_fuse_bank_complete=True,local_fuse_assembly='hardware/electronics/full-cat/servo-fuse-bank-assembly-r6/assembly.json',
        local_fuse_electrical='hardware/electronics/full-cat/servo-fuse-bank-electrical-r2/interface.json',
        local_fuse_service='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json',
        local_fuse_stock='hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r7/stock.json',
        local_prints_replace=['electronics:DeckP10-cover-mount','body:raised-upper-cover-mount','electronics:XB11-SpliceShelf'],
        added_local_prints=['electronics:servo-fuse-bank-right','electronics:servo-fuse-bank-left','electronics:FR-return-guard'],
        local_precedence='R52 six pinned local prints and receipts replace only their listed old identities; inherited unrelated prints/circuits unchanged. Historical fingerprints are provenance, not current geometry claims.',
        conditions=['Phase1 remains15/20=75%; local bank is not wholeW5.', 'FullE3/source rating/coordination, wholeW5/K3/A2/A3 remain OPEN.',
            'Shared bank/Cover removal clear at2/5/10/30/60/100mm, not continuous or physical PASS.',
            'PrintedMG92B adapters, catalogue factory lead100mm assumption, clips/PETG and actual crimp/thermal behavior require phase2 trials.',
            'Deck249.5mm fits256 with3mm/side brim allowance; slicer/support checks remain phase2.'],source_sha256=pins)
    qty.update(selected_prints=(OUT/'selection.json').relative_to(ROOT).as_posix(),fixed_fastener_cart=sel['fixed_fastener_cart'],nonfastener_catalog=sel['nonfastener_catalog'],
        phase1_complete=False,local_fuse_stock=sel['local_fuse_stock'],local_fuse_added_roles=added_roles,source_sha256=pins)
    for p in sel['prints']:assert sha(ROOT/p['stl'])==p['sha256'],p['identity']
    for r in qty['lines']:
        if 'product_binding' in r:assert r['planning_quantity']==r['product_binding']['planning_quantity'],r['id']
    for n,j in [('selection.json',sel),('one-order-quantities.json',qty),('fixed-fastener-cart.json',cart),('nonfastener-catalog.json',catalog)]:save(OUT/n,j)
    end=datetime.now(timezone.utc)
    save(OUT/'local-bank-reconciliation.json',dict(status='ONE_LOCAL_BANK_SELECTED_R52_PHASE1_INCOMPLETE',local_bank_complete=True,physical_pass=False,W5_complete=False,
        print_jobs=76,PETG_installed=115,local_prints=prints,added_fastener_roles=added_roles,nominal_input_wire_mm=3020,
        P_ports=20,TE_ends=24,local_ties_installed=53,service_replacements=49,
        full_E3_complete=False,full_K3_complete=False,phase1_completed_count=15,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=t.isoformat(),finished_utc=end.isoformat()))
    print('ONE_R52_LOCAL_BANK_SELECTED',76,115,'PHASE1_15_OF_20',flush=True)
if __name__=='__main__':main()
