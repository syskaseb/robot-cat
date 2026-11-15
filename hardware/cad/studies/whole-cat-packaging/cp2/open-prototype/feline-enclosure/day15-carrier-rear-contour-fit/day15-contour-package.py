from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,csv,shutil
ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');P=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-carrier-rear-contour-fit';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
g=json.loads((P/'rear-contour-material-and-first-gate.json').read_bytes());h=json.loads((P/'missing-whole-carrier-gate.json').read_bytes());post=json.loads((P/'P05-current-interface-fact.json').read_bytes())
write('bounded-disposition.json',dict(utc=datetime.now(timezone.utc).isoformat(),status='ONE_R5_CONTOUR_S0_CLEAR_CURRENT_H03_AND_P05_HOLD_MEASUREMENT_COUPON_ONLY',actual_first_clock='2026-11-15T19:09:01.0681463Z',one_contour_no_grid=True,derived_R_interval=[3.7391725408681555,5.414213562373095],chosenR5=True,planned_working_floor_stop_loss130p572_not_hidden=True,protected9_actualmembers0missing=True,S0_actual_gap=g['actual_S0_gate']['gap'],S0_common0=True,first_missing_whole_falsifier=h['first_falsifier'],missing_bounds=h['bounds'],missing_exact=len(h['checks']),current_alias_binding='H03_panel_M3x55_1 IS ACTUALcurrentM3x50 complete stack1 (axis110,15 shaft42.52..92.52), notobsolete/namewaiver',retained_P05_actual_common=post['common'],retained_P05_planeX107_Y12to18=True,necessary_rear_wall_band=dict(outerXmax105p75=True,innerX105_afterhalfmmfit=True,width0p75=True,initial_trial_wall2_project_notimmutable=True),no_global_retention_impossibility_claim=True,consequence='Chosencontinuousfullwidthrearwall isunqualifiedatretainedpost. Keepnewdirectroot. Needactualfunctionalendcaptureposition/distribution aroundP05 ORactualpack/revisionmeasurement; no secondcontour/bolt/cellpose inthischunk.',export='ONE8x42x7.2closedpositivebenchMEASUREMENTcouponSTLonly, notinstalledcarrierpart',current_P10_internalPi_not_oldff08_STL=True,P10_P12_P19_largeSTL_not_released=True,initial_cell_opening=dict(actualX40_Y=[-14,16],width30=True,nominalcell35=True,verticaldrop_notaccepted=True,one_order='Cellandwholekit beforeP12closure; rarebatteryremovalneedsrealpartialP12release inclonePi-onP10corner, solderedE1keptwhole, actualfactoryleadparkingFIT2'),remaining_tool_nutfeed_andassembly_andstock_OPEN=True,newdirectroot_fullsteel_material_scope_reused_no1815replay=True,physical_pass=False,whole_kit_ready=False,actual_fit_cut_slack=None))
refs=[]
old=P.parent/'day15-frame-fastening'
for p in sorted(old.glob('*.stl')):
 if any(n in p.name for n in ['P11','P13','P14','P15','P16','P17','P18']):refs.append(dict(path=str(p),sha256=sha(p),status='UNCHANGED_GEOMETRY_REFERENCE_NOT_WHOLEKIT_RELEASE'))
write('current-print-index.json',dict(release='MEASUREMENT_COUPON_ONLY',new_STL=[dict(path='MEASURE_ONLY_rear_floor_endstop_coupon.stl',sha256=sha(P/'MEASURE_ONLY_rear_floor_endstop_coupon.stl'),qty=1,status='BENCH_MEASURE_ONLY_KNOWN_H03_P05_HOLD_DO_NOT_INSTALL_AS_CARRIER')],large_dependencies=[dict(native_object=n,status='CURRENT_NATIVE_ONLY_NO_STL',note='P10internalPi/currentP12source from32ac/89e3, neverinheritoldSTLbyfilename') for n in ['P10_front_gate','P12_common_deck_speaker','P19_shared_lower_carrier']],unchanged_mesh_references=refs,no9meshcopy=True))
sources=[P.parent/'day15-direct-carrier-frame-joint/manifest.json',P.parent/'day15-direct-carrier-frame-joint/direct-carrier.FCStd',P.parent/'day15-p12-integrated-retention/manifest.json',P.parent/'day14-fasttrack-first-fit/fit-kit-ready/parts.json',ROOT/'hardware/electronics/kicad-current/selected-components.csv']
for folder in ['day15-direct-carrier-frame-joint','day15-strapped-carrier-first-fit','day15-head-ola-whole-proposal','day15-p12-integrated-retention']:
 base=P.parent/folder
 for x in json.loads((base/'manifest.json').read_bytes())['files']:
  f=Path(x['path']);f=f if f.is_absolute() else base/f;assert sha(f)==x['sha256'],f
