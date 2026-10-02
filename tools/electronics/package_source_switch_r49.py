"""Select the single completed S0 local interface, retaining incomplete W5."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,copy,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
from release_check import verify
from source_switch_interface_r1 import verify_reports
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r48'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r49'
OUT=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1'
LOCAL=ROOT/'hardware/electronics/full-cat/source-switch-interface-r1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    start=datetime.now(timezone.utc)
    assert not (BATCH/'manifest.json').exists()
    reports,_=verify_reports();card=read(LOCAL/'interface.json');proof=read(LOCAL/'checks.json')
    for rel,h in proof['source_sha256'].items():assert sha(ROOT/rel)==h,rel
    parent=read(PARENT/'manifest.json');assert verify(ROOT,parent)['integrity_ok']
    BATCH.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    card.update(status='SELECTED_NOMINAL_LOCAL_SOURCE_SWITCH_ONLY',selected=True,current_selected_batch=BATCH.name,remaining=card['remaining'][2:])
    save(OUT/'interface.json',card)
    body=read(ROOT/'hardware/electronics/full-cat/battery-feed-selected-r1/body-harness.json')
    endpoints={r['id']:(r['a'],r['b'],r['net']) for r in body['conductors']}
    for row in body['conductors']:
        if row['id'] in card['nominal_wire_blanks_mm']:
            row.update(nominal_selected_blank_mm=card['nominal_wire_blanks_mm'][row['id']],current_selected_route_checked=True,
                selected_recipe=(OUT/'interface.json').relative_to(ROOT).as_posix(),actual_cut_mm=None)
            row['material']=card[row['id']+'_material']
    assert len(body['conductors'])==80 and endpoints=={r['id']:(r['a'],r['b'],r['net']) for r in body['conductors']}
    count=sum(r.get('nominal_selected_blank_mm') is not None for r in body['conductors']);assert count==14
    body.update(parent=PARENT.name,complete=False,W5_complete=False,local_source_switch=(OUT/'interface.json').relative_to(ROOT).as_posix())
    save(OUT/'body-harness.json',body)
    s,q=copy.deepcopy(read(PARENT/'selection.json')),copy.deepcopy(read(PARENT/'one-order-quantities.json'))
    row=next(r for r in s['prints'] if r['identity']=='electronics:DeckP10-cover-mount')
    row.update(stl=card['STLs'][0],native=card['native_deck'],sha256=sha(ROOT/card['STLs'][0]),
        recipe=(OUT/'interface.json').relative_to(ROOT).as_posix(),orientation='Original lower Deck base on bed,+Zup;S0 portals/cradles and matched bolt axes.')
    stl=card['STLs'][1]
    s['prints'].append(dict(identity='electronics:S0-source-switch-mount',module='source switch',stl=stl,native=card['native_mount'],
        sha256=sha(ROOT/stl),quantity=1,purpose='installed_candidate',material='PETG',status='conditional_hobby_phase1_selection',
        recipe=(OUT/'interface.json').relative_to(ROOT).as_posix(),orientation='Broad panelY98 face down; exported68.5x99x8.5mm.',
        supports='Phase2 slicer: inspect/support posts and lateral feet; no layer/strength/toolpath claim.',print_size_mm_including_5mm_brim=[78.5,109,8.5]))
    fast=read(ROOT/s['fixed_fastener_cart'])
    for sku,quantity in [('0912A2-M020X012VISK',2),('00125202',4),('SKL000381',2)]:
        row=next(r for r in q['lines'] if r.get('supplier_sku')==sku)
        role=dict(id='fastener:S0:'+sku,planning_quantity=quantity,source=(OUT/'interface.json').relative_to(ROOT).as_posix(),note='One installed S0 mount; parent spare allowance unchanged.')
        row['roles'].append(role);row['quantity_ids'].append(role['id']);row['planning_quantity']+=quantity
        row['retail_order_quantity']=math.ceil(max(row['planning_quantity'],row['retail_minimum_pieces'])/row['retail_multiple_pieces'])*row['retail_multiple_pieces']
        row['pack_excess_quantity']=row['retail_order_quantity']-row['planning_quantity']
        fast['rows'][next(i for i,r in enumerate(fast['rows']) if r['supplier_sku']==sku)]=copy.deepcopy(row)
    for part in card['new_quantities_to_allocate']['M6_M10']:
        sku=part['sku'];assert not any(r.get('supplier_sku')==sku for r in q['lines']),sku
        role=dict(id='fastener:S0:'+sku,planning_quantity=part['quantity'],source=(OUT/'interface.json').relative_to(ROOT).as_posix(),note='Sourced nominal S0 hardware; no credit for unspecified supplied nuts.')
        row=dict(id='supplier:NORMREICH:'+sku,name=sku,unit='pcs',supplier='NORMREICH',supplier_sku=sku,url=part['url'],
            dimensions_mm={k:v for k,v in part.items() if k not in ('sku','quantity','url')},quantity_ids=[role['id']],roles=[role],
            planning_quantity=part['quantity'],retail_order_quantity=part['quantity'],pack_excess_quantity=0,
            retail_minimum_pieces=1,retail_multiple_pieces=1,evidence='Supplier offer1x and nominal dimensions read2026-10-02; prices/stock/delivery refreshed in phase2.',
            source=(OUT/'interface.json').relative_to(ROOT).as_posix(),physical_pass=False)
        q['lines'].append(row);fast['rows'].append(copy.deepcopy(row))
    fast.update(source_roles=sum(len(r['roles']) for r in fast['rows']),supplier_rows=len(fast['rows']),K2_complete=False)
    assert fast['supplier_rows']==34 and fast['source_roles']==44
    save(BATCH/'fixed-fastener-cart.json',fast)
    tie=next(r for r in q['lines'] if r['id']=='tie:111-02370');assert tie['installed']==102
    tie.update(installed=104);tie['note']+=' R49 adds2 W066 ties; planning200 unchanged. Not final W5 census.'
    wire=next(r for r in q['lines'] if r['id']=='p0:WIRE-RED4-P0');assert wire['planning_quantity']==2
    wire['note']+=' R49 reserves330mm forW066 replacing legacy300mm, not adding both. Remaining1670mm shared by unresolvedW064/W065/W067/W068; not final stock approval.'
    rings=next(r for r in q['lines'] if r['id']=='p0:TERMINAL-S0-P0');assert rings['planning_quantity']==2
    rings['note']+=' Both rings allocated toW076/W066; no additional quantity.'
    s.update(parent_selection_sha256=sha(PARENT/'selection.json'),jobs=73,installed_jobs=69,installed_petg_parts=112,
        body_harness=(OUT/'body-harness.json').relative_to(ROOT).as_posix(),body_harness_sha256=sha(OUT/'body-harness.json'),
        local_source_switch=(OUT/'interface.json').relative_to(ROOT).as_posix(),fixed_fastener_cart=(BATCH/'fixed-fastener-cart.json').relative_to(ROOT).as_posix(),phase1_percent=70)
    q.update(selected_prints=(BATCH/'selection.json').relative_to(ROOT).as_posix(),body_harness=s['body_harness'],fixed_fastener_cart=s['fixed_fastener_cart'],line_count=len(q['lines']))
    assert len(s['prints'])==73 and sum(r['quantity'] for r in s['prints'] if r['purpose']=='installed_candidate')==112
    assert len(q['lines'])==114 and len({r['id'] for r in q['lines']})==114
    save(BATCH/'selection.json',s);save(BATCH/'one-order-quantities.json',q)
    save(BATCH/'validation.json',dict(phase1_percent=70,print_jobs=73,installed_PETG=112,fit_samples=4,selected_body_blanks=14,
        total_body_blanks=80,quantity_rows=114,fastener_offers=34,fastener_roles=44,small_ties_working=104,small_ties_planning=200,
        endpoints_preserved=True,W5_complete=False,K2_complete=False,K3_complete=False,physical_pass=False))
    end=datetime.now(timezone.utc);save(OUT/'work-time.json',dict(started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    pins={r['path']:r['sha256'] for r in parent['files']}
    folders=[OUT,BATCH,LOCAL]
    for f in ('source-switch-layout-r6','source-switch-restraints-r2','source-switch-mount-finish-r4','source-switch-assembly-finish-r3','source-switch-deck-native-r1','source-switch-deck-native-r3'):
        folders.append(ROOT/'hardware/electronics/full-cat'/f)
    for f in ('source-switch-mount-finish-r4','source-switch-deck-native-r1','source-switch-deck-native-r3'):
        folders.append(ROOT/'hardware/cad/studies'/f)
    for folder in folders:
        for p in folder.iterdir():
            if p.is_file() and p.suffix in ('.json','.brep','.stl','.FCStd') and p.name!='manifest.json':
                rel=p.relative_to(ROOT).as_posix();assert rel not in pins or pins[rel]==sha(p),rel;pins[rel]=sha(p)
    for name in ('source_switch_layout_r6.py','source_switch_restraints_r2.py','source_switch_mount_finish_r4.py','source_switch_assembly_finish_r3.py','source_switch_deck_native_r1.py','source_switch_deck_native_r3.py','source_switch_interface_r1.py','package_source_switch_r49.py','test_source_switch_interface_r1.py'):
        rel='tools/electronics/'+name;pins[rel]=sha(ROOT/rel)
    manifest=copy.deepcopy(parent);manifest.update(files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())],parent_pins_preserved=len(parent['files']),newly_selected_stls=2,W5_complete=False)
    result=verify(ROOT,manifest);assert result['integrity_ok'],result;save(BATCH/'manifest.json',manifest)
    print(json.dumps(dict(status='R49_LOCAL_SOURCE_SWITCH_SELECTED',jobs=73,installed_PETG=112,body_blanks=14,phase1_percent=70,pins=len(pins))),flush=True)

if __name__=='__main__':main()
