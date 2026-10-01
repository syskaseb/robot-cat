"""Preserve R33; reconcile exact fuse data without claiming source qualification."""
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'hardware/manufacturing/one-batch-prototype-r33'
OUT = ROOT / 'hardware/electronics/full-cat/protection-selection-r2'
BATCH = ROOT / 'hardware/manufacturing/one-batch-prototype-r34'
START = datetime.fromisoformat('2026-10-01T21:42:32+00:00')
DEADLINE = datetime.fromisoformat('2026-10-01T23:58:50+00:00')
URLS = {
    'minival.pdf': 'https://www.tme.eu/Document/38439f1a8d3b50ce6254df476b91dadd/MTA_miniVAL_Technical_Data_Sheet.pdf',
    'atof.pdf': 'https://www.littelfuse.com/assetdocs/littelfuse_datasheet_287_atof_r2.7.pdf?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40',
    's821.pdf': 'https://www.nkkswitches.com/pdf/stoggleshighcap.pdf',
    'nkk-load-ratings.pdf': 'https://www.nkkswitches.com/pdf/ElectricalRatings.pdf',
    'feetech-st3215-c018.pdf': 'https://www.feetechrc.com/Data/feetechrc/upload/file/20260622/6391772519923113075854851.pdf',
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    value = datetime.now(timezone.utc)
    assert value < DEADLINE, 'Deadline: keep recoverable files; do not select another revision.'
    return value


def scenario(ref):
    if ref == 'F0':
        return 20, 'Project whole-robot continuous ceiling; NOT enforced current limiting.'
    if ref in ('F_FL', 'F_FR', 'F_RL', 'F_RR'):
        return 8.1, 'Three times manufacturer 2.7A stall reference; NOT allowed continuous stall.'
    if ref == 'F_PI':
        return 5.2 * 3 / (9 * .8) + .01, '3A/5.2V output, assumed efficiency0.8, VIN9V and10mA allowance.'
    if ref == 'F_AUX':
        return 6.24 * 3 / (9 * .8) + .01, '3A/6.24V output, assumed efficiency0.8, VIN9V and10mA allowance.'
    if ref == 'F_PWM':
        return .020, 'Retained E2 project input budget, not measured.'
    if ref in ('F_HY', 'F_HP', 'F_TY'):
        return None, 'Manufacturer page does not provide MG92B current or wire gauge. Do not use SG90 data.'
    return 2.7, 'Single ST3215 manufacturer stall reference, not guaranteed running current or fault limit.'


def render(rows):
    img = Image.new('RGB', (1570, 1040), '#f5f6f8')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 19)
    title = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 25)
    draw.text((25, 20), 'E3: 23 FUSE ROLES / EXACT DATASHEETS / SOURCE COORDINATION OPEN', font=title, fill='#18304a')
    draw.text((25, 64), 'Ref       fuse / A      VDC   break/A    scenario/A    factory-wire evidence', font=font, fill='black')
    for i, row in enumerate(rows):
        current = '--' if row['scenario_A'] is None else f"{row['scenario_A']:.3f}"
        fact = 'UNKNOWN' if row['factory_wire_required'] else 'not a servo factory lead'
        line = f"{row['ref']:9} {row['rating_a']:7g}      {row['dc_rating_v']:3}    {row['dc_interrupt_a']:5}       {current:>6}        {fact}"
        draw.text((25, 98 + 30 * i), line, font=font, fill='#9b3c24' if row['factory_wire_required'] else '#18304a')
    notes = [
        'No new STL, hardware, higher-rated fuses, GUARD or BMS. R33 prints/quantities retained.',
        'MTA1000A/32V and opening table recovered from earlier supplier reference; not a new measurement.',
        'F0:1000A requires evidence for source/loop. 30C*2.2Ah=66A is NOT a short-circuit bound.',
        'ATO/MINI110% can persist>=100h. Typical melting I2t is NOT guaranteed total-clearing energy.',
        'Short insulated prefuse leads are mechanical precautions, not proof of F0 thermal protection.',
        'S821 DC resistive30A is NOT a DC motor rating. No intentional LiPo shorts or shaft stalls.',
        'Phase1 remains13/20=65%. E3 OPEN. This is not electrical or physical PASS.',
    ]
    for i, note in enumerate(notes):
        draw.text((25, 815 + 28 * i), note, font=font, fill='#9b3c24' if i > 1 else '#18304a')
    img.save(OUT / 'preview.png')


