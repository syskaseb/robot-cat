"""One reusable workshop-access set; no ownership, purchase or physical PASS."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/assembly-tools-k3-r2'
REF = ROOT / 'hardware/reference/assembly-tools-2026-10-02'
START = '2026-10-02T06:11:42+00:00'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')


def payload():
    # Product facts only; temperatures are NOT an approved solder/shrink process.
    weller = 'https://www.weller-tools.com/'
    wera = 'https://www.wera.de/'
    tools = [
        dict(role='solder_station', maker='Weller', sku='T0053298699', quantity=1,
             model='WE1010 Set 230V with WEP70/PH70', iron_power_W=70, supply_V=230,
             tip_family='ET', source=weller+'eu/gb/industrial-soldering/products/soldering-stations/we1010-set-230v',
             use='Pola MAIN/PWM, stałe splices i XT60; nie lutować baterii. Moc nominalna nie dowodzi czasu nagrzania złącza4mm².'),
        dict(role='solder_tip_large', maker='Weller', sku='4ETD-1', quantity=1,
             width_mm=4.6, thickness_mm=.8, compatible_iron='WEP70',
             source=weller+'mea/gb/industrial-soldering/products/soldering-tips/et-d',
             use='XT60 i większe końce; geometria grotu nie zastępuje próby lutowania na odłączonej próbce.'),
        dict(role='solder_tip_board', maker='Weller', sku='4ETB-1', quantity=1,
             width_mm=2.4, thickness_mm=.8, compatible_iron='WEP70',
             source=weller+'mea/gb/industrial-soldering/products/soldering-tips/et-b',
             use='Pola płytki i małe końce; sprawdzić zawartość pożyczonego zestawu, nie liczyć posiadanego grotu drugi raz.'),
        dict(role='wire_strip_and_cut', maker='KNIPEX', sku='12 40 200', quantity=1,
             EAN='4003773026662', wire_area_mm2=[.03,10], stranded_cut_max_mm2=10,
             old_stop_range_mm=[3,18], current_stop_range_mm=[3,22], project_stop_range_mm=[3,18],
             source='https://assets.knipex.net/1240200_en.pdf', local_source='Knipex-1240200.pdf',
             use='Pokrywa0,14..4mm² i zatwierdzone odizolowania7..14mm. Stara i nowa rewizja mają inne ograniczniki; wspólny zakres wystarcza. Dobrać głębokość do dostarczonej izolacji, nie przecinać drucików.'),
        dict(role='heat_shrink', maker='Bosch', sku='06032A6100', quantity=1,
             model='UniversalHeat600 EU', nozzle_settings_C=[50,300,600],
             source='https://www.bosch-diy.com/de/de/p/universalheat-600-06032a6100',
             use='Koszulki grzać na odłączonych przewodach poza PETG i baterią. Nastawa dyszy NIE jest temperaturą materiału; przymierzyć na próbce wg karty wybranej koszulki. Bez płomienia.'),
        dict(role='DC_voltage_and_continuity', maker='UNI-T', sku='UT33D+', quantity=1,
             DC_range_for_cat_V=20, continuity=True, included=['test leads','2×R03'],
             source='https://meters.uni-trend.com/product/ut33plus-series/',
             use='Faza2: polaryzacja/napięcie; ciągłość tylko bez napięcia. COM/VΩ, nigdy wejścieA do szeregowego pomiaru całego kota. Żadnego uruchamiania teraz; nie stosować do instalacji sieciowej.'),
        dict(role='caliper', maker='Bahco', sku='1150D', quantity=1,
             range_mm=[0,150], resolution_mm=.01, catalog_accuracy_mm=.03,
             source='https://www.bahco.com/int_en/precision-measuring-digital-callipers-with-lcd-screen-pb_1150d_.html',
             use='Przymiarka wydruków/wałka/łączników. Rozdzielczość0,01 NIE jest dokładnością0,01 ani potwierdzeniem profilu zębów wieloklinu.'),
        dict(role='hex_socket_screws', maker='Wera', sku='05133163001', quantity=1,
             model='950/9 Hex-Plus3', required_sizes_mm=[1.5,2,2.5], included_sizes_mm=[1.5,2,2.5,3,4,5,6,8,10],
             source='https://hybris-media.wera.de/download/pdfgenerator-datasheets/en/05133163001.pdf', local_source='Wera-950-9.pdf',
             use='DIN912M2/M2,5/M3:1,5/2/2,5mm. Zestaw jest przykładem dostępu; posiadane trzy zgodne klucze wystarczą. Używać prostego końca do końcowego docisku, nie wkrętarki w PETG.'),
    ]
    for sku, AF, OD, nut in [('05118120001',4,5.7,'M2'),('05118124001',5,7,'M2.5'),('05118126001',5.5,7.8,'M3')]:
        tools.append(dict(role='nut_'+nut, maker='Wera', sku=sku, quantity=1,
            model='2069 Micro', AF_mm=AF, catalog_shank_diameter_mm=OD, blade_length_mm=60,
            source='https://hybris-media.wera.de/download/pdfgenerator-datasheets/en/05118120001.pdf', local_source='Wera-2069.pdf',
            use='Nakrętki dostępne przed zamknięciem korpusu; kieszenie zatrzymujące nakrętki nie wymagają wkładania nasadki. Średnica katalogowej klingi nie dowodzi prześwitu całej główki. Nie rozwiercać kieszeni pod nasadkę.'))
    for sku, tip in [('05118020001','PH00'),('05118022001','PH0/JCIS0'),('05118024001','PH1')]:
        tools.append(dict(role='factory_screw_'+tip, maker='Wera', sku=sku, quantity=1,
            model='2050PH Micro', tip=tip,
            source=wera+'en/tools/2050-ph-screwdriver-for-phillips-screws-for-electronic-applications',
            use='Dostęp do małych wkrętów dostawy. Nie zakładać gniazda MG92B z samej średnicy śruby; wybrać pasujący profil przy przymiarce, nie wciskać PH1. PH0 tego SKU jest modyfikowany wg JCIS0.'))
    solder = dict(id='consumable:solder:T0051402499', name='Weller WSW SAC M1 1.0mm100g, T0051402499',
        manufacturer='Weller', manufacturer_sku='T0051402499', planning_quantity=1, unit='spool100g',
        purchase_pack_count=1, stock_per_pack=100, stock_unit='g',
        alloy='Sn96.5Ag3.0Cu0.5', diameter_mm=1, flux_percent=3.5, flux='No-Clean core',
        verified_consumption_g=None, no_separate_flux_required_in_default_set=True,
        source=weller+'us/en/industrial-soldering/products/soldering-wire/wsw-sac-m1-10mm-100g-sn30ag05cu35',
        note='Jeden wspólny zapas do wszystkich lutów, nie jedna rolka na moduł.100g to wybrany standardowy rozmiar opakowania, nie pomiar zużycia. Rdzeń jest topnikiem; nie dokładać osobnej butelki bez potrzeby procesu. Pożyczenie materiału zamiast zakupu dopuszczalne.')
    return dict(status='SELECTED_WORKSHOP_ACCESS_AND_ONE_SOLDER_STOCK_NOT_WHOLE_K3',
        parent='one-batch-prototype-r42', phase1_percent=70, K3_complete=False, W5_complete=False,
        physical_pass=False, no_purchase=True, no_power=True, tools=tools, solder=solder,
        requires_exact_brand_purchase=False, tool_access_confirmed=False,
        access_rule='To jedna lista ról i katalogowych przykładów. Użyć posiadanego/pożyczonego funkcjonalnego odpowiednika o wymaganym zakresie; nie kupować całego warsztatu. Zaciskarki TE nadal według R42, bez przypadkowego zamiennika matrycy.',
        workshop_requirements=[
            dict(role='printed_part_finishing', required='Wiertła2,4/3/6,5mm, stopniowe do24mm oraz gratownik; przymiarka na pustych częściach, średnica tylko wg wybranego interfejsu. Nie wiercić przy zamontowanych przewodach/PCB.', catalog_SKU_selected=False),
            dict(role='holding_and_trim', required='Małe szczypce/pęseta, izolowane miękkie szczęki lub trzecia ręka, nożyczki/obcinaczki do opasek i oplotu. Nie trzymać przewodów kombinerkami za druciki.', catalog_SKU_selected=False),
            dict(role='solder_workspace', required='Niepalna podstawka, odciąg oparów/wentylacja, okulary i osłona sąsiednich powierzchni; wszystko poza robotem i odłączoną baterią.', catalog_SKU_selected=False)],
        optional_phase2_DC_clamp='Pożyczony miernik cęgowy DC≥40A do prób napędów; nie jest częścią potrzebną do samego składania, nie dodano go jako obowiązkowego zakupu.',
        unselected_flux_review=dict(old='MG836-P discontinued; not selected', current='MG836LFNC-P10ml valid alternate, not selected/not extra stock',
            source='https://mgchemicals.com/downloads/tds/tds-836lfnc-p.pdf', local_source='MG-836LFNC-P-TDS.pdf',
            condition='No-Clean marketing and recommended cleaning in TDS coexist; do not treat arbitrary IPA as verified remover. Core solder avoids a default extra chemistry choice.'),
        process_sequence=[
            'Zasilanie odłączone: przymierzyć trasy i końce; założyć koszulki przed wykonaniem końca.',
            'Ściągnąć izolację wg konkretnego końca R42/W5, nie jedną długością dla WAGO, zacisku i lutowania. Próbka dostarczonej linki bez naciętych drucików.',
            'Lutować moduły/splices poza wydrukiem; stały uchwyt, właściwy grot i czyste pola. Temperatura/czas na próbce, nie zgadywany limit dla wszystkich złącz.',
            'Osobno izolować polaryzacje, odciążyć izolację za końcem; nie zalewać lutem zacisków/WAGO. Grot/koszulka nie mogą naruszać sąsiednich pól.',
            'Po ostygnięciu oględziny, ciągłość i brak zwarć bez napięcia. Dopiero później osadzić we wcześniej przygotowanym mocowaniu; uruchomienie dopiero w fazie2.'],
        remaining=['W5: rzeczywiste wybrane trasy i odciążenia wszystkich końców, w tym odrzucone MAIN-positive i W036 oraz12wiązek nóg/balans.',
            'K3: pełny spis cięć/izolacji/opasek i wspólny bilans stanów; ogólne wykończenie/utrzymanie nadal opisane wymaganiami, nie katalogowym kompletem.',
            'K2/E3/A2/A3 nadal otwarte; karta narzędzi nie jest zamknięciem fazy.'])


def build_payload(v, selection, quantities):
    s, q = copy.deepcopy(selection), copy.deepcopy(quantities)
    sid = v['solder']['id']
    assert sid not in {r['id'] for r in q['lines']}
    q['lines'].append(copy.deepcopy(v['solder']))
    # Replace covered generic tool roles, retain crimping and unfinished workshop requirements.
    # Legacy package has mojibake in several labels. Index by stable list position,
    # asserting the unchanged parent rather than rewriting unrelated historical names.
    role_positions={0:'DC_voltage_and_continuity',1:'solder_station',2:'heat_shrink',3:'wire_strip_and_cut',6:'hex_socket_screws',7:'caliper'}
    assert len(q['required_tools_buy_or_borrow'])==9
    for i, role in role_positions.items():
        t=next(t for t in v['tools'] if t['role']==role)
        q['required_tools_buy_or_borrow'][i]=dict(tool=t['maker']+' '+t['sku'], role=role,
            status='Zapewnić dostęp do posiadanego/pożyczonego odpowiednika; nic nie zakupiono.',
            required_for=t['use'], recipe='hardware/electronics/full-cat/assembly-tools-k3-r2/tools.json')
    q['required_tools_buy_or_borrow'][6]['tool']='Imbusy1,5/2/2,5mm; nasadki4/5/5,5mm; fabrycznePH00/PH0/PH1 wg dostawy'
    q['exact_workshop_access_requirements']=copy.deepcopy(v['tools'])
    q['workshop_access_rule']=v['access_rule']
    q['general_workshop_requirements']=copy.deepcopy(v['workshop_requirements'])
    s['assembly_tooling']='hardware/electronics/full-cat/assembly-tools-k3-r2/tools.json'
    s['K3_complete']=False
    assert s['prints']==selection['prints'] and q['lines'][:-1]==quantities['lines']
    return s,q


def main():
    OUT.mkdir(exist_ok=True,parents=True)
    assert not (OUT/'tools.json').exists()
    v=payload()
    v['source_sha256']={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(REF.iterdir()) if p.is_file()}
    v['script_sha256']=sha(Path(__file__))
    v['checked_date']='2026-10-02'
    v['work_start_utc']=START
    v['generated_utc']=datetime.now(timezone.utc).isoformat()
    save(OUT/'tools.json',v)
    print(json.dumps(dict(tool_access_SKUs=len(v['tools']),added_consumable_SKUs=1,K3_complete=False,physical_pass=False)))


if __name__=='__main__':
    main()