write('source-pins.json',dict(source_commit='89e3c97380b0a1cd314c50e40ff4a1fbee5613f6',previous23_plus20_plus20_plus36_exact_unchanged=True,pins=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sources],sourceworldcopy_not_serialbyteidentity=True,only_activeprint_changed='P19functionalrearcontour and0.5rearfit allowance; fixedroot/P10P12/steel/sourcebody/boards/battery/strapsunchanged',currentH03actualM3x50binding=True,all57_extras_factoryends_protection_preserved=True,no_oldmatrix_replay=True))
for n in ['day15-contour-start.py','day15-contour-missing.py','day15-contour-plot.py']:shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/n,P/n)
with (P/'coupon-and-BOM.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['item','qty','status','notes']);w.writerow(['Rear floor/endstop coupon PETG',1,'BENCH_MEASURE_ONLY','8x42x7.2; closedpositiveSTL; flatfloorZ0; notcarrier']);w.writerow(['WholeP19/currentP12/currentP10',0,'NO_LARGE_STL_RELEASE','Nativecurrentgeometry+sourcepins, P10internalnut isnotoldff08']);w.writerow(['NewdirectISO10642M3x12/nut/washer',1,'UNCONFIRMED_SOURCE89e3_SCOPE_REUSE','No newsteel orrootchange']);w.writerow(['FoundationH03',4,'CURRENT_M3x50_NOT_OBSOLETE','Fullparts/sourcefunction retained']);w.writerow(['Selectedbatterystraps',2,'SAME_FULL_200_UNITS','210includesbuckle; cloth/lap/strengthFIT; notframeclamp'])
(P/'START_HERE.md').write_bytes('''# Tylny obrys carriera — jeden wynik i jeden kupon

**Do pomiaru na stole wydano tylko `MEASURE_ONLY_rear_floor_endstop_coupon.stl` (1szt). Cały carrier pozostaje HOLD. Nie montować kuponu jako części zabezpieczającej baterię.**

Aktualny cały model: `carrier-contour.FCStd`. Najważniejsze źródłowe dane i porównanie obu stron: `actual-rear-two-sided-section.png`. `whole-contour-context.png` jest rzeczywistym widokiem wnętrza. Nowy pionowy węzeł P12/carriera, wszystkie kupne części/pozy i cztery stopy są zachowane. Nie zmieniano głowy/wyglądu ani nie prowadzono nowej rundy recenzji.

## Co zamknięto

Z rzeczywistego walca S0 R28,5/środek(135,5;-29,328917) oraz zapasu1,25 wynika R naroża≥3,739. Nominalne ogniwo, luz przymiarki0,5 i przyjęta do próby użyteczna ścianka2mm dają R≤5,414. Wybrano R5, bez siatki prób. To jeden ciągły obrys tylnej podłogi i roboczego stopera; skrajne X108 pozostawiono, wewnętrzny tył maX105. Naroże ma2,172mm materiału, a rzeczywisty odstęp od pełnego S0 wynosi **1,627055mm/common0/valid**. Jawnie zastąpiono130,572mm³ roboczego starego prostokątnego obrysu; nie ukryto straty materiału.

Dziewięć chronionych rzeczywistych grup (4stopy, tylne ramię, wspólna MTAfloor i3człony nowego korzenia) ma0missing. Nowy pionowy root/pełna stal/parting i Pi4/guide/audio odziedziczone tylko w niezmienionym odebranym zakresie; bez powtórki1815/6 lub dawnych macierzy. Obie całe200opaski pozostają dla baterii, bez udawania kotwy ramy.

## Dlaczego nie ma dużych STL

Pierwszy dotąd nieodebrany sąsiad po tej poprawce: **P19–H03 gap0,5<1,25/common0**. ID `H03_panel_M3x55_1` oznacza obecny **pełny M3x50**, oś(110,15), wałekZ42,52..92,52 — nie wolno go skasować jako starej rezerwy. Zapisany świadek P19 `(108,15,Z60,8/65/68)`.

Ten sam aktualny węzeł ma rzeczywistą podporę `P05_spacer_instance2`: lewa pełna powierzchnia X107, Y12..18/Z48,52..88,52. **Aktualny P19 przecina ją na41,231061mm³**; to nominalny kontakt dwóch obecnych wydruków, nie dopuszczony interfejs ani fizyczny pomiar. Dla pozostawienia1,25 wolnego miejsca zewnętrzna ściana może kończyć się najwyżejX105,75. Przy ogniwie doX104,5 i luzie0,5 zostaje **0,75mm** na ciągłą pełną tylną ściankę w tym pasie; to mniej niż wybrana próbna2mm. To granica tej pełnoszerokiej ścianki, nie dowód niemożliwości innego funkcjonalnego rozłożenia stopów.

Nie ruszono podpory/śruby/S0/ogniwa ani nowego korzenia, nie obniżono marginesu i nie zbudowano drugiego konturu. Następna decyzja: rzeczywiste funkcjonalne zatrzymanie końca baterii **wokół zachowanego P05**, z zachowaniem podparcia, izolacji i całych pasków. Nie kolejny łeb/oś/root ani przypadkowy mikroradius.

## Kupon i konkretny pomiar — dwie osoby

A trzyma rzeczywiste niepodłączone ogniwo lub jego wzornik, B sprawdza kupon na stole: długość i tylny narożnik, luz0,5 i brak nacisku na ogniwo. Kupon jest przycięciem obecnej geometrii,8×42×7,2mm, jedna zamknięta dodatnia siatka, PETG płaskim spodemZ0; lokalna podłoga4,2/stop3mm. Profil drukarki i rzeczywiste tolerancje nieprzypięte. To nie polecenie druku ani odbiór wytrzymałości.

Zmierz rzeczywisty tył ogniwa względem przedniego stopuX−2 oraz pozycję lewego boku P05 w aktualnej rewizji. Ta sama pełnoszeroka ścianka2mm/luz0,5 wymagałaby długości ogniwa≤105,25mm zamiast nominalnych106,5; nie zaliczono takiej różnicy ani nowej wersji baterii na papierze. Nie dociskać znanego kolizyjnego obrysu kuponu do P05. Rzeczywista izolacja/padding/pasek/buckle/lap/masa i nośność pozostają do przymiarki, bez zabierania na nie dostępnego luzu.

## Rzeczywisty otwór wejścia i kolejność

Aktualny przekrój P12 przyX40 ma krawędzieY−14/+16: **otwór30mm, ogniwo nominalnie35mm**. Nie przyjęto pionowego dropin przez zamkniętą ramę. Jedna proponowana kolejność po rozwiązaniu obrysu: dummy/ogniwo i całe paski na otwartym P19 przed rzeczywistym zamknięciem P12, pełne4MTA220/oba końce układane otwarcie przed keeperami, driver/nut przed MAIN/bankami. Pełny feed/tool i cała instalacja pozostają UNRECEIVED poHOLD.

Sporadyczna wymiana może wymagać P15mic -> P13BUS -> rzeczywiste XT60/balance, zwolnienia rzeczywistego roguPi naP10 i mocowań P12, a potem podniesienia całego podpartego zestawu. Nie udawać odpięcia lutowanego E1; realny luz/zasięg końców przy takim podparciu toFIT2 i nadal brak dowodu pełnego wyjmowania. Nie obiecano szybkiego serwisu.

`current-print-index.json` wskazuje WYŁĄCZNIE kupon jako nowy STL. P10 z wewnętrznym Pi-capture/P12/P19 są bieżącymi zależnościami native, nie starymi STL o tych samych nazwach. P11/P13/P14/P15/jaws wskazane przez niezmienione SHA bez kopiowania dziewięciu siatek; nie jest to wholekitGO. Wszystkie57+extras/ochrona/4DATA5plus7G/4niezależne220 i fabryczne końce zachowane. Actualfit/cut/slack=NULL, physicalPASSfalse/wholekitfalse; pozostałe mocowania PCB/bank/audio i korzeń głowy nadal odrębnieOPEN.
'''.encode())
print(json.dumps(dict(prepared=str(P),coupon_only=True,current_H03='M3x50',P05_common=post['common'])))