def main():
    now()
    if (BATCH / 'manifest.json').exists():
        assert '--draft-refresh' in sys.argv, 'Checkpoint already exists.'
        active = (ROOT / 'hardware/HOBBY_COMPLETION_PLAN.md').read_text(encoding='utf-8').split('## Aktualna granica')[0]
        assert 'K1 Jeden wybrany zestaw STL/ilości/orientacji: R33,' in active, 'R34 already selected; do not overwrite.'
    sys.path.insert(0, str(ROOT / 'tools/cad'))
    from release_check import verify
    parent = read(OLD / 'manifest.json')
    assert verify(ROOT, parent)['integrity_ok']
    OUT.mkdir(exist_ok=True)
    BATCH.mkdir(exist_ok=True)
    save(OUT / 'plan.json', dict(status='SOURCE_SAVED_BEFORE_RECONCILIATION', start_utc=START.isoformat(),
                               scope='E3 only, current F0/S0/manualS1 topology', new_STL=0, physical_pass=False))
    downloads = []
    for name, url in URLS.items():
        now()
        target = OUT / name
        if not target.exists():
            try:
                with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20) as response:
                    raw = response.read(12000001)
                    assert raw.startswith(b'%PDF') and len(raw) <= 12000000
                    target.write_bytes(raw)
            except Exception as error:
                downloads.append(dict(url=url, saved=False, error=str(error), web_tool_read=True))
                continue
        downloads.append(dict(url=url, saved=True, path=target.relative_to(ROOT).as_posix(), sha256=sha(target)))
    sources = dict(
        retrieved_utc=now().isoformat(), downloads=downloads,
        minival=dict(url=URLS['minival.pdf'], revision='version00 PRELIMINARY November2018',
                     exact_supplier='https://www.tme.eu/en/details/amfm-10a/miniature-automotive-fuses/mta/minival-10a/',
                     previous_evidence='hardware/reference/protection-sourcing-2026-09-23/README.md',
                     conclusion='Resolves missing MINIVAL source field in R30; no new physical data.',
                     dc_v=32, breaking_A=1000, ten_amp_test_cable_mm2=1,
                     opening_at_135percent_max_s=120, test_ambient_C=23,
                     typical_I2t_not_guaranteed_total_clearing=True),
        atof=dict(url=URLS['atof.pdf'], revision='02/04/2025 as printed', dc_v=32, breaking_A=1000,
                  opening_at_135percent_max_s=600, test_cable_mm2={'1': .35, '3': .35, '4': .35, '30': 4},
                  typical_load_at65C_A={'1': 1, '3': 3, '4': 3, '30': 23},
                  test_cable_is_not_project_ampacity_approval=True),
        s821=dict(url=URLS['s821.pdf'], page_1based=2, exact_model='S821, NOT S821D',
                  contacts_on=[['2', '3'], ['5', '6']], dc_resistive_A=30, dc_resistive_V=30,
                  DC_inductive_or_motor_rating_in_exact_table=None,
                  AC_motor_750W_NOT_DC_rating=True, no_parallel_poles=True),
        battery=dict(url='https://gensace.de/products/gens-ace-g-tech-soaring-2200mah-11-1v-30c-3s1p-lipo-battery-pack-with-xt60-plug',
                     exact_sku='GEA223S30X6GT', capacity_Ah=2.2, discharge_C=30,
                     manufacturer_fault_current_upper_A=None, manufacturer_impedance_lower_ohm=None),
        factory_wires=dict(st3215='https://www.waveshare.com/wiki/ST3215_Servo',
                           mg92b='https://towerpro.com.tw/product/mg92b/',
                           manufacturer_cross_section_mm2=None, manufacturer_insulation_temperature_C=None),
        feetech_reference=dict(url=URLS['feetech-st3215-c018.pdf'], model='ST-3215-C018', edition='A/0',
                              product_url='https://www.feetechrc.com/525603.html', page_1based=4,
                              connector='5264-3P', cable_length_cm=15,
                              pin_table={'1': 'GND', '2': 'Vcc', '3': 'Signal/TTL'},
                              wire_area_mm2=None, insulation_temperature_C=None,
                              same_delivered_Waveshare_revision_NOT_verified=True,
                              pin_table_NOT_transferred_without_view_orientation=True),
        converter=dict(main='https://www.pololu.com/product/4853', aux='https://www.pololu.com/product/4092',
                       known='Manufacturer over-current/short-circuit/thermal features; not a specified wire-protection threshold.',
                       output_fault_current_guaranteed_upper_A=None,
                       reverse_input_protection_NOT_output_reverse_energy_proof=True),
        pwm=dict(evidence='hardware/electronics/full-cat/pwm-complete-e2-r1/electrical-design.json',
                 url='https://www.littelfuse.com/assetdocs/fuse-242-datasheet?assetguid=6bb278dd-0465-4cc6-8eb1-e0bef73415c4'))
    save(OUT / 'sources.json', sources)
    original = read(ROOT / 'hardware/electronics/full-cat/protection-selection-r1/branch-protection.json')
    rows = copy.deepcopy(original['rows'])
    for row in rows:
        ref, rating = row['ref'], row['rating_a']
        family = '242' if ref == 'F_PWM' else 'MINIVAL' if ref in ('F_FL', 'F_FR', 'F_RL', 'F_RR') else 'ATOF'
        row['family'] = family
        row['dc_interrupt_a'] = 4000 if family == '242' else 1000
        row['dc_rating_v'] = 250 if family == '242' else 32
        row['source'] = sources['pwm']['url'] if family == '242' else URLS['minival.pdf' if family == 'MINIVAL' else 'atof.pdf']
        row['scenario_A'], row['scenario_basis'] = scenario(ref)
        row['fraction_of_fuse_rating'] = None if row['scenario_A'] is None else row['scenario_A'] / rating
        row['factory_wire_required'] = ref in ('F_HY', 'F_HP', 'F_TY') or (len(ref) == 5 and ref[-1] in '123')
        row['factory_wire_qualified'] = False if row['factory_wire_required'] else None
        row['wire_thermal_fault_coordination'] = 'OPEN; no guaranteed lead ampacity or total-clearing proof'
        row['nominal_selection_status'] = 'conditional_hobby_candidate_not_energize_approval'
        row['typical_65C_load_A_not_guarantee'] = sources['atof']['typical_load_at65C_A'].get(str(rating)) if family == 'ATOF' else None
        if family != '242':
            row['opening_table_s'] = {'1.10': {'min': 360000, 'max': None},
                                      '1.35': {'min': .75 if rating > 2 or family == 'MINIVAL' else .35,
                                               'max': 120 if family == 'MINIVAL' else 600},
                                      '1.60': {'min': .25, 'max': 50}, '2.00': {'min': .15 if rating > 2 or family == 'MINIVAL' else .1, 'max': 5},
                                      '3.50': {'min': .04 if family == 'MINIVAL' else .08 if rating > 2 else .02, 'max': .5},
                                      '6.00': {'min': .02 if family == 'MINIVAL' else None, 'max': .1}}
            row['constant_2x_current_time_envelope_A2s_not_clearing_guarantee'] = (2 * rating) ** 2 * 5
        else:
            row['opening_table_s'] = {'3.00': {'max': 10}, '10.00': {'max': .002}}
    assert len(rows) == 23 and len({r['ref'] for r in rows}) == 23
    assert sum(r['factory_wire_required'] for r in rows) == 15
    assert all(r['dc_rating_v'] >= 12.6 and r['dc_interrupt_a'] >= 1000 for r in rows)
    blockers = [
        dict(id='SOURCE', affected=['F0'] + [r['ref'] for r in rows if r['family'] != '242'],
             missing='Guaranteed prospective source fault current or defensible minimum complete-loop impedance.',
             known='Selected pack manufacturer gives30C, no fault-current upper bound. At12.6V,1000A comparison needs>=0.0126ohm.',
             next='Obtain exact pack source bound; analyze each protected loop with guaranteed data. Do not short pack or infer from charger IR.'),
        dict(id='SERVO_LEADS', affected=[r['ref'] for r in rows if r['factory_wire_required']],
             missing='Exact delivered factory lead copper area, insulation limit and connector contact evidence.',
             next='Identify documented cable/contact revision or revise to documented replacement harness; ISO test cable size is not a cable certificate.'),
        dict(id='PREFUSE', affected=['F_PI', 'F_AUX', 'F_PWM'],
             missing='F0 clearing/let-through versus thinner branch before its own fuse.',
             known='Insulated short/restrained routing and<=50mm rule preserved, not thermal qualification.',
             next='Use source bound plus guaranteed total-clearing data and wire limit; evaluate physical assembly with current-limited supply, never deliberate LiPo short.'),
        dict(id='SWITCH_CONVERTERS', affected=['S1', 'MAIN4853', 'AUX4092'],
             missing='Actual DC switched servo/SMPS inrush and reverse-energy behavior; guaranteed output fault-current envelope.',
             next='Retain manualS1 and separate rails; cannot transfer S821D or AC motor rating to S821. No invented limiter/clamp.')]
    save(OUT / 'branch-protection.json', dict(status='EXACT_FUSE_DATA_RECONCILED_SOURCE_COORDINATION_OPEN',
         rows=rows, blockers=blockers, installed_fuses=23, installed_inline_FHAC0001ZXJ=5,
         E3_complete=False, physical_pass=False, new_STL=0))
    budget = dict(assumptions_not_measurements=True, source_max_V=12.6, source_PSC_A=None,
                  required_source_loop_lower_ohm_for1000A=.0126,
                  C_rate_continuous_arithmetic_A=2.2 * 30, C_rate_NOT_fault_bound=True,
                  whole_current_ceiling_A=20, automatic_current_limit=False,
                  aux_input_scenario_A=scenario('F_AUX')[0], main_input_scenario_A=scenario('F_PI')[0],
                  rear_six_ST_stall_plus_aux_pwm_A=16.2 + scenario('F_AUX')[0] + .02,
                  all12_ST_stall_reference_A=12 * 2.7,
                  all12_ST_stall_NOT_allowed_continuous=True,
                  f0_constant60A_5s_envelope_A2s=18000,
                  f0_envelope_NOT_total_clearing_energy=True,
                  guarantee_selective_opening_between_leg10A_and_ST4A=False,
                  selective_opening_note='At4A-ST fuse fault8A,10A trunk is below rating; at high fault both time bands overlap. No complete selectivity claim.',
                  fuse_is_NOT_motor_overload_or_current_clamp=True)
    save(OUT / 'budget.json', budget)
    assert abs(budget['aux_input_scenario_A'] - 2.61) < 1e-9
    assert abs(budget['rear_six_ST_stall_plus_aux_pwm_A'] - 18.83) < 1e-9
    assert budget['all12_ST_stall_reference_A'] > budget['whole_current_ceiling_A']
    # One bounded regression suite: preserve choices and prevent unknown -> PASS.
    old_rows = {r['ref']: r for r in original['rows']}
    regression = {
        '23_unique_refs': len(rows) == len({r['ref'] for r in rows}) == 23,
        'all_SKUs_currents_holders_unchanged': all(all(r[k] == old_rows[r['ref']][k] for k in ('sku', 'rating_a', 'holder')) for r in rows),
        'all_wire_areas_unchanged': all(r['wire_area_design_mm2'] == old_rows[r['ref']]['wire_area_design_mm2'] for r in rows),
        '15_factory_leads_still_unqualified': sum(r['factory_wire_required'] and r['factory_wire_qualified'] is False for r in rows) == 15,
        '3_MG_currents_not_inferred_from_SG90': all(r['scenario_A'] is None for r in rows if r['ref'] in ('F_HY', 'F_HP', 'F_TY')),
        '4_MINIVAL_exact_135percent_time': all(r['opening_table_s']['1.35']['max'] == 120 for r in rows if r['family'] == 'MINIVAL'),
        'ATOF_135percent_not_MINIVAL_time': all(r['opening_table_s']['1.35']['max'] == 600 for r in rows if r['family'] == 'ATOF'),
        'PWM_250V_and_4000A': all(r['dc_rating_v'] == 250 and r['dc_interrupt_a'] == 4000 for r in rows if r['ref'] == 'F_PWM'),
        'source_not_assumed_from_C_rating': budget['source_PSC_A'] is None and budget['C_rate_NOT_fault_bound'],
        'S821_not_S821D_or_AC_rating': sources['s821']['DC_inductive_or_motor_rating_in_exact_table'] is None,
        'no_selectivity_claim': not budget['guarantee_selective_opening_between_leg10A_and_ST4A'],
        'nothing_marked_physical_PASS': all(r['physical_pass'] is False for r in rows),
    }
    assert all(regression.values()), regression
    save(OUT / 'regression.json', dict(tests=regression, tests_passed=len(regression),
         scope='Nominal source reconciliation only, not wire thermal/fault or physical qualification'))
    save(OUT / 'checks.json', dict(status='RECONCILIATION_CHECKS_ONLY', rows=23, factory_lead_open_rows=15,
         missing_minival_r1_field_resolved=True, primary_minival_reference_preexisted=True,
         corrected_F_PWM_DC_rating_V=250, actual_voltage_stress_or_transients_qualified=False,
         data_and_topology_consistent=True, E3_complete=False, phase1_percent=65, new_STL=0,
         physical_pass=False, no_new_circuit=True, no_purchases=True))
    render(rows)
    (OUT / 'README.md').write_text('''# E3: dobór nominalny, koordynacja źródła nadal otwarta

Jedna karta23wybranych bezpieczników, bez nowych części i wydruków. R33 CAD,
wiązka, ilości i wartości wkładek zachowane. Nie podniesiono amperażu.
Źródłowa karta MTA już była w referencji23.09, ale R30 utraciło ten dowód:
R34 przywraca jej32V/1000A i charakterystykę dla konkretnego MiniVAL10A.
KartaMTA jest v00 PRELIMINARY2018, nie pomiar dostawy. F_PWM ma250VDC/4000A
według wybranego E2; korygujemy stary ogólny wpis32V, nie projekt kasetki.

W sources.json są odnośniki do producentów, rewizje i wynik lokalnego
pobrania. branch-protection.json łączy każdą wkładkę, gałąź i obliczenie.
Prądy referencyjne/zadaną granicę20A oddzielono od prądu zwarcia.
23wkładki NIE chronią same z siebie przed zablokowaniem wszystkich napędów.
Nie twierdzimy pełnej selektywności wkładek10A/4A.

E3 pozostaje OPEN: źródło/F0,15fabrycznych doprowadzeń, cieńsze końce przed
ich wkładkami oraz DCłączone obciążenieS821/przetwornic. To braki dowodu
elektrycznego, nie brak mechaniki głowy. Nie wolno ich zaliczyć jako PASS
ani zastąpić typowym topikowymI²t lub założeniem50mm. Karta dokładnegoS821
podaje DCresistive30A, ocena750Wmotor jestAC125V; S821D to inny model.

Próby fazy2: oględziny przewodów/styków, kontrola odizolowania/polaryzacji,
prądowe i termiczne próby na kontrolowanym zasilaniu po doborze granic.
Bez celowego zwarcia pakietu ani blokowania wałów, bez utożsamiania
odczytu rezystancji ładowarką z gwarantowanym minimum impedancji zwarcia.
Brak zasilania/zakupów/GUARD/BMS. 13/20=65%,0nowychSTL; fizycznyPASS=false.
''', encoding='utf-8')
    s = copy.deepcopy(read(OLD / 'selection.json'))
    q = copy.deepcopy(read(OLD / 'one-order-quantities.json'))
    s.update(parent_selection_sha256=sha(OLD / 'selection.json'), E3_complete=False,
             protection_selection=(OUT / 'branch-protection.json').relative_to(ROOT).as_posix(),
             protection_selection_sha256=sha(OUT / 'branch-protection.json'))
    s['conditions'].append('R34 exact fuse data retained; SOURCE/SERVO_LEADS/PREFUSE/SWITCH_CONVERTERS E3 OPEN. No energize approval.')
    q['selected_prints'] = (BATCH / 'selection.json').relative_to(ROOT).as_posix()
    q['protection_reconciliation'] = s['protection_selection']
    assert s['prints'] == read(OLD / 'selection.json')['prints']
    assert q['lines'] == read(OLD / 'one-order-quantities.json')['lines']
    save(BATCH / 'selection.json', s)
    save(BATCH / 'one-order-quantities.json', q)
    (BATCH / 'README.md').write_text('# R34: ten sam zestaw R33, poprawione źródła zabezpieczeń\n\n71zadań/110PETG/4próbki,113pozycji ilości bez zmian.0nowychSTL.\nE3 nadalOPEN;13/20=65%. Dobór i braki: protection-selection-r2.\nBez fizycznegoPASS/zakupu/pushowania. R33 i wcześniejsze pakiety zachowane.\n', encoding='utf-8')
    end = now()
    save(OUT / 'work-time.json', dict(start_utc=START.isoformat(), end_utc=end.isoformat(),
         wall_seconds=(end-START).total_seconds(), kind='E3 exact source and23branch reconciliation including instruction/research/packaging',
         phases_separately_measured=False, result='MiniVAL evidence restored/F_PWM voltage corrected;4source coordination gaps;E3OPEN',
         new_STL=0, physical_pass=False, sealing_and_final_validation_follow=True))
    pins = {r['path']: r['sha256'] for r in parent['files']}
    deps = [Path(__file__), OLD / 'manifest.json', ROOT / 'hardware/reference/protection-sourcing-2026-09-23/README.md']
    deps += [p for d in (OUT, BATCH) for p in d.iterdir() if p.is_file() and p.name not in ('manifest.json', 'validation.json')]
    for p in deps:
        name, digest = p.relative_to(ROOT).as_posix(), sha(p)
        assert name not in pins or pins[name] == digest, name
        pins[name] = digest
    m = copy.deepcopy(parent)
    m.update(new_stls=0, newly_selected_stls=0, E3_complete=False, parent_pins_preserved=len(parent['files']),
             files=[dict(path=p, sha256=h) for p, h in sorted(pins.items())])
    m['gates']['electrical'] = dict(status='open', reason='Exact fuse data known; source/lead/prefuse/switch-converter coordination OPEN.',
                                  evidence=[s['protection_selection']])
    assert all(pins[r['path']] == r['sha256'] for r in parent['files'])
    report = verify(ROOT, m)
    assert report['integrity_ok']
    assert not verify(ROOT, m, True)['integrity_ok']
    save(BATCH / 'manifest.json', m)
    save(BATCH / 'validation.json', dict(integrity=report, parent_pins_preserved=len(parent['files']),
         all_prints_and_quantity_lines_unchanged=True, print_ready_denied=True, physical_pass=False))
    print(json.dumps(dict(pins=len(pins), parent_pins=len(parent['files']), E3_complete=False,
                         installed_fuses=23, new_STL=0, phase1_percent=65, downloads=downloads)))


if __name__ == '__main__':
    main()
