"""Current E1 nominal module selection, not global W5/E3/print approval."""
from collections import Counter
import math
from datetime import datetime, timezone
import json, time
from pathlib import Path
from package_open_prototype_tail import ROOT, BASE, read, save, sha, stl_size
from release_check import verify, REQUIRED_GATES

OUT = BASE / 'body-harness-checkpoint'
PROOFS = ('u1-socket-passives-resolved', 'u1-common-wiring-checks',
          'u1-grouped-grips-checks',
          'u1-board-grips-checks', 'u1-power-grips-checks',
          'u1-service-departures-checks', 'e2-tail-insulation-current')


def require_clear(proof):
    assert 'status' in proof and 'errors' in proof
    assert not proof['errors']
    assert any(k in proof for k in ('contacts','wire_contacts','passive_material_resolutions'))
    for key in ('contacts', 'reservation_resolutions', 'self_proximity',
                'local_link_material_resolutions', 'passive_material_resolutions',
                'wire_contacts','material_resolutions','USB_fit_reservations',
                'wire_clearance_resolutions','overlaps'):
        assert not proof.get(key), key


def current_routes(common, departures):
    routes = {**common['complete_routes'], **common['changed_MAIN_pair'],
              **departures['replacements']}
    assert len(routes) == 13
    rows = []
    for name, r in routes.items():
        source = r.get('source', {})
        if name in ('W079','W080'):
            source = dict(a={'ref':'MAIN.OUT+' if name=='W079' else 'MAIN.OUT-',
                             'world_mm':r['parts'][0]['start']},
                          b={'ref':'Pi.USB-C via sealed K1474 and Delock60047',
                             'net':'5V_PI' if name=='W079' else 'G_SYS',
                             'world_mm':r['parts'][-1]['end']},
                          sku_candidate='K1474-existing-18AWG',
                          construction='Retain sealed K1474 receiver; named MAIN solder end, passive USB-C elbow only. Source pin/fit must be checked without power.')
        sku = source.get('sku_candidate', 'K1474-existing-18AWG' if name in ('W079', 'W080') else None)
        assert sku and r['nominal_blank_mm'] >= r['guide_mm'], name
        rows.append(dict(wire=name, sku=sku, guide_mm=r['guide_mm'],
                         nominal_fit_blank_mm=r['nominal_blank_mm'], actual_cut_mm=None,
                         ends=[source.get('a'), source.get('b')],
                         construction=source.get('construction', 'Existing sealed K1474 cable: preserve receiver, trim only permitted terminal end'),
                         source_end_record=r if not source else source))
    assert next(x for x in rows if x['wire']=='XL01')['nominal_fit_blank_mm']==186
    assert next(x for x in rows if x['wire']=='XL09')['nominal_fit_blank_mm']==144
    return rows


