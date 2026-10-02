"""Select the completed local source feed, without claiming S0 or whole W5."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,copy,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from release_check import verify
from servo_fuse_inputs_r1 import save,sha
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r47'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r48'
PAIR=ROOT/'hardware/electronics/full-cat/battery-feed-access-finish-r1'
OUT=ROOT/'hardware/electronics/full-cat/battery-feed-selected-r1'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    started=datetime.now(timezone.utc)
    assert not (BATCH/'manifest.json').exists()
    evidence=read(PAIR/'checks.json')
    assert evidence['status']=='NOMINAL_LOCAL_FEED_PAIR_WITH_ASSEMBLY_ACCESS_CONDITION' and not evidence['hits'] and not evidence['errors']
    for rel,h in evidence['source_sha256'].items():assert sha(ROOT/rel)==h,rel
    assert sha(ROOT/'tools/electronics/battery_feed_access_finish_r1.py')==evidence['script_sha256']
    assert sha(ROOT/evidence['parent_check'])==evidence['parent_check_sha256']
    parent=read(PARENT/'manifest.json');assert verify(ROOT,parent)['integrity_ok']
    BATCH.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    card=dict(status='SELECTED_NOMINAL_LOCAL_FEED_ONLY',parent='one-batch-prototype-r47',
        source_checks=(PAIR/'checks.json').relative_to(ROOT).as_posix(),source_checks_sha256=sha(PAIR/'checks.json'),
        source_mount_xy=evidence['mount_xy'],source_ties=7,fasteners=evidence['extra_fasteners'],
        wire_blanks_mm={'W001':140,'W075':40},actual_cut_mm=None,
        W075_material='Original LittelfuseFHAC0002ZXJ orange12AWG GXL lead; not an added LAPP conductor.',
        W001_material='LAPP0107001 black12AWG PTFE; one conductor per G1.1 port.',
        prototype_assumptions=['F0 body51x17.7x22, lead axis10 and OD4.5/R10 not supplier dimensions.',
            'Robot XT60 cup pitch7 provisional; actual marked polarity controls soldering, not left/right coordinates.',
            'XT60 solder strip5mm is a fitting allowance, NOT a manufacturer solder-process specification.',
            'Nut/socket tool clearances are modeled reserves, not an exact supplied-tool model.'],
        assembly=['Disconnect battery; install the bridge and prethread its six ties while Deck underside is accessible.',
            'Align bridge and Deck holes at(-10,53)/(61,53);2DIN912M2x12,4DIN125M2,2DIN934M2. Hold lower nuts; no PETG torque invented.',
            evidence['assembly_access_condition'],
            'Fix F0 body with two ties atX-2/24; robot-side XT60 with its body tie. Restrain all three intact insulated leads separately.',
            'Check actual F0 lead length before trimming W075 to nominal40mm; direct robotXT60 plus to F0, no pre-fuse intermediate joint.',
            'W001 nominal140mm includes14mm G1 strip,5mm solder allowance and10mm fitting margin. Check reach and delivered markings before cutting.',
            'Prethread independent G1BAT tie through full Deck slots; terminate W001 inG1.1/X51 without tinning or double-wire stuffing. Grip insulation by hand.',
            'W076 free switch lead is only parked/retained, not cut to a selected length. S0/W066 and whole battery mate/reach remain open.'],
        conditions=[evidence['assembly_access_condition'],'Existing R44 soft insulation contact condition is retained; not whole-robot collision freedom.',
            'Factory F0 minimum lead tolerance/OD, actual grip, battery mate/reach, electrical/thermal tests are phase2, not performed.',
            'Complete source needs S0 location and both remaining routes; this local selection does not close W5 or E3.'],
        selected=True,W5_complete=False,E3_complete=False,physical_pass=False)
    save(OUT/'interface.json',card)
    body=read(ROOT/'hardware/electronics/full-cat/body-harness-w5-r2/interface.json')
    body=copy.deepcopy(body);before={r['id']:(r['a'],r['b'],r['net']) for r in body['conductors']}
    for row in body['conductors']:
        if row['id'] in card['wire_blanks_mm']:
            row.update(nominal_selected_blank_mm=card['wire_blanks_mm'][row['id']],current_selected_route_checked=True,
                       selected_recipe=(OUT/'interface.json').relative_to(ROOT).as_posix(),actual_cut_mm=None)
            row['material']=card[row['id']+'_material']
    assert len(body['conductors'])==80 and before=={r['id']:(r['a'],r['b'],r['net']) for r in body['conductors']}
    selected=sum(r.get('nominal_selected_blank_mm') is not None for r in body['conductors'])
    assert selected==12,selected
    body.update(parent='one-batch-prototype-r47',complete=False,W5_complete=False,
                local_source_feed=(OUT/'interface.json').relative_to(ROOT).as_posix())
    save(OUT/'body-harness.json',body)
    s,q=copy.deepcopy(read(PARENT/'selection.json')),copy.deepcopy(read(PARENT/'one-order-quantities.json'))
    decks=[r for r in s['prints'] if r['identity']=='electronics:DeckP10-cover-mount'];assert len(decks)==1
    decks[0].update(stl='hardware/cad/studies/battery-feed-pair-r2/Deck_x1.stl',native=evidence['deck_native'],
                    recipe=(OUT/'interface.json').relative_to(ROOT).as_posix(),
                    sha256=sha(ROOT/'hardware/cad/studies/battery-feed-pair-r2/Deck_x1.stl'),
                    orientation='Original lower Deck base on bed, +Zup; retained R44 features plus matched source bores and G1.1 restraint.')
    bridge='hardware/cad/studies/battery-feed-mount-finish-r2/Bridge_x1.stl'
    s['prints'].append(dict(identity='electronics:F0-XT60-source-bridge',module='independent source feed',stl=bridge,
        native=evidence['bridge_native'],sha256=sha(ROOT/bridge),quantity=1,purpose='installed_candidate',material='PETG',
        status='conditional_hobby_phase1_selection',recipe=(OUT/'interface.json').relative_to(ROOT).as_posix(),
        orientation='Floor57 on bed, +Zup; bridge99x60x48mm, including5mm brim109x70x48.',
        supports='Phase2 slicer: support suspended foot overhangs and inspect tie slots; no toolpath claim.',
        print_size_mm_including_5mm_brim=[109,70,48]))
    assert len(s['prints'])==72 and sum(r['quantity'] for r in s['prints'] if r['purpose']=='installed_candidate')==111
    assert sum(r['quantity'] for r in s['prints'] if r['purpose']!='installed_candidate')==4
    assert len({r['identity'] for r in s['prints']})==72
    fast=read(ROOT/s['fixed_fastener_cart'])
    for sku,count in [('0912A2-M020X012VISK',2),('00125202',4),('SKL000381',2)]:
        row=next(r for r in q['lines'] if r.get('supplier_sku')==sku)
        role=dict(id='fastener:source-feed:'+sku,planning_quantity=count,source=(OUT/'interface.json').relative_to(ROOT).as_posix(),note='Added installed source bridge hardware; parent spare allowance unchanged.')
        row['roles'].append(role);row['quantity_ids'].append(role['id']);row['planning_quantity']+=count
        row['retail_order_quantity']=math.ceil(max(row['planning_quantity'],row['retail_minimum_pieces'])/row['retail_multiple_pieces'])*row['retail_multiple_pieces']
        row['pack_excess_quantity']=row['retail_order_quantity']-row['planning_quantity']
        oldrow=next(i for i,r in enumerate(fast['rows']) if r['supplier_sku']==sku);fast['rows'][oldrow]=copy.deepcopy(row)
    fast.update(source_roles=36,supplier_rows=29,K2_complete=False)
    save(BATCH/'fixed-fastener-cart.json',fast)
    tie=next(r for r in q['lines'] if r['id']=='tie:111-02370');assert tie['installed']==95
    tie.update(installed=102,planning_quantity=200)
    tie['note']+=' R48 adds7 source/G1 ties:102 working; choose2bags100 because one bag cannot cover102. Not a final W5/K3 census.'
    tie['product_binding']['planning_quantity']=200
    catalog=read(ROOT/s['nonfastener_catalog'])
    next(r for r in catalog['rows'] if r['quantity_id']=='tie:111-02370')['planning_quantity']=200
    save(BATCH/'nonfastener-catalog.json',catalog)
    s.update(parent_selection_sha256=sha(PARENT/'selection.json'),jobs=72,installed_jobs=68,installed_petg_parts=111,phase1_percent=70,
        quantity_only_revision=False,
        body_harness=(OUT/'body-harness.json').relative_to(ROOT).as_posix(),body_harness_sha256=sha(OUT/'body-harness.json'),
        local_source_feed=(OUT/'interface.json').relative_to(ROOT).as_posix(),
        fixed_fastener_cart=(BATCH/'fixed-fastener-cart.json').relative_to(ROOT).as_posix(),
        nonfastener_catalog=(BATCH/'nonfastener-catalog.json').relative_to(ROOT).as_posix(),W5_complete=False,K2_complete=False,K3_complete=False)
    q.update(selected_prints=(BATCH/'selection.json').relative_to(ROOT).as_posix(),
        body_harness=s['body_harness'],fixed_fastener_cart=s['fixed_fastener_cart'],nonfastener_catalog=s['nonfastener_catalog'],
        W5_complete=False,K2_complete=False,K3_complete=False)
    assert len(q['lines'])==109 and len({r['id'] for r in q['lines']})==109
    q['line_count']=109
    save(BATCH/'selection.json',s);save(BATCH/'one-order-quantities.json',q)
    end=datetime.now(timezone.utc)
    save(OUT/'validation.json',dict(print_jobs=72,installed_PETG=111,fit_samples=4,selected_blanks=12,total_conductors=80,
        quantity_rows=109,fastener_offers=29,fastener_roles=36,small_ties_working=102,small_ties_planning=200,
        original_electrical_endpoints_preserved=True,phase1_percent=70,W5_complete=False,physical_pass=False))
    save(OUT/'work-time.json',dict(package_started_utc=started.isoformat(),package_finished_utc=end.isoformat(),package_wall_seconds=(end-started).total_seconds()))
    pins={r['path']:r['sha256'] for r in parent['files']}
    directories=[OUT,BATCH,PAIR,ROOT/'hardware/electronics/full-cat/battery-feed-pair-r2',ROOT/'hardware/cad/studies/battery-feed-pair-r2',
        ROOT/'hardware/electronics/full-cat/battery-feed-bridge-r1',ROOT/'hardware/cad/studies/battery-feed-bridge-r1',
        ROOT/'hardware/electronics/full-cat/battery-feed-return-finish-r2',ROOT/'hardware/cad/studies/battery-feed-return-finish-r2',
        ROOT/'hardware/electronics/full-cat/battery-feed-mount-finish-r2',ROOT/'hardware/cad/studies/battery-feed-mount-finish-r2']
    for folder in directories:
        for pp in folder.iterdir():
            if pp.is_file() and pp.suffix!='.FCBak' and pp.name not in ('manifest.json',):
                rel=pp.relative_to(ROOT).as_posix();assert rel not in pins or pins[rel]==sha(pp);pins[rel]=sha(pp)
    for n in ['battery_feed_bridge_r1.py','battery_feed_return_finish_r2.py','battery_feed_mount_finish_r2.py','battery_feed_pair_r2.py','battery_feed_access_finish_r1.py','package_battery_feed_r48.py','test_battery_feed_selection_r1.py']:
        pp=ROOT/'tools/electronics'/n;pins[pp.relative_to(ROOT).as_posix()]=sha(pp)
    manifest=copy.deepcopy(parent);manifest.update(files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())],
        parent_pins_preserved=len(parent['files']),newly_selected_stls=2,W5_complete=False,K3_complete=False)
    result=verify(ROOT,manifest);assert result['integrity_ok'],result
    save(BATCH/'manifest.json',manifest)
    save(BATCH/'validation.json',dict(integrity=result,phase1_percent=70,W5_complete=False,K2_complete=False,K3_complete=False,
        print_jobs=72,installed_PETG=111,fit_samples=4,selected_blanks=12,physical_pass=False))
    print(json.dumps(dict(status='R48_LOCAL_SOURCE_FEED_SELECTED',phase1_percent=70,jobs=72,selected_blanks=12,pins=len(pins))),flush=True)


if __name__=='__main__':main()