def run():
    tick = time.monotonic()
    n = read(OUT / 'e1-current-assembly-native.json')
    assert n['status'] == 'E1_LINKED_NATIVE_ASSEMBLY_PREPARED_SELECTION_OPEN'
    assert n['fresh_relocated_reopen'] and n['parameter_link_test_mm'] == [2.5, 2.7, 2.5]
    assert n['full_guide_count'] == 13 and n['actual_purchased_PCB_holes']
    assert sha(ROOT / n['native']) == n['native_sha256']
    pins = {OUT / 'e1-current-assembly-native.json', ROOT / n['native'], Path(__file__)}
    for path, digest in n['source_sha256'].items():
        assert sha(ROOT / path) == digest, path
        pins.add(ROOT / path)
    proofs = {}
    for name in PROOFS:
        f = OUT / (name + '.json'); proofs[name] = read(f)
        require_clear(proofs[name]); pins.add(f)
    # Earlier receipts retain their dated OPEN labels. Their exact unchanged
    # scope, not a refreshed all-robot verdict, is carried by this selection.
    reuse = proofs['u1-socket-passives-resolved']['reused_scope']
    assert reuse['retained_context_sources_verified']
    assert reuse['reconstructed_previous_carrier_SHA256_verified']
    assert reuse['unchanged_physical_leads'] == 84
    carrier = read(OUT / 'u1-socket-carrier-plan.json')
    assert carrier['checks']['source_circuit_preserved'] and carrier['checks']['copper_graph_connected']
    assert carrier['checks']['occupied_holes']==100 and carrier['checks']['chip_pins']==24
    common = read(OUT / 'u1-common-wiring-plan.json')
    dep = read(OUT / 'u1-service-departures-plan.json')
    routes = current_routes(common, dep)
    links = read(OUT / 'u1-socket-links-plan.json')
    assert not links['conflicts'] and links['wire_nominal_sum_mm']==324
    leads = read(OUT / 'u1-socket-passive-leads.json')
    assert not leads['stock_failures'] and not leads['conflicts']
    prints = []
    for row in n['current_print_exports']:
        assert sha(ROOT/row['path']) == row['sha256']
        size = stl_size(ROOT/row['path']); assert max(size)+10 < 256
        prints.append({**row, 'print_size_mm':size, 'margin_each_mm':5,
                       'allocation':'One current physical part; replaces prior export with same identity, never an additional carrier'})
        pins.add(ROOT/row['path'])
    assert len(prints)==9 and len({r['part'] for r in prints})==9
    components = Counter()
    for row in carrier['parts']:
        components[row['sku']] += row.get('quantity', row.get('qty',1))
    for row in carrier['adapter_local_parts'] + carrier['connectors']:
        components[row['sku']] += row.get('quantity',1)
    components.update({'Adafruit1608':1,'Adafruit1208':1,'SN74LVC8T245PW':1})
    sleeve_blanks = [dict(ref=r['ref'],sku=r['sleeve_candidate'],
                         nominal_fit_blank_mm=math.ceil(r['guide_mm']+1),
                         note='Raw allowance; trim to keep solder/body lands exposed after restricted recovery. Actual coverage/length change is a delivery gate.')
                     for r in leads['leads'] if r.get('sleeve_candidate')]
    assert len(sleeve_blanks)==7
    # Native references and source graph, not an unknown external U1 pinout.
    selection = dict(status='CURRENT_E1_NOMINAL_MODULE_SELECTED', result_id='E1',
        selected=True, E1_complete=True, W5_complete=False, E3_complete=False, physical_pass=False,
        native=n['native'], native_sha256=n['native_sha256'], prints=prints,
        scope='Complete current PWM signal module, known source circuit/population, shared native supports, local/full interfaces and independent grips. No cosmetic shell or whole-robot service qualification.',
        components=dict(components), board=carrier['board'], adapter=carrier['adapter'],
        retained_purchased_modules={'Adafruit815_PCA9685':1,'owned_Pi4B':1,'K1474_receiver_and_existing_power_cable':1},
        USB_receiver=common['USB_receiver'],
        copper_cuts=carrier['copper_cuts'], circuit_checks=carrier['checks'],
        remote_parts='R7/R8/R9 remain in qualified W3/W4 head/tail connector modules, not another three local parts.',
        full_routes=routes, local_links=links['links'], ground_bus=links['ground_bus'],
        formed_component_leads=leads['leads'],
        materials=dict(Adafruit1446_fixed_logic_mm=773, local_link_mm=324,
            LAPP4126002S_fixed_logic_mm=474, Pololu1871_factory_600mm_leads=5,
            K1474_existing_receiver_blanks_mm=[186,221],
            new_T18R=9, retainer_T18I=2, new_metal_fasteners=0,
            AlphaWire802534B_lacing_blanks_mm=[150,150,150,150],
            lacing_practice_allowance_mm=400, lacing_procurement='Cut-length contribution only; actual short supply/whole K3 stock not selected here.',
            E2_Temflex165_replacement_blanks_mm=[[300,10],[300,10]],
            foam_pads_mm=[[5,3,2],[5,3,2]],
            sleeve_blanks=sleeve_blanks,
            sleeve='TE MT-LWA-1/32-X-STK / CR3042-000, seven fixed logic component leads per formed_component_leads; finished OD<=1.2 is a delivery gate, not catalogue wall thickness'),
        assembly=[
            'No source attached. Bench-build actual1608/1208 source population; make only the three specified copper cuts and check isolated copper/24 chip nets without power.',
            'Form/sleeve fixed local links and seven component leads before mounting in PETG. Heat shrink only on bench; protect components. Trim male header tails<=1.4mm above adapter; keep orientation key.',
            'Prepare changed E2 board ends with two long insulation wraps and jacket overlap; retain the unchanged third wrap separately. Fit LowerCarrier/E2Fixture before upper board stack.',
            'Install current AnchorLeft/Right using existing PCB bolts, then keyed RetainerBar/two foam pads/twoT18I. No metal washer against copper.',
            'Mount PCA9685/1608 on the bench upper carrier. Solder named current pads, dress thirteen whole wires in the saved guides and tie the independent GPIO/PCA/board/MAIN/USB grip lands, never solder pads or WAGO levers.',
            'Use GPIO/PCA existing bolts raised0.7mm with integral feet replacing four upper washers; MAIN similarly replaces two upper washers. No extra metal kit.',
            'Fit Pi/BUS and lower wiring first, then upper carrier on existing32mm posts/side-access nuts, then MTA above U1. Retain MAIN worldZ46.52 and both exits of all four MTA.',
            'For deeper repair remove sources, label/release the affected wiring and reverse staged assembly including MTA/upper carrier. Cut only affected replaceable ties/lacing. Fast in-situ U1/BUS parking is NOT claimed; connected whole-robot teardown remains A2/W5.'
        ],
        electrical_disposition=dict(
            source='hardware/reference/u1-socket-connectors-2026-10-12/sleeve-facts.json',
            decision='Nominal prototype preparation only. Sleeve retained exclusively on fixed logic leads, not raw battery/motor wiring, load restraint, fire containment or proof of fault coordination. Catalogue non-flame-retardancy and unverified finished wall remain explicit. The original candidate no-power/E3 gate remains mandatory; this nominal choice is not electrical acceptance.',
            power_allowed=False, global_E3_gate_waived=False),
        phase2_gates=carrier['delivery_gates'] + [
            'Delivered sleeve/lead coverage and OD, solder fillets and header retention; magnified inspection and unpowered continuity before insertion.',
            'Delivered wire jackets and bends, actual WAGO entry/levers, USB plug fit and pin registration; manually inspect all grip lands before power.',
            'PETG coupon/creep, tie pressure and printed asymmetric key; actual manual assembly and motion fit.',
            'Global E3 battery/fuse/factory-wire/fault/thermal approval before any power. No physical PASS.'
        ], reused_geometry_scope=reuse,
        excluded_failed_studies=['BUS-current-removal','BUS-ground-service','BUS-service-current'],
        measured_native_seconds=n['worker_seconds'], checked_utc=datetime.now(timezone.utc).isoformat())
    save(OUT/'e1-selection.json',selection)
    for name in ('e1-selection.json','E1-README.md','u1-socket-carrier-plan.json',
                 'u1-common-wiring-plan.json','u1-service-departures-plan.json',
                 'u1-socket-links-plan.json','u1-socket-passive-leads.json'):
        pins.add(OUT/name)
    pins.add(ROOT/'hardware/reference/u1-socket-connectors-2026-10-12/sleeve-facts.json')
    pins.add(ROOT/'tools/cad/test_current_e1_package.py')
    pins.add(OUT/'.gitattributes')
    manifest=dict(schema_version=1,readiness='prototype',result_id='E1',physical_pass=False,
        files=[dict(path=f.relative_to(ROOT).as_posix(),sha256=sha(f)) for f in sorted(pins)],
        gates={g:dict(status='open',reason='Delivered phase2 gate. No power or physical approval; whole W5/A2 and global E3 remain open.') for g in REQUIRED_GATES})
    manifest['gates']['geometry']=dict(status='pass',reason='Current E1 scoped native ownership, 9 current exports, 13 full routes, 28 independent grip lands and qualified changed interfaces. Reused unchanged evidence explicit, rejected fast service not passed.',evidence=[(OUT/'e1-current-assembly-native.json').relative_to(ROOT).as_posix(),(OUT/'e1-selection.json').relative_to(ROOT).as_posix()])
    assert verify(ROOT,manifest)['integrity_ok'];assert not verify(ROOT,manifest,True)['integrity_ok']
    save(OUT/'e1-manifest.json',manifest)
    print(json.dumps(dict(integrity_ok=True, files=len(pins), current_prints=9,
                         E1_nominal_complete=True, score_not_automatically_changed=True,
                         seconds=round(time.monotonic()-tick,3))))


if __name__=='__main__':run()
